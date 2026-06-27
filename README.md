# Report_PIFF0054-ng

Sistema de visualizacao tecnica de ensaios industriais com persistencia de observacoes por coordenada, exportacao CSV/PDF e diagnosticos operacionais.

## Arquitetura

- src/domain: entidades, contratos e erros de dominio.
- src/application: casos de uso, validacoes e DTOs.
- src/infrastructure: SQL Server, cache e exportadores.
- src/ui: interface Streamlit.
- tests: testes unitarios e integracao.

## Requisitos

- Python 3.11+
- SQL Server com banco Projeto_54
- Driver ODBC SQL Server instalado no Windows

## Configuracao

Copie `.env.example` para `.env` e ajuste os valores.

Variaveis principais:
- PIFF_SQL_SERVER
- PIFF_SQL_DATABASE
- PIFF_SQL_USERNAME
- PIFF_SQL_PASSWORD
- PIFF_SQL_TRUSTED_CONNECTION

## Execucao

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Testes

```powershell
pytest
```

## Performance SQL (recorte 01-06)

Scripts versionados em `sql/performance`:
- `01_baseline_benchmark.sql`
- `02_create_composite_indexes.sql`
- `03_update_stats_and_index_review.sql`
