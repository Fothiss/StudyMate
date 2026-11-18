"""Регистрация и вход."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import Token, UserRead, UserRegister
from app.services.users import UsernameAlreadyTaken, authenticate, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация",
)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    """Создаёт учётную запись с уникальным логином."""
    try:
        return create_user(db, payload)
    except UsernameAlreadyTaken as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken",
        ) from error


@router.post("/login", response_model=Token, summary="Вход")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Выдаёт токен доступа.

    Неверный пароль и несуществующий логин дают одинаковый ответ, поэтому
    перебором нельзя выяснить, какие учётные записи существуют.
    """
    user = authenticate(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))
