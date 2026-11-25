import { ArrowLeft, ArrowRight, Flag, Loader2, PenLine } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DraftQuestion } from "@/lib/practice-storage";
import { cn } from "@/lib/utils";

type PracticeRunProps = {
  questions: DraftQuestion[];
  requestedTotal: number;
  index: number;
  answer: number | string | undefined;
  submitting: boolean;
  onAnswer: (value: number | string) => void;
  onPrevious: () => void;
  onNext: () => void;
  onSubmit: () => void;
};

export function PracticeRun({
  questions,
  requestedTotal,
  index,
  answer,
  submitting,
  onAnswer,
  onPrevious,
  onNext,
  onSubmit,
}: PracticeRunProps) {
  const question = questions[index];
  const total = questions.length;
  const last = index === total - 1;
  const progress = ((index + 1) / total) * 100;
  const shortfall = requestedTotal > total ? requestedTotal - total : 0;

  return (
    <div className="space-y-4">
      {shortfall > 0 && (
        <p className="rounded-xl border border-warning/40 bg-warning/10 px-4 py-3 text-sm">
          Модель вернула {total} из {requestedTotal} запрошенных вопросов — проходим то, что
          получилось.
        </p>
      )}

      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs font-medium text-muted-foreground">
          <span>
            Вопрос {index + 1} из {total}
          </span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[var(--aurora-1)] via-[var(--aurora-2)] to-[var(--aurora-3)] transition-[width] duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <Card className="solid-surface">
        <CardHeader>
          <CardTitle className="font-heading text-lg leading-snug">{question.text}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {question.kind === "choice" ? (
            <div className="space-y-2">
              {question.options.map((option, optionIndex) => {
                const active = answer === optionIndex;
                return (
                  <button
                    key={`${question.text}-${optionIndex}`}
                    type="button"
                    onClick={() => onAnswer(optionIndex)}
                    aria-pressed={active}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 text-left text-sm transition-colors",
                      active
                        ? "border-primary/50 bg-primary/10 font-medium ring-1 ring-primary/30"
                        : "border-border hover:bg-secondary",
                    )}
                  >
                    <span
                      className={cn(
                        "grid size-6 shrink-0 place-items-center rounded-md text-xs font-semibold",
                        active
                          ? "bg-primary text-primary-foreground"
                          : "bg-secondary text-muted-foreground",
                      )}
                    >
                      {"АБВГ"[optionIndex] ?? optionIndex + 1}
                    </span>
                    {option}
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="space-y-2">
              <label
                htmlFor="open-answer"
                className="flex items-center gap-2 text-xs font-medium text-muted-foreground"
              >
                <PenLine className="size-3.5" aria-hidden />
                Ответ своими словами
              </label>
              <textarea
                id="open-answer"
                value={typeof answer === "string" ? answer : ""}
                onChange={(event) => onAnswer(event.target.value)}
                rows={4}
                placeholder="Напишите ответ — GigaChat оценит его по смыслу"
                className="min-h-28 w-full resize-y rounded-xl border border-input bg-transparent px-3 py-2 text-sm outline-none transition-[color,box-shadow] placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex items-center justify-between gap-3">
        <Button variant="ghost" onClick={onPrevious} disabled={index === 0 || submitting}>
          <ArrowLeft className="size-4" aria-hidden />
          Назад
        </Button>

        {last ? (
          <Button onClick={onSubmit} size="lg" disabled={submitting}>
            {submitting ? (
              <Loader2 className="size-4 animate-spin" aria-hidden />
            ) : (
              <Flag className="size-4" aria-hidden />
            )}
            {submitting ? "Отправляем…" : "Завершить тест"}
          </Button>
        ) : (
          <Button onClick={onNext} size="lg" disabled={submitting}>
            Далее
            <ArrowRight className="size-4" aria-hidden />
          </Button>
        )}
      </div>

      <p className="text-center text-xs text-muted-foreground">
        Правильные ответы появятся в разборе после завершения
      </p>
    </div>
  );
}
