"""Общие части ORM-моделей."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


def new_uuid() -> str:
    """Идентификатор строкой: одинаково представим в SQLite и PostgreSQL."""
    return str(uuid4())


def utc_now() -> datetime:
    """Текущее время в UTC."""
    return datetime.now(UTC)


class IdCreatedAtMixin:
    """Первичный ключ и дата создания, общие для всех сущностей."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
