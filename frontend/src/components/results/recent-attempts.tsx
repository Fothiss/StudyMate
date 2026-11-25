import { Loader2, TriangleAlert } from "lucide-react";
import { Link } from "react-router";

import { AttemptRow } from "@/components/results/attempt-row";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Attempt } from "@/lib/api";
import type { LoadState } from "@/lib/load-state";

/** Сколько последних попыток показывать на дашборде. */
const RECENT_LIMIT = 3;

type RecentAttemptsProps = {
  state: LoadState;
  attempts: Attempt[];
  errorMessage?: string;
  onRetry: () => void;
};

/**
 * Раздел «Результаты» на дашборде: последние попытки и вход в историю.
 * Ссылка на историю есть в любом состоянии, включая пустое.
 */
export function RecentAttempts({
  state,
  attempts,
  errorMessage,
  onRetry,
}: RecentAttemptsProps) {
  const recent = attempts.slice(0, RECENT_LIMIT);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-base">Результаты</CardTitle>
        <CardAction>
          <Link to="/results" className={buttonVariants({ variant: "ghost", size: "sm" })}>
            Вся история
          </Link>
        </CardAction>
      </CardHeader>

      <CardContent>
        {state === "loading" && (
          <p className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="size-4 animate-spin" aria-hidden />
            Загружаем результаты…
          </p>
        )}

        {state === "error" && (
          <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
            <span className="flex items-center gap-2 text-destructive">
              <TriangleAlert className="size-4" aria-hidden />
              {errorMessage ?? "Не удалось загрузить результаты"}
            </span>
            <Button variant="outline" size="sm" onClick={onRetry}>
              Повторить
            </Button>
          </div>
        )}

        {state === "ready" && recent.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Оценки последних попыток появятся здесь после первого завершённого теста.
          </p>
        )}

        {state === "ready" && recent.length > 0 && (
          <ul className="space-y-2">
            {recent.map((attempt) => (
              <li key={attempt.id}>
                <AttemptRow attempt={attempt} />
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
