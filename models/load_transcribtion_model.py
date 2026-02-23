from faster_whisper import WhisperModel
import config
import logging

logger = logging.getLogger(__name__)


def _resolve_whisper_runtime() -> tuple[str, str]:
    device = (config.WHISPER_DEVICE or "").strip().lower() or "cpu"
    compute_type = (config.WHISPER_COMPUTE_TYPE or "").strip().lower() or "int8"
    if device not in {"cpu", "cuda"}:
        device = "cpu"

    try:
        import torch
    except Exception:
        if device == "cuda":
            logger.warning("Whisper requested CUDA, but PyTorch is unavailable. Falling back to CPU.")
        device = "cpu"
    else:
        cuda_available = torch.cuda.is_available()
        if device == "cpu" and cuda_available:
            logger.info("CUDA detected. Switching Whisper device from CPU to CUDA.")
            device = "cuda"

        if device == "cuda" and not cuda_available:
            logger.warning("Whisper requested CUDA, but CUDA is not available. Falling back to CPU.")
            device = "cpu"

    if device == "cpu" and compute_type in {"float16", "bfloat16"}:
        logger.warning("Whisper compute type '%s' is not supported on CPU. Falling back to 'int8'.", compute_type)
        compute_type = "int8"

    return device, compute_type


def build_transcriber() -> WhisperModel:
    device, compute_type = _resolve_whisper_runtime()
    model_hint = (config.WHISPER_MODEL or "").lower()
    if device == "cpu" and "large" in model_hint:
        logger.warning("Whisper model '%s' on CPU may be very slow.", config.WHISPER_MODEL)
    return WhisperModel(
        config.WHISPER_MODEL_PATH,
        device=device,
        compute_type=compute_type,
    )
