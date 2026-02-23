import sounddevice as sd
from queue import Empty
from audio.input import w_audio_callback, w_audio_q
from config import SAMPLE_RATE_HZ, WAKE_TRESHOLD, WAKE_BLOCK_SEC, AUDIO_INPUT_DEVICE
import logging

logger = logging.getLogger(__name__)


def _resolve_input_device():
    if not AUDIO_INPUT_DEVICE:
        return None

    candidate = AUDIO_INPUT_DEVICE.strip()
    if candidate.isdigit():
        return int(candidate)
    return candidate


def clear_w_audio_q():
    while True:
        try:
            w_audio_q.get_nowait()
        except Empty:
            break


def wait_for_wake_word(model):
    block_samples = int(SAMPLE_RATE_HZ * WAKE_BLOCK_SEC)
    input_device = _resolve_input_device()
    clear_w_audio_q()
    if hasattr(model, "reset"):
        try:
            model.reset()
        except Exception:
            pass

    logger.info("Listening to wake word...")
    logger.info("Wake-word input device: %s", input_device if input_device is not None else "default")

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE_HZ,
            channels=1,
            dtype="int16",
            blocksize=block_samples,
            callback=w_audio_callback,
            device=input_device,
        ):
            idle_wait_seconds = 0.0
            while True:
                try:
                    block = w_audio_q.get(timeout=1.0)
                    idle_wait_seconds = 0.0
                except Empty:
                    idle_wait_seconds += 1.0
                    if idle_wait_seconds >= 5.0 and int(idle_wait_seconds) % 5 == 0:
                        logger.warning(
                            "No microphone frames for wake-word stream for %.0f seconds.",
                            idle_wait_seconds,
                        )
                    continue

                prediction = model.predict(block)

                if prediction["hey_jarvis_v0.1"] > WAKE_TRESHOLD:
                    print("Hooray! You called me!")
                    break

                logger.debug(prediction)
    except Exception as exc:
        logger.error("Unable to open wake-word input stream: %s", exc)
