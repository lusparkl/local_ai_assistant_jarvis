from faster_whisper import WhisperModel
import config

def build_transcriber() -> WhisperModel:
    try:
        return WhisperModel(
            config.WHISPER_MODEL_PATH, config.WHISPER_DEVICE, compute_type=config.WHISPER_COMPUTE_TYPE
        )
    except Exception as exc:
        raise RuntimeError(
            "Failed to load Whisper model. Run `jarvis doctor` and `jarvis setup`, then retry."
        ) from exc

