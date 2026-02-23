from TTS.api import TTS
import config

def build_tts():
    return TTS(config.XTTS_MODEL).to(config.XTTS_DEVICE)