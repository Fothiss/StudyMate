import { Navigate, Route, Routes } from "react-router";

import { AppShell } from "@/app/shell/app-shell";
import { RequireAuth } from "@/app/require-auth";
import LoginPage from "@/pages/login/page";
import OverviewPage from "@/pages/overview/page";
import PracticePage from "@/pages/practice/page";
import RegisterPage from "@/pages/register/page";
import AttemptPage from "@/pages/results/attempt/page";
import ResultsPage from "@/pages/results/page";

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<RequireAuth />}>
        <Route element={<AppShell />}>
          <Route index element={<OverviewPage />} />
          <Route path="/quiz" element={<PracticePage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/results/:attemptId" element={<AttemptPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
