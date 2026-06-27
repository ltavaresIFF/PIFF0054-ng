"""Testes de consulta real ao banco - todos os cilindros 01-06.
Ativado com: pytest tests/integration/test_db_queries.py -v -s
"""
from __future__ import annotations

import pytest

from src.config.settings import SETTINGS
from src.domain.models import TestContext
from src.infrastructure.sql.connection import SqlServerConnection
from src.infrastructure.sql.repositories import SqlTestQueryRepository


@pytest.fixture(scope="module")
def repo():
    conn = SqlServerConnection(SETTINGS)
    return SqlTestQueryRepository(conn)


@pytest.mark.parametrize("cyl_num", [1, 2, 3, 4, 5, 6])
def test_list_test_ids(repo, cyl_num):
    ids = repo.list_test_ids(cyl_num)
    print(f"\nCIL {cyl_num:02d}: {len(ids)} IDs | primeiro={ids[0] if ids else 'N/A'}")
    assert isinstance(ids, list), "Deve retornar lista"
    assert len(ids) > 0, f"Cilindro {cyl_num} sem IDs de ensaio"


@pytest.mark.parametrize("cyl_num", [1, 2, 3, 4, 5, 6])
def test_load_dynamic_rows(repo, cyl_num):
    ids = repo.list_test_ids(cyl_num)
    first_id = ids[0]
    ctx = TestContext(cyl_num=cyl_num, test_id=first_id)
    result = repo.load_dynamic_rows(ctx)
    print(f"\nCIL {cyl_num:02d} / {first_id}: {result.total_rows} linhas | cols={list(result.rows.columns)}")
    assert result.total_rows > 0, f"Sem linhas dinamicas para cilindro {cyl_num}"
    assert "LocalCol" in result.rows.columns, "LocalCol ausente"


@pytest.mark.parametrize("cyl_num", [1, 2, 3, 4, 5, 6])
def test_load_static_row(repo, cyl_num):
    ids = repo.list_test_ids(cyl_num)
    ctx = TestContext(cyl_num=cyl_num, test_id=ids[0])
    result = repo.load_static_row(ctx)
    print(f"\nCIL {cyl_num:02d}: tabela={result.table_used} | cols={list(result.row.columns)}")
    assert result.table_used, "Tabela estatica nao encontrada"
    assert not result.row.empty, "Registro estatico vazio"


@pytest.mark.parametrize("cyl_num", [1, 2, 3, 4, 5, 6])
def test_detect_force_column(repo, cyl_num):
    fc = repo.detect_force_column(cyl_num)
    print(f"\nCIL {cyl_num:02d}: coluna de forca={fc}")
    assert fc is not None, f"Coluna de forca nao detectada para cilindro {cyl_num}"


@pytest.mark.parametrize("cyl_num", [1, 2, 3, 4, 5, 6])
def test_available_y_columns(repo, cyl_num):
    ycols = repo.load_available_y_columns(cyl_num)
    print(f"\nCIL {cyl_num:02d}: eixos Y={ycols}")
    assert len(ycols) > 0, f"Nenhum eixo Y disponivel para cilindro {cyl_num}"
