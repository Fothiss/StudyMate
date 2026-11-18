"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { setUnauthorizedHandler } from "@/lib/api";
import { clearToken, getToken } from "@/lib/token";

/**
 * Клиентская проверка сессии.
 *
 * Токен лежит в локальном хранилище браузера, поэтому ни сервер, ни middleware
 * его не видят: защита срабатывает после монтирования. Пока проверка не прошла,
 * `authenticated` равно `false` и экран показывает состояние загрузки.
 */
export function useSession() {
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState(false);

  const signOut = useCallback(() => {
    clearToken();
    setAuthenticated(false);
    router.replace("/login");
  }, [router]);

  useEffect(() => {
    setUnauthorizedHandler(signOut);
    return () => setUnauthorizedHandler(null);
  }, [signOut]);

  useEffect(() => {
    if (getToken()) {
      setAuthenticated(true);
      return;
    }
    router.replace("/login");
  }, [router]);

  return { authenticated, signOut };
}
