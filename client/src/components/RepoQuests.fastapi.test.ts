import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("RepoQuests FastAPI migration", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/Quests.tsx"), "utf8");

  it("uses FastAPI personal and consent-filtered country quest queries", () => {
    expect(source).toContain('"/activity/quest-summary"');
    expect(source).toContain("/organization/quests${");
    expect(source).not.toContain("trpc.parity.quests");
  });
});
