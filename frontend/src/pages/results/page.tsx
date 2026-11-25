import { History, Loader2, TriangleAlert, Wand2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router";

import { AttemptRow } from "@/components/results/attempt-row";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { describeError, fetchAttempts, type Attempt } from "@/lib/api";
import { describeChoiceScore, summarizeProgress } from "@/lib/attempts";
import type { LoadState } from "@/lib/load-state";

export default function ResultsPage() {
  const [attempts, setAttempts] = useState<Attempt[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    let cancelled = false;

    fetchAttempts()
      .then((list) => {
        if (cancelled) return;
        setAttempts(list);
        setState("ready");
      })
      .catch((caught: unknown) => {
        if (cancelled) return;
        setError(describeError(caught));
        setState("error");
      });

    return () => {
      cancelled = true;
    };
  }, [reload]);

  const retry = useCallback(() => {
    setState("loading");
    setError(null);
    setReload((value) => value + 1);
  }, []);

  const summary = summarizeProgress(attempts);

  return (
    <div className="space-y-5">
      <header className="rise glass rounded-3xl p-6">
        <p className="text-[0.7rem] font-semibold tracking-[0.18em] text-muted-foreground uppercase">
          Прогресс
        </p>
        <h1 className="mt-1 font-heading text-3xl font-extrabold tracking-tight">Результаты</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          Каждая сдача сохраняется: историю можно перечитать позже, в новой вкладке или по
          прямой ссылке.
        </p>

        <div className="mt-6">
          <Link
            to="/quiz"
            className="sheen inline-flex h-11 items-center gap-2 rounded-xl bg-gradient-to-r from-[var(--aurora-1)] via-[var(--aurora-2)] to-[var(--aurora-3)] px-5 text-sm font-semibold text-white shadow-lg shadow-[var(--aurora-1)]/30 transition-transform hover:-translate-y-0.5"
          >
            <Wand2 className="size-4" aria-hidden />
            Пройти новый тест
          </Link>
        </div>
      </header>

      {state === "loading" && (
        <Card>
          <CardContent className="flex items-center gap-3 py-8 text-sm text-muted-foreground">
            <Loader2 className="size-4 animate-spin" aria-hidden />
            Загружаем историю попыток…
          </CardContent>
        </Card>
      )}

      {state === "error" && (
        <Card>
          <CardContent className="space-y-3 py-8">
            <p className="flex items-center gap-2 text-sm font-medium">
              <TriangleAlert className="size-4 text-destructive" aria-hidden />
              {error ?? "Не удалось загрузить историю попыток"}
            </p>
            <Button variant="outline" size="sm" onClick={retry}>
              Повторить
            </Button>
          </CardContent>
        </Card>
      )}

      {state === "ready" && attempts.length === 0 && (
        <Card>
          <CardContent className="space-y-3 py-8">
            <p className="flex items-center gap-2 font-heading text-base font-semibold">
              <History className="size-4 text-primary" aria-hidden />
              Пока пусто
            </p>
            <p className="text-sm text-muted-foreground">
              Здесь появятся ваши результаты: оценка по тестовым вопросам, разбор ответов и
              прогресс по материалам. Засчитывается каждая завершённая попытка.
            </p>
            <Link to="/quiz" className={buttonVariants({ variant: "outline", size: "sm" })}>
              Перейти к тесту
            </Link>
          </CardContent>
        </Card>
      )}

      {state === "ready" && attempts.length > 0 && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="font-heading text-base">Прогресс по материалам</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="grid gap-3 sm:grid-cols-2">
                {summary.map((entry) => (
                  <li key={entry.materialId} className="rounded-xl border p-3">
                    <p className="truncate text-sm font-medium">{entry.materialTitle}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Попыток: {entry.attemptCount} · последняя:{" "}
                      {describeChoiceScore(entry.latest)}
                    </p>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="solid-surface">
            <CardHeader>
              <CardTitle className="font-heading text-base">История попыток</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {attempts.map((attempt) => (
                  <li key={attempt.id}>
                    <AttemptRow attempt={attempt} />
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
