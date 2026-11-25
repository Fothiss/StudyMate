"""Описание API: новые пути и поле `test_id` в ответе генерации."""

from fastapi.testclient import TestClient

NEW_PATHS = {
    "/tests/{test_id}/attempts",
    "/attempts",
    "/attempts/{attempt_id}",
    "/attempts/{attempt_id}/check",
}


def test_openapi_lists_new_paths(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()

    assert NEW_PATHS <= set(spec["paths"])


def test_generation_response_has_test_id(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    properties = spec["components"]["schemas"]["TestRead"]["properties"]

    assert "test_id" in properties
    assert {"summary", "questions"} <= set(properties)


def test_legacy_check_path_is_gone(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()

    assert "/quiz/check" not in spec["paths"]
    assert client.post("/quiz/check", json={}).status_code == 404
