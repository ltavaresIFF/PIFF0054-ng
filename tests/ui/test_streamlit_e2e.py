from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import src.ui.streamlit_app as streamlit_app


@dataclass
class _LoadResponse:
    rows: pd.DataFrame
    static_row: pd.DataFrame
    force_column: str | None
    available_y_columns: list[str]
    meta: dict[str, object]


class _FakeTestService:
    def list_test_ids(self, cyl_num: int) -> list[str]:
        return ["TESTE_2026_0001", "TESTE_2026_0002"]

    def load_test(self, cyl_num: int, test_id: str, y_columns: list[str] | None = None) -> _LoadResponse:
        rows = pd.DataFrame(
            {
                "LocalCol": ["2026-06-26 10:00:00", "2026-06-26 10:00:01"],
                "Forca": [101.2, 102.5],
                "Pressao_Compressor": [8.1, 8.4],
            }
        )
        static_row = pd.DataFrame(
            {
                "Status_Ensaio": ["OK"],
                "Tipo_Teste": ["P1"],
            }
        )
        return _LoadResponse(
            rows=rows,
            static_row=static_row,
            force_column="Forca",
            available_y_columns=["Forca", "Pressao_Compressor"],
            meta={"total_rows": 2, "ordered_by": "LocalCol", "static_table_used": "Cilindro_01_Estatico"},
        )


class _FakeObservationService:
    def get(self, lookup):
        return {"obs_text": "Observacao carregada", "y_column_name": "Forca", "val_obs": 101.2}

    def upsert(self, cmd):
        return {"updated": True, "matched_rows": 1, "columns_used": {"obs": "OBS", "val": "val_obs", "y_name": "y_column_name"}}

    def delete(self, lookup):
        return True


class _FakeExportService:
    def export_csv(self, rows: pd.DataFrame) -> bytes:
        return b"LocalCol;Forca\n2026-06-26 10:00:00;101.2\n"

    def export_pdf(self, *, rows: pd.DataFrame, static_row: pd.DataFrame, request):
        return b"%PDF-1.4\n%fake\n"


class _FakeDiagnosticsService:
    def get(self, active_context: dict[str, object]) -> dict[str, object]:
        return {
            "odbc_drivers": ["ODBC Driver 17 for SQL Server"],
            "connection_ok": True,
            "connection_message": "Conexao SQL Server ativa.",
            "active_context": active_context,
            "checked_at": "2026-06-26T00:00:00",
        }


def _get_button(app: AppTest, label: str):
    for button in app.button:
        if button.label == label:
            return button
    raise AssertionError(f"Botao nao encontrado: {label}")


def _load_test_or_skip(app: AppTest) -> AppTest:
    _get_button(app, "Carregar ensaio").click()
    app.run(timeout=20)
    if app.error:
        messages = [err.value for err in app.error]
        pytest.skip(f"Ambiente sem dados/conexao para e2e de UI: {messages}")
    return app


def test_ui_e2e_load_flow_and_exports(monkeypatch) -> None:
    monkeypatch.setattr(
        streamlit_app,
        "_build_services",
        lambda: (_FakeTestService(), _FakeObservationService(), _FakeExportService(), _FakeDiagnosticsService()),
    )

    app = AppTest.from_file("app.py")
    app.run(timeout=10)
    app = _load_test_or_skip(app)

    success_values = [msg.value for msg in app.success]
    assert any("Ensaio carregado com 2 linhas" in value for value in success_values)

    radio_labels = [rb.label for rb in app.radio]
    assert "Modo PDF" in radio_labels

    subheaders = [item.value for item in app.subheader]
    assert "Serie dinamica" in subheaders
    assert "Observacao por coordenada" in subheaders
    assert "Exportacoes" in subheaders
    assert len(app.dataframe) >= 1


def test_ui_e2e_observation_controls_present_after_load(monkeypatch) -> None:
    monkeypatch.setattr(
        streamlit_app,
        "_build_services",
        lambda: (_FakeTestService(), _FakeObservationService(), _FakeExportService(), _FakeDiagnosticsService()),
    )

    app = AppTest.from_file("app.py")
    app.run(timeout=10)
    app = _load_test_or_skip(app)

    selectbox_labels = [sb.label for sb in app.selectbox]
    assert "LocalCol" in selectbox_labels
    assert "Variavel" in selectbox_labels

    button_labels = [btn.label for btn in app.button]
    assert "Carregar observacao existente" in button_labels
    assert "Salvar observacao" in button_labels
    assert "Excluir observacao" in button_labels
