from openwakeword.model import Model
import config

def build_wake() -> Model:
    try:
        return Model(wakeword_models=[config.WAKE_WORD_MODEL_PATH])
    except Exception as exc:
        raise RuntimeError(
            "Failed to load wakeword model. Run `jarvis setup` and verify WAKE_WORD_MODEL_PATH."
        ) from exc
