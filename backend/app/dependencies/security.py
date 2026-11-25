"""Определение текущего пользователя по токену."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.dependencies.repositories import UserRepo
from app.models.user import User

# tokenUrl используется только для того, чтобы в /docs появилась кнопка Authorize.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    users: UserRepo,
) -> User:
    """Определяет пользователя исключительно по токену.

    Ни тело, ни query-параметры на выбор пользователя не влияют — иначе чужой
    идентификатор в запросе стал бы способом читать чужие данные.
    """
    user_id = decode_access_token(token)
    if user_id is None:
        raise _unauthorized()
    user = users.get(user_id)
    if user is None:
        raise _unauthorized()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
