import config
import logging

logger = logging.getLogger(__name__)


def _resolve_tts_device() -> str:
    requested_device = (config.XTTS_DEVICE or "").strip().lower()
    if requested_device not in {"cpu", "cuda"}:
        requested_device = "cpu"

    try:
        import torch
    except Exception:
        if requested_device == "cuda":
            logger.warning("XTTS requested CUDA, but PyTorch is unavailable. Falling back to CPU.")
        return requested_device

    cuda_available = torch.cuda.is_available()
    if requested_device == "cpu" and cuda_available:
        logger.info("CUDA detected. Switching XTTS device from CPU to CUDA.")
        return "cuda"

    if requested_device == "cuda" and not cuda_available:
        logger.warning("XTTS requested CUDA, but CUDA is not available. Falling back to CPU.")
        return "cpu"

    return requested_device

def build_tts():
    try:
        from TTS.api import TTS
    except ImportError as exc:
        raise RuntimeError(
            "TTS dependencies are missing. Install PyTorch and Torchaudio in this environment. "
            "If you installed with pipx, run: "
            "pipx inject local-ai-assistant-jarvis torch torchaudio"
        ) from exc

    return TTS(config.XTTS_MODEL).to(_resolve_tts_device())
