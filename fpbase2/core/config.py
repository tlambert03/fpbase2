from typing import Any

from pydantic import (
    AnyHttpUrl,
    AnyUrl,
    BaseSettings,
    PostgresDsn,
    validator,
)


class SQLiteDsn(AnyUrl):
    allowed_schemes = {"sqlite"}
    host_required = False


class Settings(BaseSettings):
    PROJECT_NAME: str = "fpbase"
    DEBUG: bool = False
    ALLOW_QM: bool = False
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    POSTGRES_SERVER: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    SQLITE_DB: str | None = None
    DATABASE_URI: SQLiteDsn | PostgresDsn = SQLiteDsn.build(scheme="sqlite", host="/")
    PRODUCTION_DB_URL: PostgresDsn | None = None

    class Config:
        case_sensitive = True
        env_file = ".env"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        elif sqlite_db := values.get("SQLITE_DB"):
            return SQLiteDsn.build(scheme="sqlite", host="/", path=sqlite_db)
        return (
            PostgresDsn.build(
                scheme="postgresql",
                host=host,
                user=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                path=f"/{values.get('POSTGRES_DB') or ''}",
            )
            if (host := values.get("POSTGRES_SERVER"))
            else None
        )


settings = Settings()
