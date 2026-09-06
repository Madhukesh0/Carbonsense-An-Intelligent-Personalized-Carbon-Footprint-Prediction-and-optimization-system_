import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("attached React/Vite structure alignment", () => {
  const source = resolve(process.cwd(), "client/src");
  it("provides api, store, utils, nested auth/admin pages, and shared layout/chart modules", () => {
    for (const file of ["api/carbonsense.ts", "store/auth.ts", "utils/baseline.ts", "pages/auth/Login.tsx", "pages/auth/Register.tsx", "pages/admin/Dashboard.tsx", "pages/admin/Users.tsx", "components/layout/AppShell.tsx", "components/layout/NavBar.tsx", "components/charts/WorldMap.tsx", "pages/About.tsx", "pages/Baseline.tsx", "pages/Dashboard.tsx", "pages/Forecast.tsx", "pages/History.tsx", "pages/Predict.tsx", "pages/WhatIf.tsx", "pages/Organization.tsx", "pages/Recommendations.tsx"]) {
      expect(existsSync(resolve(source, file))).toBe(true);
    }
  });
});
