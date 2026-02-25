import json
import os
from pathlib import Path
from typing import Any


def _normalize_path(value: str | Path) -> str:
    return Path(value).expanduser().resolve().as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return data if isinstance(data, dict) else {}


def _auto_cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def _parse_env_value(raw_value: str, default: Any) -> Any:
    if isinstance(default, bool):
        return raw_value.strip().lower() in {"1", "true", "yes", "on"}
    if isinstance(default, int):
        return int(raw_value)
    if isinstance(default, float):
        return float(raw_value)
    if isinstance(default, list):
        candidate = raw_value.strip()
        if candidate.startswith("["):
            parsed = json.loads(candidate)
            if isinstance(parsed, list):
                return parsed
            return default
        return [value.strip() for value in candidate.split(",") if value.strip()]
    return raw_value


PACKAGE_ROOT = Path(__file__).resolve().parent
ASSETS_ROOT = PACKAGE_ROOT / "audio"

DATA_DIR = Path(os.environ.get("JARVIS_HOME", Path.home() / ".jarvis")).expanduser().resolve()
CONFIG_PATH = Path(os.environ.get("JARVIS_CONFIG_PATH", DATA_DIR / "config.json")).expanduser().resolve()
MODELS_DIR = DATA_DIR / "models"
LOCAL_DB_PATH = _normalize_path(DATA_DIR / "local.db")

for runtime_dir in (DATA_DIR, MODELS_DIR, Path(LOCAL_DB_PATH).parent):
    try:
        runtime_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # The preflight command surfaces a clear actionable error if this fails.
        pass

_user_config = _load_json(CONFIG_PATH)
_use_cuda = _auto_cuda_available()
_default_device = "cuda" if _use_cuda else "cpu"


def _setting(key: str, default: Any) -> Any:
    env_key = f"JARVIS_{key}"
    if env_key in os.environ:
        try:
            return _parse_env_value(os.environ[env_key], default)
        except Exception:
            return default

    if key in _user_config:
        return _user_config[key]

    return default


def user_config_path() -> Path:
    return CONFIG_PATH


def write_user_config(overrides: dict[str, Any]) -> Path:
    data = _load_json(CONFIG_PATH)
    data.update(overrides)

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return CONFIG_PATH


def default_wakeword_model_path() -> str:
    return _normalize_path(MODELS_DIR / "wake" / "hey_jarvis_v0.1.tflite")


def default_whisper_model_path() -> str:
    return _normalize_path(MODELS_DIR / "whisper")


def default_reference_wavs() -> list[str]:
    return [
        _normalize_path(ASSETS_ROOT / "reference_sounds" / "jarvis_example_0.wav"),
        _normalize_path(ASSETS_ROOT / "reference_sounds" / "jarvis_example_1.wav"),
        _normalize_path(ASSETS_ROOT / "reference_sounds" / "jarvis_example_2.wav"),
        _normalize_path(ASSETS_ROOT / "reference_sounds" / "jarvis_example_3.wav"),
    ]


# Logging
LOG_LEVEL = str(_setting("LOG_LEVEL", "INFO"))

# Wake Word
WAKE_WORD_MODEL_PATH = _normalize_path(_setting("WAKE_WORD_MODEL_PATH", default_wakeword_model_path()))
WAKE_BLOCK_SEC = float(_setting("WAKE_BLOCK_SEC", 2))
WAKE_TRESHOLD = float(_setting("WAKE_TRESHOLD", 0.5))

# Whisper transcription
WHISPER_MODEL_PATH = _normalize_path(_setting("WHISPER_MODEL_PATH", default_whisper_model_path()))
WHISPER_MODEL = str(_setting("WHISPER_MODEL", "distil-large-v3"))
WHISPER_COMPUTE_TYPE = str(_setting("WHISPER_COMPUTE_TYPE", "float16" if _use_cuda else "int8"))
WHISPER_DEVICE = str(_setting("WHISPER_DEVICE", _default_device))
BLOCK_SEC = float(_setting("BLOCK_SEC", 0.25))
STEP_SEC = float(_setting("STEP_SEC", 0.25))
TRANSCRIBTION_STAB_WINDOW = int(_setting("TRANSCRIBTION_STAB_WINDOW", 2))
WINDOW_SEC = float(_setting("WINDOW_SEC", 7))
ENDPOINT_SILENCE_MS = int(_setting("ENDPOINT_SILENCE_MS", 1500))

