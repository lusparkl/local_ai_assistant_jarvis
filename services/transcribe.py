import numpy as np
import sounddevice as sd
from queue import Empty
from audio.input import t_audio_callback, t_audio_q
from config import (
    SAMPLE_RATE_HZ,
    AUDIO_INPUT_DEVICE,
    BLOCK_SEC,
    WINDOW_SEC,
    STEP_SEC,
    LANGUAGE,
    ENDPOINT_SILENCE_MS,
    TRANSCRIBTION_STAB_WINDOW,
)
from services.stabilize_transcription import stabilize_transcription, extract_step_words
from models.load_transcribtion_model import _resolve_whisper_runtime
import logging

logger = logging.getLogger(__name__)


def _resolve_input_device():
    if not AUDIO_INPUT_DEVICE:
        return None

    candidate = AUDIO_INPUT_DEVICE.strip()
    if candidate.isdigit():
        return int(candidate)
    return candidate


def _log_input_device_diagnostics(device) -> None:
    try:
        default_input, _ = sd.default.device
    except Exception:
        default_input = None

    logger.info(
        "Transcription input device: %s (default input index: %s)",
        device if device is not None else "default",
        default_input,
    )


def clear_t_audio_q():
    dropped = 0
    while True:
        try:
            t_audio_q.get_nowait()
            dropped += 1
        except Empty:
            break

    if dropped:
        logger.debug("Dropped %s stale audio blocks", dropped)


def _resolve_decode_profile() -> tuple[float, float, bool]:
    step_sec = STEP_SEC
    window_sec = WINDOW_SEC
    word_timestamps = True

    device, _ = _resolve_whisper_runtime()
    if device == "cpu":
        # CPU + large whisper models can stall if we decode too often.
        step_sec = max(step_sec, 1.5)
        window_sec = min(window_sec, 3.5)
        word_timestamps = False

    return step_sec, window_sec, word_timestamps


def start_transcribing(model):
    block_samples = int(SAMPLE_RATE_HZ * BLOCK_SEC)
    decode_step_sec, decode_window_sec, use_word_timestamps = _resolve_decode_profile()
    window_samples = int(SAMPLE_RATE_HZ * decode_window_sec)
    step_samples = int(SAMPLE_RATE_HZ * decode_step_sec)

    end_silence_sec = ENDPOINT_SILENCE_MS / 1000.0
    start_timeout_sec = 10.0
    max_listen_sec = 20.0
    queue_wait_sec = 1.0

    end_silence_samples = int(end_silence_sec * SAMPLE_RATE_HZ)
    start_timeout_samples = int(start_timeout_sec * SAMPLE_RATE_HZ)
    max_listen_samples = int(max_listen_sec * SAMPLE_RATE_HZ)

    rolling = np.zeros(0, dtype=np.float32)
    since_last_decode = 0
    committed_text = ""
    last_partial_text = ""
    max_partial_words_len = 0
    st_window = []

    speech_started = False
    no_new_words_samples = 0
    total_listen_samples = 0
    idle_wait_seconds = 0.0

    input_device = _resolve_input_device()
    clear_t_audio_q()
    logger.info("Listening to transcribe...")
    _log_input_device_diagnostics(input_device)
    logger.info(
        "Transcription decode profile: step=%.2fs, window=%.2fs, word_timestamps=%s",
        decode_step_sec,
        decode_window_sec,
        use_word_timestamps,
    )

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE_HZ,
            channels=1,
            dtype="float32",
            blocksize=block_samples,
            callback=t_audio_callback,
            device=input_device,
        ):
            while True:
                try:
                    block = t_audio_q.get(timeout=queue_wait_sec)
                    idle_wait_seconds = 0.0
                except Empty:
                    idle_wait_seconds += queue_wait_sec
                    if idle_wait_seconds >= 5.0 and int(idle_wait_seconds) % 5 == 0:
                        logger.warning(
                            "No microphone frames received for %.0f seconds. "
                            "Check microphone permissions and selected input device.",
                            idle_wait_seconds,
                        )
                    if idle_wait_seconds >= start_timeout_sec:
                        return False
                    continue

                total_listen_samples += block.size

                if speech_started:
                    no_new_words_samples += block.size

                rolling = np.concatenate([rolling, block])
                if rolling.size > window_samples:
                    rolling = rolling[-window_samples:]

                since_last_decode += block.size
                if since_last_decode < step_samples:
                    if speech_started and no_new_words_samples >= end_silence_samples and committed_text.strip():
                        return committed_text.strip()
                    if speech_started and no_new_words_samples >= end_silence_samples and last_partial_text.strip():
                        return last_partial_text.strip()
                    if not speech_started and total_listen_samples >= start_timeout_samples:
                        return False
                    if total_listen_samples >= max_listen_samples:
                        if committed_text.strip():
                            return committed_text.strip()
                        if last_partial_text.strip():
                            return last_partial_text.strip()
                        return False
                    continue
                since_last_decode = 0

                try:
                    segments, _ = model.transcribe(
                        rolling,
                        beam_size=1,
                        vad_filter=True,
                        word_timestamps=use_word_timestamps,
                        language=LANGUAGE,
                        condition_on_previous_text=False,
                    )
                except Exception as exc:
                    logger.warning("Transcription decode failed, skipping current step: %s", exc)
                    continue

                partial_words = extract_step_words(segments)
                if partial_words and len(partial_words) > max_partial_words_len:
                    partial_text = " ".join(getattr(segment, "text", "").strip() for segment in segments).strip()
                    last_partial_text = partial_text if partial_text else " ".join(partial_words)
                    max_partial_words_len = len(partial_words)
                    speech_started = True
                    no_new_words_samples = 0

                new_chunk, new_committed_text = stabilize_transcription(
                    segments,
                    committed_text,
                    st_window,
                    window_size=TRANSCRIBTION_STAB_WINDOW,
                )
                if new_committed_text != committed_text:
                    committed_text = new_committed_text
                    max_partial_words_len = max(max_partial_words_len, len(committed_text.split()))
                    speech_started = True
                    no_new_words_samples = 0
                    if new_chunk:
                        logger.debug("Committed chunk: %s", new_chunk)

                if speech_started and no_new_words_samples >= end_silence_samples and committed_text.strip():
                    return committed_text.strip()
                if speech_started and no_new_words_samples >= end_silence_samples and last_partial_text.strip():
                    return last_partial_text.strip()

                if not speech_started and total_listen_samples >= start_timeout_samples:
                    return False

                if total_listen_samples >= max_listen_samples:
                    if committed_text.strip():
                        return committed_text.strip()
                    if last_partial_text.strip():
                        return last_partial_text.strip()
                    return False
    except Exception as exc:
        logger.error("Unable to open transcription input stream: %s", exc)
        return False
