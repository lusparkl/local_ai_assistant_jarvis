from config import CHUNKS_CHAR_LIMIT
from pathlib import Path
from random import randint

def list_get(list: list, i: int, default):
    return list[i] if i < len(list) else default

def split_text_into_sentences(text: str) -> list:
    splited = text.strip().split("\n")
    sentences = []
    for par in splited:
        if par:
            par = par.strip()
            if len(par) < CHUNKS_CHAR_LIMIT:
                sentences.append(par.strip())
            else:
                sentences.extend(par.split("."))
            
    return sentences

def cut_responce_to_text_chunks(llm_responce: str) -> list:
    sentences = split_text_into_sentences(llm_responce)
    curr = ""
    chunks = []
    for i in range(len(sentences)):
        curr = f"{curr} {sentences[i]}"

        next_iter_len = len(f"{curr} {list_get(sentences, i+1, ' ')}")
        if next_iter_len < CHUNKS_CHAR_LIMIT and i != len(sentences)-1:
            continue

        chunks.append(curr)
        curr = ""
    
    return chunks

def list_files(folder_path):
    try:
        p = Path(folder_path)
        if not p.is_dir():
            raise NotADirectoryError(f"'{folder_path}' there is no placeholder sounds yet, please generate them with utils/create_plaseholder_sounds.py.")

        return [file.name for file in p.iterdir() if file.is_file()]

    except Exception as e:
        print(f"Error: {e}")
        return []

def pick_random_placeholder_sound() -> str:
    sounds = list_files("audio/thinking_sounds")
    path = f"audio/thinking_sounds/{sounds[randint(0, len(sounds) - 1)]}"
    
    return path
