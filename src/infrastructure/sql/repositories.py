from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from src.domain.errors import AmbiguousMatchError, NotFoundError, PersistenceError
from src.domain.models import (
    DiagnosticsInfo,
    DynamicDataResult,
    ObservationCommand,
    ObservationLookup,
    ObservationRecord,
    ObservationResult,
    StaticDataResult,
    TestContext,
)
from src.infrastructure.sql.connection import SqlServerConnection
from src.infrastructure.sql.safe_sql import escape_identifier, escape_table
from src.infrastructure.sql.schema import (
    CANONICAL_OBSERVATION_COLUMNS,
    DYNAMIC_DEFAULT_COLUMNS,
    DYNAMIC_EXCLUDE_COLUMNS,
    FORCE_COLUMN_CANDIDATES,
    cylinder_id_column,
    dynamic_table_name,
    static_table_candidates,
)


class SqlTestQueryRepository:
    def __init__(self, conn: SqlServerConnection):
        self.conn = conn
        # Schema caches: populated on first call, valid for the lifetime of the
        # repository instance (which is bound to @st.cache_resource).
        self._columns_cache: dict[str, list[str]] = {}
        self._tables_cache: dict[str, bool] = {}

    def _fetch(self, query: str, params: tuple = (), _conn: Any = None):
        """Use shared connection when available, otherwise open a new one."""
        if _conn is not None:
            return self.conn.fetch_all_on(_conn, query, params)
        return self.conn.fetch_all(query, params)

    def _table_exists(self, table_name: str, _conn: Any = None) -> bool:
        if table_name not in self._tables_cache:
            query = f"SELECT 1 FROM sys.tables WHERE name = ?"
            _, rows = self._fetch(query, (table_name,), _conn)
            self._tables_cache[table_name] = bool(rows)
        return self._tables_cache[table_name]

    def _get_columns(self, table_name: str, _conn: Any = None) -> list[str]:
        if table_name in self._columns_cache:
            return self._columns_cache[table_name]
        # Use a zero-row query against the real table to get column metadata
        # instantly — orders of magnitude faster than INFORMATION_SCHEMA.COLUMNS
        # which materialises a view across *all* tables in the database.
        safe = escape_table(table_name)
        query = f"SELECT TOP 0 * FROM {safe}"
        headers, _ = self._fetch(query, (), _conn)
        if headers:
            self._columns_cache[table_name] = headers
            return headers
        # Fallback: sys.columns (rarely needed)
        query2 = """
        SELECT name FROM sys.columns
        WHERE object_id = OBJECT_ID(?)
        ORDER BY column_id
        """
        _, rows2 = self._fetch(query2, (table_name,), _conn)
        self._columns_cache[table_name] = [r[0] for r in rows2]
        return self._columns_cache[table_name]

    def list_test_ids(self, cyl_num: int) -> list[str]:
        id_col = cylinder_id_column(cyl_num)
        dyn_table = dynamic_table_name(cyl_num)
        source_table = dyn_table
        if not self._table_exists(source_table):
            static_candidates = static_table_candidates(cyl_num)
            source_table = next((t for t in static_candidates if self._table_exists(t)), static_candidates[0])
        query = f"""
        SELECT DISTINCT {escape_identifier(id_col)}
        FROM {escape_table(source_table)}
        WHERE {escape_identifier(id_col)} IS NOT NULL
        ORDER BY {escape_identifier(id_col)}
        """
        _, rows = self.conn.fetch_all(query)
        return [r[0] for r in rows]

    def load_dynamic_rows(
        self, ctx: TestContext, selected_columns: list[str] | None = None, _conn: Any = None
    ) -> DynamicDataResult:
        id_col = cylinder_id_column(ctx.cyl_num)
        table_name = dynamic_table_name(ctx.cyl_num)
        all_columns = self._get_columns(table_name, _conn)
        if not all_columns:
            raise NotFoundError("Tabela dinamica sem colunas disponiveis.")

        if selected_columns:
            filtered = [c for c in selected_columns if c in all_columns]
            columns = [id_col, "LocalCol", *filtered]
            columns = [c for i, c in enumerate(columns) if c in all_columns and c not in columns[:i]]
        else:
            # Seleciona apenas colunas uteis alinhadas com o indice composto
            # (ID_Teste, LocalCol) INCLUDE (...). Evita SELECT * que causava
            # key lookups e full table scan de ~12s.
            useful = DYNAMIC_DEFAULT_COLUMNS & set(all_columns)
            columns = [id_col, "LocalCol"] + sorted(useful)

        select_expr = ", ".join(escape_identifier(c) for c in columns)
        query = f"""
        SELECT {select_expr}
        FROM {escape_table(table_name)}
        WHERE {escape_identifier(id_col)} = ?
        ORDER BY {escape_identifier('LocalCol')}
        """
        headers, rows = self._fetch(query, (ctx.test_id,), _conn)
        frame = pd.DataFrame(rows, columns=headers)
        return DynamicDataResult(rows=frame, ordered_by="LocalCol")

    def _find_static_table(self, cyl_num: int, _conn: Any = None) -> str | None:
        """Discover the static table for a cylinder with a single round-trip."""
        # Most common suffix first (accented), avoids 4× sys.tables queries.
        candidates = static_table_candidates(cyl_num)
        placeholders = ", ".join("?" for _ in candidates)
        query = f"SELECT name FROM sys.tables WHERE name IN ({placeholders})"
        _, rows = self._fetch(query, tuple(candidates), _conn)
        existing = {r[0] for r in rows}
        for name in candidates:
            if name in existing:
                return name
        return None

    def load_static_row(self, ctx: TestContext, _conn: Any = None) -> StaticDataResult:
        id_col = cylinder_id_column(ctx.cyl_num)
        table_name = self._find_static_table(ctx.cyl_num, _conn)
        if table_name is None:
            raise NotFoundError("Nenhuma tabela estatica encontrada para o cilindro informado.")
        columns = self._get_columns(table_name, _conn)
        if not columns:
            raise NotFoundError("Tabela estatica sem colunas disponiveis.")
        select_expr = ", ".join(escape_identifier(c) for c in columns)
        query = f"""
        SELECT {select_expr}
        FROM {escape_table(table_name)}
        WHERE {escape_identifier(id_col)} = ?
        """
        headers, rows = self._fetch(query, (ctx.test_id,), _conn)
        frame = pd.DataFrame(rows, columns=headers)
        return StaticDataResult(row=frame, table_used=table_name)

    def detect_force_column(self, cyl_num: int, _conn: Any = None) -> str | None:
        columns = self._get_columns(dynamic_table_name(cyl_num), _conn)
        for candidate in FORCE_COLUMN_CANDIDATES:
            if candidate in columns:
                return candidate
        return None

    def load_available_y_columns(self, cyl_num: int, _conn: Any = None) -> list[str]:
        columns = self._get_columns(dynamic_table_name(cyl_num), _conn)
        id_col = cylinder_id_column(cyl_num)
        excluded = {id_col, "LocalCol", "MSecCol", "TimeCol", "CreatedAt", "OBS", "val_obs", "y_column_name"}
        return [c for c in columns if c not in excluded]


