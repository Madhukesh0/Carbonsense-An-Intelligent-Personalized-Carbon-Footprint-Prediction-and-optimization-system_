import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const project = process.cwd();
const read = (relative: string) => readFileSync(resolve(project, relative), "utf8");

describe("Additional FastAPI parity routes", () => {
  it("keeps the planning surface to What-if with a completed-result gate", () => {
    const source = read("backend/app/routers/planning.py");
    expect(source).toContain('@router.post("/what-if")');
    expect(source).toContain('@router.get("/latest-completed")');
    expect(source).toContain("Complete an AI prediction and transparent baseline");
    expect(source).toContain("planning comparison, not a verified outcome");
    expect(source).not.toContain('@router.post("/net-zero")');
    expect(source).not.toContain('@router.post("/optimize")');
  });

  it("keeps privacy, history, and assistant data scoped to the authenticated user", () => {
    const privacy = read("backend/app/routers/privacy.py");
    const history = read("backend/app/routers/history.py");
    const assistant = read("backend/app/routers/assistant.py");
    expect(privacy).toContain('"share_aggregates"');
    expect(history).toContain('"user_id": str(user["_id"])');
    expect(assistant).toContain('"user_id": user_id');
    expect(assistant).toContain("your authenticated activity ledger, goals, recommendations, and organization state");
  });
});
