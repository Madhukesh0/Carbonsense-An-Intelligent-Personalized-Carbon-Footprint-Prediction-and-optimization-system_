# CarbonSense Dataset Freeze Record

**Freeze date:** 31 August 2026  
**Review boundary:** 31 May 2027  
**Status:** Frozen baseline for the current CarbonSense model and application

## Decision

CarbonSense will use the following files as its fixed dataset pair through May 2027:

| Role | Frozen file | Purpose |
|---|---|---|
| Human-readable source | Kaggle `Individual Carbon Footprint Calculation` dataset (10,000 rows) | Auditing, explanation, feature interpretation |
| Machine-learning input | `data/final_training/clean_dataset.csv` | Training and inference using the current 44-feature model contract |

These files are treated as one versioned baseline. The clean dataset is the machine-readable transformation of the Kaggle source; it is not an independent population to append to the source file.

## Verification completed on 31 August 2026

| Check | Result |
|---|---|
| Kaggle source rows | 10,000 |
| Clean dataset rows | 10,000 |
| Model input features | 44 |
| Missing values in either file | 0 |
| Duplicate rows in either file | 0 |
| Target column present | Yes: `carbon_emission_kgco2e_month` |
| Feature names match the frozen model contract | Yes |
| Feature order matches the frozen model contract | Yes |

The current model is tied to the 44 transformed input features and the monthly target represented by these files.

## Change-control rule

No replacement, concatenation, augmentation, relabeling, or feature redesign of the frozen dataset pair should be made before 31 May 2027 unless the project owner explicitly approves a new dataset version. Existing results generated from this frozen baseline must remain reproducible.

If a future dataset change is approved after the review boundary, it must receive a new version identifier, a new data dictionary, a comparison report against this baseline, a retraining record, and updated validation tests.

## Scientific honesty

The dataset and target are synthetic or formula-derived, as documented in `MODEL_RUNTIME_NOTES.md`. CarbonSense should describe current predictions as model estimates for a structured prototype and should not present them as independently validated measurements of real-world personal emissions.
