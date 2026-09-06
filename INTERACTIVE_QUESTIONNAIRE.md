# Interactive frozen-model questionnaire

CarbonSense now presents every user-entered part of the frozen prediction payload as a four-step interactive questionnaire. It contains **21 answer controls**: 18 direct model values, two multi-select source controls that generate recycling and cooking flags, and one age field retained as survey context. All number inputs expose their permitted range and unit; categorical options are explicit selectable controls; and multi-select choices include the contract-supported `none` option.

The page deliberately distinguishes this from the **34-column raw model contract**. Sixteen of those contract columns are deterministically engineered from the user’s interactive source answers and are not editable. The page labels them as calculated in the contract view to prevent users from accidentally breaking the frozen 34 → 54 preprocessing path.

## Verification

On 20 August 2026, `/predict` was reviewed at 1280 px and 390 px widths in an authenticated preview. The desktop layout presented each first-step question in readable cards; the mobile layout converted them to a single, touch-friendly stack without clipping, while preserving the section progress, exact-contract disclosure, labels, descriptions, selection states, and continue control. TypeScript validation and the focused interface suite passed after the change.
