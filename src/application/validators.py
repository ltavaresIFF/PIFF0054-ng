"""@brief Funções de validação da camada de aplicação.

Centraliza a validação de dados de entrada antes de alcançar
o domínio, garantindo integridade das regras de negócio.
"""

from __future__ import annotations

from src.domain.errors import ValidationError
from src.domain.models import ObservationCommand, ObservationLookup


def validate_cylinder(cyl_num: int) -> None:
    """@brief Valida se o número do cilindro está no intervalo permitido (1 a 6).

    @param cyl_num Número do cilindro a validar.
    @raise ValidationError Se cyl_num não estiver entre 1 e 6.
    """
    if cyl_num not in {1, 2, 3, 4, 5, 6}:
        raise ValidationError("Cilindro invalido. Use valores entre 1 e 6.")


def validate_test_id(test_id: str) -> None:
    """@brief Valida se o identificador do teste não está vazio.

    @param test_id Identificador do teste a validar.
    @raise ValidationError Se test_id for nulo ou composto apenas por espaços.
    """
    if not test_id or not test_id.strip():
        raise ValidationError("ID_Teste obrigatorio.")


def validate_obs_text(obs_text: str | None) -> str | None:
    """@brief Valida e normaliza o texto de observação.

    Remove espaços extras e verifica o limite máximo de 500 caracteres.

    @param obs_text Texto da observação a validar.
    @return Texto normalizado, ou None se vazio após trim.
    @raise ValidationError Se o texto exceder 500 caracteres.
    """
    if obs_text is None:
        return None
    normalized = obs_text.strip()
    if not normalized:
        return None
    if len(normalized) > 500:
        raise ValidationError("Observacao excede limite de 500 caracteres.")
    return normalized


def validate_y_column_name(y_column_name: str) -> None:
    """@brief Valida se o nome da coluna Y não está vazio.

    @param y_column_name Nome da coluna Y a validar.
    @raise ValidationError Se y_column_name for nulo ou vazio.
    """
    if not y_column_name or not y_column_name.strip():
        raise ValidationError("Nome da coluna Y obrigatorio.")


def validate_observation_command(cmd: ObservationCommand) -> ObservationCommand:
    """@brief Valida e normaliza um comando de observação completo.

    Aplica todas as validações individuais e retorna um novo
    ObservationCommand com dados normalizados.

    @param cmd Comando de observação a validar.
    @return ObservationCommand validado e normalizado.
    @raise ValidationError Se qualquer campo obrigatório estiver inválido.
    """
    validate_cylinder(cmd.cyl_num)
    validate_test_id(cmd.test_id)
    validate_y_column_name(cmd.y_column_name)
    obs_text = validate_obs_text(cmd.obs_text)
    return ObservationCommand(
        cyl_num=cmd.cyl_num,
        test_id=cmd.test_id,
        local_col=cmd.local_col,
        y_column_name=cmd.y_column_name.strip(),
        y_value=cmd.y_value,
        obs_text=obs_text,
    )


def validate_observation_lookup(lookup: ObservationLookup) -> None:
    """@brief Valida os campos de uma chave de busca de observação.

    @param lookup Chave de busca a validar.
    @raise ValidationError Se qualquer campo obrigatório estiver inválido.
    """
    validate_cylinder(lookup.cyl_num)
    validate_test_id(lookup.test_id)
    validate_y_column_name(lookup.y_column_name)
