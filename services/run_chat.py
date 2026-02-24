from services.transcribe import start_transcribing
from services.get_gpt_res import get_gpt_responce
from tools.memory import save_chat, get_properties, save_properties
from services.play_responce import dub_and_play_responce
from audio.output import play_placeholder_sound
from audio.utils import pick_random_placeholder_sound
import config
import logging
import re

logger = logging.getLogger(__name__)
last_assistant_responce_global = ""

def normalize_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9']+", text.lower()))

def normalize_llm_responce(text: str) -> str:
    # Keep Unicode text so non-ASCII replies do not become empty and get skipped.
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()

def is_echo_like_prompt(user_text: str, last_assistant_text: str) -> bool:
    if not user_text or not last_assistant_text:
        return False

    normalized_user = normalize_text(user_text)
    normalized_assistant = normalize_text(last_assistant_text)
    if not normalized_user or not normalized_assistant:
        return False

    user_words = normalized_user.split()
    assistant_words = normalized_assistant.split()
    if normalized_user == normalized_assistant:
        return True

    if len(user_words) <= 4 and normalized_user in normalized_assistant:
        return True

    if len(user_words) >= 5:
        overlap_words = [word for word in user_words if word in assistant_words]
        overlap_ratio = len(overlap_words) / len(user_words)
        if overlap_ratio >= 0.7:
            return True

    return False

def run_new_chat(transcribing_model, tts):
    global last_assistant_responce_global
    messages = [{"role":"system", "content":config.SYSTEM_PROMT + get_properties()}]
    empty_turns = 0
    last_assistant_responce = last_assistant_responce_global
    logger.info("Started new chat")
    play_placeholder_sound("audio/pointing_sounds/pipip.wav")
    while True:
        transcribtion = start_transcribing(transcribing_model)
        
        if not transcribtion:
            empty_turns += 1
            if empty_turns >= 3:
                break
            logger.info("No clear user promt, listening once more")
            continue
        
        empty_turns = 0

        if is_echo_like_prompt(transcribtion, last_assistant_responce):
            logger.info("Ignored echo-like promt: %s", transcribtion)
            continue
        
        logger.info(f"Transcribed user promt, working on it: {transcribtion}")
        play_placeholder_sound(pick_random_placeholder_sound())
        messages.append({"role": "user", "content": transcribtion})
        llm_responce = normalize_llm_responce(get_gpt_responce(messages))
        if not llm_responce:
            break

        last_assistant_responce = llm_responce
        last_assistant_responce_global = llm_responce

        logger.info("Got LLM responce, streaming it.")
        dub_and_play_responce(tts, llm_responce)

    if len(messages) > 1:
        play_placeholder_sound("audio/pointing_sounds/saved_chat.wav")
        save_chat(messages)
        save_properties(messages)
        logger.info("Saved chat")

