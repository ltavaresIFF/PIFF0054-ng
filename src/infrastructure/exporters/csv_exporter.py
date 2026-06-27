from __future__ import annotations

from io import BytesIO

import pandas as pd


class SemicolonCsvExporter:
    def export(self, rows: pd.DataFrame) -> bytes:
        buffer = BytesIO()
        rows.to_csv(buffer, sep=";", index=False, encoding="utf-8-sig")
        return buffer.getvalue()
