import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("RepoOrganizationRecommendations FastAPI migration", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/components/recommendations/OrganizationPanel.tsx"), "utf8");

  it("uses FastAPI overview, assignment, and verification routes with string MongoDB user IDs", () => {
    expect(source).toContain('"/recommendations/organization-overview"');
    expect(source).toContain('"/recommendations/assign"');
    expect(source).toContain("user_id: memberId");
    expect(source).not.toContain("trpc.organizationRecommendationPanel");
  });
});
