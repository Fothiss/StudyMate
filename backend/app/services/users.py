"""Операции с пользователями."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserRegister


class UsernameAlreadyTaken(Exception):
    """Запрошенный `username` уже занят."""


def get_by_username(db: Session, username: str) -> User | None:
    """Ищет пользователя по логину."""
    return db.scalar(select(User).where(User.username == username))


def create_user(db: Session, payload: UserRegister) -> User:
    """Создаёт пользователя.

    Дубликат проверяется явно, а `IntegrityError` страхует от гонки двух
    одновременных регистраций с одним и тем же логином.
    """
    if get_by_username(db, payload.username) is not None:
        raise UsernameAlreadyTaken

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise UsernameAlreadyTaken from error
    db.refresh(user)
    return user


def authenticate(db: Session, username: str, password: str) -> User | None:
    """Возвращает пользователя при верных данных и `None` иначе.

    Не уточняет, что именно неверно — это должно остаться неразличимым снаружи.
    """
    user = get_by_username(db, username)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
