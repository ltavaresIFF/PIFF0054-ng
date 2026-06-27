"""@brief Schema do banco de dados Projeto_54.

Centraliza nomes canônicos de tabelas, colunas e funções de derivação
de identificadores para cada cilindro, garantindo consistência nas consultas.
"""

from __future__ import annotations


## @brief Mapeamento de nomes canônicos para colunas de observação no banco.
CANONICAL_OBSERVATION_COLUMNS = {
    "obs": "OBS",
    "val": "val_obs",
    "y_name": "y_column_name",
}

## @brief Candidatos a coluna de força (com e sem acento, português e inglês).
FORCE_COLUMN_CANDIDATES = ["Forca", "For\u00e7a", "FORCA", "Carga", "Load"]

## @brief Colunas excluídas automaticamente das consultas dinâmicas.
DYNAMIC_EXCLUDE_COLUMNS = {
    "RowId",
    "CreatedAt",
}

# Colunas carregadas por padrao (substitui SELECT *).
# Alinhadas com o INCLUDE do indice IX_Cilindro_XX_ID_Teste_LocalCol
# para garantir covering index scan — sem key lookups.
## @brief Conjunto padrão de colunas carregadas das tabelas dinâmicas.
DYNAMIC_DEFAULT_COLUMNS = {
    "Forca",
    "Pressao_Compressor",
    "Pressao_Reguladora",
    "Temperatura_Ambiente",
    "Tipo_Teste",
    "LeituraIndice",
    "Em_Alarme",
    "Setpoint",
    "TimeCol",
    "OBS",
    "val_obs",
    "y_column_name",
}


def cylinder_id_column(cyl_num: int) -> str:
    """@brief Retorna o nome da coluna de ID de teste para um cilindro.

    @param cyl_num Número do cilindro (1 a 6).
    @return Nome da coluna: Cilindro_XX_ID_Teste.
    """
    return f"Cilindro_{cyl_num:02d}_ID_Teste"


def dynamic_table_name(cyl_num: int) -> str:
    """@brief Retorna o nome da tabela dinâmica para um cilindro.

    @param cyl_num Número do cilindro (1 a 6).
    @return Nome da tabela: Cilindro_XX (schema dbo).
    """
    return f"Cilindro_{cyl_num:02d}"


def static_table_candidates(cyl_num: int) -> list[str]:
    """@brief Retorna candidatos a nome de tabela estática para um cilindro.

    Tenta variações com/sem acento para compatibilidade com diferentes
    versões do schema.

    @param cyl_num Número do cilindro (1 a 6).
    @return Lista de possíveis nomes de tabela estática.
    """
    base = f"Cilindro_{cyl_num:02d}"
    return [f"{base}_Estatico", f"{base}_Est\u00e1tico", f"{base}_Estatico_Estatico", f"{base}_Est\u00e1tico_Est\u00e1tico"]
