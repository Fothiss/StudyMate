import { ArrowLeft, BookOpenCheck, FileText, Loader2, Wand2 } from "lucide-react";
import { Link } from "react-router";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { Material, QuizCounts } from "@/lib/api";
import type { LoadState } from "@/lib/load-state";
import { cn } from "@/lib/utils";

export const MAX_CHOICE_QUESTIONS = 15;
export const MAX_OPEN_QUESTIONS = 10;

type PracticeConfigProps = {
  materials: Material[];
  materialsState: LoadState;
  materialsError?: string;
  onRetryMaterials: () => void;
  selectedId: string | null;
  onSelect: (materialId: string) => void;
  counts: QuizCounts;
  onCountsChange: (counts: QuizCounts) => void;
  onGenerate: () => void;
  error: string | null;
};

/** Проверка формы: повторяет ограничения backend, чтобы не гонять пустой запрос. */
export function validateCounts(counts: QuizCounts): string | null {
  if (counts.choiceCount < 0 || counts.openCount < 0) {
    return "Количество вопросов не может быть отрицательным";
  }
  if (counts.choiceCount > MAX_CHOICE_QUESTIONS) {
    return `Не больше ${MAX_CHOICE_QUESTIONS} тестовых вопросов`;
  }
  if (counts.openCount > MAX_OPEN_QUESTIONS) {
    return `Не больше ${MAX_OPEN_QUESTIONS} открытых вопросов`;
  }
  if (counts.choiceCount + counts.openCount === 0) {
    return "Нужен хотя бы один вопрос";
  }
  return null;
}

export function PracticeConfig({
  materials,
  materialsState,
  materialsError,
  onRetryMaterials,
  selectedId,
  onSelect,
  counts,
  onCountsChange,
  onGenerate,
  error,
}: PracticeConfigProps) {
  const hasMaterials = materials.length > 0;
  const validationError = validateCounts(counts);
  const canGenerate = hasMaterials && validationError === null;

  if (materialsState === "loading") {
    return (
      <Card>
        <CardContent className="flex items-center gap-2 py-8 text-sm text-muted-foreground">
          <Loader2 className="size-4 animate-spin" aria-hidden />
          Загружаем материалы…
        </CardContent>
      </Card>
    );
  }

  if (materialsState === "error") {
    return (
      <Card>
        <CardContent className="space-y-3 py-8">
          <p className="text-sm text-destructive">
            {materialsError ?? "Не удалось загрузить материалы"}
          </p>
          <Button variant="outline" size="sm" onClick={onRetryMaterials}>
            Повторить
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!hasMaterials) {
    return (
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 font-heading text-lg">
            <FileText className="size-4 text-primary" aria-hidden />
            Сначала нужен материал
          </CardTitle>
          <CardDescription>
            Тест строится только по вашему тексту, поэтому без загруженного PDF вопросов не
            будет.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-sm font-semibold text-primary underline-offset-4 hover:underline"
          >
            <ArrowLeft className="size-4" aria-hidden />
            К загрузке материала
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-lg">1. Материал</CardTitle>
          <CardDescription>Вопросы строятся только по тексту выбранного файла</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 sm:grid-cols-2">
            {materials.map((material) => {
              const active = material.id === selectedId;
              return (
                <button
                  key={material.id}
                  type="button"
                  onClick={() => onSelect(material.id)}
                  aria-pressed={active}
                  className={cn(
                    "flex items-start gap-3 rounded-xl border px-3 py-2.5 text-left transition-colors",
                    active
                      ? "border-primary/50 bg-primary/10 ring-1 ring-primary/30"
                      : "border-border hover:bg-secondary",
                  )}
                >
                  <span
                    className={cn(
                      "mt-0.5 grid size-8 shrink-0 place-items-center rounded-lg",
                      active
                        ? "bg-primary text-primary-foreground"
                        : "bg-secondary text-muted-foreground",
                    )}
                  >
                    <BookOpenCheck className="size-4" aria-hidden />
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-medium">{material.title}</span>
                    <span className="block truncate text-xs text-muted-foreground">
                      {material.filename}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-lg">2. Сколько вопросов</CardTitle>
          <CardDescription>
            Открытые вопросы проверяет GigaChat: он объяснит, что верно и что упущено
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="choice-count">Тестовые</Label>
              <Input
                id="choice-count"
                type="number"
                min={0}
                max={MAX_CHOICE_QUESTIONS}
                value={counts.choiceCount}
                onChange={(event) =>
                  onCountsChange({ ...counts, choiceCount: Number(event.target.value) })
                }
              />
              <p className="text-xs text-muted-foreground">4 варианта ответа, до 15</p>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="open-count">Открытые</Label>
              <Input
                id="open-count"
                type="number"
                min={0}
                max={MAX_OPEN_QUESTIONS}
                value={counts.openCount}
                onChange={(event) =>
                  onCountsChange({ ...counts, openCount: Number(event.target.value) })
                }
              />
              <p className="text-xs text-muted-foreground">Проверка по смыслу, до 10</p>
            </div>
          </div>

          {(validationError ?? error) && (
            <p className="text-sm text-destructive">{validationError ?? error}</p>
          )}

          <Button onClick={onGenerate} disabled={!canGenerate} size="lg">
            <Wand2 className="size-4" aria-hidden />
            Сгенерировать тест
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
