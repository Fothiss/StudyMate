"""Сервисы как зависимости FastAPI.

Провайдеры только собирают объект: ни условий, ни запросов, ни чтения настроек.
"""

from typing import Annotated

from fastapi import Depends

from app.dependencies.repositories import MaterialRepo, UserRepo
from app.services.materials import MaterialService
from app.services.users import AccountService


def get_account_service(users: UserRepo) -> AccountService:
    return AccountService(users)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


def get_material_service(materials: MaterialRepo) -> MaterialService:
    return MaterialService(materials)


MaterialServiceDep = Annotated[MaterialService, Depends(get_material_service)]
