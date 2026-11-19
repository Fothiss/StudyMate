import { useCallback, useEffect, useState } from "react";

export type Theme = "light" | "dark";

export const THEME_STORAGE_KEY = "studymate.theme";

function hasStoredChoice(): boolean {
  try {
    return localStorage.getItem(THEME_STORAGE_KEY) !== null;
  } catch {
    return false;
  }
}

function readAppliedTheme(): Theme {
  return document.documentElement.classList.contains("dark") ? "dark" : "light";
}

/**
 * Тема живёт в двух местах: класс `dark` на `<html>` выставлен инлайн-скриптом
 * из `index.html` ещё до первого пейнта, а выбор запоминается в `localStorage`.
 * Хук только читает текущее состояние и переключает его.
 */
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(readAppliedTheme);

  const apply = useCallback((next: Theme) => {
    document.documentElement.classList.toggle("dark", next === "dark");
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch {
      // Приватный режим: тема просто не запомнится.
    }
    setTheme(next);
  }, []);

  const toggle = useCallback(() => {
    apply(theme === "dark" ? "light" : "dark");
  }, [apply, theme]);

  // Пока пользователь не выбрал тему сам, следуем системной настройке.
  useEffect(() => {
    if (hasStoredChoice()) {
      return;
    }

    const query = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = () => apply(query.matches ? "dark" : "light");
    query.addEventListener("change", listener);
    return () => query.removeEventListener("change", listener);
  }, [apply]);

  return { theme, toggle };
}
