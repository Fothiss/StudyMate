"use client";

import { useRef, useState, type ChangeEvent, type FormEvent } from "react";

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
import { describeError, uploadMaterial, type Material } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { LoadState } from "@/lib/load-state";

type MaterialsBlockProps = {
  state: LoadState;
  materials: Material[];
  errorMessage?: string;
  onRetry: () => void;
  onUploaded: (material: Material) => void;
  className?: string;
};

export function MaterialsBlock({
  state,
  materials,
  errorMessage,
  onRetry,
  onUploaded,
  className,
}: MaterialsBlockProps) {
  const formRef = useRef<HTMLFormElement>(null);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [titleError, setTitleError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const count = materials.length;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTitleError(null);
    setFormError(null);

    if (title.trim().length === 0) {
      setTitleError("Введите название материала");
      return;
    }
    if (file === null) {
      setFormError("Выберите файл");
      return;
    }

    setPending(true);
    try {
      const material = await uploadMaterial(title.trim(), file);
      onUploaded(material);
      setTitle("");
      setFile(null);
      formRef.current?.reset();
    } catch (error) {
      setFormError(describeError(error));
    } finally {
      setPending(false);
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-baseline gap-2">
          Мои материалы
          {state === "ready" && (
            <span className="text-sm font-normal text-muted-foreground">{count}</span>
          )}
        </CardTitle>
        {state === "ready" && count > 0 && (
          <CardDescription>Загружены раньше — показаны первыми</CardDescription>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {state === "loading" && (
          <p className="text-sm text-muted-foreground">Загрузка материалов…</p>
        )}

        {state === "error" && (
          <div className="space-y-2">
            <p className="text-sm text-destructive">
              {errorMessage ?? "Не удалось загрузить материалы"}
            </p>
            <Button variant="outline" size="sm" onClick={onRetry}>
              Повторить
            </Button>
          </div>
        )}

        {state === "ready" && count === 0 && (
          <div className="space-y-1">
            <p className="text-sm font-medium">Материалов пока нет</p>
            <p className="text-sm text-muted-foreground">
              Загрузите лекцию, конспект или презентацию — по ним можно будет проходить тесты.
            </p>
          </div>
        )}

        {state === "ready" && count > 0 && (
          <ul className="divide-y">
            {materials.map((material) => (
              <li
                key={material.id}
                className="flex items-baseline justify-between gap-3 py-2 first:pt-0 last:pb-0"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{material.title}</p>
                  <p className="truncate text-xs text-muted-foreground">{material.filename}</p>
                </div>
                <span className="shrink-0 text-xs text-muted-foreground">
                  {formatDate(material.created_at)}
                </span>
              </li>
            ))}
          </ul>
        )}

        <form ref={formRef} onSubmit={handleSubmit} className="space-y-3 border-t pt-4">
          <div className="space-y-1.5">
            <Label htmlFor="material-title">Название</Label>
            <Input
              id="material-title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Например, Лекция 1"
              maxLength={255}
              disabled={pending}
            />
            {titleError && <p className="text-xs text-destructive">{titleError}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="material-file">Файл (PDF, DOCX или PPTX)</Label>
            <Input
              id="material-file"
              type="file"
              accept=".pdf,.docx,.pptx"
              onChange={handleFileChange}
              disabled={pending}
            />
          </div>

          {formError && <p className="text-sm text-destructive">{formError}</p>}

          <Button type="submit" disabled={pending}>
            {pending ? "Загружаем…" : "Загрузить материал"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
