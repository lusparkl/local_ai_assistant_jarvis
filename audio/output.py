import queue
from typing import Iterable
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import config


def _speaker_candidates(tts, preferred: str | None) -> list[str]:
    candidates: list[str] = []
    if preferred:
        normalized = str(preferred).strip()
        if normalized:
            candidates.append(normalized)

    available = getattr(tts, "speakers", None) or []
    for name in available:
        normalized = str(name).strip()
        if not normalized or normalized in candidates:
            continue
        candidates.append(normalized)

    return candidates


def _missing_voice_file_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "voice file" in message and "not found" in message


def tts_stream_audio_chunks(
    tts,
    text_chunks: Iterable[str],
    out_q: queue.Queue,
    speaker: str | None = None,
    language: str = "en",
    speaker_wav: str | list[str] | None = None,
) -> None:
    # Producer: text chunks -> audio chunks
    configured_speaker = speaker if speaker is not None else str(getattr(config, "XTTS_SPEAKER", "Jarvis")).strip() or None
    effective_speaker_wav = speaker_wav
    if effective_speaker_wav is None and not configured_speaker:
        effective_speaker_wav = config.REFERENCE_WAVS

    for chunk in text_chunks:
        wav = None
        last_error: Exception | None = None

        for candidate in _speaker_candidates(tts, configured_speaker):
            try:
                wav = tts.tts(text=chunk, speaker=candidate, language=language)
                break
            except Exception as exc:
                last_error = exc
                if not _missing_voice_file_error(exc):
                    break

        if wav is None and effective_speaker_wav:
            try:
                wav = tts.tts(text=chunk, speaker_wav=effective_speaker_wav, language=language)
            except Exception as exc:
                last_error = exc

        if wav is None:
            if last_error is not None:
                raise last_error
            raise RuntimeError("XTTS could not synthesize audio with current speaker configuration.")

        wav = np.asarray(wav, dtype=np.float32)
        out_q.put(wav)

    out_q.put(None)


def play_streamed_audio_chunks_outputstream(
    in_q: queue.Queue,
    sample_rate: int = 24000,
) -> None:
    while True:
        item = in_q.get()

        if item is None:
            break

        audio = np.asarray(item, dtype=np.float32)
        if audio.size == 0:
            continue

        if audio.ndim == 2 and audio.shape[0] == 1 and audio.shape[1] > 1:
            audio = audio.ravel()
        elif audio.ndim > 1:
            audio = audio.mean(axis=1)

        sd.play(audio, sample_rate, blocking=True)


def play_placeholder_sound(wav) -> None:
    sample_rate, audio = wavfile.read(wav)
    
    sd.play(audio, sample_rate)
