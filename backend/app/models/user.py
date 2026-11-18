"""Модель пользователя."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.base import IdCreatedAtMixin


class User(IdCreatedAtMixin, Base):
    """Учётная запись.

    Ролей нет: в solo-сценарии пользователь сам загружает материалы и сам же
    проходит по ним тесты, поэтому делить пользователей на учителей и учеников
    пока не на что.
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
