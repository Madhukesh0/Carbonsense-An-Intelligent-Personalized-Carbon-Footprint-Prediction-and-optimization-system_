import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("RepoProfile FastAPI migration", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/Profile.tsx"), "utf8");

  it("saves through FastAPI and refreshes the native current-user query", () => {
    expect(source).toContain('useFastApiMutation<any, { name: string; country?: string; region?: string }>("/profile", "PATCH", [["fastapi", "auth", "me"]])');
    expect(source).not.toContain("trpc.profile.update");
  });
});
