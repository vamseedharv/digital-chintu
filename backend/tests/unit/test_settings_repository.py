from sqlalchemy.orm import Session

from app.repositories.settings_repository import SettingsRepository


def test_get_returns_none_for_an_unset_key(db_session: Session) -> None:
    repo = SettingsRepository(db_session)

    assert repo.get("app_name") is None


def test_set_then_get_returns_the_stored_value(db_session: Session) -> None:
    repo = SettingsRepository(db_session)

    repo.set("app_name", "Jarvis")

    assert repo.get("app_name") == "Jarvis"


def test_set_on_an_existing_key_overwrites_it(db_session: Session) -> None:
    repo = SettingsRepository(db_session)

    repo.set("app_name", "Jarvis")
    repo.set("app_name", "Friday")

    assert repo.get("app_name") == "Friday"


def test_get_all_returns_every_stored_key(db_session: Session) -> None:
    repo = SettingsRepository(db_session)

    repo.set("app_name", "Jarvis")
    repo.set("default_theme", "dark")

    assert repo.get_all() == {"app_name": "Jarvis", "default_theme": "dark"}


def test_get_all_returns_an_empty_dict_when_nothing_is_stored(db_session: Session) -> None:
    repo = SettingsRepository(db_session)

    assert repo.get_all() == {}


def test_writes_are_visible_to_a_second_repository_on_the_same_session(
    db_session: Session,
) -> None:
    SettingsRepository(db_session).set("app_name", "Jarvis")

    assert SettingsRepository(db_session).get("app_name") == "Jarvis"
