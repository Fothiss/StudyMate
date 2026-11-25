"""Регистрация, вход и загрузка материала на временной базе."""

from fastapi.testclient import TestClient

from tests.helpers import upload_material


def test_material_is_uploaded(api: TestClient, auth: dict[str, str]) -> None:
    material = upload_material(api, auth)

    assert material["title"] == "Конспект"
    assert material["filename"] == "guide.pdf"
    assert material["id"]


def test_materials_are_isolated(api: TestClient, auth: dict[str, str], other_auth: dict[str, str]) -> None:
    upload_material(api, auth)

    response = api.get("/materials", headers=other_auth)

    assert response.status_code == 200
    assert response.json() == []
