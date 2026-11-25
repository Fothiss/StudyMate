"""Репозитории как зависимости FastAPI."""

from typing import Annotated

from fastapi import Depends

from app.dependencies.database import DbSession
from app.repositories.attempts import AttemptRepository
from app.repositories.materials import MaterialRepository
from app.repositories.tests import TestRepository
from app.repositories.users import UserRepository


def get_user_repo(session: DbSession) -> UserRepository:
    return UserRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repo)]


def get_material_repo(session: DbSession) -> MaterialRepository:
    return MaterialRepository(session)


MaterialRepo = Annotated[MaterialRepository, Depends(get_material_repo)]


def get_test_repo(session: DbSession) -> TestRepository:
    return TestRepository(session)


TestRepo = Annotated[TestRepository, Depends(get_test_repo)]


def get_attempt_repo(session: DbSession) -> AttemptRepository:
    return AttemptRepository(session)


AttemptRepo = Annotated[AttemptRepository, Depends(get_attempt_repo)]
