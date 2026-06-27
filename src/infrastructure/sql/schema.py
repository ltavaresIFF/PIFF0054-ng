from __future__ import annotations


CANONICAL_OBSERVATION_COLUMNS = {
    "obs": "OBS",
    "val": "val_obs",
    "y_name": "y_column_name",
}

FORCE_COLUMN_CANDIDATES = ["Forca", "For\u00e7a", "FORCA", "Carga", "Load"]

DYNAMIC_EXCLUDE_COLUMNS = {
    "RowId",
    "CreatedAt",
}

# Colunas carregadas por padrao (substitui SELECT *).
# Alinhadas com o INCLUDE do indice IX_Cilindro_XX_ID_Teste_LocalCol
# para garantir covering index scan — sem key lookups.
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
    return f"Cilindro_{cyl_num:02d}_ID_Teste"


def dynamic_table_name(cyl_num: int) -> str:
    return f"Cilindro_{cyl_num:02d}"


def static_table_candidates(cyl_num: int) -> list[str]:
    base = f"Cilindro_{cyl_num:02d}"
    return [f"{base}_Estatico", f"{base}_Est\u00e1tico", f"{base}_Estatico_Estatico", f"{base}_Est\u00e1tico_Est\u00e1tico"]
