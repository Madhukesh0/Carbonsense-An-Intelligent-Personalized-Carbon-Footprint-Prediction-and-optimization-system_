## Cover

# From lifestyle answers to a live XGBoost estimate

### CarbonSense frozen 34 → 54 feature contract

## Slide 1

# 21 user controls become one trained-model input

**A guided form collects practical lifestyle information—not 34 unrelated questions.**

| User input layer | Count | Examples |
|---|---:|---|
| Direct model inputs | 18 | Diet, heating, transport, vehicle distance, grocery spend, digital-use hours |
| Multi-select source controls | 2 | Recycling materials and cooking appliances |
| Survey context | 1 | Age is retained in the form but is not used by this frozen XGBoost artifact |

**The fixed transformation path**

`21 controls` → `34 frozen raw columns` → `54 preprocessed features` → `live XGBoost estimate`

| Transformation step | What happens |
|---|---|
| 34 raw columns | 18 direct values + 11 recycling/cooking flags + 5 deterministic interaction columns |
| 54 model features | Persisted preprocessor preserves numeric/binary values and one-hot encodes categories in training-time order |
| XGBoost result | The trained tree ensemble scores the exact 54-feature vector and returns a prediction plus grouped contributions |

> **Key message:** The user’s 20 model-relevant answers are used directly or deterministically transformed. Only age is context-only in the current frozen model.
