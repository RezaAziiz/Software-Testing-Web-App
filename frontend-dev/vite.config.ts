/// <reference types="vitest" />
import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/setupTests.ts"],
    globals: true,
    coverage: {
      provider: "v8",
      include: [
        "src/pages/CreateTestCasePage.tsx",
        "src/pages/ExecutionTestCaseFailPage.tsx",
        "src/pages/ExecutionTestCasePassPage.tsx",
        "src/hooks/useAuthGuard.ts",
        "src/components/custom/ModuleWorkspaceLayout.tsx",
        "src/components/custom/FailCard.tsx",
        "src/components/custom/PassCard.tsx",
        "src/components/custom/MinimalCard.tsx",
      ],
    },
  },
})
