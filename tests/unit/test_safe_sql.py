import pytest

from src.domain.errors import ValidationError
from src.infrastructure.sql.safe_sql import escape_identifier, escape_table


def test_escape_identifier_valid_ascii():
    assert escape_identifier("Cilindro_01") == "[Cilindro_01]"


def test_escape_identifier_valid_unicode():
    # Tabelas com acento sao validas no SQL Server com brackets
    assert escape_identifier("Cilindro_01_Est\u00e1tico") == "[Cilindro_01_Est\u00e1tico]"


def test_escape_identifier_empty_raises():
    with pytest.raises(ValidationError):
        escape_identifier("")


def test_escape_identifier_null_byte_raises():
    with pytest.raises(ValidationError):
        escape_identifier("tabela\x00injetada")


def test_escape_identifier_brackets_escaped():
    # ] dentro do nome vira ]] (SQL Server bracket escaping)
    assert escape_identifier("tab]le") == "[tab]]le]"


def test_escape_table_with_schema():
    assert escape_table("dbo.Cilindro_01") == "[dbo].[Cilindro_01]"
