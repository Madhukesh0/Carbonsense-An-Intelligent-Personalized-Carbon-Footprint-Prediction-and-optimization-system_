import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("Administrator reports FastAPI page", () => {
  const page = readFileSync(resolve(process.cwd(), "client/src/pages/admin/Reports.tsx"), "utf8");
  const app = readFileSync(resolve(process.cwd(), "client/src/App.tsx"), "utf8");

  it("keeps the queue role-gated and status updates scoped to a report identifier", () => {
    expect(page).toContain('auth.user?.role === "org_admin"');
    expect(page).toContain('"/reports/admin"');
    expect(page).toContain("fastApi.reports.update(id, { status })");
    expect(app).toContain('path="/admin/reports" component={AdminReports}');
  });
});
