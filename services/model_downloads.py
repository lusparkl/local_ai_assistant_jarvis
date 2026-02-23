from pathlib import Path
import os
import config

JARVIS_WAKE_MODEL_FILENAME = "hey_jarvis_v0.1.tflite"
JARVIS_WAKE_MODEL_NAMES = ("hey_jarvis_v0.1", "hey jarvis")


def _pick_jarvis_wake_path(paths: list[str], openwakeword_dir: Path) -> str:
    expected_model_path = openwakeword_dir / JARVIS_WAKE_MODEL_FILENAME
    if expected_model_path.exists():
        return str(expected_model_path.resolve())

    for path in paths:
        resolved = Path(path).resolve()
        name = resolved.name.lower()
        if "jarvis" in name and name.endswith(".tflite"):
            return str(resolved)

    for path in openwakeword_dir.glob("*jarvis*.tflite"):
        return str(path.resolve())

    raise RuntimeError(
        "Jarvis wake-word model was not found. "
        f"Expected '{JARVIS_WAKE_MODEL_FILENAME}' under '{openwakeword_dir}'."
    )


def download_runtime_models(
    whisper_model: str | None = None,
    models_root: str | Path | None = None,
) -> dict[str, str]:
    import faster_whisper
    import openwakeword

    whisper_model_name = whisper_model or config.WHISPER_MODEL
    root = Path(models_root) if models_root else (Path(config.DATA_DIR) / "models")
    openwakeword_dir = root / "openwakeword"
    whisper_dir = root / "whisper"

    openwakeword_dir.mkdir(parents=True, exist_ok=True)
    whisper_dir.mkdir(parents=True, exist_ok=True)

    previous_openwakeword_dir = os.getenv("OPENWAKEWORD_MODEL_DIR")
    os.environ["OPENWAKEWORD_MODEL_DIR"] = str(openwakeword_dir)
    try:
        for wake_model_name in JARVIS_WAKE_MODEL_NAMES:
            try:
                openwakeword.utils.download_models([wake_model_name])
            except Exception:
                continue

        wake_path = _pick_jarvis_wake_path(
            openwakeword.get_pretrained_model_paths(),
            openwakeword_dir,
        )
    finally:
        if previous_openwakeword_dir is None:
            os.environ.pop("OPENWAKEWORD_MODEL_DIR", None)
        else:
            os.environ["OPENWAKEWORD_MODEL_DIR"] = previous_openwakeword_dir

    whisper_path = faster_whisper.download_model(whisper_model_name, str(whisper_dir))

    return {
        "wake_word_model_path": str(Path(wake_path).resolve()),
        "whisper_model_path": str(Path(whisper_path).resolve()),
    }
