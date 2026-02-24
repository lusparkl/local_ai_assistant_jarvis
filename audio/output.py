import queue
from typing import Iterable
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

def tts_stream_audio_chunks(
    tts,
    text_chunks: Iterable[str],
    out_q: queue.Queue,
    speaker: str = "Jarvis",
    language: str = "en",
) -> None:
    # Producer: text chunks -> audio chunks
    for chunk in text_chunks:
        wav = tts.tts(text=chunk, speaker=speaker, language=language)
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
