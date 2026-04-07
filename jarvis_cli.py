import argparse
from typing import Sequence

from preflight import format_preflight_report, run_preflight


def _command_doctor() -> int:
    report = run_preflight()
    print(format_preflight_report(report))
    return 0 if report.ok else 1


def _command_setup(skip_doctor: bool) -> int:
    from setup.download_models import download_required_models

    print("Running Jarvis model setup...")
    try:
        results = download_required_models()
    except Exception as exc:
        print(f"Setup failed: {exc}")
        return 1

    print("Model setup complete.")
    print(f"Wakeword model: {results['wakeword_path']}")
    print(f"Whisper model: {results['whisper_path']}")
    print(f"XTTS device: {results['xtts_device']}")
    if "xtts_speaker" in results:
        print(f"XTTS speaker: {results['xtts_speaker']}")
    print(f"Saved config: {results['config_path']}")

    if skip_doctor:
        return 0

    print("Running post-setup checks...")
    return _command_doctor()


def _command_run(skip_preflight: bool) -> int:
    if not skip_preflight:
        report = run_preflight()
        print(format_preflight_report(report))
        if not report.ok:
            return 1

    from main import run_assistant, setup_logging

    setup_logging()
    try:
        run_assistant()
    except KeyboardInterrupt:
        print("Jarvis stopped by user.")
        return 0
    except Exception as exc:
        print(f"Jarvis failed to start: {exc}")
        print("Run `jarvis doctor` for detailed diagnostics.")
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jarvis",
        description="Local voice assistant CLI.",
    )
    subparsers = parser.add_subparsers(dest="command")

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Check dependencies, devices, models, and runtime configuration.",
    )
    doctor_parser.set_defaults(handler=lambda args: _command_doctor())

    setup_parser = subparsers.add_parser(
        "setup",
        help="Download required models and write local Jarvis config.",
    )
    setup_parser.add_argument(
        "--skip-doctor",
        action="store_true",
        help="Skip running checks after setup completes.",
    )
    setup_parser.set_defaults(handler=lambda args: _command_setup(skip_doctor=args.skip_doctor))

    for command_name, help_text in (
        ("run", "Run Jarvis assistant (runs preflight checks first by default)."),
        ("start", "Alias for `run`."),
    ):
        run_parser = subparsers.add_parser(
            command_name,
            help=help_text,
        )
        run_parser.add_argument(
            "--skip-preflight",
            action="store_true",
            help="Run assistant without startup checks.",
        )
        run_parser.set_defaults(handler=lambda args: _command_run(skip_preflight=args.skip_preflight))

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        return _command_run(skip_preflight=False)

    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