# GPT
GPT_MODEL = str(_setting("GPT_MODEL", "qwen3:8b"))
SYSTEM_PROMT = str(
    _setting(
        "SYSTEM_PROMT",
        (
            "You are Jarvis, created by lusparkl, a practical assistant for everyday tasks. "
            "Respond in clear, natural English optimized for text to speech. "
            "Use plain text only: no markdown, no bullet points, no numbering, no asterisks, "
            "no code blocks, no emojis, and no extra blank lines. "
            "Keep replies short, direct, accurate, and useful; add detail only if asked. "
            "Rewrite symbols, formulas, abbreviations, and units into spoken words. "
            "Examples: plus, minus, times, divided by, equals, less than, greater than, squared, cubed; "
            "kilometers per hour, miles per hour, meters per second, degrees Celsius, degrees Fahrenheit, "
            "kilograms, grams, millimeters, centimeters, meters, kilometers, liters, milliliters, "
            "kilowatt hours, watts, volts, percent. "
            "Rewrite shorthand into natural speech, including slash forms and symbols like ampersand and at sign, "
            "based on context. "
            "Read numbers, dates, times, and currency naturally for speech. "
            "If information is uncertain, say so briefly instead of guessing. "
            "Never use emojis."
        ),
    )
)
PROPS_PROMT = str(
    _setting(
        "PROPS_PROMT",
        (
            "You are Jarvis Memory Extractor. "
            "Read the full chat and extract only truly useful new facts about the user that will improve future conversations. "
            "Input may include previously saved memories; do not repeat old facts unless a new message clearly corrects them. "
            "Use only facts explicitly stated by the user, not guesses or assistant claims. "
            "Save long-term, reusable facts such as name, close people, preferences, dislikes, phobias, hobbies, projects, goals, routines, language, location, and important personal context. "
            "Ignore temporary or low-value details like one-time plans, casual small talk, or uncertain information. "
            "Output must be strict JSON only, with no markdown or extra text. "
            "Return an array of objects in this exact shape: [{'title':'...', 'description':'...'}]. "
            "Each object must contain exactly one key-value pair, where the key is a short title and the value is a concise description. "
            "If there is no valuable new memory, return an empty array: []. "
            "Do not output duplicates."
        ),
    )
)

# Memory
MEMORY_DB_PATH = _normalize_path(_setting("MEMORY_DB_PATH", DATA_DIR / "memory"))
COLLECTION_NAME = str(_setting("COLLECTION_NAME", "chat_history"))
SUMMARIZING_PROMT = str(
    _setting(
        "SUMMARIZING_PROMT",
        "Describe the following conversation using only 3 keywords separated by a comma (for example: 'finance, volatility, stocks').",
    )
)

# TTS
XTTS_MODEL = str(_setting("XTTS_MODEL", "xtts_v2"))
REFERENCE_WAVS = [_normalize_path(path) for path in _setting("REFERENCE_WAVS", default_reference_wavs())]
LANGUAGE = str(_setting("LANGUAGE", "en"))
CHUNKS_CHAR_LIMIT = int(_setting("CHUNKS_CHAR_LIMIT", 250))
XTTS_DEVICE = str(_setting("XTTS_DEVICE", _default_device))

# General
SAMPLE_RATE_HZ = int(_setting("SAMPLE_RATE_HZ", 16000))
INPUT_DEVICE = _setting("INPUT_DEVICE", None)
MIC_SAMPLE_RATE_HZ = _setting("MIC_SAMPLE_RATE_HZ", None)

# Built-in sound assets
POINTING_SOUND_PATH = _normalize_path(ASSETS_ROOT / "pointing_sounds" / "pipip.wav")
SAVED_CHAT_SOUND_PATH = _normalize_path(ASSETS_ROOT / "pointing_sounds" / "saved_chat.wav")
THINKING_SOUNDS_DIR = _normalize_path(ASSETS_ROOT / "thinking_sounds")
