import { ChevronRight } from "lucide-react";
import { Link } from "react-router";

import type { Attempt } from "@/lib/api";
import { describeChoiceScore } from "@/lib/attempts";
import { formatDate } from "@/lib/format";

type AttemptRowProps = {
  attempt: Attempt;
};

/** Строка истории попыток: материал, дата и счёт по тестовым вопросам. */
export function AttemptRow({ attempt }: AttemptRowProps) {
  const score = describeChoiceScore(
    attempt.choice_total > 0
      ? { correct: attempt.choice_correct, total: attempt.choice_total }
      : null,
  );

  return (
    <Link
      to={`/results/${attempt.id}`}
      className="flex items-center justify-between gap-3 rounded-xl border px-4 py-3 transition-colors hover:bg-secondary"
    >
      <span className="min-w-0">
        <span className="block truncate text-sm font-medium">{attempt.material_title}</span>
        <span className="text-xs text-muted-foreground">{formatDate(attempt.created_at)}</span>
      </span>

      <span className="flex shrink-0 items-center gap-2">
        <span className="rounded-lg bg-secondary px-2 py-1 text-xs font-semibold">
          {score}
        </span>
        <ChevronRight className="size-4 text-muted-foreground" aria-hidden />
      </span>
    </Link>
  );
}
