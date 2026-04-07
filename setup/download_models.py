from pathlib import Path
import shutil
import faster_whisper
import openwakeword
from TTS.api import TTS
import config


def _normalize_path(path: str | Path) -> str:
    return Path(path).expanduser().resolve().as_posix()


def _existing_reference_wavs() -> list[str]:
    existing_paths: list[str] = []
    for wav_path in config.REFERENCE_WAVS:
        candidate = Path(wav_path).expanduser()
        if candidate.exists():
            existing_paths.append(candidate.resolve().as_posix())

    if not existing_paths:
        raise RuntimeError(
            "No reference voice samples were found. Reinstall Jarvis package to restore bundled WAV files."
        )

    return existing_paths


def _speaker_candidates(tts) -> list[str]:
    candidates: list[str] = []
    preferred = str(getattr(config, "XTTS_SPEAKER", "Jarvis")).strip()
    if preferred:
        candidates.append(preferred)

    available = getattr(tts, "speakers", None) or []
    for speaker_name in available:
        name = str(speaker_name).strip()
        if not name or name in candidates:
            continue
        candidates.append(name)

    return candidates


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


def _warmup_tts_model() -> tuple[str, str | None]:
    selected_device = config.XTTS_DEVICE
    tts = TTS(config.XTTS_MODEL)
    try:
        tts = tts.to(selected_device)
    except Exception:
        if selected_device.lower() != "cuda":
            raise
        selected_device = "cpu"
        tts = tts.to(selected_device)

    failures: list[str] = []
    for speaker_name in _speaker_candidates(tts):
        try:
            tts.tts(
                text="Hello",
                language=config.LANGUAGE,
                speaker=speaker_name,
            )
            return selected_device, speaker_name
        except Exception as exc:
            failures.append(f"{speaker_name}: {exc}")

    reference_wavs = _existing_reference_wavs()
    try:
        tts.tts(
            text="Hello",
            language=config.LANGUAGE,
            speaker_wav=reference_wavs,
        )
    except Exception as exc:
        speaker_failures = "; ".join(failures[:5]) if failures else "no speaker presets were available"
        raise RuntimeError(
            "XTTS failed to synthesize with built-in speakers and reference WAV fallback. "
            f"Speaker attempts: {speaker_failures}. "
            "If reference WAV fallback is used, ensure FFmpeg is installed."
        ) from exc
    return selected_device, None


def download_required_models() -> dict[str, str]:
    wakeword_path = _download_wakeword_model()
    whisper_path = _download_whisper_model()
    xtts_device, xtts_speaker = _warmup_tts_model()

    config_overrides = {
        "WAKE_WORD_MODEL_PATH": wakeword_path,
        "WHISPER_MODEL_PATH": whisper_path,
        "XTTS_DEVICE": xtts_device,
    }
    if xtts_speaker is not None:
        config_overrides["XTTS_SPEAKER"] = xtts_speaker
    else:
        # Explicit empty value means runtime should use reference_wav cloning.
        config_overrides["XTTS_SPEAKER"] = ""

    config.write_user_config(config_overrides)

    results = {
        "wakeword_path": wakeword_path,
        "whisper_path": whisper_path,
        "xtts_device": xtts_device,
        "config_path": config.user_config_path().as_posix(),
    }
    if xtts_speaker is not None:
        results["xtts_speaker"] = xtts_speaker
    return results


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
    if "xtts_speaker" in results:
        print(f"XTTS speaker: {results['xtts_speaker']}")
    print(f"Saved config: {results['config_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
