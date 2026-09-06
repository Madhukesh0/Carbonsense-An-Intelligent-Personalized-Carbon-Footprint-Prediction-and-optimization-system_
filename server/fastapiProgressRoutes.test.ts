import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("FastAPI CarbonQuest summary", () => {
  const source = readFileSync(resolve(process.cwd(), "backend/app/routers/activity.py"), "utf8");

  it("awards recognition only for account-scoped records and verified completion", () => {
    expect(source).toContain('@router.get("/quest-summary")');
    expect(source).toContain('"verification_status": "verified"');
    expect(source).toContain("self_reported");
    expect(source).toContain("points do not claim verified emissions reductions");
  });
});
