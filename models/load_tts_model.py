from TTS.api import TTS
import config

def build_tts():
    try:
        return TTS(config.XTTS_MODEL).to(config.XTTS_DEVICE)
    except Exception as exc:
        raise RuntimeError(
            "Failed to load XTTS model. Run `jarvis doctor` and confirm XTTS_DEVICE configuration."
        ) from exc
