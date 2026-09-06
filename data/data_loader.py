"""
Data Loader for CarbonSense
Supports both Synthetic and Real Kaggle datasets with column mapping.
"""

import pandas as pd
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


# ==================== COLUMN MAPPING ====================
# Map real Kaggle column names → your internal feature names
COLUMN_MAPPING = {
    "Body Type": "body_type",
    "Sex": "sex",
    "Diet": "diet",
    "How Often Shower": "how_often_shower",
    "Heating Energy Source": "heating_energy_source",
    "Transport": "transport",
    "Vehicle Type": "vehicle_type",
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
    "Recycling": "recycling",
    "Cooking_With": "cooking_with",
    "CarbonEmission": "carbon_emission_kgco2e_month"
}


def load_real_kaggle_data(file_name: str = "individual_carbon_footprint.csv") -> pd.DataFrame:
    """Load and preprocess the real Kaggle dataset"""
    file_path = RAW_DIR / file_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"Real dataset not found at: {file_path}")
    
    df = pd.read_csv(file_path)
    print(f"Loaded real Kaggle dataset: {df.shape[0]} rows")
    
    # Rename columns to match internal naming
    df = df.rename(columns=COLUMN_MAPPING)
    
    # Keep only the columns we use
    expected_cols = list(COLUMN_MAPPING.values())
    available_cols = [col for col in expected_cols if col in df.columns]
    df = df[available_cols]
    
    print(f"After mapping, dataset has {df.shape[1]} features")
    return df


def get_training_data(use_real_data: bool = False) -> pd.DataFrame:
    """
    Main function to get training data.
    
    Args:
        use_real_data: Set to True after downloading Kaggle dataset
    """
    if use_real_data:
        try:
            return load_real_kaggle_data()
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            print("Falling back to synthetic data...")
            from synthetic_data import generate_synthetic_carbon_data
            return generate_synthetic_carbon_data(2000)
    else:
        from synthetic_data import generate_synthetic_carbon_data
        return generate_synthetic_carbon_data(2000)


if __name__ == "__main__":
    # Test loading real data
    df = get_training_data(use_real_data=True)
    print(df.head())
    print("\nColumns:", df.columns.tolist())