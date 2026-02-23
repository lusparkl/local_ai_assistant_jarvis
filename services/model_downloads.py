from pathlib import Path
import os
import config


def _pick_jarvis_wake_path(paths: list[str]) -> str:
    for path in paths:
        lower_path = path.lower()
        if "jarvis" in lower_path and lower_path.endswith(".tflite"):
            return path
    for path in paths:
        if path.lower().endswith(".tflite"):
            return path
    raise RuntimeError("No wake-word model path returned by openwakeword.")


def download_runtime_models(
    whisper_model: str | None = None,
    models_root: str | Path | None = None,
) -> dict[str, str]:
    import faster_whisper
    import openwakeword

    model_name = whisper_model or config.WHISPER_MODEL
    root = Path(models_root) if models_root else (Path(config.DATA_DIR) / "models")
    openwakeword_dir = root / "openwakeword"
    whisper_dir = root / "whisper"

    openwakeword_dir.mkdir(parents=True, exist_ok=True)
    whisper_dir.mkdir(parents=True, exist_ok=True)

    previous_openwakeword_dir = os.getenv("OPENWAKEWORD_MODEL_DIR")
    os.environ["OPENWAKEWORD_MODEL_DIR"] = str(openwakeword_dir)
    try:
        openwakeword.utils.download_models(["hey jarvis"])
        wake_path = _pick_jarvis_wake_path(openwakeword.get_pretrained_model_paths())
    finally:
        if previous_openwakeword_dir is None:
            os.environ.pop("OPENWAKEWORD_MODEL_DIR", None)
        else:
            os.environ["OPENWAKEWORD_MODEL_DIR"] = previous_openwakeword_dir

    whisper_path = faster_whisper.download_model(model_name, str(whisper_dir))

    return {
        "wake_word_model_path": str(Path(wake_path).resolve()),
        "whisper_model_path": str(Path(whisper_path).resolve()),
    }
