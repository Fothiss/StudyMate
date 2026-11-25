"""Описание API: новые пути, поле `test_id` и устаревший `/quiz/check`."""

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


def test_legacy_check_is_deprecated(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()

    assert spec["paths"]["/quiz/check"]["post"]["deprecated"] is True
