"""Операции с учётными записями."""

from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.user import UserRegister


class UsernameAlreadyTaken(Exception):
    """Запрошенный `username` уже занят."""


class AccountService:
    """Регистрация и проверка учётных данных.

    Сервис владеет границей транзакции: репозиторий только готовит строку.
    """

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def register(self, payload: UserRegister) -> User:
        """Создаёт пользователя.

        Дубликат проверяется явно, а `IntegrityError` страхует от гонки двух
        одновременных регистраций с одним и тем же логином.
        """
        if self._users.get_by_username(payload.username) is not None:
            raise UsernameAlreadyTaken

        user = User(
            username=payload.username,
            password_hash=hash_password(payload.password),
        )
        try:
            self._users.add(user)
            self._users.session.commit()
        except IntegrityError as error:
            self._users.session.rollback()
            raise UsernameAlreadyTaken from error
        return user

    def authenticate(self, username: str, password: str) -> User | None:
        """Возвращает пользователя при верных данных и `None` иначе.

        Не уточняет, что именно неверно — это должно остаться неразличимым снаружи.
        """
        user = self._users.get_by_username(username)
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
