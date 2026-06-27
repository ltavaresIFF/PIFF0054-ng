from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from src.application.dto import ExportPdfRequest, LoadTestResponse
from src.application.validators import (
    validate_cylinder,
    validate_observation_command,
    validate_observation_lookup,
    validate_test_id,
)
from src.domain.errors import NotFoundError
from src.domain.models import ObservationCommand, ObservationLookup, TestContext
from src.domain.repositories import (
    CsvExporter,
    DiagnosticsRepository,
    ObservationCommandRepository,
    PdfExporter,
    TestQueryRepository,
)
from src.infrastructure.cache import TTLCache


class TestReadService:
    __test__ = False

    def __init__(self, repository: TestQueryRepository, cache: TTLCache):
        self.repository = repository
        self.cache = cache

    def list_test_ids(self, cyl_num: int) -> list[str]:
        validate_cylinder(cyl_num)
        cache_key = f"ids:{cyl_num}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        ids = self.repository.list_test_ids(cyl_num)
        self.cache.set(cache_key, ids)
        return ids

    def load_test(self, cyl_num: int, test_id: str, y_columns: list[str] | None = None) -> LoadTestResponse:
        validate_cylinder(cyl_num)
        validate_test_id(test_id)
        cache_key = f"test:{cyl_num}:{test_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        ctx = TestContext(cyl_num=cyl_num, test_id=test_id)
        # Single ODBC connection for all queries — avoids ~300ms handshake per query.
        with self.repository.conn.connect_shared() as _conn:  # type: ignore[attr-defined]
            dynamic = self.repository.load_dynamic_rows(ctx, selected_columns=y_columns, _conn=_conn)
            if dynamic.rows.empty:
                raise NotFoundError("Nenhum dado dinamico encontrado para o teste informado.")
            static_data = self.repository.load_static_row(ctx, _conn=_conn)
            force_column = self.repository.detect_force_column(cyl_num, _conn=_conn)
            available_y = self.repository.load_available_y_columns(cyl_num, _conn=_conn)
        response = LoadTestResponse(
            rows=dynamic.rows,
            static_row=static_data.row,
            force_column=force_column,
            available_y_columns=available_y,
            meta={
                "ordered_by": dynamic.ordered_by,
                "total_rows": dynamic.total_rows,
                "static_table_used": static_data.table_used,
            },
        )
        self.cache.set(cache_key, response)
        return response


class ObservationService:
    def __init__(self, repository: ObservationCommandRepository):
        self.repository = repository

    def upsert(self, cmd: ObservationCommand) -> dict[str, object]:
        valid_cmd = validate_observation_command(cmd)
        result = self.repository.upsert_observation(valid_cmd)
        return asdict(result)

    def get(self, lookup: ObservationLookup) -> dict[str, object] | None:
        validate_observation_lookup(lookup)
        record = self.repository.get_observation(lookup)
        if record is None:
            return None
        return asdict(record)

    def delete(self, lookup: ObservationLookup) -> bool:
        validate_observation_lookup(lookup)
        return self.repository.delete_observation(lookup)


class ExportService:
    def __init__(self, csv_exporter: CsvExporter, pdf_exporter: PdfExporter):
        self.csv_exporter = csv_exporter
        self.pdf_exporter = pdf_exporter

    def export_csv(self, rows: pd.DataFrame) -> bytes:
        return self.csv_exporter.export(rows)

    def export_pdf(
        self,
        *,
        rows: pd.DataFrame,
        static_row: pd.DataFrame,
        request: ExportPdfRequest,
    ) -> bytes:
        export_rows = rows
        if request.export_mode == "config_atual" and len(rows) > request.table_sample_max_rows:
            export_rows = rows.head(request.table_sample_max_rows)
        return self.pdf_exporter.export(
            rows=export_rows,
            static_row=static_row,
            metadata=request.metadata,
            graph_png=request.graph_png,
            sample_max_rows=request.table_sample_max_rows,
        )


class DiagnosticsService:
    def __init__(self, repository: DiagnosticsRepository):
        self.repository = repository

    def get(self, active_context: dict[str, object]) -> dict[str, object]:
        data = self.repository.diagnostics(active_context)
        return {
            "odbc_drivers": data.odbc_drivers,
            "connection_ok": data.connection_ok,
            "connection_message": data.connection_message,
            "active_context": data.active_context,
            "checked_at": data.checked_at.isoformat(),
        }
