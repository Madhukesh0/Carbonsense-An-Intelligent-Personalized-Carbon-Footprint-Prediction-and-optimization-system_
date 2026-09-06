import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("Privacy FastAPI page", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/Privacy.tsx"), "utf8");
  const appSource = readFileSync(resolve(process.cwd(), "client/src/App.tsx"), "utf8");

  it("uses authenticated FastAPI privacy preferences and keeps aggregate disclosure bounded", () => {
    expect(source).toContain('useFastApiQuery<PrivacyPreferences>(\n    ["fastapi", "privacy"],\n    "/privacy"');
    expect(source).toContain('useFastApiMutation<PrivacyPreferences, PrivacyPreferences>(\n    "/privacy",\n    "PATCH"');
    expect(source).toContain("individual records, names, and member");
    expect(source).toContain('return <RepoAuthPage mode="login" />');
    expect(appSource).toContain('path="/privacy" component={Privacy}');
  });
});
