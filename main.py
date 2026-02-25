from services.wake import wait_for_wake_word
from services.run_chat import run_new_chat
from models.load_all_models import load_models
from services.local_db import setup_database
from config import LOG_LEVEL
import logging

def setup_logging():
    logging.basicConfig(level=LOG_LEVEL,
                        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                        datefmt="%H:%M:%S"
                        )
    logging.getLogger("faster_whisper").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def run_assistant():
    transcriber_model, wake_model, tts_model = load_models()
    setup_database()
    logger.info("Assistant Started")
    while True:
        wait_for_wake_word(wake_model)
        run_new_chat(transcriber_model, tts_model)

if __name__ == "__main__":
    from jarvis_cli import main as cli_main

    raise SystemExit(cli_main(["run"]))

