import { defineConfig } from "@playwright/test";

const python = process.env.E2E_PYTHON ?? "python";

export default defineConfig({
  testDir: "e2e",
  timeout: 120_000,
  reporter: [["list"], ["json", { outputFile: "e2e-results/results.json" }]],
  outputDir: "e2e-results/artifacts",
  use: {
    baseURL: "http://localhost:3010",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    viewport: { width: 1360, height: 900 },
    launchOptions: process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {},
  },
  webServer: [
    { command: `${python} -m tests.e2e_server`, cwd: "../backend", url: "http://127.0.0.1:8010/health", reuseExistingServer: false, timeout: 60_000 },
    {
      command: "npx next build && npx next start -p 3010",
      env: { NEXT_PUBLIC_API_URL: "http://127.0.0.1:8010", NEXT_PUBLIC_AUTH_MODE: "dev" },
      url: "http://localhost:3010",
      reuseExistingServer: false,
      timeout: 300_000,
    },
  ],
});
