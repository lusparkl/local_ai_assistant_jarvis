# my-own-jarvis

Fully local voice assistant inspired by J.A.R.V.I.S.

- GitHub: https://github.com/lusparkl/local_ai_assistant_jarvis
- Full release guide: https://github.com/lusparkl/local_ai_assistant_jarvis/blob/main/README_RELEASE.md
- Issues: https://github.com/lusparkl/local_ai_assistant_jarvis/issues

## Requirements

- Windows 10/11
- Python `>=3.11` and `<3.14` (Python `3.12` recommended)
- `pipx` in `PATH`
- Microphone + speakers/headphones
- Ollama runtime/CLI in `PATH` (`https://ollama.com/download`)

## Install

CPU/default:

```powershell
pipx install my-own-jarvis --python 3.12
```

CUDA 12.6:

```powershell
pipx install my-own-jarvis --python 3.12 --pip-args "--extra-index-url https://download.pytorch.org/whl/cu126"
```

## First run

```powershell
ollama pull qwen3:8b
jarvis setup
jarvis doctor
jarvis run
```

`jarvis start` is available as an alias for `jarvis run`.

## Update

```powershell
pipx upgrade my-own-jarvis
jarvis doctor
```

## Uninstall

```powershell
pipx uninstall my-own-jarvis
```

