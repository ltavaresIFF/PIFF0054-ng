from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class TestContext:
    cyl_num: int
    test_id: str


@dataclass(frozen=True)
class ObservationCommand:
    cyl_num: int
    test_id: str
    local_col: Any
    y_column_name: str
    y_value: float | None
    obs_text: str | None


@dataclass(frozen=True)
class ObservationLookup:
    cyl_num: int
    test_id: str
    local_col: Any
    y_column_name: str
    y_value: float | None


@dataclass(frozen=True)
class ObservationResult:
    updated: bool
    matched_rows: int
    columns_used: dict[str, str]


@dataclass(frozen=True)
class ObservationRecord:
    obs_text: str | None
    y_column_name: str | None
    val_obs: float | None


@dataclass(frozen=True)
class DynamicDataResult:
    rows: pd.DataFrame
    ordered_by: str

    @property
    def total_rows(self) -> int:
        return len(self.rows)


@dataclass(frozen=True)
class StaticDataResult:
    row: pd.DataFrame
    table_used: str


@dataclass(frozen=True)
class DiagnosticsInfo:
    odbc_drivers: list[str]
    connection_ok: bool
    connection_message: str
    active_context: dict[str, Any]
    checked_at: datetime
