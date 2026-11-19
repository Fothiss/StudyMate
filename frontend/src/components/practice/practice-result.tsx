import { CheckCircle2, Loader2, RotateCcw, Sparkles, TriangleAlert, XCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CheckedAnswer, ChoiceQuestion, Quiz } from "@/lib/api";
import type { LoadState } from "@/lib/load-state";
import type { PracticeAnswers } from "@/lib/practice-storage";
import { cn } from "@/lib/utils";

import { ScoreRing } from "@/components/practice/score-ring";

type PracticeResultProps = {
  quiz: Quiz;
  answers: PracticeAnswers;
  evaluation: CheckedAnswer[] | null;
  evaluationState: LoadState;
  evaluationError: string | null;
  onRetryEvaluation: () => void;
  onRestart: () => void;
};

export function PracticeResult({
  quiz,
  answers,
  evaluation,
  evaluationState,
  evaluationError,
  onRetryEvaluation,
  onRestart,
}: PracticeResultProps) {
  const choicePositions = quiz.questions.flatMap((question, index) =>
    question.kind === "choice" ? [index] : [],
  );
  const openPositions = quiz.questions.flatMap((question, index) =>
    question.kind === "open" ? [index] : [],
  );

  const correct = choicePositions.filter(
    (index) =>
      answers[index] === (quiz.questions[index] as ChoiceQuestion).correct_index,
  ).length;

  const feedbackByIndex = new Map((evaluation ?? []).map((item) => [item.index, item]));

  return (
    <div className="space-y-4">
      <Card className="aurora-border border-0">
        <CardContent className="flex flex-col items-center gap-6 py-8 sm:flex-row sm:items-center">
          {choicePositions.length > 0 ? (
            <ScoreRing correct={correct} total={choicePositions.length} />
          ) : (
            <div className="grid size-24 shrink-0 place-items-center rounded-full bg-secondary text-muted-foreground">
              <Sparkles className="size-6" aria-hidden />
            </div>
          )}

          <div className="space-y-2 text-center sm:text-left">
            <h2 className="font-heading text-2xl font-extrabold">Тест завершён</h2>
            <p className="text-sm text-muted-foreground">
              {choicePositions.length > 0
                ? `Верно ${correct} из ${choicePositions.length} тестовых вопросов.`
                : "В этом тесте не было тестовых вопросов — смотрите разбор открытых ниже."}
              {openPositions.length > 0 &&
                " Открытые ответы оцениваются отдельно и появляются под вопросами."}
            </p>
            <Button variant="outline" size="sm" onClick={onRestart}>
              <RotateCcw className="size-4" aria-hidden />
              Новый тест
            </Button>
          </div>
        </CardContent>
      </Card>

      {quiz.summary.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="font-heading text-base">Краткое содержание</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1.5 text-sm text-muted-foreground">
              {quiz.summary.map((point, index) => (
                <li key={`summary-${index}`} className="flex gap-2">
                  <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" aria-hidden />
                  {point}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {openPositions.length > 0 && evaluation === null && evaluationState !== "loading" && (
        <div
          className={cn(
            "flex flex-wrap items-center justify-between gap-3 rounded-xl border px-4 py-3 text-sm",
            evaluationError
              ? "border-destructive/30 bg-destructive/10 text-destructive"
              : "border-border bg-secondary/50 text-muted-foreground",
          )}
        >
          <span className="flex items-center gap-2">
            <TriangleAlert className="size-4" aria-hidden />
            {evaluationError ?? "Открытые ответы ещё не проверены"}
          </span>
          <Button variant="outline" size="sm" onClick={onRetryEvaluation}>
            Проверить снова
          </Button>
        </div>
      )}

      <Card className="solid-surface">
        <CardHeader>
          <CardTitle className="font-heading text-base">Разбор</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-3">
            {quiz.questions.map((question, index) => {
              const given = answers[index];

              if (question.kind === "choice") {
                const answered = typeof given === "number";
                const isCorrect = answered && given === question.correct_index;

                return (
                  <li key={`question-${index}`} className="rounded-xl border p-3">
                    <p className="flex items-start gap-2 text-sm font-medium">
                      {isCorrect ? (
                        <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-success" aria-hidden />
                      ) : (
                        <XCircle className="mt-0.5 size-4 shrink-0 text-destructive" aria-hidden />
                      )}
                      {index + 1}. {question.text}
                    </p>
                    <p className="mt-2 pl-6 text-xs text-muted-foreground">
                      Ваш ответ:{" "}
                      <span className={cn("font-medium", !answered && "italic")}>
                        {answered ? question.options[given] : "не отвечен"}
                      </span>
                    </p>
                    <p className="mt-1 pl-6 text-xs text-success">
                      Верно: {question.options[question.correct_index]}
                    </p>
                  </li>
                );
              }

              const feedback = feedbackByIndex.get(index);

              return (
                <li key={`question-${index}`} className="rounded-xl border p-3">
                  <p className="text-sm font-medium">
                    {index + 1}. {question.text}
                  </p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    Ваш ответ:{" "}
                    <span className={cn(!given && "italic")}>
                      {typeof given === "string" && given.trim().length > 0
                        ? given
                        : "не отвечен"}
                    </span>
                  </p>

                  {feedback ? (
                    <div className="mt-2 rounded-lg bg-secondary/60 p-3">
                      <p className="flex items-center justify-between text-xs font-semibold">
                        <span className="flex items-center gap-1.5">
                          <Sparkles className="size-3.5 text-primary" aria-hidden />
                          Оценка GigaChat
                        </span>
                        <span className="text-primary">{feedback.score} / 100</span>
                      </p>
                      <p className="mt-1.5 text-xs text-muted-foreground">{feedback.feedback}</p>
                    </div>
                  ) : evaluationState === "loading" ? (
                    <p className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                      <Loader2 className="size-3.5 animate-spin" aria-hidden />
                      Проверяем ответ…
                    </p>
                  ) : (
                    <p className="mt-2 text-xs text-muted-foreground">
                      Оценка не получена — попробуйте проверить ещё раз.
                    </p>
                  )}

                  <p className="mt-2 text-xs text-muted-foreground">
                    Эталон: <span className="text-foreground">{question.reference}</span>
                  </p>
                </li>
              );
            })}
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
