from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


@dataclass(frozen=True)
class Settings:
    sql_server: str = os.getenv("PIFF_SQL_SERVER", "localhost")
    sql_database: str = os.getenv("PIFF_SQL_DATABASE", "Projeto_54")
    sql_username: str = os.getenv("PIFF_SQL_USERNAME", "sa")
    sql_password: str = os.getenv("PIFF_SQL_PASSWORD", "P@ssw0rd_Projeto54!")
    sql_driver: str = os.getenv("PIFF_SQL_DRIVER", "ODBC Driver 18 for SQL Server")
    trusted_connection: bool = _as_bool(os.getenv("PIFF_SQL_TRUSTED_CONNECTION"), default=False)
    cache_ttl_seconds: int = int(os.getenv("PIFF_CACHE_TTL_SECONDS", "300"))

    @property
    def allowed_cylinders(self) -> tuple[int, ...]:
        return (1, 2, 3, 4, 5, 6)


SETTINGS = Settings()
