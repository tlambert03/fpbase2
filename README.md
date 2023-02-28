# FPbase2

[![codecov](https://codecov.io/gh/tlambert03/fpbase2/branch/main/graph/badge.svg?token=PEfGzZ2Kyl)](https://codecov.io/gh/tlambert03/fpbase2)

A rewrite of the FPbase backend, using
[sqlmodel](https://github.com/tiangolo/sqlmodel) and
[FastAPI](https://fastapi.tiangolo.com)

## Installation

[install poetry](https://python-poetry.org/docs/#installation) (if you don't already have it),
then:

```bash
git clone https://github.com/tlambert03/fpbase2.git
cd fpbase2
poetry install
poetry run pytest
```

(You can also use `poetry shell` to activate the virtual environment,
and then run `pytest` directly)

## Usage

```bash
fpb run
```

Then navigate to <http://127.0.0.1:8000/docs> to see the interactive
API docs.
