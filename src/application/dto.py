from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LoadTestResponse:
    rows: Any
    static_row: Any
    force_column: str | None
    available_y_columns: list[str]
    meta: dict[str, Any]


@dataclass(frozen=True)
class ExportPdfRequest:
    export_mode: str
    metadata: dict[str, Any]
    graph_png: bytes | None
    table_sample_max_rows: int = 500
