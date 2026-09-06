import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";

const source = fs.readFileSync(path.resolve(process.cwd(), "client/src/components/onboarding/FirstUsePath.tsx"), "utf8");

describe("first-use onboarding path", () => {
  it("uses account-scoped history for estimate and follow-up evidence and routes to existing workflows", () => {
    expect(source).toContain('useFastApiQuery<{ id: string }[]>(["insights", "history"], "/insights/history", isAuthenticated)');
    expect(source).toContain("const { isAuthenticated } = useAuth()");
    expect(source).toContain("const hasEstimate = runs.length > 0");
    expect(source).toContain("const hasFollowUp = runs.length > 1");
    expect(source).toContain("Run an estimate");
    expect(source).toContain("Review a top driver");
    expect(source).toContain("Choose a planning tool");
    expect(source).toContain("Record a follow-up");
    expect(source).toContain("Completion reflects saved estimate history only");
  });
});
