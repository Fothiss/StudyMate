"""Сессия БД как зависимость FastAPI."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import SessionLocal


def get_db() -> Iterator[Session]:
    """Зависимость FastAPI: одна сессия на запрос.

    FastAPI кэширует результат в пределах запроса, поэтому все зависимости,
    которым нужна сессия, получают один и тот же объект.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]
