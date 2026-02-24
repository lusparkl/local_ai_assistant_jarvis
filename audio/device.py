import sounddevice as sd
import config


def _available_input_devices(channels: int) -> list[int]:
    devices = []
    for index, info in enumerate(sd.query_devices()):
        if info.get("max_input_channels", 0) >= channels:
            devices.append(index)
    return devices


def _supports_input_settings(device, sample_rate: int, channels: int, dtype: str) -> bool:
    try:
        sd.check_input_settings(
            device=device,
            samplerate=sample_rate,
            channels=channels,
            dtype=dtype,
        )
        return True
    except Exception:
        return False


def _preferred_rates_for_device(device, target_sample_rate: int) -> list[int]:
    configured_rate = getattr(config, "MIC_SAMPLE_RATE_HZ", None)
    if configured_rate not in (None, ""):
        return [int(configured_rate)]

    rates = [int(target_sample_rate)]
    try:
        default_rate = int(sd.query_devices(device).get("default_samplerate", 0) or 0)
        if default_rate > 0:
            rates.append(default_rate)
    except Exception:
        pass

    rates.extend([48000, 44100])
    # Keep order while removing duplicates.
    return list(dict.fromkeys(rates))


def resolve_input_stream_settings(
    target_sample_rate: int,
    channels: int = 1,
    dtype: str = "float32",
):
    configured_device = getattr(config, "INPUT_DEVICE", None)
    default_input = sd.default.device[0]

    if configured_device not in (None, ""):
        device_candidates = [configured_device]
    else:
        device_candidates = []
        if default_input is not None and default_input >= 0:
            try:
                info = sd.query_devices(default_input)
                if info.get("max_input_channels", 0) >= channels:
                    device_candidates.append(int(default_input))
            except Exception:
                pass

        for device in _available_input_devices(channels):
            if device not in device_candidates:
                device_candidates.append(device)

    if not device_candidates:
        raise RuntimeError(
            "No input device found. Connect a microphone or set INPUT_DEVICE in config.py."
        )

    for device in device_candidates:
        for sample_rate in _preferred_rates_for_device(device, target_sample_rate):
            if _supports_input_settings(device, sample_rate, channels, dtype):
                return device, sample_rate

    if configured_device not in (None, ""):
        raise RuntimeError(
            "Configured INPUT_DEVICE is not compatible with current audio settings. "
            "Try another INPUT_DEVICE or set MIC_SAMPLE_RATE_HZ in config.py."
        )

    raise RuntimeError(
        "No compatible input device/settings found. "
        "Set INPUT_DEVICE and MIC_SAMPLE_RATE_HZ in config.py."
    )


def resolve_input_device():
    device, _ = resolve_input_stream_settings(target_sample_rate=getattr(config, "SAMPLE_RATE_HZ", 16000))
    return device
