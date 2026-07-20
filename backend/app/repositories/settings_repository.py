"""Data access for the settings table — plain key/value reads and writes,
no business rules (validation and default-resolution live in
app/services/settings_service.py)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SettingModel


class SettingsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, key: str) -> str | None:
        model = self._db.get(SettingModel, key)
        return model.value if model is not None else None

    def get_all(self) -> dict[str, str]:
        rows = self._db.execute(select(SettingModel)).scalars().all()
        return {row.key: row.value for row in rows}

    def set(self, key: str, value: str) -> None:
        model = self._db.get(SettingModel, key)
        if model is None:
            self._db.add(SettingModel(key=key, value=value))
        else:
            model.value = value
        self._db.commit()
