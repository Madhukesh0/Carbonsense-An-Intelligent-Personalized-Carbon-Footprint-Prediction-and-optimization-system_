"""Frozen CarbonSense model contract — 44-feature clean build (no regional noise)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
import math
import numpy as np

# ── Raw survey inputs that engineer_features() reads ───────────────────
RAW_COLUMNS = [
    "monthly_grocery_bill", "vehicle_monthly_distance_km", "waste_bag_weekly_count",
    "how_long_tv_pc_daily_hour", "how_many_new_clothes_monthly", "how_long_internet_daily_hour",
    "recycle_paper", "recycle_plastic", "recycle_metal", "recycle_glass",
    "cook_stove", "cook_oven", "cook_microwave", "cook_grill", "cook_airfryer",
    "body_type", "sex", "diet", "how_often_shower", "heating_energy_source",
    "transport", "vehicle_type", "social_activity",
    "frequency_of_traveling_by_air", "waste_bag_size", "energy_efficiency",
]

# ── Transformed feature vector (44 features) ───────────────────────────
FEATURE_NAMES = [
    # 6 numeric
    "monthly_grocery_bill", "vehicle_monthly_distance_km", "waste_bag_weekly_count",
    "how_long_tv_pc_daily_hour", "how_many_new_clothes_monthly", "how_long_internet_daily_hour",
    # body_type (reference: normal)
    "body_type_obese", "body_type_overweight", "body_type_underweight",
    # sex (reference: female)
    "sex_male",
    # diet (reference: omnivore)
    "diet_pescatarian", "diet_vegan", "diet_vegetarian",
    # how_often_shower (reference: daily)
    "how_often_shower_often", "how_often_shower_rarely", "how_often_shower_twice a day",
    # heating_energy_source (reference: electricity)
    "heating_energy_source_natural gas", "heating_energy_source_wood",
    # transport (reference: private)
    "transport_public", "transport_walk/bicycle",
    # vehicle_type (reference: diesel)
    "vehicle_type_electric", "vehicle_type_hybrid", "vehicle_type_lpg",
    "vehicle_type_none", "vehicle_type_petrol",
    # social_activity (reference: never)
    "social_activity_often", "social_activity_sometimes",
    # frequency_of_traveling_by_air (reference: never)
    "frequency_of_traveling_by_air_often", "frequency_of_traveling_by_air_rarely",
    "frequency_of_traveling_by_air_very frequently",
    # waste_bag_size (reference: extra large)
    "waste_bag_size_large", "waste_bag_size_medium", "waste_bag_size_small",
    # energy_efficiency (reference: No)
    "energy_efficiency_Sometimes", "energy_efficiency_Yes",
    # recycling binary (4)
    "recycle_glass", "recycle_metal", "recycle_paper", "recycle_plastic",
    # cooking binary (5)
    "cook_airfryer", "cook_grill", "cook_microwave", "cook_oven", "cook_stove",
]

SUPPORTED = {
    "body_type": {"underweight", "normal", "overweight", "obese"},
    "sex": {"male", "female"},
    "diet": {"vegan", "vegetarian", "omnivore", "pescatarian"},
    "how_often_shower": {"rarely", "daily", "often", "twice a day"},
    "heating_energy_source": {"electricity", "natural gas", "wood"},
    "transport": {"private", "public", "walk/bicycle"},
    "vehicle_type": {"none", "petrol", "diesel", "electric", "hybrid", "lpg"},
    "social_activity": {"never", "sometimes", "often"},
    "frequency_of_traveling_by_air": {"never", "rarely", "often", "very frequently"},
    "waste_bag_size": {"small", "medium", "large", "extra large"},
    "energy_efficiency": {"No", "Sometimes", "Yes"},
}

DEFAULTS = {
    "monthly_grocery_bill": 200.0, "vehicle_monthly_distance_km": 300.0,
    "waste_bag_weekly_count": 3, "how_long_tv_pc_daily_hour": 4.0,
    "how_many_new_clothes_monthly": 2, "how_long_internet_daily_hour": 4.0,
    "body_type": "normal", "sex": "female", "diet": "omnivore", "how_often_shower": "daily",
    "heating_energy_source": "electricity", "energy_efficiency": "Sometimes", "transport": "private",
    "vehicle_type": "petrol", "social_activity": "sometimes", "frequency_of_traveling_by_air": "rarely",
    "waste_bag_size": "medium", "recycling": [], "cooking_with": [],
}


def _choice(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key, DEFAULTS[key])
    if value not in SUPPORTED[key]:
        raise ValueError(f"Unsupported {key}={value!r}; supported values: {sorted(SUPPORTED[key])}")
    return str(value)


def _multi(payload: Mapping[str, Any], key: str, allowed: set[str]) -> set[str]:
    value = payload.get(key, [])
    if isinstance(value, str):
        raise ValueError(f"{key} must be a JSON array of values, not a string")
    values = set(value or [])
    invalid = values - allowed
    if invalid:
        raise ValueError(f"Unsupported {key} values: {sorted(invalid)}")
    return values


def engineer_features(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return exactly 26 raw features for the 44-feature transformed contract."""
    out: dict[str, Any] = {}

    # 6 numeric features
    for key in ["monthly_grocery_bill", "vehicle_monthly_distance_km", "waste_bag_weekly_count",
                "how_long_tv_pc_daily_hour", "how_many_new_clothes_monthly", "how_long_internet_daily_hour"]:
        value = float(payload.get(key, DEFAULTS[key]))
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{key} must be a finite non-negative number")
        out[key] = value

    # Recycling binary flags
    recycling = _multi(payload, "recycling", {"paper", "plastic", "metal", "glass", "none"})
    for item in ["paper", "plastic", "metal", "glass"]:
        out[f"recycle_{item}"] = int(item in recycling)

    # Cooking binary flags
    cooking = _multi(payload, "cooking_with", {"stove", "oven", "microwave", "grill", "airfryer", "none"})
    for item in ["stove", "oven", "microwave", "grill", "airfryer"]:
        out[f"cook_{item}"] = int(item in cooking)

    # Categorical features
    for key in ["body_type", "sex", "diet", "how_often_shower", "heating_energy_source",
                "transport", "vehicle_type", "social_activity",
                "frequency_of_traveling_by_air", "waste_bag_size", "energy_efficiency"]:
        out[key] = _choice(payload, key)

    if len(out) != 26 or set(out) != set(RAW_COLUMNS):
        raise AssertionError(f"Feature contract mismatch: got {len(out)} columns, expected 26")
    for key, value in out.items():
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"Non-finite engineered feature: {key}")
    return out


