import os

import pytest

from src.config.settings import SETTINGS
from src.infrastructure.sql.connection import SqlServerConnection
from src.infrastructure.sql.repositories import SqlTestQueryRepository


pytestmark = pytest.mark.skipif(
    os.getenv("PIFF_RUN_INTEGRATION", "false").lower() != "true",
    reason="Teste de integracao depende de SQL Server local com dados do Projeto_54.",
)


def test_list_test_ids_integration_smoke():
    conn = SqlServerConnection(SETTINGS)
    repo = SqlTestQueryRepository(conn)
    ids = repo.list_test_ids(1)
    assert isinstance(ids, list)
