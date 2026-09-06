# Result-led recommendations

CarbonSense recommendations now follow the same completed-result sequence as What-if and the Reduction Optimizer.

1. A signed-in user completes the AI prediction and transparent baseline with one matching questionnaire profile.
2. The recommendations route finds the newest matching private result pair for that user.
3. It displays the stored AI prediction and transparent baseline as its starting evidence.
4. It selects only approved catalog actions that match the submitted profile and shows an explicit reason and provenance for every action.

## Provenance labels

| Recommendation trigger | Provenance shown |
|---|---|
| Private travel and stored distance | AI profile + transparent transport factor |
| Petrol, diesel, or LPG vehicle | AI profile + transparent transport factor |
| Electricity heating | AI profile + transparent electricity factor |
| Omnivore or pescatarian diet | AI profile + baseline screening proxy |

The labels do not claim that an action will cause the displayed estimate reduction. They explain why the approved action is relevant to the completed profile and whether the supporting lens is the trained-profile input, a compatible transparent factor, or a disclosed screening proxy.

## Verification

At desktop and 390 px mobile widths, the completed user profile rendered starting values of **715 kg AI** and **480 kg baseline**, four relevant approved actions, a provenance label, a “Why shown” explanation, and the existing accept/completion tracking controls. The private-result query and selection helper are covered by result-profile unit tests.
