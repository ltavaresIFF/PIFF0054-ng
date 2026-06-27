"""@brief Protocolos (interfaces) da camada de domínio.

Define os contratos que os adaptadores de infraestrutura devem implementar
para consulta de dados, persistência de observações, exportação e diagnóstico.
"""

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
    """@brief Protocolo para consulta de dados de ensaio no banco SQL.

    Define as operações de leitura para tabelas dinâmicas (série temporal)
    e estáticas (configuração) por cilindro e ID de teste.
    """

    def list_test_ids(self, cyl_num: int) -> list[str]:
        """@brief Lista os IDs de teste disponíveis para um cilindro."""

    def load_dynamic_rows(self, ctx: TestContext, selected_columns: list[str] | None = None) -> DynamicDataResult:
        """@brief Carrega as linhas da tabela dinâmica (série temporal) para um ensaio."""

    def load_static_row(self, ctx: TestContext) -> StaticDataResult:
        """@brief Carrega a linha de configuração estática para um ensaio."""

    def detect_force_column(self, cyl_num: int) -> str | None:
        """@brief Detecta automaticamente a coluna de força disponível na tabela dinâmica."""

    def load_available_y_columns(self, cyl_num: int) -> list[str]:
        """@brief Lista as colunas numéricas disponíveis como variáveis Y para plotagem."""


class ObservationCommandRepository(Protocol):
    """@brief Protocolo para operações CRUD de observações por coordenada."""

    def upsert_observation(self, cmd: ObservationCommand) -> ObservationResult:
        """@brief Cria ou atualiza uma observação em uma coordenada específica."""

    def get_observation(self, lookup: ObservationLookup) -> ObservationRecord | None:
        """@brief Recupera uma observação existente pela chave composta."""

    def delete_observation(self, lookup: ObservationLookup) -> bool:
        """@brief Remove uma observação pela chave composta."""


class DiagnosticsRepository(Protocol):
    """@brief Protocolo para obtenção de informações de diagnóstico do sistema."""

    def diagnostics(self, active_context: dict[str, object]) -> DiagnosticsInfo:
        """@brief Retorna diagnóstico completo: drivers ODBC, estado da conexão e contexto ativo."""


class CsvExporter(Protocol):
    """@brief Protocolo para exportação de dados no formato CSV."""

    def export(self, rows: pd.DataFrame) -> bytes:
        """@brief Exporta um DataFrame para bytes no formato CSV."""


class PdfExporter(Protocol):
    """@brief Protocolo para exportação de relatório técnico em PDF."""

    def export(
        self,
        *,
        rows: pd.DataFrame,
        static_row: pd.DataFrame,
        metadata: dict[str, object],
        graph_png: bytes | None,
        sample_max_rows: int,
    ) -> bytes:
        """@brief Gera um relatório PDF com gráfico, tabela estática e amostra dos dados dinâmicos."""
