import { CalendarDays, FileText, Loader2, Upload } from "lucide-react";
import { useRef, useState, type ChangeEvent, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
        <CardTitle className="flex items-center gap-2 font-heading text-lg">
          <FileText className="size-4 text-primary" aria-hidden />
          Мои материалы
          {state === "ready" && (
            <span className="rounded-full bg-secondary px-2 py-0.5 text-xs font-semibold text-muted-foreground">
              {count}
            </span>
          )}
        </CardTitle>
        <CardDescription>
          {state === "ready" && count > 0
            ? "Загружены раньше — показаны первыми"
            : "PDF с текстовым слоем, до 20 МБ"}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-5">
        {state === "loading" && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="size-4 animate-spin" aria-hidden />
            Загрузка материалов…
          </div>
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
          <div className="rounded-xl border border-dashed px-4 py-6 text-center">
            <p className="text-sm font-medium">Материалов пока нет</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Загрузите лекцию, конспект или презентацию — по ним можно будет проходить тесты.
            </p>
          </div>
        )}

        {state === "ready" && count > 0 && (
          <ul className="space-y-1.5">
            {materials.map((material) => (
              <li
                key={material.id}
                className="flex items-center gap-3 rounded-xl bg-secondary/50 px-3 py-2.5 transition-colors hover:bg-secondary"
              >
                <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-primary/12 text-primary">
                  <FileText className="size-4" aria-hidden />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{material.title}</p>
                  <p className="truncate text-xs text-muted-foreground">{material.filename}</p>
                </div>
                <span className="flex shrink-0 items-center gap-1 text-xs text-muted-foreground">
                  <CalendarDays className="size-3.5" aria-hidden />
                  {formatDate(material.created_at)}
                </span>
              </li>
            ))}
          </ul>
        )}

        <form
          ref={formRef}
          onSubmit={handleSubmit}
          className="space-y-3 rounded-xl border border-dashed p-4"
        >
          <p className="flex items-center gap-2 text-sm font-medium">
            <Upload className="size-4 text-primary" aria-hidden />
            Добавить материал
          </p>

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
            <Label htmlFor="material-file">Файл (PDF)</Label>
            <Input
              id="material-file"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={pending}
            />
          </div>

          {formError && <p className="text-sm text-destructive">{formError}</p>}

          <Button type="submit" disabled={pending}>
            {pending ? (
              <>
                <Loader2 className="size-4 animate-spin" aria-hidden />
                Загружаем…
              </>
            ) : (
              "Загрузить материал"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
