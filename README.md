# Jarvis. Fully local AI assistant.

PyPI package description is sourced from `README_PYPI.md`.

For release installs and full setup documentation, use [README_RELEASE.md](README_RELEASE.md).

## Fully functional, but still unfinished AI assistant written on Python thats works on your PC!

This project is my recreation of the J.A.R.V.I.S from "Iron Man" movie. He can listen, think, speak, memorize and most important use ANY tools you provide him. It's very customizable project.

## Warning
Windows 10/11 x64 only. Linux/macOS are not supported yet.

## Short trailer for the project, haven't covered all features, but I really worked hard to create it!

[![Jarvis Trailer](https://img.youtube.com/vi/jkSiXKr-uqs/hqdefault.jpg)](http://www.youtube.com/watch?v=jkSiXKr-uqs "Jarvis Trailer")

## Deps:

* Ollama - must be in your path
* Cuda - not neccesary, but without it it'll be too slow
* Python `>=3.11` and `<3.13` (Python `3.12` recommended, x64 from python.org)
* [Ollama runtime/CLI](https://ollama.com/download) - required (Python package `ollama` is not enough)

## Main libraries I used to build Jarvis:

* [ollama](https://github.com/ollama/ollama-python)
* [coqui-ai-TTS](https://github.com/idiap/coqui-ai-TTS)
* [faster whisper](https://github.com/SYSTRAN/faster-whisper)
* [chroma](https://github.com/chroma-core/chroma)
* [sounddevice](https://github.com/spatialaudio/python-sounddevice)
* [openwakeword](https://github.com/dscripka/openWakeWord)

**Many thanks to the devs!!**

## How to install Jarvis to your PC

### Fast path (recommended): `pipx`

1. Install with pipx:
   - PyPI (after release):
     - `pipx install my-own-jarvis --python 3.12`
   - Local repo:
     - `pipx install .`
   - CPU/default install:
     - `pipx install "git+https://github.com/lusparkl/local_ai_assistant_jarvis.git"`
   - CUDA 12.6 install:
     - `pipx install "git+https://github.com/lusparkl/local_ai_assistant_jarvis.git" --python 3.12 --pip-args "--extra-index-url https://download.pytorch.org/whl/cu126"`
2. Install Ollama runtime/CLI from `https://ollama.com/download` (if not already installed).
3. Pull your configured LLM model:
   - `ollama pull qwen3:8b`
4. Download required models and persist config:
   - `jarvis setup`
5. Run full environment check:
   - `jarvis doctor`
6. Start Jarvis:
   - `jarvis run` (or `jarvis start`)

### What `jarvis doctor` checks

- Python version compatibility (`>=3.11` and `<3.13`)
- Required Python dependencies import correctly
- Microphone and speaker devices are available
- Audio stream settings are compatible with runtime config
- Required model files exist (wakeword + whisper)
- Ollama CLI/server/model availability (`ollama pull <model>`)
- Runtime storage paths and writable local data directories

All failures are reported with clear actionable messages.

## Sounddevice install errors

If you see build-tool or compiler errors while installing:

- Use Python 3.12 x64 from python.org (avoid the Microsoft Store build).
- Upgrade pip: `python -m pip install -U pip`
- Ensure you are not forcing source builds (`PIP_NO_BINARY` unset, avoid `--no-binary`).
- If you must build from source, install Microsoft C++ Build Tools + Windows SDK.

### Local data/config location

- Jarvis stores runtime files in `~/.jarvis` by default.
- Override location with `JARVIS_HOME`.
- Config file path: `~/.jarvis/config.json` (override with `JARVIS_CONFIG_PATH`).

## How to tweak this project for your own uses

Since I'm trying to write modular project It'll be easy to change modules as you want. You can completly change tts model or even switch to some api(what I'll totaly understand, because it might be really slow on weak PC's). 

But the easisest way - add your tools. You can write tools that YOU really need, and I'm sure that there will be some, because I'm writing only tools that almost everyone needs. Now to add your tool you need:
1. Create your file or write code in existing if theme is the same in the /tools
2. Write your tool function that AI will use, you can use my functions as examples. And don't forget about commenting your function so AI will understand what it's for!!
3. Import and add your tool to the services/manage_tools. You can disable tools by setting value in front of it's name to False btw

Your tool is now working!

## Find a bug?

I'm sure that next few weeks this project will be all in bugs because I haven't even tested it perciselly by myself, only short conversations. So if you found a bug, please submit an issue using the issues tab above. I'll try to fix all issues as fast as possible!

