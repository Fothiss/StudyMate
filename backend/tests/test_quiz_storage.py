"""Конвертация ответа модели в строки теста."""

from app.services.quiz_storage import build_test
from tests.helpers import default_quiz


def test_quiz_is_converted_to_rows() -> None:
    test = build_test(
        default_quiz(),
        user_id="user-id",
        material_id="material-id",
        generation_params={"choice_count": 1, "open_count": 1},
    )

    assert test.user_id == "user-id"
    assert test.material_id == "material-id"
    assert test.summary == ["Фотосинтез превращает свет в химическую энергию"]
    assert test.generation_params == {"choice_count": 1, "open_count": 1}

    choice, open_question = test.questions
    assert (choice.type, choice.order_index, choice.text) == (
        "choice",
        0,
        "Что запасает энергию?",
    )
    assert [option.text for option in choice.options] == ["Глюкозу", "Кислород", "Воду"]
    assert [option.order_index for option in choice.options] == [0, 1, 2]
    assert [option.is_correct for option in choice.options] == [True, False, False]
    assert choice.rubric is None

    assert (open_question.type, open_question.order_index) == ("open", 1)
    assert open_question.options == []
    assert (
        open_question.rubric.reference_answer
        == "Процесс превращения световой энергии в химическую."
    )
