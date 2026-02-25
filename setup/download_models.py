from pathlib import Path
import shutil
import faster_whisper
import openwakeword
from TTS.api import TTS
import config


def _normalize_path(path: str | Path) -> str:
    return Path(path).expanduser().resolve().as_posix()


def _find_jarvis_wakeword_path(inference_framework: str) -> Path:
    for candidate in openwakeword.get_pretrained_model_paths(inference_framework):
        name = Path(candidate).name.lower()
        if "jarvis" in name:
            return Path(candidate)

    raise RuntimeError(
        f"OpenWakeWord download finished but the Jarvis wakeword model was not found for '{inference_framework}'."
    )


def _download_wakeword_model() -> str:
    openwakeword.utils.download_models()

    target_dir = Path(config.MODELS_DIR) / "wake"
    target_dir.mkdir(parents=True, exist_ok=True)

    selected_path: Path | None = None
    copied_any = False
    for inference_framework in ("onnx", "tflite"):
        try:
            source_path = _find_jarvis_wakeword_path(inference_framework)
        except RuntimeError:
            continue

        target_path = target_dir / source_path.name
        shutil.copy2(source_path, target_path)
        copied_any = True
        if source_path.suffix.lower() == ".onnx":
            selected_path = target_path
        elif selected_path is None:
            selected_path = target_path

    if not copied_any or selected_path is None:
        raise RuntimeError(
            "Failed to copy Jarvis wakeword models. Reinstall openwakeword and run setup again."
        )

    return _normalize_path(selected_path)


def _download_whisper_model() -> str:
    output_dir = Path(config.MODELS_DIR) / "whisper"
    output_dir.mkdir(parents=True, exist_ok=True)
    whisper_path = faster_whisper.download_model(
        config.WHISPER_MODEL,
        output_dir=output_dir.as_posix(),
    )
    return _normalize_path(whisper_path)


def _warmup_tts_model() -> str:
    selected_device = config.XTTS_DEVICE
    tts = TTS(config.XTTS_MODEL)
    try:
        tts = tts.to(selected_device)
    except Exception:
        if selected_device.lower() != "cuda":
            raise
        selected_device = "cpu"
        tts = tts.to(selected_device)

    tts.tts_with_vc(
        "Hello",
        language=config.LANGUAGE,
        speaker_wav=config.REFERENCE_WAVS,
        speaker="Jarvis",
    )
    return selected_device


def download_required_models() -> dict[str, str]:
    wakeword_path = _download_wakeword_model()
    whisper_path = _download_whisper_model()
    xtts_device = _warmup_tts_model()

    config.write_user_config(
        {
            "WAKE_WORD_MODEL_PATH": wakeword_path,
            "WHISPER_MODEL_PATH": whisper_path,
            "XTTS_DEVICE": xtts_device,
        }
    )

    return {
        "wakeword_path": wakeword_path,
        "whisper_path": whisper_path,
        "xtts_device": xtts_device,
        "config_path": config.user_config_path().as_posix(),
    }


def main() -> int:
    print("Downloading required models. This can take several minutes.")
    try:
        results = download_required_models()
    except Exception as exc:
        print(f"Model setup failed: {exc}")
        return 1

    print("Model setup complete.")
    print(f"Wakeword model: {results['wakeword_path']}")
    print(f"Whisper model: {results['whisper_path']}")
    print(f"XTTS device: {results['xtts_device']}")
    print(f"Saved config: {results['config_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
