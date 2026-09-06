// The REAL frozen model contract (26 raw columns -> 44 features), matching
// server/model_runtime/app/core/final_contract.py RAW_COLUMNS exactly.
// The old 34-column / 54-feature list described the retired regional XGBoost
// build and has been replaced with the deployed GradientBoosting contract.

// 16 questions are asked: country + household_size (the v2.4 dataset
// columns that scale the grid and per-person attribution), 12 that map to
// model contract columns, and 2 compound selections (recycling, cooking)
// that expand into 9 binary columns. The 5 remaining categorical contract
// columns (sex, body type, shower frequency, social activity,
// energy-efficiency scale) have no defensible emission mechanism and are
// sent at dataset reference values. The retired `region` (grid mix) field
// is still sent (dataset reference) so the frozen payload stays valid.
export const TOTAL_INTERACTIVE_QUESTIONS = 15;
export const DIRECT_MODEL_VALUE_COUNT = 14;
export const DERIVED_MODEL_COLUMN_COUNT = 9;

export const contractColumns = ["monthly_grocery_bill", "vehicle_monthly_distance_km", "waste_bag_weekly_count", "how_long_tv_pc_daily_hour", "how_many_new_clothes_monthly", "how_long_internet_daily_hour", "recycle_paper", "recycle_plastic", "recycle_metal", "recycle_glass", "cook_stove", "cook_oven", "cook_microwave", "cook_grill", "cook_airfryer", "body_type", "sex", "diet", "how_often_shower", "heating_energy_source", "transport", "vehicle_type", "social_activity", "frequency_of_traveling_by_air", "waste_bag_size", "energy_efficiency"] as const;

export const derivedColumns = new Set(["recycle_paper", "recycle_plastic", "recycle_metal", "recycle_glass", "cook_stove", "cook_oven", "cook_microwave", "cook_grill", "cook_airfryer"]);

export const directlyEnteredModelColumns = new Set(["monthly_grocery_bill", "vehicle_monthly_distance_km", "waste_bag_weekly_count", "how_long_tv_pc_daily_hour", "how_many_new_clothes_monthly", "how_long_internet_daily_hour", "body_type", "sex", "diet", "how_often_shower", "heating_energy_source", "transport", "vehicle_type", "social_activity", "frequency_of_traveling_by_air", "waste_bag_size", "energy_efficiency"]);
