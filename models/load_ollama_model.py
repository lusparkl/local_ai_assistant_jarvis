import subprocess
import time
import requests
import ollama
import config
import logging
import shutil

logger = logging.getLogger(__name__)

def start_ollama_server():
    if not shutil.which("ollama"):
        raise RuntimeError("Ollama CLI is not installed or not in PATH. Install Ollama first.")

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=1)
        if response.status_code == 200:
            logger.info("Ollama server is already running.")
            return None
    except requests.exceptions.RequestException:
        pass

    try:
        process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info("Ollama server starting...")

        for _ in range(10):
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=1)
                if response.status_code == 200:
                    logger.info("Ollama server is ready.")
                    return process
            except requests.exceptions.RequestException:
                time.sleep(1)

        process.terminate()
        raise RuntimeError("Ollama server did not respond in time. Start it manually with `ollama serve`.")

    except FileNotFoundError:
        raise RuntimeError("Ollama is not installed or not in PATH.")
    
def start_ollama_model():
    start_ollama_server()
    try:
        ollama.generate(model=config.GPT_MODEL, prompt="responce with just '1'", keep_alive=-1)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to start Ollama model '{config.GPT_MODEL}'. Pull the model with `ollama pull {config.GPT_MODEL}`."
        ) from exc

    logger.info("Ollama model started")
