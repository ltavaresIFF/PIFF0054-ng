"""@brief Funções seguras para construção de consultas SQL.

Utilitários para escapar identificadores e nomes de tabela usando
brackets do SQL Server, prevenindo injeção SQL em identificadores dinâmicos.
"""

from __future__ import annotations

from src.domain.errors import ValidationError

# SQL Server bracket-quoted identifiers aceita qualquer caractere exceto ] e \x00.
# O ] dentro do nome e escapado como ]] conforme especificacao do SQL Server.
_FORBIDDEN = frozenset(["\x00"])


def escape_identifier(name: str) -> str:
    """@brief Escapa um identificador SQL Server usando brackets.

    Permite Unicode e caracteres especiais válidos para SQL Server.
    Rejeita strings vazias e null bytes.

    @param name Nome do identificador a escapar.
    @return Identificador entre brackets: [nome].
    @raise ValidationError Se name for vazio ou contiver null byte.
    """
    if not name:
        raise ValidationError("Identificador SQL invalido: string vazia")
    if any(c in _FORBIDDEN for c in name):
        raise ValidationError(f"Identificador SQL invalido: caracter proibido em {name!r}")
    safe = name.replace("]", "]]")
    return f"[{safe}]"


def escape_table(name: str) -> str:
    """@brief Escapa um nome de tabela, com suporte a schema.

    Se o nome conter ponto (ex: dbo.Tabela), escapa ambas as partes.

    @param name Nome da tabela (opcionalmente com schema).
    @return Nome escapado: [dbo].[Tabela] ou [schema].[tabela].
    @raise ValidationError Se o formato for inválido.
    """
    if "." in name:
        parts = name.split(".")
        if len(parts) != 2:
            raise ValidationError("Nome de tabela invalido.")
        return f"{escape_identifier(parts[0])}.{escape_identifier(parts[1])}"
    return f"[dbo].{escape_identifier(name)}"
