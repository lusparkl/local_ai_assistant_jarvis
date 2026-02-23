# Jarvis. Fully local AI assistant.

## Fully functional, but still unfinished AI assistant written on Python thats works on your PC!

Jarvis is a local voice assistant that listens for a wake word, transcribes speech, runs an Ollama model, speaks responses, and can use tools (weather, clipboard, todos, memory).

## Check it out!

Place for vid, I'll update it when create first ship!

## Main libraries I used to build Jarvis:

* [ollama](https://github.com/ollama/ollama-python)
* [coqui-ai-TTS](https://github.com/idiap/coqui-ai-TTS)
* [faster whisper](https://github.com/SYSTRAN/faster-whisper)
* [chroma](https://github.com/chroma-core/chroma)
* [sounddevice](https://github.com/spatialaudio/python-sounddevice)
* [openwakeword](https://github.com/dscripka/openWakeWord)

**Many thanks to the devs!!**

## Requirements

- Python 3.11 or 3.12
- Ollama installed and available in PATH
- Microphone and speakers
- Optional GPU (CPU also works with slower settings)

## Install

Install with pipx (recommended):
`pipx install "git+https://github.com/lusparkl/local_ai_assistant_jarvis.git"`

Or for local development:
`python -m venv .venv`
`.venv\Scripts\activate`
`python -m pip install -e .`


## First-time setup

Run:
`jarvis init`

This creates runtime folders, prepares `.env`, initializes local storage, and can set up model paths.

Then run health checks:
`jarvis doctor`

## Run

Start assistant:
`jarvis start`

## Useful commands

- `jarvis init --help`
- `jarvis doctor`
- `jarvis autostart enable`
- `jarvis autostart status`
- `jarvis autostart disable`

## Environment variables

Set `WEATHER_API_KEY` in `.env` to enable weather tool.  
`jarvis init` tells you the `.env` path it uses.

## Adding tools

1. Add a tool function in `tools/<name>.py` with a clear docstring.
2. Import and enable it in `services/manage_tools.py`.
3. If needed, add dependencies in `pyproject.toml`.

## Find a bug?

I'm sure that next few weeks this project will be all in bugs because I haven't even tested it perciselly by myself, only short conversations. So if you found a bug, please submit an issue using the issues tab above. I'll try to fix all issues as fast as possible!

