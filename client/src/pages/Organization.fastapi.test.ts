import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("Organization FastAPI page", () => {
  const page = readFileSync(resolve(process.cwd(), "client/src/pages/Organization.tsx"), "utf8");
  const app = readFileSync(resolve(process.cwd(), "client/src/App.tsx"), "utf8");

  it("uses the role-gated aggregate endpoint and explicitly avoids individual records", () => {
    expect(page).toContain('"/organization/summary"');
    expect(page).toContain('auth.user?.role === "org_admin"');
    expect(page).toContain("never exposes individual records");
    expect(app).toContain('path="/organization" component={Organization}');
  });
});
