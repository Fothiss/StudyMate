import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vitest/config";

/** Тесты проверяют чистые функции, поэтому окружение браузера не нужно. */
export default defineConfig({
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    environment: "node",
    // Потоки вместо форков: тестам не нужен отдельный процесс, а форк-пул
    // не запускается там, где процессам запрещены каналы stdio.
    pool: "threads",
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
