"""main fpbase cli.

run with `fpb`:

    fpb --help
"""

import os
import subprocess
from pathlib import Path

import typer

app = typer.Typer(name="Manage FPbase", no_args_is_help=True)


@app.command()
def run(
    prod: bool = typer.Option(False),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    "Run FPbase application."
    args = []
    if not prod:
        args.append("--reload")
    if verbose:
        args.extend(["--log-level", "debug"])
    app_file = os.getenv("FASTAPI_APP", "fpbase2.main")
    subprocess.call(["uvicorn", f"{app_file}:app", *args])  # noqa: S603, S607


@app.command()
def shell() -> None:
    """Start ipython with models loaded."""
    import IPython
    from traitlets.config import Config

    c = Config()
    c.InteractiveShellApp.exec_lines = [
        "from sqlmodel import *",
        "from fpbase2.models.protein import *",
        "from fpbase2.core.db import *",
        "from fpbase2.core.config import settings",
        "from fpbase2._dev import *",
        "from fpbase2._dev._import import *",
        "from fpbase2._dev._factories import *",
        "from fpbase2.utils import *",
        "from rich import print",
        "from rich import pretty; pretty.install()",
        "session = Session(engine)",
        "init_db()",
    ]

    c.InteractiveShell.colors = "Neutral"
    c.InteractiveShell.confirm_exit = False
    c.TerminalIPythonApp.display_banner = False
    IPython.start_ipython([], config=c)


@app.command()
def rebuild(
    start_shell: bool = typer.Option(
        True, "--shell/--no-shell", help="Start ipython shell after rebuild."
    ),
) -> None:
    """Recreate the database and tables."""

    from fpbase2._dev._import import add_fpb_proteins, add_fpb_references, add_fpb_users
    from fpbase2.core.config import settings
    # from fpbase2.core.db import init_db

    typer.echo(f"Rebuilding database... {settings.SQLALCHEMY_DATABASE_URI}")
    if (uri := settings.SQLALCHEMY_DATABASE_URI) and uri.scheme == "sqlite":
        Path(str(uri.path).lstrip("/")).unlink(missing_ok=True)
        # init_db()

    add_fpb_users()
    add_fpb_references()
    add_fpb_proteins()
    if start_shell:
        shell()


@app.command()
def check() -> None:
    """Run checks"""
    proc = subprocess.run(["pre-commit", "run", "--all-files"])  # noqa: S603, S607
    typer.Exit(proc.returncode)
