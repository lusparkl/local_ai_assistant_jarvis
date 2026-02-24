import numpy as np
import sounddevice as sd
from queue import Empty
from audio.input import w_audio_callback, w_audio_q
from audio.device import resolve_input_stream_settings
from audio.resample import resample_block
from config import SAMPLE_RATE_HZ, WAKE_TRESHOLD, WAKE_BLOCK_SEC
import logging

logger = logging.getLogger(__name__)

def clear_w_audio_q():
    while True:
        try:
            w_audio_q.get_nowait()
        except Empty:
            break

def wait_for_wake_word(model):
    input_device, input_sample_rate = resolve_input_stream_settings(
        target_sample_rate=SAMPLE_RATE_HZ,
        channels=1,
        dtype="int16",
    )
    block_samples = int(input_sample_rate * WAKE_BLOCK_SEC)
    clear_w_audio_q()
    if hasattr(model, "reset"):
        try:
            model.reset()
        except Exception:
            pass

    logger.info("Listening to wake word...")
    with sd.InputStream(
        samplerate=input_sample_rate,
        device=input_device,
        channels=1,
        dtype="int16",
        blocksize=block_samples,
        callback=w_audio_callback
    ):
        while True:
            block = w_audio_q.get()
            block = resample_block(
                block,
                source_rate=input_sample_rate,
                target_rate=SAMPLE_RATE_HZ,
                dtype=np.int16,
            )
            prediction = model.predict(block)

            if prediction["hey_jarvis_v0.1"] > WAKE_TRESHOLD:
                print("Hooray! You called me!")
                break
            
            logger.debug(prediction)
