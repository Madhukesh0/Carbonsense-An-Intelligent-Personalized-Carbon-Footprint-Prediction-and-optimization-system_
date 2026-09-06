import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("Goals FastAPI page", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/Goals.tsx"), "utf8");
  const appSource = readFileSync(resolve(process.cwd(), "client/src/App.tsx"), "utf8");

  it("uses the authenticated goals endpoint with the retained 90-day target behavior", () => {
    expect(source).toContain('useFastApiQuery<Goal[]>(["fastapi", "goals"], "/goals", auth.isAuthenticated)');
    expect(source).toContain('useFastApiMutation<{ success: boolean }, GoalInput>("/goals", "POST"');
    expect(source).toContain("90 * 24 * 60 * 60 * 1000");
    expect(source).toContain('return <RepoAuthPage mode="login" />');
    expect(appSource).toContain('path="/goals" component={Goals}');
  });
});
