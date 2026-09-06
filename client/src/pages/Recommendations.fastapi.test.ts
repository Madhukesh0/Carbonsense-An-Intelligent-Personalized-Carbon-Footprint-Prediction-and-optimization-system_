import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("Result-led recommendations migration", () => {
  const page = readFileSync(resolve(process.cwd(), "client/src/pages/Recommendations.tsx"), "utf8");
  const router = readFileSync(resolve(process.cwd(), "backend/app/routers/recommendations.py"), "utf8");
  const app = readFileSync(resolve(process.cwd(), "client/src/App.tsx"), "utf8");

  it("retains the completed-result prerequisite, selectors, and direct FastAPI route", () => {
    expect(router).toContain('@router.get("/result-led")');
    expect(router).toContain("Complete an AI prediction and transparent baseline with the same answers before viewing recommendations.");
    expect(router).toContain("AI profile + transparent transport factor");
    expect(page).toContain('"/recommendations/result-led"');
    expect(page).toContain('"/recommendations/accept", "POST"');
    expect(app).toContain('path="/recommendations" component={Recommendations}');
  });
});
