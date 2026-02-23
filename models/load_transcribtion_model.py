from faster_whisper import WhisperModel
import config

def build_transcriber() -> WhisperModel:
    return WhisperModel(
        config.WHISPER_MODEL_PATH, config.WHISPER_DEVICE, compute_type=config.WHISPER_COMPUTE_TYPE
    )

