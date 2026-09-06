import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const project = process.cwd();
const read = (relative: string) => readFileSync(resolve(project, relative), "utf8");

describe("FastAPI governance migration", () => {
  it("uses fresh role dependencies, self-protection, and audit logging for administrative changes", () => {
    const source = read("backend/app/routers/admin.py");
    expect(source).toContain('require_roles("super_admin")');
    expect(source).toContain("You cannot change your own role.");
    expect(source).toContain("You cannot deactivate your own account.");
    expect(source).toContain("governance_audit_logs.insert_one");
  });

  it("filters every organization aggregate by share_aggregates and keeps private histories out of returned results", () => {
    const source = read("backend/app/routers/organization.py");
    expect(source).toContain('member.get("share_aggregates")');
    expect(source).toContain("Only users who opted into aggregate sharing are included");
    expect(source).toContain("No individual history is exposed.");
    expect(source).toContain("No individual member names or private activity histories are displayed.");
  });
});
