import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const source = readFileSync(resolve(process.cwd(), "client/src/lib/fastapiClient.ts"), "utf8");

describe("FastAPI React client foundation", () => {
  it("uses same-origin versioned FastAPI calls with secure cookie credentials and CSRF headers", () => {
    expect(source).toContain("/api/v1");
    expect(source).toContain('credentials: "include"');
    expect(source).toContain('X-CSRF-Token');
  });

  it("covers the migrated auth, model, planning, activity, insight, governance, and report route groups", () => {
    for (const group of ["auth", "model", "planning", "activity", "goals", "insights", "recommendations", "reports", "profile", "admin", "organization"]) {
      expect(source).toContain(`${group}:`);
    }
  });
});
