import numpy as np
import sounddevice as sd
from queue import Empty
from audio.input import t_audio_callback, t_audio_q
from config import (
    SAMPLE_RATE_HZ,
    BLOCK_SEC,
    WINDOW_SEC,
    STEP_SEC,
    ENDPOINT_SILENCE_MS,
    TRANSCRIBTION_STAB_WINDOW,
)
from services.stabilize_transcription import stabilize_transcription, extract_step_words
import logging

logger = logging.getLogger(__name__)

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

def start_transcribing(model):
    block_samples = int(SAMPLE_RATE_HZ * BLOCK_SEC)
    window_samples = int(SAMPLE_RATE_HZ * WINDOW_SEC)
    step_samples = int(SAMPLE_RATE_HZ * STEP_SEC)

    END_SILENCE_SEC = ENDPOINT_SILENCE_MS / 1000.0
    START_TIMEOUT_SEC = 10.0
    MAX_LISTEN_SEC = 20.0

    end_silence_samples = int(END_SILENCE_SEC * SAMPLE_RATE_HZ)
    start_timeout_samples = int(START_TIMEOUT_SEC * SAMPLE_RATE_HZ)
    max_listen_samples = int(MAX_LISTEN_SEC * SAMPLE_RATE_HZ)

    rolling = np.zeros(0, dtype=np.float32)
    since_last_decode = 0
    committed_text = ""
    last_partial_text = ""
    max_partial_words_len = 0
    st_window = []

    speech_started = False
    no_new_words_samples = 0
    total_listen_samples = 0

    clear_t_audio_q()
    logger.info("Listening to transcribe...")
    with sd.InputStream(
        samplerate=SAMPLE_RATE_HZ,
        channels=1,
        dtype="float32",
        blocksize=block_samples,
        callback=t_audio_callback
    ):
        while True:
            block = t_audio_q.get()
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

            segments, _ = model.transcribe(
                rolling,
                beam_size=1,
                vad_filter=True,
                word_timestamps=True,
                condition_on_previous_text=False
            )

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
