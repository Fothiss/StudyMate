import { useCallback, useEffect } from "react";
import { useNavigate } from "react-router";

import { setUnauthorizedHandler } from "@/lib/api";
import { clearToken } from "@/lib/token";

/**
 * Клиентская работа с сессией.
 *
 * Токен лежит в локальном хранилище браузера, поэтому ни сервер, ни роутер
 * его не видят: доступ к защищённым маршрутам проверяет `RequireAuth`, а этот
 * хук отвечает за выход и за единую реакцию на `401`.
 */
export function useSession() {
  const navigate = useNavigate();

  const signOut = useCallback(() => {
    clearToken();
    navigate("/login", { replace: true });
  }, [navigate]);

  useEffect(() => {
    setUnauthorizedHandler(signOut);
    return () => setUnauthorizedHandler(null);
  }, [signOut]);

  return { signOut };
}
