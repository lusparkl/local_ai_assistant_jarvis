from pathlib import Path

import openwakeword
from openwakeword.model import Model

import config


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = path.expanduser().as_posix().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _package_jarvis_model_paths() -> list[Path]:
    candidates: list[Path] = []
    for inference_framework in ("onnx", "tflite"):
        try:
            pretrained_paths = openwakeword.get_pretrained_model_paths(inference_framework)
        except Exception:
            continue

        for candidate in pretrained_paths:
            candidate_path = Path(candidate)
            if "jarvis" in candidate_path.name.lower():
                candidates.append(candidate_path)
    return candidates


def _candidate_model_paths() -> list[Path]:
    configured = Path(config.WAKE_WORD_MODEL_PATH).expanduser()
    candidates = [configured]

    if configured.suffix.lower() == ".tflite":
        candidates.append(configured.with_suffix(".onnx"))
    elif configured.suffix.lower() == ".onnx":
        candidates.append(configured.with_suffix(".tflite"))

    candidates.extend(_package_jarvis_model_paths())
    return _dedupe_paths(candidates)


def _framework_for_model(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".onnx":
        return "onnx"
    if suffix == ".tflite":
        return "tflite"
    return "tflite"


def build_wake() -> Model:
    candidate_paths = _candidate_model_paths()
    existing_candidates = [path for path in candidate_paths if path.exists()]
    existing_candidates.sort(key=lambda path: 0 if path.suffix.lower() == ".onnx" else 1)

    if not existing_candidates:
        raise RuntimeError(
            "No wakeword model file found. Run `jarvis setup` to download required models."
        )

    failures: list[str] = []
    for model_path in existing_candidates:
        try:
            return Model(
                wakeword_models=[model_path.as_posix()],
                inference_framework=_framework_for_model(model_path),
            )
        except Exception as exc:
            failures.append(f"{model_path.as_posix()}: {exc}")

    error_details = "; ".join(failures)
    raise RuntimeError(
        "Failed to load wakeword model with available runtimes. "
        "Run `jarvis setup` to refresh models. "
        "If problem persists, install `onnxruntime` (preferred) or `tflite-runtime`. "
        f"Tried: {error_details}"
    )
