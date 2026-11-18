"""Pydantic-схемы пользователя и токена."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

USERNAME_PATTERN = r"^[A-Za-z0-9_.-]+$"

# bcrypt молча обрезает всё после 72 байт, поэтому длина ограничена явно.
BCRYPT_MAX_PASSWORD_BYTES = 72


class UserRegister(BaseModel):
    """Тело запроса на регистрацию."""

    username: str = Field(min_length=3, max_length=64, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=8, max_length=BCRYPT_MAX_PASSWORD_BYTES)
    full_name: str = Field(min_length=1, max_length=255)


class UserRead(BaseModel):
    """Пользователь в ответах API. Пароля и хеша здесь нет и быть не должно."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    full_name: str
    created_at: datetime


class Token(BaseModel):
    """Ответ на успешный вход."""

    access_token: str
    token_type: str = "bearer"
