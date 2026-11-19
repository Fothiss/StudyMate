import { LogOut, TriangleAlert } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Outlet } from "react-router";

import { AuroraField } from "@/components/aurora-field";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { useSession } from "@/hooks/use-session";
import { describeError, fetchMe, type User } from "@/lib/api";
import type { LoadState } from "@/lib/load-state";

import { Brand } from "@/app/shell/brand";
import { NavLinks } from "@/app/shell/nav-links";
import { ProfileContext } from "@/app/shell/profile-context";

/**
 * Оболочка приватной части приложения: сайдбар, профиль и выход.
 * Живёт в layout-маршруте, поэтому при переходах между страницами
 * не размонтируется и профиль не перезапрашивается.
 */
export function AppShell() {
  const { signOut } = useSession();

  const [profile, setProfile] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [attempt, setAttempt] = useState(0);

  const retry = useCallback(() => {
    setState("loading");
    setError(null);
    setAttempt((value) => value + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    fetchMe()
      .then((user) => {
        if (cancelled) return;
        setProfile(user);
        setState("ready");
      })
      .catch((cause: unknown) => {
        if (cancelled) return;
        setProfile(null);
        setError(describeError(cause));
        setState("error");
      });

    return () => {
      cancelled = true;
    };
  }, [attempt]);

  const login = state === "ready" ? (profile?.username ?? null) : null;

  return (
    <ProfileContext.Provider value={profile}>
      <AuroraField />

      <div className="flex min-h-full">
        <aside className="glass sticky top-0 hidden h-dvh w-60 shrink-0 flex-col gap-6 border-r p-4 md:flex">
          <Brand />
          <NavLinks />
          <div className="mt-auto space-y-3">
            <div className="rounded-xl bg-secondary/60 px-3 py-2.5">
              <p className="truncate text-sm font-semibold">{login ?? "…"}</p>
              <p className="text-xs text-muted-foreground">Личный кабинет</p>
            </div>
            <div className="flex items-center gap-1">
              <ThemeToggle />
              <Button
                variant="ghost"
                size="sm"
                className="flex-1 justify-start"
                onClick={signOut}
              >
                <LogOut aria-hidden />
                Выйти
              </Button>
            </div>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="glass sticky top-0 z-10 flex items-center justify-between gap-3 border-b px-4 py-2 md:hidden">
            <Brand compact />
            <div className="flex items-center gap-1">
              <NavLinks orientation="horizontal" />
              <ThemeToggle />
              <Button variant="ghost" size="icon" onClick={signOut} aria-label="Выйти">
                <LogOut aria-hidden />
              </Button>
            </div>
          </header>

          <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 sm:px-8 sm:py-10">
            {state === "error" && (
              <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                <span className="flex items-center gap-2">
                  <TriangleAlert className="size-4" aria-hidden />
                  {error ?? "Не удалось загрузить профиль"}
                </span>
                <Button variant="outline" size="sm" onClick={retry}>
                  Повторить
                </Button>
              </div>
            )}

            <Outlet />
          </main>
        </div>
      </div>
    </ProfileContext.Provider>
  );
}
