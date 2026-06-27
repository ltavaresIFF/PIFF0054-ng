"""@brief Aplicação Streamlit do Painel Técnico PIFF-0054.

Interface web para visualização de ensaios industriais com gráficos
multi-eixo interativos (Plotly), anotação de observações por coordenada
e exportação de relatórios CSV/PDF.
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.application.dto import ExportPdfRequest
from src.application.services import DiagnosticsService, ExportService, ObservationService, TestReadService
from src.config.settings import SETTINGS
from src.domain.errors import DomainError
from src.domain.models import ObservationCommand, ObservationLookup
from src.infrastructure.cache_redis import RedisCache
from src.infrastructure.exporters.csv_exporter import SemicolonCsvExporter
from src.infrastructure.exporters.pdf_exporter import TechnicalPdfExporter
from src.infrastructure.sql.connection import SqlServerConnection
from src.infrastructure.sql.repositories import (
    SqlDiagnosticsRepository,
    SqlObservationRepository,
    SqlTestQueryRepository,
)
from src.ui.theme import inject_theme, render_kpis, render_signature_flow


def _build_services() -> tuple[TestReadService, ObservationService, ExportService, DiagnosticsService]:
    """@brief Constrói ou recupera os serviços da sessão Streamlit.

    Os serviços são persistidos em st.session_state para que o cache TTL
    e o cache de colunas do repositório sobrevivam aos rerenders do Streamlit,
    evitando reconstrução em cada interação.

    @return Tupla (TestReadService, ObservationService, ExportService, DiagnosticsService).
    """
    # Persist services in session_state so TTLCache and repository column-cache
    # survive across Streamlit rerenders (avoids rebuilding on every interaction).
    if "_svc" not in st.session_state:
        conn = SqlServerConnection(SETTINGS)
        cache = RedisCache(ttl_seconds=SETTINGS.cache_ttl_seconds)
        test_repo = SqlTestQueryRepository(conn)
        obs_repo = SqlObservationRepository(conn)
        diag_repo = SqlDiagnosticsRepository(conn)
        test_service = TestReadService(test_repo, cache)
        obs_service = ObservationService(obs_repo)
        export_service = ExportService(SemicolonCsvExporter(), TechnicalPdfExporter())
        diag_service = DiagnosticsService(diag_repo)
        st.session_state._svc = (test_service, obs_service, export_service, diag_service)
    return st.session_state._svc


def _plot_multiaxis(df: pd.DataFrame, y_cols: list[str]) -> go.Figure:
    """@brief Gera gráfico multi-eixo interativo com Plotly.

    Cada variável Y recebe um eixo próprio sobreposto, com posição
    alternada (esquerda/direita) para visualização simultânea.
    Paleta de cores "Industrial Precision" com 6 cores.

    @param df DataFrame com os dados dinâmicos.
    @param y_cols Lista de colunas Y a plotar.
    @return Figure do Plotly (go.Figure).
    """
    # Industrial Precision colour sequence
    _TRACE_COLORS = [
        "#f0883e",  # amber
        "#5b9bd5",  # steel blue
        "#6bbf6b",  # industrial green
        "#e05555",  # warning red
        "#e8c84a",  # caution yellow
        "#9b8ec4",  # muted violet
    ]
    _GRID  = "rgba(240, 136, 62, 0.06)"
    _BG    = "#14181c"
    _PAPER = "#1a1f24"
    _INK   = "rgba(236, 232, 222, 0.72)"

    fig = go.Figure()
    if not y_cols:
        return fig
    x = df["LocalCol"] if "LocalCol" in df.columns else df.index
    for idx, col in enumerate(y_cols):
        axis_name = "y" if idx == 0 else f"y{idx + 1}"
        fig.add_trace(
            go.Scatter(
                x=x,
                y=df[col],
                mode="lines",
                name=col,
                yaxis=axis_name,
                line={
                    "color": _TRACE_COLORS[idx % len(_TRACE_COLORS)],
                    "width": 2.0,
                },
            )
        )
    _axis_style = dict(
        color=_INK,
        gridcolor=_GRID,
        zerolinecolor=_GRID,
        linecolor="rgba(240,136,62,0.15)",
        tickfont={"family": "IBM Plex Mono, monospace", "size": 10, "color": _INK},
    )
    layout_axes: dict = {}
    for idx, col in enumerate(y_cols):
        if idx == 0:
            layout_axes["yaxis"] = {
                "title": {"text": col, "font": {"family": "Barlow Condensed, sans-serif", "size": 12, "color": _INK}},
                **_axis_style,
            }
            continue
        layout_axes[f"yaxis{idx + 1}"] = {
            "title": {"text": col, "font": {"family": "Barlow Condensed, sans-serif", "size": 12, "color": _INK}},
            "overlaying": "y",
            "side": "right",
            "position": min(0.99, 1 - (idx - 1) * 0.07),
            **_axis_style,
        }
    fig.update_layout(
        plot_bgcolor=_BG,
        paper_bgcolor=_PAPER,
        xaxis={
            "title": {"text": "LocalCol", "font": {"family": "Barlow Condensed, sans-serif", "size": 12, "color": _INK}},
            **_axis_style,
        },
        margin={"l": 10, "r": 10, "t": 32, "b": 10},
        legend={
            "orientation": "h",
            "font": {"family": "IBM Plex Mono, monospace", "size": 10, "color": _INK},
            "bgcolor": "rgba(26,31,36,0.72)",
            "bordercolor": "rgba(240,136,62,0.15)",
            "borderwidth": 1,
        },
        font={"family": "Barlow Condensed, sans-serif", "color": _INK},
        **layout_axes,
    )
    return fig


def _friendly_error(exc: Exception) -> str:
    """@brief Normaliza exceções para mensagens amigáveis ao usuário.

    @param exc Exceção capturada.
    @return String com mensagem legível para o operador.
    """
    if isinstance(exc, DomainError):
        return str(exc)
    return "Falha inesperada. Verifique diagnosticos e configuracao de conexao."


def main() -> None:
    """@brief Ponto de entrada da aplicação Streamlit.

    Configura a página, injeta o tema, constrói os serviços e
    renderiza o fluxo completo de interação: seleção de ensaio,
    visualização, anotação, exportação e diagnósticos.
    """
    st.set_page_config(
        page_title="PIFF-0054 · Painel Tecnico",
        page_icon="⬡",
        layout="wide",
    )
    inject_theme()
    st.markdown(
        """
        <div class="piff-page-header">
          <div class="piff-page-title">Painel Tecnico de Ensaios Industriais</div>
          <div class="piff-page-sub">PIFF-0054 &nbsp;&middot;&nbsp; Serie temporal &nbsp;&middot;&nbsp; Anotacao &nbsp;&middot;&nbsp; Exportacao</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_signature_flow()

    test_service, obs_service, export_service, diag_service = _build_services()

    with st.sidebar:
        st.markdown(
            """
            <div class="piff-brand">
              <span class="piff-brand-icon">⬡</span>
              <div>
                <div class="piff-brand-name">PIFF-0054</div>
                <div class="piff-brand-tag">Ensaios Industriais</div>
              </div>
            </div>
            <hr class="piff-hr">
            <span class="piff-sidebar-label">Contexto do Ensaio</span>
            """,
            unsafe_allow_html=True,
        )
        cyl_num = st.selectbox(
            "Cilindro",
            options=list(SETTINGS.allowed_cylinders),
            index=0,
            help="Selecione o cilindro hidraulico a analisar. Cada cilindro possui tabela dinamica e estatica proprias no banco Projeto_54.",
        )
        try:
            test_ids = test_service.list_test_ids(cyl_num)
        except Exception as exc:
            test_ids = []
            st.error(_friendly_error(exc))
        test_id = (
            st.selectbox(
                "ID_Teste",
                options=test_ids,
                help="Identificador unico do ensaio. Formato CXX_TESTE_YYY. Lista carregada do banco para o cilindro selecionado.",
            )
            if test_ids
            else st.text_input(
                "ID_Teste",
                placeholder="Ex: C01_TESTE_001",
                help="Digite manualmente o ID do ensaio se a lista automatica nao estiver disponivel.",
            )
        )
        load_clicked = st.button(
            "Carregar ensaio",
            type="primary",
            help="Consulta as tabelas dinamica e estatica do banco e carrega os dados na sessao atual. Os resultados ficam em cache por 5 minutos.",
        )

    if "loaded_rows" not in st.session_state:
        st.session_state.loaded_rows = None
    if "loaded_static" not in st.session_state:
        st.session_state.loaded_static = None
    if "available_y" not in st.session_state:
        st.session_state.available_y = []
    if "force_col" not in st.session_state:
        st.session_state.force_col = None

    if load_clicked:
        try:
            response = test_service.load_test(cyl_num, test_id)
            st.session_state.loaded_rows = response.rows
            st.session_state.loaded_static = response.static_row
            st.session_state.available_y = response.available_y_columns
            st.session_state.force_col = response.force_column
            st.success(f"Ensaio carregado com {response.meta['total_rows']} linhas.")
        except Exception as exc:
            st.error(_friendly_error(exc))

    rows: pd.DataFrame | None = st.session_state.loaded_rows
    static_row: pd.DataFrame | None = st.session_state.loaded_static

    if rows is None or rows.empty:
        st.markdown(
            """
            <div class="piff-empty">
              <div class="piff-empty-icon">◎</div>
              <div class="piff-empty-title">Nenhum ensaio carregado</div>
              <div class="piff-empty-desc">
                Selecione o <strong>Cilindro</strong> e o <strong>ID_Teste</strong>
                no painel lateral e clique em <strong>Carregar ensaio</strong>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        preferred = [st.session_state.force_col] if st.session_state.force_col else []
        default_y = [c for c in preferred if c in st.session_state.available_y]
        y_cols = st.multiselect(
            "Variaveis Y",
            options=st.session_state.available_y,
            default=default_y,
            help="Escolha uma ou mais colunas numericas para exibir no grafico multi-eixo. A coluna de forca e pre-selecionada automaticamente quando detectada.",
        )
        render_kpis(total_rows=len(rows), y_selected=len(y_cols), obs_ready=bool(y_cols))

        tab_ops, tab_evidence, tab_diag = st.tabs(["Operacao", "Evidencias", "Diagnosticos"])

        fig = _plot_multiaxis(rows, y_cols)

        with tab_ops:
            st.plotly_chart(fig, width="stretch")

            st.markdown('<div class="piff-form-section">Observacao por Coordenada</div>', unsafe_allow_html=True)
            loc_c1, loc_c2, loc_c3 = st.columns([1, 1, 1])
            with loc_c1:
                local_col = st.selectbox(
                    "LocalCol",
                    options=list(rows["LocalCol"]),
                    help="Instante de medicao (timestamp) usado como chave para vincular a observacao. Corresponde ao eixo X do grafico.",
                )
                y_col = st.selectbox(
                    "Variavel",
                    options=y_cols or st.session_state.available_y,
                    help="Variavel numerica cujo valor sera registrado junto com a observacao. Selecione a mesma variavel de interesse no grafico.",
                )
                y_value = None
                if y_col:
                    selected = rows.loc[rows["LocalCol"] == local_col]
                    if not selected.empty and y_col in selected.columns:
                        y_value = float(selected.iloc[0][y_col])
                        st.text_input(
                            "Valor Y",
                            value=str(y_value),
                            disabled=True,
                            help="Valor lido diretamente da serie temporal para o instante e variavel selecionados. Somente leitura.",
                        )
                if st.button(
                    "Carregar observacao existente",
                    help="Busca no banco uma observacao ja salva para exatamente este instante (LocalCol), variavel e valor Y.",
                ) and y_col:
                    try:
                        existing = obs_service.get(
                            ObservationLookup(
                                cyl_num=cyl_num,
                                test_id=test_id,
                                local_col=local_col,
                                y_column_name=y_col,
                                y_value=y_value,
                            )
                        )
                        if existing:
                            st.session_state.obs_text = existing.get("obs_text") or ""
                    except Exception as exc:
                        st.error(_friendly_error(exc))

                st.markdown('<div class="piff-form-section">Registro de Observacao</div>', unsafe_allow_html=True)
                obs_text = st.text_area(
                    "Observacao",
                    value=st.session_state.get("obs_text", ""),
                    height=120,
                    placeholder="Ex: Pico acima do setpoint — verificar valvula de controle. Ruido suspeito no sensor.",
                    help="Texto livre para registrar anomalias, ajustes ou notas tecnicas sobre este ponto do ensaio. Salvo no banco vinculado ao cilindro, ensaio, instante e variavel.",
                )

                save_col, del_col = st.columns(2)
                with save_col:
                    if st.button(
                        "Salvar observacao",
                        type="primary",
                        help="Grava (ou atualiza) a observacao no banco para o contexto atual: cilindro / ensaio / instante / variavel.",
                    ) and y_col:
                        try:
                            result = obs_service.upsert(
                                ObservationCommand(
                                    cyl_num=cyl_num,
                                    test_id=test_id,
                                    local_col=local_col,
                                    y_column_name=y_col,
                                    y_value=y_value,
                                    obs_text=obs_text,
                                )
                            )
                            st.success(f"Observacao salva. matched_rows={result['matched_rows']}")
                        except Exception as exc:
                            st.error(_friendly_error(exc))
                with del_col:
                    if st.button(
                        "Excluir observacao",
                        help="Remove permanentemente a observacao do banco para o ponto selecionado. Esta acao nao pode ser desfeita.",
                    ) and y_col:
                        try:
                            deleted = obs_service.delete(
                                ObservationLookup(
                                    cyl_num=cyl_num,
                                    test_id=test_id,
                                    local_col=local_col,
                                    y_column_name=y_col,
                                    y_value=y_value,
                                )
                            )
                            if deleted:
                                st.success("Observacao excluida.")
                            else:
                                st.warning("Nenhuma observacao para excluir no ponto selecionado.")
                        except Exception as exc:
                            st.error(_friendly_error(exc))

        with tab_evidence:
            st.markdown('<div class="piff-form-section">Exportar Dados do Ensaio</div>', unsafe_allow_html=True)
            exp_c1, exp_c2 = st.columns(2)
            with exp_c1:
                st.markdown(
                    '<div class="piff-export-card">'
                    '<div class="piff-export-title">CSV (separador ;)</div>'
                    '<div class="piff-export-desc">Todos os dados dinamicos com separador ponto-e-virgula. Compativel com Excel PT-BR e pandas.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                csv_bytes = export_service.export_csv(rows)
                st.download_button(
                    "Exportar CSV (;)",
                    data=csv_bytes,
                    file_name=f"{test_id}_dados.csv",
                    mime="text/csv",
                    help="Baixa todos os dados dinamicos do ensaio em CSV com separador ponto-e-virgula. Compativel com Excel (PT-BR) e pandas.",
                )

            with exp_c2:
                st.markdown(
                    '<div class="piff-export-card">'
                    '<div class="piff-export-title">PDF Tecnico</div>'
                    '<div class="piff-export-desc">Relatorio com grafico, tabela estatica e amostra dos dados. Escolha o modo de exportacao abaixo.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                pdf_mode = st.radio(
                    "Modo PDF",
                    options=["config_atual", "todos_valores"],
                    horizontal=True,
                    help="'config_atual': inclui apenas as variaveis Y selecionadas no grafico. 'todos_valores': inclui todas as colunas numericas do ensaio.",
                )
                graph_png = None
                try:
                    graph_png = fig.to_image(format="png", width=1200, height=500)
                except Exception:
                    graph_png = None
                pdf_bytes = export_service.export_pdf(
                    rows=rows,
                    static_row=static_row if static_row is not None else pd.DataFrame(),
                    request=ExportPdfRequest(
                        export_mode=pdf_mode,
                        metadata={
                            "db_name": SETTINGS.sql_database,
                            "cyl_num": cyl_num,
                            "test_id": test_id,
                            "export_mode": pdf_mode,
                        },
                        graph_png=graph_png,
                    ),
                )
                st.download_button(
                    "Exportar PDF tecnico",
                    data=BytesIO(pdf_bytes).getvalue(),
                    file_name=f"{test_id}_relatorio.pdf",
                    mime="application/pdf",
                    help="Gera relatorio PDF com grafico da serie temporal, tabela de configuracao estatica e amostra dos dados dinamicos.",
                )

        with tab_diag:
            st.markdown('<div class="piff-form-section">Diagnosticos Operacionais</div>', unsafe_allow_html=True)
            st.markdown(
                '<p style="font-family:\'IBM Plex Mono\',monospace;font-size:0.73rem;'
                'color:var(--p-ink-dim);margin:0 0 12px;line-height:1.60">'
                'Estado em tempo real da conexao com o SQL Server, drivers ODBC instalados e contexto ativo.'
                '</p>',
                unsafe_allow_html=True,
            )
            try:
                diagnostics = diag_service.get(
                    {
                        "cyl_num": cyl_num,
                        "test_id": test_id,
                        "rows_loaded": int(len(rows)),
                    }
                )
                st.json(diagnostics)
            except Exception as exc:
                st.error(_friendly_error(exc))


if __name__ == "__main__":
    main()
