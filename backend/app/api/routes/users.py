"""Данные текущего пользователя."""

from fastapi import APIRouter

from app.dependencies.security import CurrentUser
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead, summary="Текущий пользователь")
def read_current_user(current_user: CurrentUser) -> User:
    """Отдаёт пользователя, определённого по токену."""
    return current_user
