import platform
import subprocess
import sys

DEFAULT_TASK_NAME = "JarvisAssistant"


def _require_windows() -> None:
    if platform.system() != "Windows":
        raise RuntimeError("Autostart is currently supported only on Windows.")


def _task_command() -> str:
    return f'"{sys.executable}" -m script start'


def enable_autostart(task_name: str = DEFAULT_TASK_NAME) -> str:
    _require_windows()
    command = [
        "schtasks",
        "/Create",
        "/TN",
        task_name,
        "/TR",
        _task_command(),
        "/SC",
        "ONLOGON",
        "/RL",
        "LIMITED",
        "/F",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "Unknown error").strip()
        raise RuntimeError(f"Failed to enable autostart: {details}")
    return (result.stdout or "Autostart enabled.").strip()


def disable_autostart(task_name: str = DEFAULT_TASK_NAME) -> str:
    _require_windows()
    command = ["schtasks", "/Delete", "/TN", task_name, "/F"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "Unknown error").strip()
        raise RuntimeError(f"Failed to disable autostart: {details}")
    return (result.stdout or "Autostart disabled.").strip()


def autostart_status(task_name: str = DEFAULT_TASK_NAME) -> tuple[bool, str]:
    _require_windows()
    command = ["schtasks", "/Query", "/TN", task_name]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "Task not found").strip()
        return False, details
    return True, (result.stdout or "Task exists").strip()
