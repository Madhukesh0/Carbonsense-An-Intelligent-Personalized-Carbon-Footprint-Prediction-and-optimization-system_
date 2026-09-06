import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("RepoInsights FastAPI migration", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/Insights.tsx"), "utf8");

  it("uses authenticated FastAPI history and forecast queries", () => {
    expect(source).toContain('"/insights/forecast"');
    expect(source).toContain('"/insights/history"');
    expect(source).not.toContain("trpc.timeSeries.forecast");
    expect(source).not.toContain("trpc.history.list");
  });
});
