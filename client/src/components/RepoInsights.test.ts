import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const source = readFileSync(resolve(process.cwd(), "client/src/pages/Insights.tsx"), "utf8");

describe("RepoInsights", () => {
  it("keeps Forecast and History as focused mode-specific panels", () => {
    expect(source).toContain('type InsightMode = "forecast" | "history"');
    expect(source).toContain('initialMode = "forecast"');
    expect(source).toContain('useState<InsightMode>(() => initialMode)');
    expect(source).toContain('setMode("forecast")');
    expect(source).toContain('setMode("history")');
    expect(source).toContain("Your Carbon Insights");
    expect(source).toContain("cs-explore-method-slider cs-workspace-mode-slider");
    expect(source).toContain("cs-workspace-mode-tab");
  });

  it("preserves truthful empty-state and forecast-threshold language", () => {
    expect(source).toContain("Not enough data for forecasting. Run a prediction or baseline first.");
    expect(source).toContain("No history entries yet.");
    expect(source).toContain("requiredCompleteMonths");
    expect(source).toContain("requiredDistinctActivityDays");
    expect(source).toContain("const hasForecastPoints = Boolean(forecast.data?.points?.length);");
  });
});
