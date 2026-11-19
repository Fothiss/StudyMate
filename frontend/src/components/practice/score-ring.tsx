import type { CSSProperties } from "react";

type ScoreRingProps = {
  correct: number;
  total: number;
};

/** Круговой счёт: доля верных тестовых ответов. */
export function ScoreRing({ correct, total }: ScoreRingProps) {
  const percent = total === 0 ? 0 : Math.round((correct / total) * 100);

  return (
    <div
      className="count-ring grid size-32 shrink-0 place-items-center rounded-full"
      style={{ "--ring-value": `${percent}%` } as CSSProperties}
      role="img"
      aria-label={`Верно ${correct} из ${total}`}
    >
      <div className="flex size-24 flex-col items-center justify-center rounded-full bg-surface">
        <span className="font-heading text-2xl font-extrabold">{percent}%</span>
        <span className="text-xs text-muted-foreground">
          {correct} из {total}
        </span>
      </div>
    </div>
  );
}
