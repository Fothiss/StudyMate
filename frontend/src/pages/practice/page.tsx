import { useCallback, useEffect, useState } from "react";

import { PracticeConfig } from "@/components/practice/practice-config";
import { PracticeGenerating } from "@/components/practice/practice-generating";
import { PracticeResult } from "@/components/practice/practice-result";
import { PracticeRun } from "@/components/practice/practice-run";
import {
  checkAnswers,
  describeQuizError,
  fetchMaterials,
  generateQuiz,
  type CheckedAnswer,
  type Material,
  type QuizCounts,
} from "@/lib/api";
import type { LoadState } from "@/lib/load-state";
import {
  collectOpenAnswers,
  mergeEvaluations,
  splitAnswers,
} from "@/lib/practice-evaluate";
import {
  clearPractice,
  loadPractice,
  savePractice,
  type StoredPractice,
} from "@/lib/practice-storage";

const EMPTY_OPEN_FEEDBACK =
  "Ответ не дан, поэтому балл нулевой. Сформулируйте ответ своими словами и проверьте снова.";

type Step = "config" | "generating" | "answering" | "result";

export default function PracticePage() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [materialsState, setMaterialsState] = useState<LoadState>("loading");
  const [materialsError, setMaterialsError] = useState<string | null>(null);
  const [materialsAttempt, setMaterialsAttempt] = useState(0);

  const [practice, setPractice] = useState<StoredPractice | null>(loadPractice);
  const [counts, setCounts] = useState<QuizCounts>({ choiceCount: 5, openCount: 0 });
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const [generating, setGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);

  const [evaluationState, setEvaluationState] = useState<LoadState>("ready");
  const [evaluationError, setEvaluationError] = useState<string | null>(null);

  const retryMaterials = useCallback(() => {
    setMaterialsState("loading");
    setMaterialsError(null);
    setMaterialsAttempt((value) => value + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    fetchMaterials()
      .then((list) => {
        if (cancelled) return;
        setMaterials(list);
        setMaterialsState("ready");
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setMaterialsError(describeQuizError(error, "generate"));
        setMaterialsState("error");
      });

    return () => {
      cancelled = true;
    };
  }, [materialsAttempt]);

  const currentMaterialId = selectedId ?? materials[0]?.id ?? null;

  const commit = useCallback((next: StoredPractice) => {
    savePractice(next);
    setPractice(next);
  }, []);

  const commitEvaluation = useCallback(
    (state: StoredPractice, results: CheckedAnswer[]) => {
      savePractice({ ...state, evaluation: results });
      setPractice({ ...state, evaluation: results });
      setEvaluationState("ready");
    },
    [],
  );

  const evaluate = useCallback(
    async (state: StoredPractice) => {
      const openItems = collectOpenAnswers(state.quiz, state.answers);

      if (openItems.length === 0) {
        return;
      }

      const { filled } = splitAnswers(openItems);
      setEvaluationError(null);

      // Пустые ответы не отправляем в модель: балл за них и так известен.
      if (filled.length === 0) {
        commitEvaluation(state, mergeEvaluations(openItems, [], [], EMPTY_OPEN_FEEDBACK));
        return;
      }

      setEvaluationState("loading");
      try {
        const graded = await checkAnswers(
          state.materialId,
          filled.map(({ question, reference, answer }) => ({ question, reference, answer })),
        );

        commitEvaluation(state, mergeEvaluations(openItems, filled, graded, EMPTY_OPEN_FEEDBACK));
      } catch (error) {
        setEvaluationState("error");
        setEvaluationError(describeQuizError(error, "check"));
      }
    },
    [commitEvaluation],
  );

  const generate = useCallback(async () => {
    if (currentMaterialId === null) {
      return;
    }

    const material = materials.find((item) => item.id === currentMaterialId) ?? null;
    setGenerating(true);
    setGenerationError(null);
    setEvaluationError(null);

    try {
      const quiz = await generateQuiz(currentMaterialId, counts);
      commit({
        version: 1,
        materialId: currentMaterialId,
        materialTitle: material?.title ?? "",
        summary: quiz.summary,
        quiz,
        answers: {},
        questionIndex: 0,
        requestedTotal: counts.choiceCount + counts.openCount,
        submitted: false,
        evaluation: null,
      });
      setEvaluationState("ready");
    } catch (error) {
      setGenerationError(describeQuizError(error, "generate"));
    } finally {
      setGenerating(false);
    }
  }, [commit, counts, currentMaterialId, materials]);

  const answerQuestion = useCallback(
    (value: number | string) => {
      if (practice === null) return;
      commit({
        ...practice,
        answers: { ...practice.answers, [practice.questionIndex]: value },
      });
    },
    [commit, practice],
  );

  const goTo = useCallback(
    (index: number) => {
      if (practice === null) return;
      commit({ ...practice, questionIndex: index });
    },
    [commit, practice],
  );

  const submit = useCallback(() => {
    if (practice === null || practice.submitted) return;
    const next: StoredPractice = { ...practice, submitted: true };
    commit(next);
    void evaluate(next);
  }, [commit, evaluate, practice]);

  const retryEvaluation = useCallback(() => {
    if (practice === null) return;
    void evaluate(practice);
  }, [evaluate, practice]);

  const restart = useCallback(() => {
    clearPractice();
    setPractice(null);
    setEvaluationState("ready");
    setEvaluationError(null);
    setGenerationError(null);
  }, []);

  const step: Step = generating
    ? "generating"
    : practice === null
      ? "config"
      : practice.submitted
        ? "result"
        : "answering";

  const selectedTitle =
    materials.find((item) => item.id === currentMaterialId)?.title ??
    practice?.materialTitle ??
    "материал";

  const safeIndex =
    practice === null
      ? 0
      : Math.min(practice.questionIndex, practice.quiz.questions.length - 1);

  return (
    <div className="space-y-5">
      <header className="rise glass rounded-3xl p-6">
        <p className="text-[0.7rem] font-semibold tracking-[0.18em] text-muted-foreground uppercase">
          Тренажёр
        </p>
        <h1 className="mt-1 font-heading text-3xl font-extrabold tracking-tight">Тест</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          Вопросы строятся по тексту материала. Пока тест не завершён, правильные ответы не
          показываются — иначе проверять себя бессмысленно.
        </p>
      </header>

      {step === "generating" && <PracticeGenerating materialTitle={selectedTitle} />}

      {step === "config" && (
        <PracticeConfig
          materials={materials}
          materialsState={materialsState}
          materialsError={materialsError ?? undefined}
          onRetryMaterials={retryMaterials}
          selectedId={currentMaterialId}
          onSelect={setSelectedId}
          counts={counts}
          onCountsChange={setCounts}
          onGenerate={() => void generate()}
          error={generationError}
        />
      )}

      {step === "answering" && practice !== null && (
        <PracticeRun
          quiz={practice.quiz}
          requestedTotal={practice.requestedTotal}
          index={safeIndex}
          answer={practice.answers[safeIndex]}
          onAnswer={answerQuestion}
          onPrevious={() => goTo(Math.max(0, safeIndex - 1))}
          onNext={() => goTo(Math.min(practice.quiz.questions.length - 1, safeIndex + 1))}
          onSubmit={submit}
        />
      )}

      {step === "result" && practice !== null && (
        <PracticeResult
          quiz={practice.quiz}
          answers={practice.answers}
          evaluation={practice.evaluation}
          evaluationState={evaluationState}
          evaluationError={evaluationError}
          onRetryEvaluation={retryEvaluation}
          onRestart={restart}
        />
      )}
    </div>
  );
}
