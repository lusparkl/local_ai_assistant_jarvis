from dataclasses import dataclass, field
import importlib
from pathlib import Path
import shutil
import subprocess
import sys
import os

import config


@dataclass
class PreflightIssue:
    title: str
    detail: str


@dataclass
class PreflightReport:
    errors: list[PreflightIssue] = field(default_factory=list)
    warnings: list[PreflightIssue] = field(default_factory=list)
    infos: list[PreflightIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add_error(self, title: str, detail: str) -> None:
        self.errors.append(PreflightIssue(title=title, detail=detail))

    def add_warning(self, title: str, detail: str) -> None:
        self.warnings.append(PreflightIssue(title=title, detail=detail))

    def add_info(self, title: str, detail: str) -> None:
        self.infos.append(PreflightIssue(title=title, detail=detail))


def _check_python(report: PreflightReport) -> None:
    version = sys.version_info
    if (version.major, version.minor) < (3, 11) or (version.major, version.minor) >= (3, 14):
        report.add_error(
            "Python version",
            f"Detected Python {version.major}.{version.minor}. Use Python >=3.11 and <3.14.",
        )
        return

    report.add_info("Python version", f"Python {version.major}.{version.minor} is supported.")


def _check_dependencies(report: PreflightReport) -> None:
    required_imports = [
        ("faster_whisper", "faster-whisper"),
        ("TTS", "coqui-tts"),
        ("transformers", "transformers"),
        ("torch", "torch"),
        ("torchaudio", "torchaudio"),
        ("torchvision", "torchvision"),
        ("sounddevice", "sounddevice"),
        ("openwakeword", "openwakeword"),
        ("dotenv", "python-dotenv"),
        ("ollama", "ollama"),
        ("chromadb", "chromadb"),
        ("pyperclip", "pyperclip"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("requests", "requests"),
    ]

    missing = []
    for import_name, package_name in required_imports:
        try:
            importlib.import_module(import_name)
        except Exception:
            missing.append(package_name)

    if missing:
        unique_missing = sorted(set(missing))
        report.add_error(
            "Missing Python dependencies",
            "Could not import: "
            + ", ".join(unique_missing)
            + ". Reinstall Jarvis with pipx and include CUDA index if needed.",
        )
        return

    report.add_info("Python dependencies", "All required Python packages are importable.")

    try:
        import pyperclip

        if not pyperclip.is_available():
            report.add_warning(
                "Clipboard backend",
                "pyperclip is installed but no clipboard backend was found on this system.",
            )
    except Exception:
        # Already covered by missing dependency check.
        pass


def _check_runtime_paths(report: PreflightReport) -> None:
    runtime_paths = [
        ("Jarvis home", Path(config.DATA_DIR)),
        ("Models directory", Path(config.MODELS_DIR)),
        ("Memory DB directory", Path(config.MEMORY_DB_PATH)),
        ("Local DB directory", Path(config.LOCAL_DB_PATH).parent),
    ]

    for label, path in runtime_paths:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            report.add_error(label, f"Cannot create/access '{path.as_posix()}': {exc}")

    if not report.errors:
        report.add_info("Runtime paths", f"Using data directory: {Path(config.DATA_DIR).as_posix()}")


def _check_audio_assets(report: PreflightReport) -> None:
    required_files = [
        ("Wake sound", Path(config.POINTING_SOUND_PATH)),
        ("Saved chat sound", Path(config.SAVED_CHAT_SOUND_PATH)),
    ]

    for wav_path in config.REFERENCE_WAVS:
        required_files.append(("Reference voice sample", Path(wav_path)))

    for label, path in required_files:
        if not path.exists():
            report.add_error(
                label,
                f"Required audio file is missing: {path.as_posix()}. Reinstall Jarvis package.",
            )

    thinking_dir = Path(config.THINKING_SOUNDS_DIR)
    if not thinking_dir.is_dir():
        report.add_error(
            "Thinking sounds",
            f"Required directory is missing: {thinking_dir.as_posix()}. Reinstall Jarvis package.",
        )
    else:
        wav_count = len(list(thinking_dir.glob("*.wav")))
        if wav_count == 0:
            report.add_error(
                "Thinking sounds",
                f"No .wav files found in {thinking_dir.as_posix()}.",
            )


def _check_model_paths(report: PreflightReport) -> None:
    wakeword_model = Path(config.WAKE_WORD_MODEL_PATH)
    if not wakeword_model.exists():
        report.add_error(
            "Wakeword model",
            "Wakeword model is missing. Run `jarvis setup` to download required models.",
        )

    whisper_path = Path(config.WHISPER_MODEL_PATH)
    if not whisper_path.exists():
        report.add_error(
            "Whisper model",
            "Whisper model is missing. Run `jarvis setup` to download required models.",
        )
    elif whisper_path.is_dir() and not any(whisper_path.iterdir()):
        report.add_error(
            "Whisper model",
            f"Whisper model directory is empty: {whisper_path.as_posix()}. Run `jarvis setup`.",
        )


def _check_audio_devices(report: PreflightReport) -> None:
    try:
        import sounddevice as sd
        from audio.device import resolve_input_stream_settings
    except Exception:
        # Already covered by dependency checks.
        return

    try:
        devices = sd.query_devices()
    except Exception as exc:
        report.add_error("Audio devices", f"Could not query audio devices: {exc}")
        return

    input_devices = [index for index, info in enumerate(devices) if info.get("max_input_channels", 0) > 0]
    output_devices = [index for index, info in enumerate(devices) if info.get("max_output_channels", 0) > 0]

    if not input_devices:
        report.add_error("Microphone", "No input device detected. Connect a microphone.")
    else:
        for dtype in ("int16", "float32"):
            try:
                resolve_input_stream_settings(
                    target_sample_rate=config.SAMPLE_RATE_HZ,
                    channels=1,
                    dtype=dtype,
                )
            except Exception as exc:
                report.add_error(
                    "Microphone settings",
                    f"Could not validate microphone stream settings for dtype '{dtype}': {exc}",
                )
                break

    if not output_devices:
        report.add_error("Speaker", "No output device detected. Connect speakers/headphones.")
    else:
        try:
            output_device = sd.default.device[1]
            if output_device is None or int(output_device) < 0:
                output_device = output_devices[0]

            sd.check_output_settings(
                device=output_device,
                samplerate=24000,
                channels=1,
                dtype="float32",
            )
        except Exception as exc:
            report.add_warning(
                "Speaker settings",
                f"Default output device failed validation at 24kHz mono float32: {exc}",
            )


def _check_memory_database(report: PreflightReport) -> None:
    if any(issue.title == "Missing Python dependencies" for issue in report.errors):
        return

    try:
        from tools.memory import collection

        collection.count()
        report.add_info("Memory database", "ChromaDB collection is accessible.")
    except Exception as exc:
        report.add_error(
            "Memory database",
            f"Failed to initialize memory database at {config.MEMORY_DB_PATH}: {exc}",
        )


def _check_cuda(report: PreflightReport) -> None:
    try:
        import torch
    except Exception:
        return

    needs_cuda = config.WHISPER_DEVICE.lower() == "cuda" or config.XTTS_DEVICE.lower() == "cuda"
    cuda_available = bool(torch.cuda.is_available())
    if needs_cuda and not cuda_available:
        report.add_error(
            "CUDA runtime",
            "Config requests CUDA, but CUDA is unavailable. Set WHISPER_DEVICE/XTTS_DEVICE to 'cpu' or install CUDA-compatible torch.",
        )
    elif needs_cuda and cuda_available:
        report.add_info("CUDA runtime", f"CUDA available with torch {torch.__version__}.")
    elif cuda_available:
        report.add_warning(
            "CUDA runtime",
            "CUDA is available but config is set to CPU. This is valid but slower.",
        )


def _parse_ollama_models(stdout: str) -> set[str]:
    models: set[str] = set()
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("name"):
            continue
        model_name = stripped.split()[0]
        if model_name:
            models.add(model_name)
    return models


def _check_ollama(report: PreflightReport) -> None:
    ollama_cli = shutil.which("ollama")
    if not ollama_cli:
        report.add_error(
            "Ollama CLI",
            "Ollama is not installed or not in PATH. Install Ollama from https://ollama.com/download.",
        )
        return

    try:
        proc = subprocess.run(
            [ollama_cli, "list"],
            capture_output=True,
            text=True,
            timeout=12,
            check=False,
        )
    except Exception as exc:
        report.add_error("Ollama CLI", f"Could not execute `ollama list`: {exc}")
        return

    output = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        report.add_error(
            "Ollama server",
            "Ollama command failed. Start server with `ollama serve` and retry.",
        )
        return

    installed_models = _parse_ollama_models(output)
    if config.GPT_MODEL not in installed_models:
        report.add_error(
            "Ollama model",
            f"Model '{config.GPT_MODEL}' is not pulled. Run `ollama pull {config.GPT_MODEL}`.",
        )
    else:
        report.add_info("Ollama model", f"Configured model '{config.GPT_MODEL}' is available.")


def _check_weather_api(report: PreflightReport) -> None:
    weather_key = os.environ.get("WEATHER_API_KEY")
    if not weather_key:
        try:
            from dotenv import load_dotenv

            load_dotenv()
            load_dotenv(Path(config.DATA_DIR) / ".env")
            weather_key = os.environ.get("WEATHER_API_KEY")
        except Exception:
            weather_key = None

    if not weather_key:
        report.add_warning(
            "Weather tool",
            "WEATHER_API_KEY is not set. Weather tools will fail until you set this env var.",
        )


def run_preflight() -> PreflightReport:
    report = PreflightReport()
    _check_python(report)
    _check_dependencies(report)
    _check_runtime_paths(report)
    _check_memory_database(report)
    _check_audio_assets(report)
    _check_model_paths(report)
    _check_audio_devices(report)
    _check_cuda(report)
    _check_ollama(report)
    _check_weather_api(report)
    return report


def format_preflight_report(report: PreflightReport) -> str:
    lines = ["Jarvis preflight report:"]

    if report.errors:
        lines.append(f"Errors ({len(report.errors)}):")
        for issue in report.errors:
            lines.append(f"- {issue.title}: {issue.detail}")

    if report.warnings:
        lines.append(f"Warnings ({len(report.warnings)}):")
        for issue in report.warnings:
            lines.append(f"- {issue.title}: {issue.detail}")

    if report.infos:
        lines.append(f"Checks passed ({len(report.infos)}):")
        for issue in report.infos:
            lines.append(f"- {issue.title}: {issue.detail}")

    if report.ok:
        lines.append("Status: OK")
    else:
        lines.append("Status: FAILED")

    return "\n".join(lines)


def ensure_preflight() -> PreflightReport:
    report = run_preflight()
    if not report.ok:
        raise RuntimeError(format_preflight_report(report))
    return report
