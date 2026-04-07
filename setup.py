import platform
import struct
import sys

from setuptools import setup


def _fail(message: str) -> None:
    sys.stderr.write(message.rstrip() + "\n")
    raise SystemExit(1)


def _check_install_environment() -> None:
    if sys.platform != "win32":
        _fail(
            "my-own-jarvis supports Windows 10/11 x64 only.\n"
            "Install on Windows 10/11 x64 with Python 3.12 from python.org."
        )

    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 11) or (major, minor) >= (3, 13):
        _fail(
            "my-own-jarvis requires Python >=3.11 and <3.13.\n"
            "Use Python 3.12 x64 from python.org. Build-tool errors usually mean "
            "your Python or architecture is unsupported."
        )

    machine = platform.machine().lower()
    bits = struct.calcsize("P") * 8
    if bits != 64 or machine not in ("amd64", "x86_64"):
        _fail(
            "my-own-jarvis supports Windows 10/11 x64 only.\n"
            "Install Python 3.12 x64 from python.org. Build-tool errors usually "
            "mean your Python or architecture is unsupported."
        )


_check_install_environment()

setup()
