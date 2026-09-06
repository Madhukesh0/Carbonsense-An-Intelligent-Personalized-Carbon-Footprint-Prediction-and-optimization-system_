import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const project = process.cwd();
const read = (relative: string) => readFileSync(resolve(project, relative), "utf8");

describe("FastAPI planning and insights migration", () => {
  it("requires a completed result and retains AI/baseline method separation in planning", () => {
    const planning = read("backend/app/routers/planning.py");
    expect(planning).toContain("Complete an AI prediction and transparent baseline");
    expect(planning).toContain("It is a planning comparison, not a verified outcome.");
    expect(planning).toContain('@router.post("/what-if")');
    expect(planning).not.toContain('@router.post("/optimize")');
    expect(planning).not.toContain('@router.post("/net-zero")');
  });

  it("keeps Prophet behind 12 completed months and 90 distinct activity days with a bounded fallback", () => {
    const source = read("backend/app/services/forecasting.py");
    expect(source).toContain("MIN_COMPLETE_MONTHS = 12");
    expect(source).toContain("MIN_ACTIVITY_DAYS = 90");
    expect(source).toContain("uninterrupted completed monthly totals");
    expect(source).toContain("Directional activity-ledger fallback");
    expect(source).toContain("not a verified prediction of future emissions");
  });
});
