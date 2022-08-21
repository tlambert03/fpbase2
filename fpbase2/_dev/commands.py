def serve() -> None:
    """Serves the application on `poetry run serve`"""
    from uvicorn import run

    run("fpbase2.main:app", reload=True, debug=True)


def shell() -> None:
    """Start ipython with models loaded."""
    import IPython
    from traitlets.config import Config

    c = Config()
    c.InteractiveShellApp.exec_lines = [
        "from sqlmodel import *",
        "from fpbase2.models.protein import *",
        "from fpbase2.db import *",
        "from fpbase2._dev import *",
        "from fpbase2._dev._import import *",
        "from fpbase2._dev._factories import *",
        "from rich import print",
        "from rich import pretty; pretty.install()",
        "session = Session(engine)",
        "create_db_and_tables()",
    ]

    c.InteractiveShell.colors = "Neutral"
    c.InteractiveShell.confirm_exit = False
    c.TerminalIPythonApp.display_banner = False
    IPython.start_ipython(config=c)


def recreate() -> None:
    """Recreate the database and tables."""
    from pathlib import Path

    from fpbase2.db import create_db_and_tables

    Path(__file__).parent.parent.parent.joinpath("database.db").unlink(missing_ok=True)
    create_db_and_tables()
    from fpbase2._dev._import import add_fpb_proteins, add_fpb_references, add_fpb_users

    add_fpb_users(10)
    add_fpb_references(500)
    add_fpb_proteins(500)
    shell()
