import pytest
from sqlalchemy.orm import Session

from app.core.config import Theme, get_settings
from app.repositories.settings_repository import SettingsRepository
from app.services.settings_service import SettingsService


def _service(db_session: Session) -> SettingsService:
    return SettingsService(SettingsRepository(db_session))


def test_effective_settings_fall_back_to_env_defaults_when_nothing_is_overridden(
    db_session: Session,
) -> None:
    service = _service(db_session)
    defaults = get_settings()

    effective = service.get_effective_settings()

    assert effective.app_name == defaults.app_name
    assert effective.default_theme == defaults.default_theme


def test_update_app_name_is_reflected_in_effective_settings(db_session: Session) -> None:
    service = _service(db_session)

    service.update_app_name("Jarvis")

    assert service.get_effective_settings().app_name == "Jarvis"


def test_update_default_theme_is_reflected_in_effective_settings(db_session: Session) -> None:
    service = _service(db_session)

    service.update_default_theme(Theme.DARK)

    assert service.get_effective_settings().default_theme == Theme.DARK


def test_update_app_name_rejects_a_blank_value(db_session: Session) -> None:
    service = _service(db_session)

    with pytest.raises(ValueError, match="must not be blank"):
        service.update_app_name("   ")


def test_update_app_name_rejects_an_overly_long_value(db_session: Session) -> None:
    service = _service(db_session)

    with pytest.raises(ValueError, match="64 characters or fewer"):
        service.update_app_name("x" * 65)


def test_update_app_name_trims_surrounding_whitespace(db_session: Session) -> None:
    service = _service(db_session)

    service.update_app_name("  Jarvis  ")

    assert service.get_effective_settings().app_name == "Jarvis"


def test_only_the_updated_setting_changes(db_session: Session) -> None:
    service = _service(db_session)
    defaults = get_settings()

    service.update_app_name("Jarvis")

    effective = service.get_effective_settings()
    assert effective.app_name == "Jarvis"
    assert effective.default_theme == defaults.default_theme
