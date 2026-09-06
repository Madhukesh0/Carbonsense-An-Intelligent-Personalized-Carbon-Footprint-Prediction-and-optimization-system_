"""
CarbonSense — Batch Step 1: Data Preparation
=============================================
Cleans the raw Kaggle dataset and engineers features.
NO regional noise. Saves clean CSV + preprocessed feature matrix.
"""
import sys
sys.stdout.reconfigure(line_buffering=True)

import ast
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "kaggle_carbon_footprint" / "Carbon Emission.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "final_training"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
np.random.seed(SEED)

print("=" * 70)
print("BATCH 1: Data Cleaning & Feature Engineering")
print("=" * 70)

# ── Load raw ──
df = pd.read_csv(RAW_CSV)
print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Nulls: {df.isnull().sum().sum()}")

# ── Rename to snake_case ──
col_map = {
    "Body Type": "body_type", "Sex": "sex", "Diet": "diet",
    "How Often Shower": "how_often_shower",
    "Heating Energy Source": "heating_energy_source",
    "Transport": "transport", "Vehicle Type": "vehicle_type",
    "Social Activity": "social_activity",
    "Monthly Grocery Bill": "monthly_grocery_bill",
    "Frequency of Traveling by Air": "frequency_of_traveling_by_air",
    "Vehicle Monthly Distance Km": "vehicle_monthly_distance_km",
    "Waste Bag Size": "waste_bag_size",
    "Waste Bag Weekly Count": "waste_bag_weekly_count",
    "How Long TV PC Daily Hour": "how_long_tv_pc_daily_hour",
    "How Many New Clothes Monthly": "how_many_new_clothes_monthly",
    "How Long Internet Daily Hour": "how_long_internet_daily_hour",
    "Energy efficiency": "energy_efficiency",
    "Recycling": "recycling", "Cooking_With": "cooking_with",
    "CarbonEmission": "carbon_emission_kgco2e_month",
}
df.rename(columns=col_map, inplace=True)

# ── Map values ──
df["how_often_shower"] = df["how_often_shower"].replace(
    {"less frequently": "rarely", "more frequently": "often"}
)
df["heating_energy_source"] = df["heating_energy_source"].replace({"coal": "electricity"})
df["frequency_of_traveling_by_air"] = df["frequency_of_traveling_by_air"].replace({"frequently": "often"})

# ── Fill vehicle_type nulls ──
null_count = df["vehicle_type"].isnull().sum()
df["vehicle_type"] = df["vehicle_type"].fillna("none")
print(f"Filled {null_count} vehicle_type nulls with 'none'")

# ── Save clean dataset ──
df.to_csv(OUTPUT_DIR / "clean_dataset.csv", index=False)
print(f"Saved: clean_dataset.csv ({df.shape[0]} rows)")

# ── Parse recycling & cooking into binary columns ──
def parse_multi(series, prefix):
    all_items = set()
    parsed = []
    for val in series:
        try:
            items = ast.literal_eval(str(val)) if pd.notna(val) else []
        except (ValueError, SyntaxError):
            items = []
        if isinstance(items, str):
            items = [items]
        parsed.append(set(items))
        all_items.update(items)
    result = {}
    for item in sorted(all_items):
        name = f"{prefix}_{item.lower().replace(' ', '_')}"
        result[name] = [int(item in row) for row in parsed]
    return pd.DataFrame(result)

recycle_df = parse_multi(df["recycling"], "recycle")
cook_df = parse_multi(df["cooking_with"], "cook")

# ── Numeric features ──
numeric_features = [
    "monthly_grocery_bill", "vehicle_monthly_distance_km",
    "waste_bag_weekly_count", "how_long_tv_pc_daily_hour",
    "how_many_new_clothes_monthly", "how_long_internet_daily_hour",
]

# ── Categorical one-hot ──
categorical_features = [
    "body_type", "sex", "diet", "how_often_shower",
    "heating_energy_source", "transport", "vehicle_type",
    "social_activity", "frequency_of_traveling_by_air",
    "waste_bag_size", "energy_efficiency",
]

X_num = df[numeric_features].copy()
X_cat = pd.get_dummies(df[categorical_features], drop_first=True, dtype=int)
X = pd.concat([X_num, X_cat, recycle_df, cook_df], axis=1)
y = df["carbon_emission_kgco2e_month"].copy()

# Ensure numeric
for col in X.columns:
    X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

print(f"Features: {X.shape[1]}")
print(f"Feature list: {list(X.columns)}")

# ── Save full preprocessed matrix ──
preprocessed = X.copy()
preprocessed["target"] = y.values
preprocessed.to_csv(OUTPUT_DIR / "preprocessed_features.csv", index=False)
print(f"Saved: preprocessed_features.csv")

# ── Train/test split ──
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED)

X_train.to_csv(OUTPUT_DIR / "train_X.csv", index=False)
y_train.to_csv(OUTPUT_DIR / "train_y.csv", index=False)
X_test.to_csv(OUTPUT_DIR / "test_X.csv", index=False)
y_test.to_csv(OUTPUT_DIR / "test_y.csv", index=False)

print(f"Train: {X_train.shape[0]} samples")
print(f"Test:  {X_test.shape[0]} samples")
print(f"Saved: train_X.csv, train_y.csv, test_X.csv, test_y.csv")

# ── Save feature names for later use ──
import json
with open(OUTPUT_DIR / "feature_names.json", "w") as f:
    json.dump(list(X.columns), f)
print(f"Saved: feature_names.json")

print()
print("=" * 70)
print("BATCH 1 COMPLETE — Data ready for model training")
print("=" * 70)
