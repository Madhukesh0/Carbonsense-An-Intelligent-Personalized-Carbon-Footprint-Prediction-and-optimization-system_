# Transparent baseline factor research — 2026

## Decision

CarbonSense will use the **UK Department for Energy Security and Net Zero (DESNZ) 2026 conversion-factor release** as the versioned authoritative source for activity inputs that the existing questionnaire can support directly: UK-grid electricity, private-vehicle distance, battery-electric vehicle distance, and a public-transport distance proxy. The release was published on 11 June 2026 and its automatic-processing file was corrected on 31 July 2026.[1]

The source explicitly supports activity-based accounting using values such as electricity in kWh and distance travelled. It also states that spend-based methods are appropriate only when activity data are unavailable and that users should report the method applied.[1] CarbonSense will therefore not pretend that all available lifestyle inputs have equally authoritative conversion factors.

## Selected factor set

| Baseline component | Selected value | Unit | Source mapping | How CarbonSense uses it |
|---|---:|---|---|---|
| Household electricity | 0.13096 | kgCO₂e / kWh | DESNZ 2026, UK electricity | 220 kWh monthly reference activity × factor |
| Petrol average car | 0.16152 | kgCO₂e / km | DESNZ 2026, Passenger vehicles, average car | Private petrol distance |
| Diesel average car | 0.17265 | kgCO₂e / km | DESNZ 2026, Passenger vehicles, average car | Private diesel distance |
| Hybrid average car | 0.12961 | kgCO₂e / km | DESNZ 2026, Passenger vehicles, average car | Private hybrid distance |
| LPG average car | 0.19553 | kgCO₂e / km | DESNZ 2026, Passenger vehicles, average car | Private LPG distance |
| Battery-electric average car | 0.02686 | kgCO₂e / km | DESNZ 2026, UK electricity for EVs, average car | Private electric distance |
| Public-transport proxy | 0.10151 | kgCO₂e / passenger-km | DESNZ 2026, Business travel – land, average local bus | Applied only because the current survey does not distinguish bus, rail, or tram |

## Inputs that cannot be converted with a current official activity factor

| Current survey input | Why a direct current factor is not valid | Transparent treatment |
|---|---|---|
| Air-travel frequency | DESNZ air factors require passenger-km and cabin/distance class, while the form has frequency only | Keep a clearly labelled frequency scenario lookup; do not call it a DESNZ distance factor |
| Diet category and grocery spending | There is no physical food quantity, product mix, or country/currency basis | Keep a clearly labelled screening proxy; do not call it an official activity factor |
| Waste-bag count and bag size | Official waste factors require waste mass and treatment route | Keep a clearly labelled screening proxy; do not call it an official treatment factor |
| New clothing count | Official product factors depend on material, weight, and product type | Keep a clearly labelled screening proxy; do not call it a product footprint |

The baseline will present these boundaries in its assumptions and source information. This approach is more scientifically honest than adding untraceable numerical precision.

## Geographic boundary

The DESNZ factor set is designed for UK operations and activities. CarbonSense currently asks only a broad `mixed` or `renewable_heavy` grid category, not a country or supplier-specific electricity factor. The refreshed baseline will label DESNZ values as a **UK reference factor set**, not a country-specific measurement for every user.

## Implementation verification note

At desktop and 390 px mobile widths, the `/baseline` survey remained readable and retained the four-step interactive contract flow after the factor refresh. The mobile layout preserved the source-answer cards, progress context, contract disclosure, and touch-friendly actions without clipping. The secured `/admin/model-preview` route showed its pre-existing loading-state limitation in this sandbox session rather than rendering its non-persistent result; therefore, the updated result disclosure was verified through typed procedure tests and source-level UI coverage. This limitation does not change the factor calculation or the source-reference payload returned by the baseline procedure.

## References

[1] [Department for Energy Security and Net Zero, *Greenhouse gas reporting: conversion factors 2026*](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026)

[2] [DESNZ, *UK government conversion factors for company reporting of greenhouse gas emissions*](https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)

[3] [U.S. Environmental Protection Agency, *GHG Emission Factors Hub*](https://www.epa.gov/climateleadership/ghg-emission-factors-hub)
