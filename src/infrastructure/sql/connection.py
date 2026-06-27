from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterable

import pyodbc

from src.config.settings import Settings
from src.domain.errors import InfrastructureError


def _execute_on(
    conn: pyodbc.Connection, query: str, params: Iterable[Any] = ()
) -> tuple[list[str], list[tuple[Any, ...]]]:
    """Run a query on an already-open connection. Returns (columns, rows)."""
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    columns = [col[0] for col in cursor.description] if cursor.description else []
    rows = cursor.fetchall()
    return columns, [tuple(row) for row in rows]


class SqlServerConnection:
    def __init__(self, settings: Settings):
        self.settings = settings

    def build_connection_string(self) -> str:
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
        )

    @contextmanager
    def connect(self):
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
        """Open a single connection for a block of operations.
        All fetch_all_on / execute_on calls reuse this connection,
        avoiding the ~300ms handshake per query."""
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
        with self.connect() as conn:
            return _execute_on(conn, query, params)

    def fetch_all_on(
        self, conn: pyodbc.Connection, query: str, params: Iterable[Any] = ()
    ) -> tuple[list[str], list[tuple[Any, ...]]]:
        """Run a query on an already-open connection (from connect_shared)."""
        return _execute_on(conn, query, params)

    def execute(self, query: str, params: Iterable[Any] = ()) -> int:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            conn.commit()
            return int(cursor.rowcount)

    def execute_transaction(self, statements: list[tuple[str, tuple[Any, ...]]]) -> list[int]:
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
        return list(pyodbc.drivers())
