"""Доступ к учётным записям."""

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Чтение и создание пользователей."""

    def get(self, user_id: str) -> User | None:
        """Пользователь по идентификатору."""
        return self._session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        """Пользователь по логину."""
        return self._session.scalar(select(User).where(User.username == username))

    def add(self, user: User) -> User:
        """Добавляет пользователя и делает строку видимой в текущей транзакции."""
        self._session.add(user)
        self._session.flush()
        return user
