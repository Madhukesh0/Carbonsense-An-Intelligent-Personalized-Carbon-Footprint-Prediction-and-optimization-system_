from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SurveyPayload(BaseModel):
    country: Literal["india", "us", "uk"] = "india"
    household_size: int = Field(default=2, ge=1, le=10)
    age: int = Field(ge=18, le=80)
    sex: Literal["male", "female"]
    body_type: Literal["underweight", "normal", "overweight", "obese"]
    diet: Literal["vegan", "vegetarian", "omnivore", "pescatarian"]
    how_often_shower: Literal["rarely", "daily", "often", "twice a day"]
    heating_energy_source: Literal["electricity", "natural gas", "wood"]
    energy_efficiency: Literal["No", "Sometimes", "Yes"]
    transport: Literal["private", "public", "walk/bicycle"]
    vehicle_type: Literal["none", "petrol", "diesel", "electric", "hybrid", "lpg"]
    vehicle_monthly_distance_km: float = Field(ge=0, le=10_000)
    frequency_of_traveling_by_air: Literal["never", "rarely", "often", "very frequently"]
    region: Literal["mixed", "renewable_heavy"]
    monthly_grocery_bill: float = Field(ge=0, le=5_000)
    how_many_new_clothes_monthly: int = Field(ge=0, le=50)
    waste_bag_size: Literal["small", "medium", "large", "extra large"]
    waste_bag_weekly_count: int = Field(ge=0, le=20)
    how_long_tv_pc_daily_hour: float = Field(ge=0, le=24)
    how_long_internet_daily_hour: float = Field(ge=0, le=24)
    social_activity: Literal["never", "sometimes", "often"]
    recycling: list[Literal["paper", "plastic", "metal", "glass", "none"]] = Field(default_factory=list)
    cooking_with: list[Literal["stove", "oven", "microwave", "grill", "airfryer", "none"]] = Field(default_factory=list)
    currency: str = Field(default="USD", min_length=3, max_length=3)

    @field_validator("recycling", "cooking_with")
    @classmethod
    def remove_duplicates_and_reject_none_mix(cls, value: list[str]) -> list[str]:
        values = list(dict.fromkeys(value))
        if "none" in values and len(values) > 1:
            raise ValueError("none cannot be combined with other selections")
        return values
