"""Движок SQLAlchemy, фабрика сессий и создание схемы."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core import sqlite  # noqa: F401  импорт регистрирует listener PRAGMA
from app.core.config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=_connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Базовый класс всех ORM-моделей."""


def get_db() -> Iterator[Session]:
    """Зависимость FastAPI: одна сессия на запрос."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Создаёт отсутствующие таблицы и каталог файлового хранилища.

    `create_all` только создаёт новое: колонки существующих таблиц он не меняет.
    Пока данные одноразовые, схема пересобирается удалением файла базы.
    """
    from app import models  # noqa: F401  импорт регистрирует модели в metadata

    Base.metadata.create_all(bind=engine)
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
