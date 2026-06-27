from __future__ import annotations

from typing import Protocol

import pandas as pd

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


class TestQueryRepository(Protocol):
    def list_test_ids(self, cyl_num: int) -> list[str]: ...

    def load_dynamic_rows(self, ctx: TestContext, selected_columns: list[str] | None = None) -> DynamicDataResult: ...

    def load_static_row(self, ctx: TestContext) -> StaticDataResult: ...

    def detect_force_column(self, cyl_num: int) -> str | None: ...

    def load_available_y_columns(self, cyl_num: int) -> list[str]: ...


class ObservationCommandRepository(Protocol):
    def upsert_observation(self, cmd: ObservationCommand) -> ObservationResult: ...

    def get_observation(self, lookup: ObservationLookup) -> ObservationRecord | None: ...

    def delete_observation(self, lookup: ObservationLookup) -> bool: ...


class DiagnosticsRepository(Protocol):
    def diagnostics(self, active_context: dict[str, object]) -> DiagnosticsInfo: ...


class CsvExporter(Protocol):
    def export(self, rows: pd.DataFrame) -> bytes: ...


class PdfExporter(Protocol):
    def export(
        self,
        *,
        rows: pd.DataFrame,
        static_row: pd.DataFrame,
        metadata: dict[str, object],
        graph_png: bytes | None,
        sample_max_rows: int,
    ) -> bytes: ...
