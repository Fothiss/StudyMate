"""Репозитории как зависимости FastAPI."""

from typing import Annotated

from fastapi import Depends

from app.dependencies.database import DbSession
from app.repositories.materials import MaterialRepository
from app.repositories.users import UserRepository


def get_user_repo(session: DbSession) -> UserRepository:
    return UserRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repo)]


def get_material_repo(session: DbSession) -> MaterialRepository:
    return MaterialRepository(session)


MaterialRepo = Annotated[MaterialRepository, Depends(get_material_repo)]
