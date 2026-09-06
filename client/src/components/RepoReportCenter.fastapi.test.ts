import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("RepoReportCenter FastAPI migration", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/Reports.tsx"), "utf8");

  it("uses private FastAPI history, model, health, and report routes", () => {
    expect(source).toContain('"/history"');
    expect(source).toContain('"/model/info"');
    expect(source).toContain('"/health"');
    expect(source).toContain('"/reports/mine"');
    expect(source).not.toContain("trpc.reports");
  });
});
