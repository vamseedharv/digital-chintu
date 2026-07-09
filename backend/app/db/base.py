"""Declarative base for SQLAlchemy ORM models.

No models are defined yet — this is infrastructure scaffolding for future
features (see app/domain, app/repositories).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
