# Run as a module please.
from TTS.api import TTS
import config

tts = TTS(config.XTTS_MODEL).to(config.XTTS_DEVICE)

phrases = [
    "Understood. Give me a moment to process that.",
    "Alright—running the numbers.",
    "Ok, let me think.",
    "One sec… compiling the best answer.",
    "Processing now.",
    "Working on it—stand by.",
    "Analyzing your request.",
    "Checking the details.",
    "Let me connect the dots.",
    "Give me a heartbeat.",
    "Calculating optimal response.",
    "Consulting my internal notes.",
    "Scanning for the most useful approach.",
    "Cross-referencing sources… internally.",
    "Putting that together now.",
    "Running a quick mental simulation.",
    "Thinking… almost there.",
    "Let’s see what we’ve got.",
    "Parsing the context.",
    "Mapping out the solution.",
    "Evaluating possibilities.",
    "Doing a fast systems check.",
    "Formulating an answer.",
    "Synthesizing a clean response.",
    "Let me refine that.",
    "Drafting the best version.",
    "Optimizing for clarity.",
    "Verifying assumptions.",
    "Double-checking logic.",
    "Alright—ready when you are."
]

for i, phrase in enumerate(phrases):
    kwargs = {
        "text": phrase,
        "language": config.LANGUAGE,
        "file_path": f"audio/thinking_sounds/sound_{i}.wav",
    }
    if config.XTTS_SPEAKER.strip():
        kwargs["speaker"] = config.XTTS_SPEAKER
    else:
        kwargs["speaker_wav"] = config.REFERENCE_WAVS
    tts.tts_to_file(**kwargs)



    
