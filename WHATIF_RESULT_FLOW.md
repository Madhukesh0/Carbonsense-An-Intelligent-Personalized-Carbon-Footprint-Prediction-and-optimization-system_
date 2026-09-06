# Result-led What-if Simulator

The What-if Simulator now follows the intended CarbonSense sequence:

1. A signed-in user completes the AI prediction and transparent baseline using the same submitted questionnaire profile.
2. CarbonSense stores both result records only under that user’s account.
3. The simulator locates the user’s newest matching prediction-plus-baseline pair and loads its survey answers as the scenario starting point.
4. The user changes selected scenario controls and compares the live XGBoost result against the completed result.

The simulator no longer includes a static demonstration profile. If a matching result pair does not exist, it shows a prerequisite state and routes the user to create an AI prediction and transparent baseline first. It does not expose another user’s history or store credentials in the browser.

## Verification

The pairing helper has unit coverage for matched and unmatched payloads. The interface contract test verifies the completed-result gate, removes the static profile, and asserts the authenticated profile query. At desktop and 390 px mobile widths, a completed user profile rendered the starting **715 kg AI result** and **480 kg baseline**, prefilled the scenario controls, and retained a readable, touch-friendly comparison action.
