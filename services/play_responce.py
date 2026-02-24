import queue
import threading
from audio.utils import cut_responce_to_text_chunks
from audio.output import tts_stream_audio_chunks, play_streamed_audio_chunks_outputstream



def dub_and_play_responce(tts, text):
    q = queue.Queue()
    chunks = cut_responce_to_text_chunks(text)
    if not chunks:
        cleaned = (text or "").strip()
        if cleaned:
            chunks = [cleaned]
        else:
            return

    producer = threading.Thread(
        target=tts_stream_audio_chunks,
        args=(tts, chunks, q),
        kwargs={"speaker": "Jarvis", "language": "en"},
        daemon=True,
    )
    producer.start()

    play_streamed_audio_chunks_outputstream(q, sample_rate=24000)
    producer.join()
