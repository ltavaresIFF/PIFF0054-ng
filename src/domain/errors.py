"""@brief Hierarquia de exceções da camada de domínio.

Define os tipos de erro específicos do domínio do Projeto 54,
permitindo tratamento diferenciado por tipo na camada de aplicação.
"""


class DomainError(Exception):
    """@brief Erro base da camada de domínio.

    Todas as exceções de domínio herdam desta classe.
    """


class ValidationError(DomainError):
    """@brief Erro disparado quando uma regra de validação é violada."""


class NotFoundError(DomainError):
    """@brief Erro disparado quando um recurso esperado não é encontrado."""


class AmbiguousMatchError(DomainError):
    """@brief Erro disparado quando múltiplos registros são encontrados onde deveria haver apenas um."""


class PersistenceError(DomainError):
    """@brief Erro disparado quando uma operação de persistência (insert/update/delete) falha."""


class InfrastructureError(DomainError):
    """@brief Erro disparado quando ocorre uma falha de infraestrutura, como conexão SQL."""
