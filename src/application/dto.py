"""@brief Data Transfer Objects (DTOs) da camada de aplicação.

Define estruturas de dados para transferência entre as camadas
de serviço e apresentação, desacoplando a interface dos modelos de domínio.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LoadTestResponse:
    """@brief DTO com a resposta completa do carregamento de um ensaio.

    @param rows DataFrame com os dados dinâmicos da série temporal.
    @param static_row DataFrame com os dados estáticos de configuração.
    @param force_column Nome da coluna de força detectada, ou None.
    @param available_y_columns Lista de colunas Y disponíveis para plotagem.
    @param meta Metadados da consulta (ordenação, total de linhas, tabela usada).
    """
    rows: Any
    static_row: Any
    force_column: str | None
    available_y_columns: list[str]
    meta: dict[str, Any]


@dataclass(frozen=True)
class ExportPdfRequest:
    """@brief DTO com parâmetros para exportação de relatório PDF.

    @param export_mode Modo de exportação ("config_atual" ou "todos_valores").
    @param metadata Metadados do ensaio para incluir no relatório.
    @param graph_png Imagem do gráfico em PNG, ou None.
    @param table_sample_max_rows Máximo de linhas na amostra da tabela (padrão: 500).
    """
    export_mode: str
    metadata: dict[str, Any]
    graph_png: bytes | None
    table_sample_max_rows: int = 500
