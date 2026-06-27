from __future__ import annotations

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.ui.streamlit_app import _plot_multiaxis


def test_ui_initial_render_has_core_controls() -> None:
    app = AppTest.from_file("app.py")
    app.run(timeout=10)

    assert len(app.title) >= 1
    assert "Painel Tecnico de Ensaios Industriais" in app.title[0].value

    labels = [sb.label for sb in app.selectbox]
    assert "Cilindro" in labels
    assert "ID_Teste" in labels

    button_labels = [btn.label for btn in app.button]
    assert "Carregar ensaio" in button_labels


def test_ui_initial_state_shows_empty_message() -> None:
    app = AppTest.from_file("app.py")
    app.run(timeout=10)

    info_values = [info.value for info in app.info]
    assert any("Sem dados carregados" in value for value in info_values)


def test_plot_multiaxis_generates_independent_axes() -> None:
    data = pd.DataFrame(
        {
            "LocalCol": [1, 2, 3],
            "Forca": [10.0, 11.0, 12.0],
            "Pressao_Compressor": [2.0, 2.1, 2.2],
        }
    )
    fig = _plot_multiaxis(data, ["Forca", "Pressao_Compressor"])

    assert len(fig.data) == 2
    assert fig.data[0].name == "Forca"
    assert fig.data[1].name == "Pressao_Compressor"
    assert fig.layout.yaxis.title.text == "Forca"
    assert fig.layout.yaxis2.title.text == "Pressao_Compressor"
