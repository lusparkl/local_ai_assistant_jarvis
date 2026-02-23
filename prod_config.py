# Logging
LOG_LEVEL = "INFO"

# Wake Word
WAKE_WORD_MODEL_PATH=""  # To get it run /setup/download_models.py, you'll get path in the console
WAKE_WORD_BLOCK_SEC = 2 # How much context sound your model gets, 2 works pretty well for me
WAKE_TRESHOLD = 0.5 # How frequently your model checks audio, don't set too low cuz it'll eat your cpu

# Whisper transcription
WHISPER_MODEL_PATH = "" # To get it run /setup/download_models.py, you'll get path in the console
WHISPER_MODEL = "distil-large-v3" # Set model to transcribe you, to see all models visit faster-whisper docs
WHISPER_COMPUTE_TYPE = "float16" # How you transcribe(gpu/cpu), to set cpu - "int8"
WHISPER_DEVICE = "cuda" # Device to transcribtion, must match compute type, to set cpu simply "cpu"
BLOCK_SEC = 0.25 # How long your blocks in sec
STEP_SEC = 0.25 # How often do we read your sound
TRANSCRIBTION_STAB_WINDOW = 2 # How many occurances of the word must be to think that it's "stable", I reccomend to set from 2 to 3
WINDOW_SEC = 7 # How many seconds our transcribtion model has, try to keep between 5 and 10
ENDPOINT_SILENCE_MS = 1500 # How many ms between pause and sending query to GPT module, don't set too low cuz it may cut you while you're speaking

# GPT
GPT_MODEL = "qwen3:8b" # Name of the Ollama model that you already pulled from their website, more about this in readme
SYSTEM_PROMT = (
    "You are Jarvis, created by lusparkl, a practical assistant for everyday tasks. "
    "Respond in clear, natural English optimized for text to speech. "
    "Use plain text only: no markdown, no bullet points, no numbering, no asterisks, no code blocks, no emojis, and no extra blank lines. "
    "Keep replies short, direct, accurate, and useful; add detail only if asked. "
    "Rewrite symbols, formulas, abbreviations, and units into spoken words. "
    "Examples: plus, minus, times, divided by, equals, less than, greater than, squared, cubed; kilometers per hour, miles per hour, meters per second, degrees Celsius, degrees Fahrenheit, kilograms, grams, millimeters, centimeters, meters, kilometers, liters, milliliters, kilowatt hours, watts, volts, percent. "
    "Rewrite shorthand into natural speech, including slash forms and symbols like ampersand and at sign, based on context. "
    "Read numbers, dates, times, and currency naturally for speech. "
    "If information is uncertain, say so briefly instead of guessing. "
    "Never use emojis."
) # System promt for GPT, rewrite it however you want

# Memory
MEMORY_DB_PATH = "setup/memory" # Where your chromaDB db will be stored
COLLECTION_NAME = "chat_history" # Name of your assistant memory collection
SUMMARIZING_PROMT = (
    "Describe the following conversation using only 3 keywords separated by a comma (for example: 'finance, volatility, stocks')."
) # Promt to generate tags for chats in your memory db, makes it easier to find needed chat history

# TTS
XTTS_MODEL = "xtts_v2" # Model to convert AI responce to speech
REFERENCE_WAVS = [
    "audio/reference_sounds/jarvis_example_0.wav", "audio/reference_sounds/jarvis_example_1.wav",
    "audio/reference_sounds/jarvis_example_2.wav", "audio/reference_sounds/jarvis_example_3.wav"
    ] # References of voice you want your assistant to have
LANGUAGE = "en" # Language of your assistant
CHUNKS_CHAR_LIMIT = 250 # Chars limit for one audio chunk, 250 is optimal
XTTS_DEVICE = "cuda" # How you're converting text(cpu/gpu), to set cpu - "cpu". But gpu is highly reccomendet

# General
SAMPLE_RATE_HZ = 16000 # Sample rate on which all libs that doing smth with sound are working