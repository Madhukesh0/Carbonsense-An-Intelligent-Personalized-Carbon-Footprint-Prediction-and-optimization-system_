import { describe, expect, it } from "vitest";
import { isActiveOrganizationAssignment } from "./organizationRecommendations";

describe("organization recommendation assignments", () => {
  it("shows only active administrator-assigned suggestions to current organization members", () => {
    expect(isActiveOrganizationAssignment({ id: 1, assignedByUserId: 4, status: "suggested" }, true)).toBe(true);
    expect(isActiveOrganizationAssignment({ id: 2, assignedByUserId: null, status: "suggested" }, true)).toBe(false);
    expect(isActiveOrganizationAssignment({ id: 3, assignedByUserId: 4, status: "accepted" }, true)).toBe(false);
    expect(isActiveOrganizationAssignment({ id: 4, assignedByUserId: 4, status: "suggested" }, false)).toBe(false);
  });
});
