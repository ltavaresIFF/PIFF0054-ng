"""@brief Exportador de dados para formato CSV.

Implementa a interface CsvExporter usando pandas com separador
ponto-e-vírgula (;) para compatibilidade com Excel PT-BR.
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd


class SemicolonCsvExporter:
    """@brief Exporta DataFrames para CSV com separador ponto-e-vírgula.

    Utiliza encoding UTF-8 com BOM (utf-8-sig) para compatibilidade
    com Microsoft Excel em locale português brasileiro.
    """

    def export(self, rows: pd.DataFrame) -> bytes:
        """@brief Converte um DataFrame em bytes CSV.

        @param rows DataFrame com os dados a exportar.
        @return Conteúdo do arquivo CSV em bytes.
        """
        buffer = BytesIO()
        rows.to_csv(buffer, sep=";", index=False, encoding="utf-8-sig")
        return buffer.getvalue()
