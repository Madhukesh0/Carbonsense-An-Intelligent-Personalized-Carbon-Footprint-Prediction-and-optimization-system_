# Organization-aware recommendations

CarbonSense now presents two deliberately separate recommendation sources to registered users:

| Source | Entry condition | Display label | User action |
|---|---|---|---|
| Profile-matched actions | A completed matching AI prediction and transparent baseline | AI profile + baseline/transparent-factor provenance | Accept a personal recommended action. |
| Organization-assigned actions | An active organization administrator assigns an approved catalog action to an active member | Organization-assigned action | Accept the organization action before it appears in personal action tracking. |

An organization assignment is not automatically converted into an accepted personal action. The member must actively accept it. The query is scoped to the signed-in user and requires that user to have an active organization membership. Administrators can assign only to members of their own organization, except super-administrators with their broader existing permission.

## Verification

At desktop and 390 px mobile widths, the recommendation page showed profile-matched result-led actions, starting AI/baseline values, and a visually distinct **Organization guidance** panel. For a user without organization membership, the panel clearly stated that organization actions are available after joining; it did not expose any other user’s assignment. Unit coverage verifies that only a `suggested` recommendation with an administrator source is eligible for this member-facing panel.
