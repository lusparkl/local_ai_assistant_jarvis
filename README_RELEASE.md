# Jarvis Release Guide

This guide is for end users installing Jarvis from a release (without manual project setup).

## 1. What Must Be On Your PC

Required:
- OS: Windows 10/11 (this release flow is tested on Windows)
- Python: `>=3.11` and `<3.14` (Python `3.12` recommended)
- `pipx` installed and available in `PATH`
- Microphone input device
- Speaker/headphones output device
- [Ollama runtime/CLI](https://ollama.com/download) installed and available in `PATH`
- Internet access for first-time dependency/model downloads

Strongly recommended:
- NVIDIA GPU with CUDA support
- CUDA 12.6-compatible PyTorch wheels (faster speech and transcription)

Optional:
- `WEATHER_API_KEY` env var (for weather tools)

Expected disk usage:
- Python + ML dependencies + models can consume many GB of storage
- Keep at least `15-25 GB` free for a comfortable first install

## 2. One-Time Prerequisites

### Install Python 3.12
- Install from python.org, then verify:
```powershell
py -3.12 --version
```

### Install pipx
```powershell
py -3.12 -m pip install --user pipx
py -3.12 -m pipx ensurepath
```
Close and reopen terminal after `ensurepath`.

### Install Ollama
- Download and install: `https://ollama.com/download`
- Verify:
```powershell
ollama --version
```

## 3. Install Jarvis

## Option A: Install from PyPI (recommended once published)

CPU/default:
```powershell
pipx install my-own-jarvis --python 3.12
```

CUDA 12.6 (recommended):
```powershell
pipx install my-own-jarvis --python 3.12 --pip-args "--extra-index-url https://download.pytorch.org/whl/cu126"
```

## Option B: Install from GitHub release repo

CPU/default:
```powershell
pipx install "git+https://github.com/lusparkl/local_ai_assistant_jarvis.git"
```

CUDA 12.6 (recommended):
```powershell
pipx install "git+https://github.com/lusparkl/local_ai_assistant_jarvis.git" --python 3.12 --pip-args "--extra-index-url https://download.pytorch.org/whl/cu126"
```

## Option C: Install from local folder
Run from the project root (the folder containing `pyproject.toml`):
```powershell
pipx install . --python 3.12 --pip-args "--extra-index-url https://download.pytorch.org/whl/cu126"
```

## 4. Pull Ollama Model

Default Jarvis config expects:
```powershell
ollama pull qwen3:8b
```

If you want another model, you can change `GPT_MODEL` later in `~/.jarvis/config.json`.

## 5. Run Jarvis Setup

This downloads required speech/wake models and writes config automatically:
```powershell
jarvis setup
```

Then run diagnostics:
```powershell
jarvis doctor
```

What `doctor` checks:
- Python version
- Python dependency imports
- Runtime writable directories
- Packaged audio assets
- Wakeword model path + wakeword runtime load test
- Microphone/speaker availability
- CUDA/runtime consistency
- Ollama CLI/server/model availability
- Optional weather API key presence

## 6. Start Jarvis

```powershell
jarvis run
```
or:
```powershell
jarvis start
```

## 7. Where Data/Config Are Stored

Default directory:
- `C:\Users\<you>\.jarvis`

Main files/folders:
- `config.json` (runtime config)
- `models\` (downloaded wakeword + whisper assets)
- `memory\` (ChromaDB memory store)
- `local.db` (local sqlite data)

Optional overrides:
- `JARVIS_HOME` to move all runtime data
- `JARVIS_CONFIG_PATH` to point to a different config file

## 8. Basic Configuration

Edit:
- `C:\Users\<you>\.jarvis\config.json`

Common keys:
- `GPT_MODEL`: Ollama model name (must be pulled already)
- `WHISPER_DEVICE`: `"cuda"` or `"cpu"`
- `XTTS_DEVICE`: `"cuda"` or `"cpu"`
- `INPUT_DEVICE`: optional fixed mic device (index/name), or `null` for auto
- `MIC_SAMPLE_RATE_HZ`: optional manual mic rate (for incompatible mics)
- `WAKE_TRESHOLD`: wakeword sensitivity (higher = less false triggers)

After config changes:
```powershell
jarvis doctor
jarvis run
```

## 9. Optional Weather Setup

Set Weather API key in user environment:
```powershell
[Environment]::SetEnvironmentVariable("WEATHER_API_KEY", "your_key_here", "User")
```

Reopen terminal and verify:
```powershell
jarvis doctor
```

## 10. Update Jarvis

If installed from PyPI or GitHub:
```powershell
pipx upgrade my-own-jarvis
```

If installed from local source:
```powershell
pipx install . --force --python 3.12 --pip-args "--extra-index-url https://download.pytorch.org/whl/cu126"
```

After update:
```powershell
jarvis doctor
```

## 11. Uninstall Jarvis

```powershell
pipx uninstall my-own-jarvis
```

Optional: delete runtime data:
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.jarvis"
```

## 12. Troubleshooting

### `jarvis: error: invalid choice: 'start'`
Your installed version is old. Reinstall/upgrade package.

### Wakeword load fails / TFLite warnings
- Run:
```powershell
jarvis setup
jarvis doctor
```
- This release prefers ONNX wakeword runtime automatically.

### `ImportError ... torchcodec ...`
- Reinstall current release (includes codec extra):
```powershell
pipx install . --force --python 3.12 --pip-args "--extra-index-url https://download.pytorch.org/whl/cu126"
```

### `Ollama model ... not pulled`
Run:
```powershell
ollama pull qwen3:8b
```

### Clipboard backend warning
Non-fatal. Clipboard tools may be unavailable in some environments.

### `TRANSFORMERS_CACHE` deprecation warning
Optional cleanup:
```powershell
[Environment]::SetEnvironmentVariable("HF_HOME", "$env:USERPROFILE\.cache\huggingface", "User")
[Environment]::SetEnvironmentVariable("TRANSFORMERS_CACHE", $null, "User")
```

## 13. Quick Command Reference

```powershell
jarvis setup
jarvis doctor
jarvis run
jarvis start
```

---

If install/doctor output still fails, copy the full `jarvis doctor` output into an issue. The checks are designed to point to the exact missing dependency or runtime mismatch.
