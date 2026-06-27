class DomainError(Exception):
    """Erro base da camada de dominio."""


class ValidationError(DomainError):
    """Erro de validacao de regra de negocio."""


class NotFoundError(DomainError):
    """Recurso esperado nao encontrado."""


class AmbiguousMatchError(DomainError):
    """Mais de um registro encontrado quando deveria haver unicidade."""


class PersistenceError(DomainError):
    """Falha em operacao de persistencia."""


class InfrastructureError(DomainError):
    """Falha de infraestrutura, como conexao SQL."""
