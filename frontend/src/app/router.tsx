import { Navigate, Route, Routes } from "react-router";

import { AppShell } from "@/app/shell/app-shell";
import { RequireAuth } from "@/app/require-auth";
import LoginPage from "@/pages/login/page";
import OverviewPage from "@/pages/overview/page";
import PracticePage from "@/pages/practice/page";
import RegisterPage from "@/pages/register/page";

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<RequireAuth />}>
        <Route element={<AppShell />}>
          <Route index element={<OverviewPage />} />
          <Route path="/quiz" element={<PracticePage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
