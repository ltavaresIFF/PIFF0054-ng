"""@brief Configurações do sistema via variáveis de ambiente.

Centraliza todas as variáveis de configuração suportadas pelo PIFF-0054-ng,
com valores padrão sensíveis para desenvolvimento local.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str | None, default: bool = True) -> bool:
    """@brief Converte uma string para booleano de forma flexível.

    @param value String a ser convertida (ex: "1", "true", "yes").
    @param default Valor padrão caso value seja None.
    @return True se a string representar um valor positivo.
    """
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


@dataclass(frozen=True)
class Settings:
    """@brief Configurações imutáveis do sistema.

    Lê valores de variáveis de ambiente com fallback para padrões
    que funcionam em ambiente de desenvolvimento local.

    @param sql_server Host do SQL Server (PIFF_SQL_SERVER).
    @param sql_database Nome do banco de dados (PIFF_SQL_DATABASE).
    @param sql_username Usuário SQL (PIFF_SQL_USERNAME).
    @param sql_password Senha SQL (PIFF_SQL_PASSWORD).
    @param sql_driver Driver ODBC (PIFF_SQL_DRIVER).
    @param trusted_connection Autenticação Windows (PIFF_SQL_TRUSTED_CONNECTION).
    @param cache_ttl_seconds TTL do cache em segundos (PIFF_CACHE_TTL_SECONDS).
    """
    sql_server: str = os.getenv("PIFF_SQL_SERVER", "localhost")
    sql_database: str = os.getenv("PIFF_SQL_DATABASE", "Projeto_54")
    sql_username: str = os.getenv("PIFF_SQL_USERNAME", "sa")
    sql_password: str = os.getenv("PIFF_SQL_PASSWORD", "P@ssw0rd_Projeto54!")
    sql_driver: str = os.getenv("PIFF_SQL_DRIVER", "ODBC Driver 18 for SQL Server")
    trusted_connection: bool = _as_bool(os.getenv("PIFF_SQL_TRUSTED_CONNECTION"), default=False)
    cache_ttl_seconds: int = int(os.getenv("PIFF_CACHE_TTL_SECONDS", "300"))

    @property
    def allowed_cylinders(self) -> tuple[int, ...]:
        """@brief Tupla com os números de cilindros suportados (1 a 6)."""
        return (1, 2, 3, 4, 5, 6)


## @brief Instância singleton das configurações do sistema.
SETTINGS = Settings()
