import click
from services.autostart import DEFAULT_TASK_NAME


@click.group()
def cli():
    """Jarvis command line tools."""


@cli.command()
def start():
    """Start assistant loop."""
    from main import run_assistant, setup_logging

    setup_logging()
    run_assistant()


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
