import unittest
from pathlib import Path

from backend.app.services.prediction import run_prediction


class ModelRuntimeContractTests(unittest.TestCase):
    def test_predict_and_baseline_convert_runtime_failures_to_json_service_errors(self):
        source = Path("backend/app/routers/model.py").read_text()
        self.assertIn("HTTP_503_SERVICE_UNAVAILABLE", source)
        self.assertIn("v2.5 prediction runtime is unavailable", source)
        self.assertIn('"/baseline-compute"', source)

    def test_client_reports_non_json_failures_with_status_context(self):
        source = Path("client/src/lib/fastapiClient.ts").read_text()
        self.assertIn("non-JSON response", source)
        self.assertIn("response.text()", source)

    def test_frozen_model_accepts_the_supported_survey_contract(self):
        result = run_prediction({
            "age": 31, "sex": "female", "body_type": "normal", "diet": "omnivore", "how_often_shower": "daily",
            "heating_energy_source": "electricity", "energy_efficiency": "Yes", "transport": "private", "vehicle_type": "petrol",
            "vehicle_monthly_distance_km": 300, "frequency_of_traveling_by_air": "rarely", "region": "mixed", "monthly_grocery_bill": 200,
            "how_many_new_clothes_monthly": 2, "waste_bag_size": "medium", "waste_bag_weekly_count": 3,
            "how_long_tv_pc_daily_hour": 4, "how_long_internet_daily_hour": 4, "social_activity": "sometimes",
            "recycling": ["paper", "plastic"], "cooking_with": ["stove", "oven"], "currency": "USD",
        })
        self.assertEqual(result["runtime"]["transformedFeatureCount"], 44)
        self.assertIsInstance(result["predictedKg"], float)
