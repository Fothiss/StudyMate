import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";

import "@fontsource-variable/inter";
import "@fontsource-variable/manrope";
import "@/styles/aurora.css";

import { AppRouter } from "@/app/router";

const container = document.getElementById("root");

if (container === null) {
  throw new Error("Не найден контейнер #root");
}

createRoot(container).render(
  <StrictMode>
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  </StrictMode>,
);
