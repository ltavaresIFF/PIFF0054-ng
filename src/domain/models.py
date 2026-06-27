"""@brief Modelos e estruturas de dados do domínio do Projeto 54.

Define as dataclasses imutáveis que representam os conceitos centrais
do sistema: contextos de ensaio, comandos de observação, resultados
de consultas dinâmicas/estáticas e informações de diagnóstico.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class TestContext:
    """@brief Contexto que identifica unicamente um ensaio em um cilindro.

    @param cyl_num Número do cilindro hidráulico (1 a 6).
    @param test_id Identificador único do ensaio (ex: C01_TESTE_001).
    """

    cyl_num: int
    test_id: str


@dataclass(frozen=True)
class ObservationCommand:
    """@brief Comando para criar ou atualizar uma observação em uma coordenada.

    Veicula todos os dados necessários para localizar um ponto na série
    temporal e associar-lhe um texto descritivo de observação.

    @param cyl_num Número do cilindro.
    @param test_id Identificador do ensaio.
    @param local_col Instante (coordenada X) da observação.
    @param y_column_name Nome da variável Y alvo.
    @param y_value Valor numérico da variável Y no ponto.
    @param obs_text Texto livre da observação (pode ser None).
    """

    cyl_num: int
    test_id: str
    local_col: Any
    y_column_name: str
    y_value: float | None
    obs_text: str | None


@dataclass(frozen=True)
class ObservationLookup:
    """@brief Chave de busca para recuperar uma observação existente.

    @param cyl_num Número do cilindro.
    @param test_id Identificador do ensaio.
    @param local_col Instante (coordenada X) da observação.
    @param y_column_name Nome da variável Y alvo.
    @param y_value Valor numérico da variável Y no ponto.
    """

    cyl_num: int
    test_id: str
    local_col: Any
    y_column_name: str
    y_value: float | None


@dataclass(frozen=True)
class ObservationResult:
    """@brief Resultado da operação de upsert de observação.

    @param updated True se houve atualização de registro existente.
    @param matched_rows Quantidade de linhas afetadas pela operação.
    @param columns_used Mapeamento das colunas utilizadas na operação.
    """

    updated: bool
    matched_rows: int
    columns_used: dict[str, str]


@dataclass(frozen=True)
class ObservationRecord:
    """@brief Registro de observação recuperado do banco de dados.

    @param obs_text Texto descritivo da observação (pode ser None).
    @param y_column_name Nome da variável Y associada (pode ser None).
    @param val_obs Valor numérico observado (pode ser None).
    """

    obs_text: str | None
    y_column_name: str | None
    val_obs: float | None


@dataclass(frozen=True)
class DynamicDataResult:
    """@brief Resultado da consulta de dados dinâmicos (série temporal).

    @param rows DataFrame pandas com as linhas da tabela dinâmica.
    @param ordered_by Nome da coluna utilizada para ordenação.
    """

    rows: pd.DataFrame
    ordered_by: str

    @property
    def total_rows(self) -> int:
        """@brief Retorna o número total de linhas carregadas."""
        return len(self.rows)


@dataclass(frozen=True)
class StaticDataResult:
    """@brief Resultado da consulta de dados estáticos (configuração do ensaio).

    @param row DataFrame pandas com uma única linha de dados estáticos.
    @param table_used Nome da tabela utilizada na consulta.
    """

    row: pd.DataFrame
    table_used: str


@dataclass(frozen=True)
class DiagnosticsInfo:
    """@brief Informações detalhadas de diagnóstico do sistema.

    @param odbc_drivers Lista de drivers ODBC instalados no ambiente.
    @param connection_ok Indica se a conexão com o banco está ativa.
    @param connection_message Mensagem descritiva do estado da conexão.
    @param active_context Contexto ativo no momento da verificação.
    @param checked_at Timestamp da verificação de diagnóstico.
    """

    odbc_drivers: list[str]
    connection_ok: bool
    connection_message: str
    active_context: dict[str, Any]
    checked_at: datetime
