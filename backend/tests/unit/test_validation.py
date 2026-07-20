import pytest

from app.core.validation import validate_short_text


def test_strips_surrounding_whitespace() -> None:
    assert validate_short_text("  Chintu  ", "app_name") == "Chintu"


def test_rejects_blank_value() -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        validate_short_text("   ", "app_name")


def test_rejects_value_over_the_max_length() -> None:
    with pytest.raises(ValueError, match="64 characters or fewer"):
        validate_short_text("x" * 65, "app_name")


def test_accepts_value_at_exactly_the_max_length() -> None:
    value = "x" * 64
    assert validate_short_text(value, "app_name") == value


def test_custom_max_length_is_respected() -> None:
    with pytest.raises(ValueError, match="8 characters or fewer"):
        validate_short_text("x" * 9, "field", max_length=8)
