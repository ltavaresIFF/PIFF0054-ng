"""@brief Gerenciamento de conexão com o SQL Server via ODBC.

Fornece a classe SqlServerConnection para abrir conexões, executar consultas
e gerenciar transações com o banco de dados Projeto_54.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterable

import pyodbc

from src.config.settings import Settings
from src.domain.errors import InfrastructureError


def _execute_on(
    conn: pyodbc.Connection, query: str, params: Iterable[Any] = ()
) -> tuple[list[str], list[tuple[Any, ...]]]:
    """@brief Executa uma consulta SQL em uma conexão já aberta.

    @param conn Conexão pyodbc ativa.
    @param query String SQL a executar.
    @param params Parâmetros posicionais (opcional).
    @return Tupla (colunas, linhas) com os resultados.
    """
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    columns = [col[0] for col in cursor.description] if cursor.description else []
    rows = cursor.fetchall()
    return columns, [tuple(row) for row in rows]


class SqlServerConnection:
    """@brief Gerencia conexões com o SQL Server via ODBC.

    Suporta autenticação SQL (usuário/senha) e trusted connection (Windows).
    Oferece conexões compartilhadas para otimizar múltiplas consultas.
    """

    def __init__(self, settings: Settings):
        """@brief Inicializa a conexão com as configurações fornecidas.

        @param settings Configurações do sistema (servidor, banco, credenciais).
        """
        self.settings = settings

    def build_connection_string(self) -> str:
        """@brief Constrói a string de conexão ODBC.

        Suporta trusted connection (autenticação Windows) ou SQL Auth.

        @return String formatada para pyodbc.connect().
        """
        if self.settings.trusted_connection:
            return (
                f"DRIVER={{{self.settings.sql_driver}}};"
                f"SERVER={self.settings.sql_server};"
                f"DATABASE={self.settings.sql_database};"
                "Trusted_Connection=yes;"
            )
        return (
            f"DRIVER={{{self.settings.sql_driver}}};"
            f"SERVER={self.settings.sql_server};"
            f"DATABASE={self.settings.sql_database};"
            f"UID={self.settings.sql_username};"
            f"PWD={self.settings.sql_password};"
            "TrustServerCertificate=yes;"
        )

    @contextmanager
    def connect(self):
        """@brief Abre uma nova conexão com o SQL Server (context manager).

        @yield Conexão pyodbc ativa.
        @raise InfrastructureError Se a conexão falhar.
        """
        conn = None
        try:
            conn = pyodbc.connect(self.build_connection_string(), timeout=10)
            yield conn
        except pyodbc.Error as exc:
            raise InfrastructureError(f"Falha ao conectar no SQL Server: {exc}") from exc
        finally:
            if conn is not None:
                conn.close()

    @contextmanager
    def connect_shared(self):
        """@brief Abre uma conexão compartilhada para múltiplas operações.

        Todas as chamadas fetch_all_on / execute_on reutilizam esta conexão,
        evitando o overhead de ~300ms do handshake por consulta.

        @yield Conexão pyodbc ativa.
        @raise InfrastructureError Se a conexão falhar.
        """
        conn = None
        try:
            conn = pyodbc.connect(self.build_connection_string(), timeout=10)
            yield conn
        except pyodbc.Error as exc:
            raise InfrastructureError(f"Falha ao conectar no SQL Server: {exc}") from exc
        finally:
            if conn is not None:
                conn.close()

    def fetch_all(self, query: str, params: Iterable[Any] = ()) -> tuple[list[str], list[tuple[Any, ...]]]:
        """@brief Executa uma consulta SQL em uma nova conexão.

        @param query String SQL.
        @param params Parâmetros posicionais.
        @return Tupla (colunas, linhas).
        """
        with self.connect() as conn:
            return _execute_on(conn, query, params)

    def fetch_all_on(
        self, conn: pyodbc.Connection, query: str, params: Iterable[Any] = ()
    ) -> tuple[list[str], list[tuple[Any, ...]]]:
        """@brief Executa uma consulta em uma conexão já aberta.

        @param conn Conexão pyodbc ativa (de connect_shared).
        @param query String SQL.
        @param params Parâmetros posicionais.
        @return Tupla (colunas, linhas).
        """
        return _execute_on(conn, query, params)

    def execute(self, query: str, params: Iterable[Any] = ()) -> int:
        """@brief Executa um comando SQL (INSERT/UPDATE/DELETE).

        @param query String SQL.
        @param params Parâmetros posicionais.
        @return Número de linhas afetadas.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            conn.commit()
            return int(cursor.rowcount)

    def execute_transaction(self, statements: list[tuple[str, tuple[Any, ...]]]) -> list[int]:
        """@brief Executa múltiplos comandos em uma transação atômica.

        Commit se todos bem-sucedidos, rollback em caso de erro.

        @param statements Lista de tuplas (query, params).
        @return Lista com contagem de linhas afetadas por comando.
        @raise InfrastructureError Se qualquer comando falhar.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            rowcounts: list[int] = []
            try:
                for query, params in statements:
                    cursor.execute(query, params)
                    rowcounts.append(int(cursor.rowcount))
                conn.commit()
                return rowcounts
            except pyodbc.Error as exc:
                conn.rollback()
                raise InfrastructureError(f"Falha transacional no SQL Server: {exc}") from exc

    def list_drivers(self) -> list[str]:
        """@brief Lista todos os drivers ODBC instalados no sistema.

        @return Lista de nomes de drivers ODBC disponíveis.
        """
        return list(pyodbc.drivers())
