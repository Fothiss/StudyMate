import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { AttemptDetailView } from "@/components/results/attempt-detail";
import type { AttemptDetail, AttemptQuestion } from "@/lib/api";

function question(overrides: Partial<AttemptQuestion> = {}): AttemptQuestion {
  return {
    question_id: "question-1",
    type: "choice",
    text: "Что запасает энергию?",
    options: ["Глюкоза", "Кислород", "Вода"],
    correct_index: 0,
    selected_index: null,
    answer_text: null,
    reference: null,
    is_correct: null,
    llm_score: null,
    llm_feedback: null,
    ...overrides,
  };
}

function detail(questions: AttemptQuestion[]): AttemptDetail {
  return {
    id: "attempt-1",
    test_id: "test-1",
    material_id: "material-1",
    material_title: "Конспект",
    status: "submitted",
    choice_correct: 0,
    choice_total: 1,
    created_at: "2026-11-25T10:00:00",
    checked_at: null,
    summary: ["Краткое содержание"],
    questions,
  };
}

function render(attempt: AttemptDetail): string {
  return renderToStaticMarkup(
    <AttemptDetailView
      detail={attempt}
      checkState="ready"
      checkError={null}
      onCheck={() => {}}
    />,
  );
}

describe("AttemptDetailView", () => {
  it("показывает неотвеченный вопрос и правильный вариант", () => {
    const markup = render(detail([question({ is_correct: false })]));

    expect(markup).toContain("не отвечен");
    expect(markup).toContain("Верно: Глюкоза");
  });

  it("показывает непроверенный открытый ответ и кнопку проверки", () => {
    const markup = render(
      detail([
        question({
          type: "open",
          options: [],
          correct_index: null,
          answer_text: "Фотосинтез",
          reference: "Превращение света в химическую энергию",
        }),
      ]),
    );

    expect(markup).toContain("Фотосинтез");
    expect(markup).toContain("Превращение света в химическую энергию");
    expect(markup).toContain("Ответ не проверен");
    expect(markup).toContain("Проверить открытые");
  });

  it("показывает сохранённые балл и фидбек без кнопки проверки", () => {
    const markup = render({
      ...detail([
        question({
          type: "open",
          options: [],
          correct_index: null,
          answer_text: "Фотосинтез",
          llm_score: 80,
          llm_feedback: "Смысл передан верно",
        }),
      ]),
      status: "checked",
    });

    expect(markup).toContain("80 / 100");
    expect(markup).toContain("Смысл передан верно");
    expect(markup).not.toContain("Проверить открытые");
  });
});
