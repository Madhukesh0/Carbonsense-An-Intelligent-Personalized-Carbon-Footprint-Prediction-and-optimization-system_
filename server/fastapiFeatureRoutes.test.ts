import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const project = process.cwd();
const read = (relative: string) => readFileSync(resolve(project, relative), "utf8");

describe("FastAPI feature route migration", () => {
  it("keeps activity, goals, and progress private to the authenticated MongoDB user", () => {
    const activity = read("backend/app/routers/activity.py");
    const goals = read("backend/app/routers/goals.py");
    const progress = read("backend/app/services/progress.py");
    expect(activity).toContain('"user_id": str(user["_id"])');
    expect(activity).toContain("calculate_progress");
    expect(progress).toContain("not a verified emissions measurement");
    expect(goals).toContain("Your target must be below your baseline.");
  });

  it("retains recommendation self-report labels, administrator verification, and audit trails", () => {
    const source = read("backend/app/routers/recommendations.py");
    expect(source).toContain('"verification_status": "self_reported"');
    expect(source).toContain('"verification_status": "verified"');
    expect(source).toContain("governance_audit_logs.insert_one");
    expect(source).toContain("No emissions outcome is claimed");
  });

  it("keeps report administration organization-scoped and registers all ported routers", () => {
    const reports = read("backend/app/routers/reports.py");
    const main = read("backend/app/main.py");
    expect(reports).toContain('"organization_id": user.get("organization_id")');
    expect(reports).toContain("You can only update reports in your organization.");
    for (const router of ["activity", "goals", "recommendations", "reports"]) {
      expect(main).toContain(`app.include_router(${router}.router`);
    }
  });
});