class SqlObservationRepository:
    def __init__(self, conn: SqlServerConnection):
        self.conn = conn

    @staticmethod
    def _match_query(cyl_num: int, y_column_name: str, include_select: str) -> tuple[str, str, str]:
        table_name = dynamic_table_name(cyl_num)
        id_col = cylinder_id_column(cyl_num)
        y_col = escape_identifier(y_column_name)
        obs_col = escape_identifier(CANONICAL_OBSERVATION_COLUMNS["obs"])
        val_col = escape_identifier(CANONICAL_OBSERVATION_COLUMNS["val"])
        y_name_col = escape_identifier(CANONICAL_OBSERVATION_COLUMNS["y_name"])
        query = f"""
        {include_select}
        FROM {escape_table(table_name)}
        WHERE {escape_identifier(id_col)} = ?
          AND {escape_identifier('LocalCol')} = ?
          AND ABS(CAST({y_col} AS FLOAT) - ?) <= ?
        """
        return query, obs_col, val_col + ", " + y_name_col

    def upsert_observation(self, cmd: ObservationCommand) -> ObservationResult:
        table_name = dynamic_table_name(cmd.cyl_num)
        id_col = cylinder_id_column(cmd.cyl_num)
        y_col = escape_identifier(cmd.y_column_name)
        tolerance = 1e-9
        count_query = f"""
        SELECT COUNT(*)
        FROM {escape_table(table_name)}
        WHERE {escape_identifier(id_col)} = ?
          AND {escape_identifier('LocalCol')} = ?
          AND ABS(CAST({y_col} AS FLOAT) - ?) <= ?
        """
        _, count_rows = self.conn.fetch_all(count_query, (cmd.test_id, cmd.local_col, float(cmd.y_value or 0.0), tolerance))
        matched = int(count_rows[0][0]) if count_rows else 0

        if matched == 0:
            raise NotFoundError("Nao foi encontrado ponto unico para gravar observacao.")
        if matched > 1:
            raise AmbiguousMatchError("Mais de uma linha encontrada para o ponto selecionado.")

        update_query = f"""
        UPDATE {escape_table(table_name)}
        SET {escape_identifier(CANONICAL_OBSERVATION_COLUMNS['obs'])} = ?,
            {escape_identifier(CANONICAL_OBSERVATION_COLUMNS['val'])} = ?,
            {escape_identifier(CANONICAL_OBSERVATION_COLUMNS['y_name'])} = ?
        WHERE {escape_identifier(id_col)} = ?
          AND {escape_identifier('LocalCol')} = ?
          AND ABS(CAST({y_col} AS FLOAT) - ?) <= ?
        """
        rowcount = self.conn.execute(update_query, (
            cmd.obs_text,
            cmd.y_value,
            cmd.y_column_name,
            cmd.test_id,
            cmd.local_col,
            float(cmd.y_value or 0.0),
            tolerance,
        ))
        if rowcount != 1:
            raise PersistenceError("Falha ao gravar observacao de forma atomica.")

        return ObservationResult(
            updated=True,
            matched_rows=rowcount,
            columns_used=CANONICAL_OBSERVATION_COLUMNS,
        )

    def get_observation(self, lookup: ObservationLookup) -> ObservationRecord | None:
        table_name = dynamic_table_name(lookup.cyl_num)
        id_col = cylinder_id_column(lookup.cyl_num)
        y_col = escape_identifier(lookup.y_column_name)
        tolerance = 1e-9
        query = f"""
        SELECT TOP 2
            {escape_identifier(CANONICAL_OBSERVATION_COLUMNS['obs'])},
            {escape_identifier(CANONICAL_OBSERVATION_COLUMNS['y_name'])},
            {escape_identifier(CANONICAL_OBSERVATION_COLUMNS['val'])}
        FROM {escape_table(table_name)}
        WHERE {escape_identifier(id_col)} = ?
          AND {escape_identifier('LocalCol')} = ?
          AND ABS(CAST({y_col} AS FLOAT) - ?) <= ?
        """
        _, rows = self.conn.fetch_all(query, (
            lookup.test_id,
            lookup.local_col,
            float(lookup.y_value or 0.0),
            tolerance,
        ))
        if not rows:
            return None
        if len(rows) > 1:
            raise AmbiguousMatchError("Mais de um registro encontrado para leitura de observacao.")
        row = rows[0]
        return ObservationRecord(obs_text=row[0], y_column_name=row[1], val_obs=row[2])

    def delete_observation(self, lookup: ObservationLookup) -> bool:
        table_name = dynamic_table_name(lookup.cyl_num)
        id_col = cylinder_id_column(lookup.cyl_num)
        y_col = escape_identifier(lookup.y_column_name)
        tolerance = 1e-9
        query = f"""
        UPDATE {escape_table(table_name)}
        SET {escape_identifier(CANONICAL_OBSERVATION_COLUMNS['obs'])} = NULL,
            {escape_identifier(CANONICAL_OBSERVATION_COLUMNS['val'])} = NULL,
            {escape_identifier(CANONICAL_OBSERVATION_COLUMNS['y_name'])} = NULL
        WHERE {escape_identifier(id_col)} = ?
          AND {escape_identifier('LocalCol')} = ?
          AND ABS(CAST({y_col} AS FLOAT) - ?) <= ?
        """
        rowcount = self.conn.execute(query, (
            lookup.test_id,
            lookup.local_col,
            float(lookup.y_value or 0.0),
            tolerance,
        ))
        if rowcount > 1:
            raise AmbiguousMatchError("Exclusao ambigua: mais de uma linha foi alterada.")
        return rowcount == 1


class SqlDiagnosticsRepository:
    def __init__(self, conn: SqlServerConnection):
        self.conn = conn

    def diagnostics(self, active_context: dict[str, object]) -> DiagnosticsInfo:
        drivers = self.conn.list_drivers()
        connection_ok = False
        message = "Nao testado"
        try:
            self.conn.fetch_all("SELECT 1")
            connection_ok = True
            message = "Conexao SQL Server ativa."
        except Exception as exc:  # pragma: no cover - depende de ambiente
            message = str(exc)
        return DiagnosticsInfo(
            odbc_drivers=drivers,
            connection_ok=connection_ok,
            connection_message=message,
            active_context=active_context,
            checked_at=datetime.utcnow(),
        )
