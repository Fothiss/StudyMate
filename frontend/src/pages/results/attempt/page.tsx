import { ArrowLeft, Loader2, TriangleAlert } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router";

import { AttemptDetailView } from "@/components/results/attempt-detail";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  ApiError,
  checkAttempt,
  describeQuizError,
  fetchAttempt,
  type AttemptDetail,
} from "@/lib/api";
import { hasUncheckedOpenAnswers } from "@/lib/attempts";
import type { LoadState } from "@/lib/load-state";

/** Состояние перехода после сдачи: разбор открывается сразу с проверкой. */
type SubmittedState = {
  afterSubmit?: boolean;
};

export default function AttemptPage() {
  const { attemptId = "" } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [detail, setDetail] = useState<AttemptDetail | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [missing, setMissing] = useState(false);
  const [checkState, setCheckState] = useState<LoadState>("ready");
  const [checkError, setCheckError] = useState<string | null>(null);

  // Проверку после сдачи запускаем один раз: признак живёт в состоянии
  // навигации, а повторный запуск отсекает ref, потому что строгий режим
  // монтирует компонент дважды.
  const autoCheck = useRef((location.state as SubmittedState | null)?.afterSubmit === true);

  const runCheck = useCallback(async () => {
    setCheckState("loading");
    setCheckError(null);

    try {
      await checkAttempt(attemptId);
      // Оценки пишет сервер: перечитываем разбор, а не собираем его сами.
      const refreshed = await fetchAttempt(attemptId);
      setDetail(refreshed);
      setCheckState("ready");
    } catch (caught) {
      setCheckError(describeQuizError(caught, "check"));
      setCheckState("error");
    }
  }, [attemptId]);

  const applyDetail = useCallback(
    (loaded: AttemptDetail) => {
      setDetail(loaded);
      setState("ready");

      if (autoCheck.current && hasUncheckedOpenAnswers(loaded)) {
        autoCheck.current = false;
        void runCheck();
      }
    },
    [runCheck],
  );

  const fail = useCallback((caught: unknown) => {
    setDetail(null);
    setState("error");
    if (caught instanceof ApiError && caught.status === 404) {
      setMissing(true);
      return;
    }
    setError(describeQuizError(caught, "attempt"));
  }, []);

  // Загружаем разбор при открытии ссылки: состояние ставится в обработчиках
  // промиса, поэтому эффект не пишет его синхронно.
  useEffect(() => {
    let cancelled = false;

    fetchAttempt(attemptId)
      .then((loaded) => {
        if (!cancelled) {
          applyDetail(loaded);
        }
      })
      .catch((caught: unknown) => {
        if (!cancelled) {
          fail(caught);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [attemptId, fail, applyDetail]);

  const retry = useCallback(() => {
    setState("loading");
    setError(null);
    setMissing(false);
    fetchAttempt(attemptId).then(applyDetail).catch(fail);
  }, [attemptId, fail, applyDetail]);

  return (
    <div className="space-y-4">
      <Link
        to="/results"
        className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="size-4" aria-hidden />
        К истории
      </Link>

      {state === "loading" && (
        <Card>
          <CardContent className="flex items-center gap-3 py-8 text-sm text-muted-foreground">
            <Loader2 className="size-4 animate-spin" aria-hidden />
            Загружаем разбор попытки…
          </CardContent>
        </Card>
      )}

      {state === "error" && missing && (
        <Card>
          <CardContent className="space-y-3 py-8">
            <p className="flex items-center gap-2 text-sm font-medium">
              <TriangleAlert className="size-4 text-destructive" aria-hidden />
              Попытка не найдена
            </p>
            <p className="text-sm text-muted-foreground">
              Возможно, ссылка устарела или попытка была удалена. Откройте историю и
              выберите разбор из списка.
            </p>
            <Button variant="outline" size="sm" onClick={() => void navigate("/results")}>
              К истории
            </Button>
          </CardContent>
        </Card>
      )}

      {state === "error" && !missing && (
        <Card>
          <CardContent className="space-y-3 py-8">
            <p className="flex items-center gap-2 text-sm font-medium">
              <TriangleAlert className="size-4 text-destructive" aria-hidden />
              {error ?? "Не удалось загрузить разбор попытки"}
            </p>
            <Button variant="outline" size="sm" onClick={retry}>
              Повторить
            </Button>
          </CardContent>
        </Card>
      )}

      {state === "ready" && detail !== null && (
        <AttemptDetailView
          detail={detail}
          checkState={checkState}
          checkError={checkError}
          onCheck={() => void runCheck()}
        />
      )}
    </div>
  );
}
