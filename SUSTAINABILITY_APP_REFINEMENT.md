# CarbonSense sustainability-app refinement

CarbonSense will use a **climate-intelligence cockpit** visual language rather than imitate a consumer tracker. The design system uses forest as the primary decision color, mineral blue for evidence and comparison, amber for planning/scenario work, and slate for history. Accent colors now carry explicit semantic roles instead of decorating cards arbitrarily.

The experience emphasizes a visible next climate signal, a single recommended action, a compact signal frame, differentiated instrument/action/evidence surfaces, and an accessible way to find the method boundary. This combines the action momentum and progress patterns observed in AWorld, Commons, and Joro with CarbonSense’s existing evidence, privacy, and estimation safeguards.

The typography continues with Manrope for editorial display hierarchy, DM Sans for task-oriented reading, and DM Mono for contracts, labels, and numeric context. Headings use a sharper weight and tracking relationship, while supporting copy remains spacious and readable.

## Validation

The landing, Explore, Progress, and live XGBoost QA result were reviewed at desktop and mobile widths. The mobile layouts preserve the action panel, signal frame, semantic tool tone, and readable grouped contribution rows without horizontal clipping. The updated repository-interface regression contract passes, TypeScript validation passes, and the production bundle builds successfully. A later full-suite run had only two independent MongoDB Atlas server-selection failures; all 10 non-Atlas test files and 53 assertions passed.

At desktop width, the landing’s three-step workflow and six climate-tool cards retain a scannable grid, while Explore and Progress retain their signal-frame and recommended-next-move hierarchy. At 390 px, the same routes reflow into single-column cards with complete controls and readable copy. The secured QA result preserves the `714 kgCO₂e/month` signal, `688–739` range, `34 → 54` contract, and grouped XGBoost contribution rows at both widths.
