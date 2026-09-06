import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const component = readFileSync(resolve(process.cwd(), "client/src/components/recommendations/OrganizationPanel.tsx"), "utf8");

describe("organization recommendation desk", () => {
  it("provides a role-aware approved-action assignment and member tracker", () => {
    expect(component).toContain('"/recommendations/organization-overview"');
    expect(component).toContain('"/recommendations/assign"');
    expect(component).toContain('"/recommendations/catalog"');
    expect(component).toContain("Self-reported completion");
    expect(component).toContain("Verify");
    expect(component).toContain("org_admin");
    expect(component).toContain("super_admin");
  });
});
