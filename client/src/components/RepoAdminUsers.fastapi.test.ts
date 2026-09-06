import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("RepoAdminUsers FastAPI migration", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/admin/Users.tsx"), "utf8");

  it("uses the FastAPI user list and UUID-safe role and active-state mutations", () => {
    expect(source).toContain('"/admin/users"');
    expect(source).toContain("fastApi.admin.updateRole");
    expect(source).toContain("fastApi.admin.updateActive");
    expect(source).not.toContain("trpc.admin");
  });
});
