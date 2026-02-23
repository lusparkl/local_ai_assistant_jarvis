import subprocess
import time
import requests
import ollama
import config
import logging

logger = logging.getLogger(__name__)

def start_ollama_server():
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

        logger.info("Warning: Ollama server did not respond in time.")
        return process

    except FileNotFoundError:
        logger.error("Error: Ollama is not installed or not in PATH.")
        return None
    
def start_ollama_model():
    start_ollama_server()
    ollama.generate(model=config.GPT_MODEL, prompt="responce with just '1'", keep_alive=-1) # Starting ollama server, that will run till turn pc off(keep_alive=-1)
    logger.info("Ollama model started")