"use client";

import { useCallback, useEffect, useState } from "react";

import { Header } from "@/components/header";
import { MaterialsBlock } from "@/components/materials-block";
import { UnavailableSection } from "@/components/unavailable-section";
import { Button } from "@/components/ui/button";
import { useSession } from "@/hooks/use-session";
import {
  describeError,
  fetchMaterials,
  fetchMe,
  type Material,
  type User,
} from "@/lib/api";
import type { LoadState } from "@/lib/load-state";

export default function DashboardPage() {
  const { authenticated, signOut } = useSession();

  const [profile, setProfile] = useState<User | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileState, setProfileState] = useState<LoadState>("loading");

  const [materials, setMaterials] = useState<Material[]>([]);
  const [materialsError, setMaterialsError] = useState<string | null>(null);
  const [materialsState, setMaterialsState] = useState<LoadState>("loading");

  const [attempt, setAttempt] = useState(0);

  const retry = useCallback(() => {
    setAttempt((value) => value + 1);
  }, []);

  const addMaterial = useCallback((material: Material) => {
    setMaterials((current) => [material, ...current]);
  }, []);

  useEffect(() => {
    if (!authenticated) {
      return;
    }

    let cancelled = false;
    setProfileState("loading");
    setMaterialsState("loading");
    setProfileError(null);
    setMaterialsError(null);

    fetchMe()
      .then((user) => {
        if (cancelled) return;
        setProfile(user);
        setProfileState("ready");
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setProfile(null);
        setProfileError(describeError(error));
        setProfileState("error");
      });

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
  }, [authenticated, attempt]);

  return (
    <div className="flex flex-1 flex-col">
      <Header login={profile?.username ?? null} onSignOut={signOut} />

      <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-8">
        {profileState === "error" && (
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            <span>{profileError ?? "Не удалось загрузить профиль"}</span>
            <Button variant="outline" size="sm" onClick={retry}>
              Повторить
            </Button>
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2">
          <MaterialsBlock
            className="md:col-span-2"
            state={materialsState}
            materials={materials}
            errorMessage={materialsError ?? undefined}
            onRetry={retry}
            onUploaded={addMaterial}
          />

          <UnavailableSection
            title="Тесты"
            description="Появятся, когда научимся генерировать вопросы по загруженному материалу. Пока этой возможности нет ни в интерфейсе, ни в API."
          />

          <UnavailableSection
            title="Результаты"
            description="Появятся после первого пройденного теста: здесь будут оценки, разбор ошибок и прогресс."
          />
        </div>
      </main>
    </div>
  );
}
