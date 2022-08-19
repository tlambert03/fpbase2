def serve() -> None:
    """Serves the application on `poetry run serve`"""
    from uvicorn import run

    run("fpbase2.main:app", reload=True, debug=True)
