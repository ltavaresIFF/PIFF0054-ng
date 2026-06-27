import pytest

from src.application.validators import (
    validate_cylinder,
    validate_obs_text,
    validate_test_id,
)
from src.domain.errors import ValidationError


def test_validate_cylinder_accepts_1_to_6():
    for cyl in [1, 2, 3, 4, 5, 6]:
        validate_cylinder(cyl)


def test_validate_cylinder_rejects_out_of_range():
    with pytest.raises(ValidationError):
        validate_cylinder(7)


def test_validate_test_id_rejects_blank():
    with pytest.raises(ValidationError):
        validate_test_id("  ")


def test_validate_obs_text_trim_and_null_behavior():
    assert validate_obs_text("  abc  ") == "abc"
    assert validate_obs_text("   ") is None
