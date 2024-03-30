from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

DBScheme = Literal["sqlite", "postgresql", "postgresql+psycopg"]


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        # case_sensitive=True,
    )

    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    @computed_field  # type: ignore[misc]
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    PROJECT_NAME: str = "fpbase"
    DEBUG: bool = False

    # either DB_SQLITE_PATH or POSTGRES_SERVER & POSTGRES_USER must be set
    # DB_SQLITE_PATH takes precedence
    DB_SQLITE_PATH: Literal[":memory:"] | str | None = None

    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn | str:
        # https://docs.sqlalchemy.org/en/20/core/engines.html#sqlite
        if self.DB_SQLITE_PATH:
            if self.DB_SQLITE_PATH == ":memory:":
                return "sqlite://"
            return f"sqlite:///{self.DB_SQLITE_PATH}"
        if not (self.POSTGRES_SERVER and self.POSTGRES_DB):
            raise ValueError(
                "Must set either DB_SQLITE_PATH or POSTGRES_SERVER and POSTGRES_DB"
            )

        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @model_validator(mode="after")
    def _check_db_provided(self) -> Self:
        if not self.DB_SQLITE_PATH:
            if not self.POSTGRES_SERVER and self.POSTGRES_USER:
                raise ValueError(
                    "Either DB_SQLITE_PATH or POSTGRES_SERVER and POSTGRES_USER "
                    "environment variables must be set"
                )
        return self

    # my stuff

    # Whether database is read-only. If True, no changes will be made to the database.
    READ_ONLY: bool = False


settings = Settings()
