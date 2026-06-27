"""@brief Exportador de relatório técnico em PDF.

Gera relatórios profissionais com ReportLab incluindo gráfico,
tabela de dados estáticos e amostra da série temporal dinâmica.
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class TechnicalPdfExporter:
    """@brief Gera relatório técnico em PDF com dados de ensaio.

    O relatório inclui: título, metadados, gráfico da série temporal
    (PNG), tabela de configuração estática e amostra dos dados dinâmicos.
    """

    def export(
        self,
        *,
        rows: pd.DataFrame,
        static_row: pd.DataFrame,
        metadata: dict[str, object],
        graph_png: bytes | None,
        sample_max_rows: int,
    ) -> bytes:
        out = BytesIO()
        doc = SimpleDocTemplate(out, pagesize=A4, title="Relatorio Tecnico PIFF0054")
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Relatorio Tecnico de Ensaio", styles["Title"]))
        story.append(Spacer(1, 8))
        for key, value in metadata.items():
            story.append(Paragraph(f"{key}: {value}", styles["BodyText"]))

        story.append(Spacer(1, 8))
        if graph_png:
            graph_stream = BytesIO(graph_png)
            img = Image(graph_stream, width=500, height=220)
            story.append(img)
            story.append(Spacer(1, 8))

        if not static_row.empty:
            story.append(Paragraph("Dados estaticos", styles["Heading3"]))
            first = static_row.head(1).to_dict(orient="records")[0]
            static_table = [["Campo", "Valor"]] + [[str(k), str(v)] for k, v in first.items()]
            table = Table(static_table, colWidths=[220, 300])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(table)
            story.append(Spacer(1, 8))

        story.append(Paragraph("Amostra da serie dinamica", styles["Heading3"]))
        sample = rows.head(sample_max_rows)
        head_cols = [str(c) for c in sample.columns]
        body_rows = sample.astype(str).values.tolist()
        limited = body_rows[: min(len(body_rows), 30)]
        data = [head_cols] + limited
        dyn_table = Table(data)
        dyn_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]))
        story.append(dyn_table)

        doc.build(story)
        return out.getvalue()
