import chromadb
import config
import ollama
from services.local_db import get_table_values, insert_into_table
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

_memory_init_error: str | None = None
collection = None

try:
    client = chromadb.PersistentClient(path=config.MEMORY_DB_PATH)
    collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=chromadb.utils.embedding_functions.DefaultEmbeddingFunction(),
    )
except Exception as exc:
    _memory_init_error = str(exc)


def get_collection():
    if collection is None:
        detail = _memory_init_error or "Unknown initialization error."
        raise RuntimeError(
            f"Failed to initialize memory database at {config.MEMORY_DB_PATH}: {detail}"
        )
    return collection

def save_chat(messages: list):
    if collection is None:
        logger.warning("Skipping memory save: %s", _memory_init_error or "memory initialization failed")
        return

    chat = ""
    
    for m in messages:
        chat += f'{m["role"]}: <<{m["content"]}>>' +'\n\n'
    
    try:
        id = str(collection.count() + 1)
    except Exception as exc:
        logger.warning("Skipping memory save due to collection error: %s", exc)
        return

    try:
        tags = ollama.generate(model=config.GPT_MODEL, prompt=config.SUMMARIZING_PROMT+"\n"+chat)["response"]
    except Exception as exc:
        logger.warning("Failed to generate memory tags: %s", exc)
        tags = ""

    metadata = {
        "tags": tags,
        "date": datetime.today().strftime("%Y-%m-%d"),
        "time": datetime.today().strftime("%H:%M")
    }

    try:
        collection.add(ids=[id],documents=[chat], metadatas=[metadata])
    except Exception as exc:
        logger.warning("Failed to persist memory chat: %s", exc)

def save_properties(messages: list):
    chat = ""
    for m in messages:
        chat += f"{m['role']}: <<{m['content']}>>" + "\n\n"

    try:
        new_properties = ollama.generate(model=config.GPT_MODEL, prompt=config.PROPS_PROMT+"\n"+chat)["response"]
    except Exception as exc:
        logger.warning("Skipping properties extraction due to Ollama error: %s", exc)
        return

    try:
        parsed = json.loads(new_properties)
    except Exception as exc:
        logger.warning("Skipping properties extraction due to invalid JSON response: %s", exc)
        return

    if not isinstance(parsed, list):
        logger.warning("Skipping properties extraction because model returned non-list JSON.")
        return

    if parsed:
        for property in parsed:
            if not isinstance(property, dict):
                continue
            title = property.get("title")
            description = property.get("description")
            if not title or not description:
                continue
            insert_into_table("facts", title, description)

def get_properties() -> str:
    props = get_table_values("facts")
    responce = ""
    if props:
        responce = "Here is some additional data about user: \n"
        for prop in props:
            responce += f"{prop[1]}: {prop[2]} \n"
    
    return responce


def retrieve_memory(query: str):
    """When you need additional knowledge, you can use this tool to retrieve chats history with user.
  
    Args:
      query: The user question or the topic of the current chat.

    Returns:
      Chat history with user, that you can use to respond a question.
    """
   
    clean_query = (query or "").strip()
    if not clean_query:
        return "No relevant memory found."

    if collection is None:
        return f"Memory is currently unavailable: {_memory_init_error or 'initialization failed.'}"

    try:
        res_db = collection.query(
            query_texts=[clean_query],
            n_results=5,
            include=["documents", "distances"]
        )
    except Exception as exc:
        logger.warning("Memory query failed: %s", exc)
        return "No relevant memory found."

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
