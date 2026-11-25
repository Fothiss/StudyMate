import { FileText, Wand2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router";

import { useProfile } from "@/app/shell/profile-context";
import { MaterialsBlock } from "@/components/materials-block";
import { RecentAttempts } from "@/components/results/recent-attempts";
import { describeError, fetchAttempts, fetchMaterials, type Attempt, type Material } from "@/lib/api";
import type { LoadState } from "@/lib/load-state";

export default function OverviewPage() {
  const profile = useProfile();

  const [materials, setMaterials] = useState<Material[]>([]);
  const [materialsError, setMaterialsError] = useState<string | null>(null);
  const [materialsState, setMaterialsState] = useState<LoadState>("loading");
  const [attempt, setAttempt] = useState(0);

  const [attempts, setAttempts] = useState<Attempt[]>([]);
  const [attemptsError, setAttemptsError] = useState<string | null>(null);
  const [attemptsState, setAttemptsState] = useState<LoadState>("loading");
  const [attemptsReload, setAttemptsReload] = useState(0);

  const retry = useCallback(() => {
    setMaterialsState("loading");
    setMaterialsError(null);
    setAttempt((value) => value + 1);
  }, []);

  const retryAttempts = useCallback(() => {
    setAttemptsState("loading");
    setAttemptsError(null);
    setAttemptsReload((value) => value + 1);
  }, []);

  const addMaterial = useCallback((material: Material) => {
    setMaterials((current) => [material, ...current]);
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
        setMaterialsError(describeError(error));
        setMaterialsState("error");
      });

    return () => {
      cancelled = true;
    };
  }, [attempt]);

  useEffect(() => {
    let cancelled = false;

    fetchAttempts()
      .then((list) => {
        if (cancelled) return;
        setAttempts(list);
        setAttemptsState("ready");
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setAttemptsError(describeError(error));
        setAttemptsState("error");
      });

    return () => {
      cancelled = true;
    };
  }, [attemptsReload]);

  return (
    <div className="space-y-5">
      <section className="rise glass relative overflow-hidden rounded-3xl p-6 sm:p-8">
        <div
          className="pointer-events-none absolute -top-20 -right-16 size-64 rounded-full bg-[var(--aurora-2)] opacity-25 blur-3xl"
          aria-hidden
        />
        <p className="text-[0.7rem] font-semibold tracking-[0.18em] text-muted-foreground uppercase">
          Личный кабинет
        </p>
        <h1 className="mt-2 font-heading text-3xl font-extrabold tracking-tight sm:text-4xl">
          Привет{profile ? `, ${profile.username}` : ""}
        </h1>
        <p className="mt-2 max-w-xl text-sm text-muted-foreground">
          Загрузите лекцию — и превратите её в тест. Вопросы строятся только по вашему
          материалу, ничего не придумывается.
        </p>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Link
            to="/quiz"
            className="sheen inline-flex h-11 items-center gap-2 rounded-xl bg-gradient-to-r from-[var(--aurora-1)] via-[var(--aurora-2)] to-[var(--aurora-3)] px-5 text-sm font-semibold text-white shadow-lg shadow-[var(--aurora-1)]/30 transition-transform hover:-translate-y-0.5"
          >
            <Wand2 className="size-4" aria-hidden />
            Сгенерировать тест
          </Link>

          <span className="inline-flex items-center gap-2 rounded-xl bg-secondary/70 px-3 py-2 text-xs font-medium text-muted-foreground">
            <FileText className="size-4" aria-hidden />
            {materialsState === "ready" ? `${materials.length} материалов` : "загрузка…"}
          </span>
        </div>
      </section>

      <div className="rise" style={{ animationDelay: "60ms" }}>
        <MaterialsBlock
          state={materialsState}
          materials={materials}
          errorMessage={materialsError ?? undefined}
          onRetry={retry}
          onUploaded={addMaterial}
        />
      </div>

      <div className="rise" style={{ animationDelay: "120ms" }}>
        <RecentAttempts
          state={attemptsState}
          attempts={attempts}
          errorMessage={attemptsError ?? undefined}
          onRetry={retryAttempts}
        />
      </div>
    </div>
  );
}
