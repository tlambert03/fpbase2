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
        "from rich import print",
        "from rich import pretty; pretty.install()",
        "session = next(get_session())",
        "create_db_and_tables()",
    ]

    c.InteractiveShell.colors = "Neutral"
    c.InteractiveShell.confirm_exit = False
    c.TerminalIPythonApp.display_banner = False
    IPython.start_ipython(config=c)
