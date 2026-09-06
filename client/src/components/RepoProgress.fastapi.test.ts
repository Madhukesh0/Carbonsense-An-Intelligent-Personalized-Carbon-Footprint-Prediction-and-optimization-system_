import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("RepoProgress FastAPI migration", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/Progress.tsx"), "utf8");

  it("uses FastAPI personal quest and consent-filtered contributor queries", () => {
    expect(source).toContain('"/activity/quest-summary"');
    expect(source).toContain("/organization/contributors${");
    expect(source).not.toContain("trpc.quests.summary");
    expect(source).not.toContain("trpc.parity.contributors");
  });
});
