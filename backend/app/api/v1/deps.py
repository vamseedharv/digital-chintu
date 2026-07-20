"""Shared FastAPI dependency providers for the v1 API."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.settings_repository import SettingsRepository
from app.services.settings_service import SettingsService


def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    return SettingsService(SettingsRepository(db))
