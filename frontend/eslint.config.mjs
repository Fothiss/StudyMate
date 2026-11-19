import { defineConfig, globalIgnores } from "eslint/config";
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

export default defineConfig([
  globalIgnores(["dist/**", "node_modules/**", "*.config.ts", "*.config.mjs"]),
  tseslint.configs.recommended,
  reactHooks.configs.flat.recommended,
]);
