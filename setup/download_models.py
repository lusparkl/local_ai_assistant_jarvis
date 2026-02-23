from pathlib import Path
from services.model_downloads import download_runtime_models
import config


if __name__ == "__main__":
    print("Downloading models, this may take a while.")
    downloaded = download_runtime_models(
        whisper_model=config.WHISPER_MODEL,
        models_root=Path(config.DATA_DIR) / "models",
    )
    print(
        "Finished.\n"
        f"openwakeword: <{downloaded['wake_word_model_path']}>\n"
        f"whisper: <{downloaded['whisper_model_path']}>"
    )
