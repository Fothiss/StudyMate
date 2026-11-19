import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

import { Card, CardContent } from "@/components/ui/card";

const PHASES = ["Читаем материал", "Составляем вопросы", "Проверяем формулировки"];

type PracticeGeneratingProps = {
  materialTitle: string;
};

/**
 * Ожидание генерации. Модель отвечает до минуты, поэтому вместо
 * бесконечного спиннера показываются сменяющиеся фазы — декоративные,
 * они не претендуют на измерение прогресса.
 */
export function PracticeGenerating({ materialTitle }: PracticeGeneratingProps) {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setPhase((value) => (value + 1) % PHASES.length);
    }, 4000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <Card className="aurora-border border-0">
      <CardContent className="space-y-5 py-10">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Loader2 className="size-4 animate-spin text-primary" aria-hidden />
          {PHASES[phase]}…
        </div>
        <p className="text-sm text-muted-foreground">
          Материал: «{materialTitle}». Обычно это занимает до минуты — не закрывайте вкладку.
        </p>
        <div className="h-2 overflow-hidden rounded-full bg-secondary">
          <div className="pulse-soft h-full w-1/3 rounded-full bg-gradient-to-r from-[var(--aurora-1)] via-[var(--aurora-2)] to-[var(--aurora-3)]" />
        </div>
        <div className="space-y-2" aria-hidden>
          {[0, 1, 2].map((row) => (
            <div
              key={row}
              className="pulse-soft h-4 rounded bg-secondary"
              style={{ width: `${88 - row * 16}%`, animationDelay: `${row * 200}ms` }}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
