SAMPLE_RATE_HZ = 16000

#Wake Word
WAKE_BLOCK_SEC = 2
WAKE_WORD_MODEL_PATH = "D:/tech_stuff/coding/ai_models/openwakeword_models/hey_jarvis_v0.1.tflite"
WAKE_TRESHOLD = 0.5

#Transcribtion
BLOCK_SEC=0.25
WINDOW_SEC=7
STEP_SEC = 0.25
ENDPOINT_SILENCE_MS=2000
WHISPER_MODEL = "distil-large-v3"
WHISPER_MODEL_PATH = "D:/tech_stuff/coding/ai_models/huggingface_cache/hub/models--Systran--faster-distil-whisper-large-v3/snapshots/c3058b475261292e64a0412df1d2681c06260fab"
WHISPER_COMPUTE_TYPE = "float16"
WHISPER_DEVICE = "cuda"
TRANSCRIBTION_STAB_WINDOW = 2

#Logging
LOG_LEVEL="INFO"

#LLM
GPT_MODEL="qwen3:8b"
SYSTEM_PROMT = (
    "You are Jarvis, created by lusparkl to help with tasks. "
    "Respond in clear, natural spoken English for TTS. "
    "Use plain text only: no markdown, no asterisks, no bullet points, no emojis, no extra blank lines. "
    "Keep replies short, direct, and informative. "
    "When math or symbols appear, rewrite them in words (for example: x squared, divided by, plus, minus, equals)."
    "Don't use emojis."
)
MEMORY_DB_PATH="D:/tech_stuff/coding/Jarvis_Memory"
COLLECTION_NAME="chat_history"
SUMMARIZING_PROMT=("Describe the following conversation using only 3 keywords separated by a comma (for example: 'finance, volatility, stocks').")
PROPS_PROMT=(
    "You are Jarvis Memory Extractor. "
    "Read the full chat and extract only truly useful new facts about the user that will improve future conversations. "
    "Input may include previously saved memories; do not repeat old facts unless a new message clearly corrects them. "
    "Use only facts explicitly stated by the user, not guesses or assistant claims. "
    "Save long-term, reusable facts such as name, close people, preferences, dislikes, phobias, hobbies, projects, goals, routines, language, location, and important personal context. "
    "Ignore temporary or low-value details like one-time plans, casual small talk, or uncertain information. "
    "Output must be strict JSON only, with no markdown or extra text. "
    "Return an array of objects in this exact shape: [{'title':'...', 'description':'...'}]. "
    "Each object must contain exactly one key-value pair, where the key is a short title and the value is a concise description. "
    "If there is no valuable new memory, return an empty array: []. "
    "Do not output duplicates. "
)

#TTS
XTTS_MODEL="xtts_v2"
REFERENCE_WAVS = ["D:/tech_stuff/coding/ai_models/jarvis_voice_examples/jarvis_example_0.wav", "D:/tech_stuff/coding/ai_models/jarvis_voice_examples/jarvis_example_1.wav", "D:/tech_stuff/coding/ai_models/jarvis_voice_examples/jarvis_example_2.wav", "D:/tech_stuff/coding/ai_models/jarvis_voice_examples/jarvis_example_3.wav"]
LANGUAGE="en"
CHUNKS_CHAR_LIMIT=250
XTTS_DEVICE="cuda"

