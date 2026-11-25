"""Сервисы как зависимости FastAPI.

Провайдеры только собирают объект: ни условий, ни запросов, ни чтения настроек.
"""

from typing import Annotated

from fastapi import Depends

from app.dependencies.repositories import AttemptRepo, MaterialRepo, TestRepo, UserRepo
from app.services.ai import AIService
from app.services.attempts import AttemptService
from app.services.materials import MaterialService
from app.services.users import AccountService


def get_account_service(users: UserRepo) -> AccountService:
    return AccountService(users)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


def get_ai_service() -> AIService:
    return AIService()


AIServiceDep = Annotated[AIService, Depends(get_ai_service)]


def get_material_service(
    materials: MaterialRepo,
    tests: TestRepo,
    ai: AIServiceDep,
) -> MaterialService:
    return MaterialService(materials, tests, ai)


MaterialServiceDep = Annotated[MaterialService, Depends(get_material_service)]


def get_attempt_service(
    attempts: AttemptRepo,
    tests: TestRepo,
    ai: AIServiceDep,
) -> AttemptService:
    return AttemptService(attempts, tests, ai)


AttemptServiceDep = Annotated[AttemptService, Depends(get_attempt_service)]
