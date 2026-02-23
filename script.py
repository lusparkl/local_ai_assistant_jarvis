import click
import sys
from services.autostart import DEFAULT_TASK_NAME

_MIN_PYTHON = (3, 11)
_MAX_PYTHON_EXCLUSIVE = (3, 14)


def _ensure_supported_python() -> None:
    current = sys.version_info[:2]
    if _MIN_PYTHON <= current < _MAX_PYTHON_EXCLUSIVE:
        return

    raise click.ClickException(
        "Unsupported Python version. "
        "Jarvis supports Python 3.11 to 3.13. "
        "Reinstall with pipx using a supported interpreter, for example: "
        "pipx install --python 3.12 <package-spec>"
    )


@click.group()
def cli():
    """Jarvis command line tools."""
    _ensure_supported_python()


@cli.command()
def start():
    """Start assistant loop."""
    from main import run_assistant, setup_logging

    try:
        setup_logging()
        run_assistant()
    except Exception as exc:
        raise click.ClickException(str(exc))


@cli.command()
@click.option("--skip-model-download", is_flag=True, help="Skip downloading wake-word and whisper models.")
@click.option("--skip-ollama-pull", is_flag=True, help="Skip checking/pulling the configured Ollama model.")
@click.option("--force", is_flag=True, help="Rewrite core .env keys with current defaults.")
def init(skip_model_download: bool, skip_ollama_pull: bool, force: bool):
    """Bootstrap runtime directories, .env, models, and DB."""
    from services.bootstrap import run_bootstrap

    try:
        summary = run_bootstrap(
            skip_model_download=skip_model_download,
            skip_ollama_pull=skip_ollama_pull,
            force_update=force,
        )
    except Exception as exc:
        raise click.ClickException(str(exc))

    click.echo("Init completed.")
    click.echo(f".env path: {summary['env_path']}")
    if "ollama_model" in summary:
        click.echo(f"Ollama model ready: {summary['ollama_model']}")
    if "downloaded_models" in summary:
        downloaded = summary["downloaded_models"]
        click.echo(f"Wake model path: {downloaded['wake_word_model_path']}")
        click.echo(f"Whisper model path: {downloaded['whisper_model_path']}")
    click.echo(f"Local DB path: {summary['database_path']}")
    click.echo(f"Memory DB path: {summary['memory_db_path']}")


@cli.command()
def doctor():
    """Run environment checks."""
    from services.bootstrap import run_doctor

    checks = run_doctor()
    failed = 0
    for check in checks:
        if check["ok"]:
            click.echo(f"[OK] {check['name']}: {check['detail']}")
        else:
            failed += 1
            click.echo(f"[FAIL] {check['name']}: {check['detail']}")

    if failed:
        raise click.ClickException(f"{failed} check(s) failed.")


@cli.command()
def devices():
    """List available audio input devices."""
    try:
        import sounddevice as sd
    except Exception as exc:
        raise click.ClickException(f"Unable to import sounddevice: {exc}")

    try:
        all_devices = sd.query_devices()
    except Exception as exc:
        raise click.ClickException(f"Unable to query audio devices: {exc}")

    input_count = 0
    for index, device in enumerate(all_devices):
        max_input = int(device.get("max_input_channels", 0))
        if max_input <= 0:
            continue
        input_count += 1
        name = device.get("name", "Unknown device")
        click.echo(f"[{index}] {name} (inputs: {max_input})")

    if input_count == 0:
        click.echo("No audio input devices detected.")


@cli.group()
def autostart():
    """Manage OS autostart for Jarvis."""


@autostart.command("enable")
@click.option("--task-name", default=DEFAULT_TASK_NAME, show_default=True, help="Task Scheduler task name.")
def autostart_enable(task_name: str):
    from services.autostart import enable_autostart

    try:
        output = enable_autostart(task_name=task_name)
        click.echo(output)
    except Exception as exc:
        raise click.ClickException(str(exc))


@autostart.command("disable")
@click.option("--task-name", default=DEFAULT_TASK_NAME, show_default=True, help="Task Scheduler task name.")
def autostart_disable(task_name: str):
    from services.autostart import disable_autostart

    try:
        output = disable_autostart(task_name=task_name)
        click.echo(output)
    except Exception as exc:
        raise click.ClickException(str(exc))


@autostart.command("status")
@click.option("--task-name", default=DEFAULT_TASK_NAME, show_default=True, help="Task Scheduler task name.")
def autostart_show_status(task_name: str):
    from services.autostart import autostart_status

    try:
        exists, details = autostart_status(task_name=task_name)
    except Exception as exc:
        raise click.ClickException(str(exc))

    if exists:
        click.echo("Autostart is enabled.")
        click.echo(details)
    else:
        click.echo("Autostart is disabled.")
        click.echo(details)


if __name__ == "__main__":
    cli()
