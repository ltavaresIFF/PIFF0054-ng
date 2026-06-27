import pandas as pd

from src.application.services import ExportService, TestReadService
from src.infrastructure.cache import TTLCache
from src.infrastructure.exporters.csv_exporter import SemicolonCsvExporter
from src.infrastructure.exporters.pdf_exporter import TechnicalPdfExporter


class _FakeRepo:
    def list_test_ids(self, cyl_num: int):
        return ["TESTE_1"]

    def load_dynamic_rows(self, ctx, selected_columns=None):
        rows = pd.DataFrame({"LocalCol": [1, 2], "Forca": [10.0, 11.0]})
        from src.domain.models import DynamicDataResult

        return DynamicDataResult(rows=rows, ordered_by="LocalCol")

    def load_static_row(self, ctx):
        row = pd.DataFrame({"Status_Ensaio": ["OK"]})
        from src.domain.models import StaticDataResult

        return StaticDataResult(row=row, table_used="Cilindro_01_Estatico")

    def detect_force_column(self, cyl_num: int):
        return "Forca"

    def load_available_y_columns(self, cyl_num: int):
        return ["Forca"]


def test_read_service_and_cache_ids():
    service = TestReadService(repository=_FakeRepo(), cache=TTLCache(60))
    ids_first = service.list_test_ids(1)
    ids_second = service.list_test_ids(1)
    assert ids_first == ids_second == ["TESTE_1"]


def test_export_service_csv_and_pdf():
    service = ExportService(SemicolonCsvExporter(), TechnicalPdfExporter())
    rows = pd.DataFrame({"LocalCol": [1], "Forca": [123.4]})
    csv_data = service.export_csv(rows)
    assert b";" in csv_data

    pdf_data = service.export_pdf(
        rows=rows,
        static_row=pd.DataFrame({"Status_Ensaio": ["OK"]}),
        request=type("Req", (), {
            "export_mode": "config_atual",
            "metadata": {"test_id": "TESTE_1"},
            "graph_png": None,
            "table_sample_max_rows": 500,
        })(),
    )
    assert pdf_data.startswith(b"%PDF")
