export type OrganizationAssignment = {
  id: number;
  assignedByUserId: number | null;
  status: "suggested" | "accepted" | "completed" | "dismissed";
};

export function isActiveOrganizationAssignment(
  row: OrganizationAssignment,
  hasOrganization: boolean,
) {
  return hasOrganization && row.assignedByUserId !== null && row.status === "suggested";
}
