import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router";
import { describe, expect, it } from "vitest";

import { RecentAttempts } from "@/components/results/recent-attempts";
import type { Attempt } from "@/lib/api";

function attempt(index: number): Attempt {
  return {
    id: `attempt-${index}`,
    test_id: `test-${index}`,
    material_id: `material-${index}`,
    material_title: `Материал ${index}`,
    status: "submitted",
    choice_correct: index,
    choice_total: 3,
    created_at: `2026-11-2${index}T10:00:00`,
    checked_at: null,
  };
}

function render(props: Parameters<typeof RecentAttempts>[0]): string {
  return renderToStaticMarkup(
    <MemoryRouter>
      <RecentAttempts {...props} />
    </MemoryRouter>,
  );
}

describe("RecentAttempts", () => {
  it("без попыток объясняет, что появятся они после теста, и оставляет ссылку на историю", () => {
    const markup = render({
      state: "ready",
      attempts: [],
      onRetry: () => {},
    });

    expect(markup).toContain("после первого завершённого теста");
    expect(markup).toContain("Вся история");
  });

  it("показывает три последние попытки", () => {
    const markup = render({
      state: "ready",
      attempts: [attempt(1), attempt(2), attempt(3), attempt(4)],
      onRetry: () => {},
    });

    expect(markup).toContain("Материал 1");
    expect(markup).toContain("Материал 3");
    expect(markup).not.toContain("Материал 4");
  });

  it("в ошибке показывает сообщение и повтор, не скрывая ссылку на историю", () => {
    const markup = render({
      state: "error",
      attempts: [],
      errorMessage: "Сервер недоступен",
      onRetry: () => {},
    });

    expect(markup).toContain("Сервер недоступен");
    expect(markup).toContain("Повторить");
    expect(markup).toContain("Вся история");
  });
});
