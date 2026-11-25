"""Точка подмены модели: тесты не обращаются к GigaChat."""

from fastapi.testclient import TestClient

from tests.helpers import FakeAI, generate_test


def test_model_is_replaced_through_dependency(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
) -> None:
    quiz = generate_test(api, auth, str(material["id"]))

    assert fake_ai.generate_calls == 1
    assert quiz["summary"] == ["Фотосинтез превращает свет в химическую энергию"]
