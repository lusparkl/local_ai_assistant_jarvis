import chromadb
import config
import ollama
from services.local_db import get_table_values, insert_into_table
from datetime import datetime
import json

client = chromadb.PersistentClient(path=config.MEMORY_DB_PATH)
collection = client.get_or_create_collection(name=config.COLLECTION_NAME, 
    embedding_function=chromadb.utils.embedding_functions.DefaultEmbeddingFunction())

def save_chat(messages: list):
    chat = ""
    
    for m in messages:
        chat += f'{m["role"]}: <<{m["content"]}>>' +'\n\n'
    
    id = str(collection.count() + 1)
    tags = ollama.generate(model=config.GPT_MODEL, prompt=config.SUMMARIZING_PROMT+"\n"+chat)["response"]
    metadata = {
        "tags": tags,
        "date": datetime.today().strftime("%Y-%m-%d"),
        "time": datetime.today().strftime("%H:%M")
    }

    collection.add(ids=[id],documents=[chat], metadatas=[metadata])

def save_properties(messages: list):
    chat = ""
    for m in messages:
        chat += f"{m['role']}: <<{m['content']}>>" + "\n\n"

    new_properties = ollama.generate(model=config.GPT_MODEL, prompt=config.PROPS_PROMT+"\n"+chat)["response"]
    parsed = json.loads(new_properties) 
    if parsed:
        for property in parsed:
            title, description = property["title"], property["description"]
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

    res_db = collection.query(
        query_texts=[clean_query],
        n_results=5,
        include=["documents", "distances"]
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
