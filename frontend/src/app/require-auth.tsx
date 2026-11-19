import { Navigate, Outlet } from "react-router";

import { getToken } from "@/lib/token";

/**
 * Защита маршрутов на уровне layout-маршрута: токен читается из локального
 * хранилища, поэтому проверка выполняется на клиенте, до отрисовки страниц.
 */
export function RequireAuth() {
  if (getToken() === null) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
