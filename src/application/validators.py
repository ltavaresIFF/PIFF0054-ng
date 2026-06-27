from __future__ import annotations

from src.domain.errors import ValidationError
from src.domain.models import ObservationCommand, ObservationLookup


def validate_cylinder(cyl_num: int) -> None:
    if cyl_num not in {1, 2, 3, 4, 5, 6}:
        raise ValidationError("Cilindro invalido. Use valores entre 1 e 6.")


def validate_test_id(test_id: str) -> None:
    if not test_id or not test_id.strip():
        raise ValidationError("ID_Teste obrigatorio.")


def validate_obs_text(obs_text: str | None) -> str | None:
    if obs_text is None:
        return None
    normalized = obs_text.strip()
    if not normalized:
        return None
    if len(normalized) > 500:
        raise ValidationError("Observacao excede limite de 500 caracteres.")
    return normalized


def validate_y_column_name(y_column_name: str) -> None:
    if not y_column_name or not y_column_name.strip():
        raise ValidationError("Nome da coluna Y obrigatorio.")


def validate_observation_command(cmd: ObservationCommand) -> ObservationCommand:
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
    validate_cylinder(lookup.cyl_num)
    validate_test_id(lookup.test_id)
    validate_y_column_name(lookup.y_column_name)
