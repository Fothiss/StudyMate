import { TriangleAlert } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { PracticeConfig } from "@/components/practice/practice-config";
import { PracticeGenerating } from "@/components/practice/practice-generating";
import { PracticeRun } from "@/components/practice/practice-run";
import {
  describeQuizError,
  fetchMaterials,
  generateQuiz,
  submitAttempt,
  type AttemptAnswerInput,
  type Material,
  type QuizCounts,
} from "@/lib/api";
import type { LoadState } from "@/lib/load-state";
import {
  clearPractice,
  createDraft,
  loadPractice,
  savePractice,
  type StoredPractice,
} from "@/lib/practice-storage";

type Step = "config" | "generating" | "answering";

/** Ответы черновика в теле сдачи: непроставленные вопросы просто не уходят. */
function buildAnswers(practice: StoredPractice): AttemptAnswerInput[] {
  const answers: AttemptAnswerInput[] = [];

  practice.questions.forEach((question, index) => {
    const given = practice.answers[index];

    if (question.kind === "choice") {
      if (typeof given === "number") {
        answers.push({ question_id: question.question_id, selected_index: given });
      }
      return;
    }

    const text = typeof given === "string" ? given.trim() : "";
    if (text.length > 0) {
      answers.push({ question_id: question.question_id, answer_text: text });
    }
  });

  return answers;
}

export default function PracticePage() {
  const navigate = useNavigate();

  const [materials, setMaterials] = useState<Material[]>([]);
  const [materialsState, setMaterialsState] = useState<LoadState>("loading");
  const [materialsError, setMaterialsError] = useState<string | null>(null);
  const [materialsAttempt, setMaterialsAttempt] = useState(0);

  const [practice, setPractice] = useState<StoredPractice | null>(loadPractice);
  const [counts, setCounts] = useState<QuizCounts>({ choiceCount: 5, openCount: 0 });
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const [generating, setGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

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

  const generate = useCallback(async () => {
    if (currentMaterialId === null) {
      return;
    }

    const material = materials.find((item) => item.id === currentMaterialId) ?? null;
    setGenerating(true);
    setGenerationError(null);
    setSubmitError(null);

    try {
      const generated = await generateQuiz(currentMaterialId, counts);
      const draft = createDraft(
        generated,
        { id: currentMaterialId, title: material?.title ?? "" },
        counts.choiceCount + counts.openCount,
      );
      commit(draft);
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

  const submit = useCallback(async () => {
    if (practice === null || submitting) {
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      const result = await submitAttempt(practice.testId, buildAnswers(practice));
      // Результат живёт на сервере, поэтому черновик больше не нужен: иначе
      // возврат на /quiz показал бы уже сданный тест.
      clearPractice();
      setPractice(null);
      navigate(`/results/${result.attempt_id}`, { state: { afterSubmit: true } });
    } catch (error) {
      setSubmitError(describeQuizError(error, "attempt"));
    } finally {
      setSubmitting(false);
    }
  }, [navigate, practice, submitting]);

  const step: Step = generating ? "generating" : practice === null ? "config" : "answering";

  const selectedTitle =
    materials.find((item) => item.id === currentMaterialId)?.title ??
    practice?.materialTitle ??
    "материал";

  const safeIndex =
    practice === null ? 0 : Math.min(practice.questionIndex, practice.questions.length - 1);

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
        <>
          {submitError && (
            <p className="flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              <TriangleAlert className="size-4" aria-hidden />
              {submitError}
            </p>
          )}

          <PracticeRun
            questions={practice.questions}
            requestedTotal={practice.requestedTotal}
            index={safeIndex}
            answer={practice.answers[safeIndex]}
            submitting={submitting}
            onAnswer={answerQuestion}
            onPrevious={() => goTo(Math.max(0, safeIndex - 1))}
            onNext={() => goTo(Math.min(practice.questions.length - 1, safeIndex + 1))}
            onSubmit={() => void submit()}
          />
        </>
      )}
    </div>
  );
}
