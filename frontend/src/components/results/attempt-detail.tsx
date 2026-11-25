import {
  CheckCircle2,
  Loader2,
  RotateCcw,
  Sparkles,
  TriangleAlert,
  XCircle,
} from "lucide-react";

import { ScoreRing } from "@/components/practice/score-ring";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AttemptDetail } from "@/lib/api";
import { buildBreakdownRows, hasUncheckedOpenAnswers } from "@/lib/attempts";
import { formatDate } from "@/lib/format";
import type { LoadState } from "@/lib/load-state";
import { cn } from "@/lib/utils";

type AttemptDetailViewProps = {
  detail: AttemptDetail;
  checkState: LoadState;
  checkError: string | null;
  onCheck: () => void;
};

/**
 * Разбор сохранённой попытки: вопросы, данные ответы, правильные варианты,
 * эталоны и сохранённые оценки. Проверку открытых запускает страница, поэтому
 * компонент только показывает её состояние.
 */
export function AttemptDetailView({
  detail,
  checkState,
  checkError,
  onCheck,
}: AttemptDetailViewProps) {
  const rows = buildBreakdownRows(detail);
  const unchecked = hasUncheckedOpenAnswers(detail);

  return (
    <div className="space-y-4">
      <Card className="aurora-border border-0">
        <CardContent className="flex flex-col items-center gap-6 py-8 sm:flex-row sm:items-center">
          {detail.choice_total > 0 ? (
            <ScoreRing correct={detail.choice_correct} total={detail.choice_total} />
          ) : (
            <div className="grid size-24 shrink-0 place-items-center rounded-full bg-secondary text-muted-foreground">
              <Sparkles className="size-6" aria-hidden />
            </div>
          )}

          <div className="space-y-2 text-center sm:text-left">
            <p className="text-[0.7rem] font-semibold tracking-[0.18em] text-muted-foreground uppercase">
              Разбор попытки
            </p>
            <h2 className="font-heading text-2xl font-extrabold">{detail.material_title}</h2>
            <p className="text-sm text-muted-foreground">
              {formatDate(detail.created_at)}
              {" · "}
              {detail.choice_total > 0
                ? `верно ${detail.choice_correct} из ${detail.choice_total} тестовых вопросов`
                : "тестовых вопросов в этом тесте не было"}
              {detail.status === "checked" && " · открытые ответы проверены"}
            </p>
          </div>
        </CardContent>
      </Card>

      {detail.summary.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="font-heading text-base">Краткое содержание</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1.5 text-sm text-muted-foreground">
              {detail.summary.map((point, index) => (
                <li key={`summary-${index}`} className="flex gap-2">
                  <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" aria-hidden />
                  {point}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {unchecked && (
        <div
          className={cn(
            "flex flex-wrap items-center justify-between gap-3 rounded-xl border px-4 py-3 text-sm",
            checkError
              ? "border-destructive/30 bg-destructive/10 text-destructive"
              : "border-border bg-secondary/50 text-muted-foreground",
          )}
        >
          <span className="flex items-center gap-2">
            <TriangleAlert className="size-4" aria-hidden />
            {checkError ?? "Открытые ответы этой попытки ещё не проверены"}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={onCheck}
            disabled={checkState === "loading"}
          >
            {checkState === "loading" ? (
              <Loader2 className="size-4 animate-spin" aria-hidden />
            ) : (
              <RotateCcw className="size-4" aria-hidden />
            )}
            Проверить открытые
          </Button>
        </div>
      )}

      <Card className="solid-surface">
        <CardHeader>
          <CardTitle className="font-heading text-base">Вопросы</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-3">
            {rows.map((row) => (
              <li key={row.questionId} className="rounded-xl border p-3">
                <p className="flex items-start gap-2 text-sm font-medium">
                  {row.type === "choice" ? (
                    row.isCorrect ? (
                      <CheckCircle2
                        className="mt-0.5 size-4 shrink-0 text-success"
                        aria-hidden
                      />
                    ) : row.answered ? (
                      <XCircle className="mt-0.5 size-4 shrink-0 text-destructive" aria-hidden />
                    ) : (
                      <TriangleAlert
                        className="mt-0.5 size-4 shrink-0 text-muted-foreground"
                        aria-hidden
                      />
                    )
                  ) : (
                    <Sparkles className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden />
                  )}
                  {row.position + 1}. {row.text}
                </p>

                <p className="mt-2 pl-6 text-xs text-muted-foreground">
                  Ваш ответ:{" "}
                  {row.answered ? (
                    <span className="font-medium text-foreground">{row.given}</span>
                  ) : (
                    <span className="italic">не отвечен</span>
                  )}
                </p>

                {row.correct !== null && (
                  <p className="mt-1 pl-6 text-xs text-success">Верно: {row.correct}</p>
                )}

                {row.type === "open" && (
                  <>
                    {row.reference !== null && row.reference.length > 0 && (
                      <p className="mt-1 pl-6 text-xs text-muted-foreground">
                        Эталон: <span className="text-foreground">{row.reference}</span>
                      </p>
                    )}

                    {row.score !== null ? (
                      <div className="mt-2 ml-6 rounded-lg bg-secondary/60 p-3">
                        <p className="flex items-center justify-between text-xs font-semibold">
                          <span className="flex items-center gap-1.5">
                            <Sparkles className="size-3.5 text-primary" aria-hidden />
                            Оценка GigaChat
                          </span>
                          <span className="text-primary">{row.score} / 100</span>
                        </p>
                        <p className="mt-1.5 text-xs text-muted-foreground">{row.feedback}</p>
                      </div>
                    ) : checkState === "loading" ? (
                      <p className="mt-2 ml-6 flex items-center gap-2 text-xs text-muted-foreground">
                        <Loader2 className="size-3.5 animate-spin" aria-hidden />
                        Проверяем ответ…
                      </p>
                    ) : (
                      <p className="mt-2 ml-6 text-xs text-muted-foreground">
                        Ответ не проверен — запустите проверку выше.
                      </p>
                    )}
                  </>
                )}
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
