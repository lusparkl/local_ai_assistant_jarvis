from faster_whisper import WhisperModel
import faster_whisper
import openwakeword
from TTS.api import TTS
import config

def normalize_path(path: str) -> str:
    return path.replace("\\", "/")

print("Downloading model, might take long time. You'r pathes will appear in the terminal one we finish")
openwakeword_path = ""
openwakeword.utils.download_models()
for path in openwakeword.get_pretrained_model_paths():
    if "jarvis" in path:
        openwakeword_path = normalize_path(path)

whisper_path = faster_whisper.download_model(config.WHISPER_MODEL, "setup/model")
whisper_path = normalize_path(whisper_path)

tts = TTS(config.XTTS_MODEL).to(config.XTTS_DEVICE)
tts.tts_with_vc("Hello", 
                language="en",
                speaker_wav=config.REFERENCE_WAVS,
                speaker="Jarvis")

print(f"Here is your pathes \n openwakeword:  <{openwakeword_path}> \n whisper:   <{whisper_path}>")