@dataclass
class FinalPreprocessor:
    feature_names: list[str]

    def fit(self, _rows: Any = None) -> "FinalPreprocessor":
        return self

    def transform(self, rows: Any) -> np.ndarray:
        data = rows.to_dict(orient="records") if hasattr(rows, "to_dict") else rows
        matrix = []
        for row in data:
            raw = engineer_features(row)
            # 6 numeric
            vector = [raw[name] for name in RAW_COLUMNS[:6]]
            # body_type (reference: normal)
            vector += [float(raw["body_type"] == value) for value in ["obese", "overweight", "underweight"]]
            # sex (reference: female)
            vector += [float(raw["sex"] == "male")]
            # diet (reference: omnivore)
            vector += [float(raw["diet"] == value) for value in ["pescatarian", "vegan", "vegetarian"]]
            # how_often_shower (reference: daily)
            vector += [float(raw["how_often_shower"] == value) for value in ["often", "rarely", "twice a day"]]
            # heating_energy_source (reference: electricity)
            vector += [float(raw["heating_energy_source"] == value) for value in ["natural gas", "wood"]]
            # transport (reference: private)
            vector += [float(raw["transport"] == value) for value in ["public", "walk/bicycle"]]
            # vehicle_type (reference: diesel)
            vector += [float(raw["vehicle_type"] == value) for value in ["electric", "hybrid", "lpg", "none", "petrol"]]
            # social_activity (reference: never)
            vector += [float(raw["social_activity"] == value) for value in ["often", "sometimes"]]
            # frequency_of_traveling_by_air (reference: never)
            vector += [float(raw["frequency_of_traveling_by_air"] == value) for value in ["often", "rarely", "very frequently"]]
            # waste_bag_size (reference: extra large)
            vector += [float(raw["waste_bag_size"] == value) for value in ["large", "medium", "small"]]
            # energy_efficiency (reference: No)
            vector += [float(raw["energy_efficiency"] == value) for value in ["Sometimes", "Yes"]]
            # recycle binary
            vector += [raw[f"recycle_{item}"] for item in ["glass", "metal", "paper", "plastic"]]
            # cook binary
            vector += [raw[f"cook_{item}"] for item in ["airfryer", "grill", "microwave", "oven", "stove"]]
            matrix.append(vector)
        result = np.asarray(matrix, dtype=float)
        if result.shape[1] != len(self.feature_names) or result.shape[1] != 44:
            raise ValueError(f"Expected 44 transformed features, got {result.shape[1]}")
        return result

    def get_feature_names_out(self) -> np.ndarray:
        return np.asarray(self.feature_names)
