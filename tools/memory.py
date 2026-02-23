from __future__ import annotations

from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any

import config
import ollama
from services.local_db import get_table_values, insert_into_table

logger = logging.getLogger(__name__)

_collection: Any | None = None
_memory_init_error: Exception | None = None


def _get_collection():
    global _collection, _memory_init_error

    if _collection is not None:
        return _collection

    if _memory_init_error is not None:
        return None

    try:
        import chromadb

        Path(config.MEMORY_DB_PATH).mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=config.MEMORY_DB_PATH)
        _collection = client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            embedding_function=chromadb.utils.embedding_functions.DefaultEmbeddingFunction(),
        )
        return _collection
    except Exception as exc:
        _memory_init_error = exc
        logger.warning("Memory store is disabled: %s", exc)
        return None


def save_chat(messages: list):
    collection = _get_collection()
    if collection is None:
        return

    chat = ""
    for message in messages:
        chat += f'{message["role"]}: <<{message["content"]}>>' + "\n\n"

    chat_id = str(collection.count() + 1)
    tags = ollama.generate(
        model=config.GPT_MODEL,
        prompt=config.SUMMARIZING_PROMT + "\n" + chat,
    )["response"]
    metadata = {
        "tags": tags,
        "date": datetime.today().strftime("%Y-%m-%d"),
        "time": datetime.today().strftime("%H:%M"),
    }

    collection.add(ids=[chat_id], documents=[chat], metadatas=[metadata])


def save_properties(messages: list):
    chat = ""
    for message in messages:
        chat += f"{message['role']}: <<{message['content']}>>" + "\n\n"

    raw_properties = ollama.generate(
        model=config.GPT_MODEL,
        prompt=config.PROPS_PROMT + "\n" + chat,
    )["response"]

    try:
        parsed = json.loads(raw_properties)
    except json.JSONDecodeError:
        logger.warning("Skipping properties save: extractor returned non-JSON output.")
        return

    if not isinstance(parsed, list):
        logger.warning("Skipping properties save: extractor output is not a JSON array.")
        return

    for item in parsed:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip()
        description = str(item.get("description", "")).strip()
        if not title or not description:
            continue

        insert_into_table("facts", title, description)


def get_properties() -> str:
    props = get_table_values("facts")
    response = ""
    if props:
        response = "Here is some additional data about user: \n"
        for prop in props:
            response += f"{prop[1]}: {prop[2]} \n"

    return response


def retrieve_memory(query: str):
    """When you need additional knowledge, you can use this tool to retrieve chats history with user.

    Args:
      query: The user question or the topic of the current chat.

    Returns:
      Chat history with user, that you can use to respond a question.
    """

    collection = _get_collection()
    if collection is None:
        return "No relevant memory found."

    clean_query = (query or "").strip()
    if not clean_query:
        return "No relevant memory found."

    res_db = collection.query(
        query_texts=[clean_query],
        n_results=5,
        include=["documents", "distances"],
    )

    documents = res_db.get("documents", [[]])[0]
    distances = res_db.get("distances", [[]])[0]

    selected_docs = []
    for doc, distance in zip(documents, distances):
        if distance is not None and distance > 1.25:
            continue

        clean_doc = (doc or "").strip()
        if clean_doc:
            selected_docs.append(clean_doc)

        if len(selected_docs) >= 3:
            break

    if not selected_docs:
        return "No relevant memory found."

    history = "\n\n".join(selected_docs).replace("\n", " ").strip()
    if len(history) > 1500:
        history = history[:1500].rstrip() + "..."

    return history
