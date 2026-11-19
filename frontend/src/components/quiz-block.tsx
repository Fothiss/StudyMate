"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { describeError, generateQuiz, type Material, type Quiz } from "@/lib/api";

type QuizBlockProps = {
  materials: Material[];
  className?: string;
};

export function QuizBlock({ materials, className }: QuizBlockProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [generatedFor, setGeneratedFor] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  // Пока материал не выбран явно, работаем с самым свежим.
  const currentId = selectedId ?? materials[0]?.id ?? null;
  const current = materials.find((material) => material.id === currentId) ?? null;

  function selectMaterial(material: Material) {
    setSelectedId(material.id);
    setQuiz(null);
    setGeneratedFor(null);
    setError(null);
  }

  async function handleGenerate() {
    if (current === null) {
      return;
    }

    setError(null);
    setPending(true);
    try {
      const generated = await generateQuiz(current.id);
      setQuiz(generated);
      setGeneratedFor(current.title);
    } catch (cause) {
      setQuiz(null);
      setGeneratedFor(null);
      setError(describeError(cause));
    } finally {
      setPending(false);
    }
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Тест</CardTitle>
        <CardDescription>
          {materials.length > 0
            ? "Вопросы строятся по тексту материала и не сохраняются"
            : "Сначала загрузите материал"}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {materials.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {materials.map((material) => (
              <Button
                key={material.id}
                size="sm"
                variant={material.id === currentId ? "default" : "outline"}
                disabled={pending}
                onClick={() => selectMaterial(material)}
              >
                {material.title}
              </Button>
            ))}
          </div>
        )}

        {materials.length > 0 && (
          <Button onClick={handleGenerate} disabled={pending || current === null}>
            {pending ? "Генерируем, это займёт до минуты…" : "Сгенерировать тест"}
          </Button>
        )}

        {error && <p className="text-sm text-destructive">{error}</p>}

        {quiz && (
          <div className="space-y-4 border-t pt-4">
            <div className="space-y-1.5">
              <p className="text-sm font-medium">Краткое содержание</p>
              <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                {quiz.summary.map((point, index) => (
                  <li key={`summary-${index}`}>{point}</li>
                ))}
              </ul>
            </div>

            <div className="space-y-1.5">
              <p className="text-sm font-medium">Вопросы</p>
              <ol className="space-y-3">
                {quiz.questions.map((question, questionIndex) => (
                  <li key={`question-${questionIndex}`} className="space-y-1">
                    <p className="text-sm font-medium">
                      {questionIndex + 1}. {question.text}
                    </p>
                    <ul className="space-y-0.5 text-sm">
                      {question.options.map((option, optionIndex) => {
                        const correct = optionIndex === question.correct_index;
                        return (
                          <li
                            key={`option-${questionIndex}-${optionIndex}`}
                            className={correct ? "text-emerald-600" : "text-muted-foreground"}
                          >
                            {correct ? "✓ " : "• "}
                            {option}
                          </li>
                        );
                      })}
                    </ul>
                  </li>
                ))}
              </ol>
            </div>

            {generatedFor && (
              <p className="text-xs text-muted-foreground">Материал: {generatedFor}</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
