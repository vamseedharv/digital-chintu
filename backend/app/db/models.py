"""SQLAlchemy ORM models. Persistence-technology-specific — pure domain
concepts live in app/domain instead (see docs/architecture/03_DATABASE_DESIGN.md).
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SettingModel(Base):
    """A single overridden setting. `key` matches a `SettingKey`
    (app/domain/settings.py); `value` is plain text — the repository/service
    layer is responsible for serializing and parsing it. Generic key/value
    shape on purpose: a new setting is a new key, never a schema migration.
    """

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
