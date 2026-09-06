import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

describe("RepoProgress", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/Progress.tsx"), "utf8");

  it("keeps the requested overview, quests, and contributor modes in one accessible progress workspace", () => {
    expect(source).toContain('type ProgressMode = "quests" | "contributors"');
    expect(source).toContain('canViewContributors ? "contributors" : "quests"');
    expect(source).toContain('role="tablist"');
    expect(source).toContain("Quests &amp; badges");
    expect(source).toContain("Contributors");
    expect(source).toContain("CarbonQuest score");
    expect(source).toContain("Day streak");
    expect(source.indexOf('id="progress-quests-panel"')).toBeLessThan(source.indexOf("Make consistent climate participation visible."));
  });

  it("uses secured score and consent-filtered aggregate contracts without creating individual contributor views", () => {
    expect(source).toContain('"/activity/quest-summary"');
    expect(source).toContain("/organization/contributors${");
    expect(source).not.toContain("trpc.quests.summary");
    expect(source).toContain("canViewContributors");
    expect(source).toContain("does not prove real-world emissions reductions");
    expect(source).toContain("Individual histories and member names are never shown.");
    expect(source).toContain("Aggregate contributor map");
    expect(source).toContain("ContributorAggregateMap");
    expect(source).toContain("Zoom and pan to examine country-level aggregate coverage");
  });
});
