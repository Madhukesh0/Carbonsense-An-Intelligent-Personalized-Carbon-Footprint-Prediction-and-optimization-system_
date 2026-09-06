import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("reference component alignment", () => {
  const source = resolve(process.cwd(), "client/src/components");

  it("provides reusable reference-style components without individual contributor modules", () => {
    for (const file of ["BackToTop.tsx", "BadgeCard.tsx", "BreakdownDonutChart.tsx", "ContinentsPicker.tsx", "HorizontalBarChart.tsx", "ScoreGauge.tsx", "SectionHub.tsx", "ShapBarChart.tsx", "SkeletonCard.tsx", "StreakCalendar.tsx"]) expect(existsSync(resolve(source, file))).toBe(true);
    expect(existsSync(resolve(source, "ContributorMarker.tsx"))).toBe(false);
    expect(existsSync(resolve(source, "ContributorCard.tsx"))).toBe(false);
  });

  it("uses the new recognition components while retaining evidence-aware disclosure", () => {
    const progress = readFileSync(resolve(process.cwd(), "client/src/pages/Progress.tsx"), "utf8");
    expect(progress).toContain("BadgeCard");
    expect(progress).toContain("ScoreGauge");
    expect(progress).toContain("StreakCalendar");
    expect(progress).toContain("It does not prove real-world emissions reductions.");
  });
});
