import unittest

from backend.app.routers.recommendations import estimate_profile_actions


HIGH_IMPACT_PROFILE = {
    "country": "india",
    "household_size": 1,
    "diet": "omnivore",
    "transport": "private",
    "vehicle_type": "petrol",
    "vehicle_monthly_distance_km": 1200,
    "heating_energy_source": "electricity",
    "frequency_of_traveling_by_air": "very frequently",
    "monthly_grocery_bill": 400,
    "how_many_new_clothes_monthly": 6,
    "waste_bag_size": "large",
    "waste_bag_weekly_count": 5,
}

LOW_IMPACT_PROFILE = {
    "country": "india",
    "household_size": 4,
    "diet": "vegan",
    "transport": "walk/bicycle",
    "vehicle_type": "none",
    "vehicle_monthly_distance_km": 0,
    "heating_energy_source": "wood",
    "frequency_of_traveling_by_air": "never",
    "monthly_grocery_bill": 80,
    "how_many_new_clothes_monthly": 0,
    "waste_bag_size": "small",
    "waste_bag_weekly_count": 0,
}


class EstimateProfileActionsTests(unittest.TestCase):
    def test_high_impact_profile_selects_and_ranks_actions_by_planning_estimate(self):
        actions = estimate_profile_actions(HIGH_IMPACT_PROFILE)
        keys = [action["key"] for action in actions]
        self.assertIn("transit_two_trips", keys)
        self.assertIn("fly_less", keys)
        self.assertIn("buy_less_new_clothing", keys)
        impacts = [action["estimatedReductionKg"] for action in actions]
        self.assertEqual(impacts, sorted(impacts, reverse=True))
        self.assertEqual(actions[0]["key"], "fly_less")
        self.assertGreater(actions[0]["estimatedReductionKg"], 200)

    def test_estimates_recalculate_with_submitted_distance(self):
        double = {**HIGH_IMPACT_PROFILE, "vehicle_monthly_distance_km": 2400}
        base = {a["key"]: a["estimatedReductionKg"] for a in estimate_profile_actions(HIGH_IMPACT_PROFILE)}
        scaled = {a["key"]: a["estimatedReductionKg"] for a in estimate_profile_actions(double)}
        self.assertGreater(scaled["fuel_efficiency"], base["fuel_efficiency"] * 1.9)

    def test_renewable_region_suppresses_cleaner_energy_action(self):
        actions = estimate_profile_actions({**HIGH_IMPACT_PROFILE, "region": "renewable_heavy"})
        self.assertNotIn("cleaner_energy", [a["key"] for a in actions])

    def test_uk_grid_yields_small_cleaner_energy_estimate_than_india(self):
        india = {a["key"]: a["estimatedReductionKg"] for a in estimate_profile_actions(HIGH_IMPACT_PROFILE)}
        uk = {a["key"]: a["estimatedReductionKg"] for a in estimate_profile_actions({**HIGH_IMPACT_PROFILE, "country": "uk"})}
        self.assertGreater(india["cleaner_energy"], uk["cleaner_energy"])

    def test_low_impact_vegan_walking_profile_gets_no_vehicle_or_diet_actions(self):
        actions = estimate_profile_actions(LOW_IMPACT_PROFILE)
        keys = [action["key"] for action in actions]
        self.assertNotIn("transit_two_trips", keys)
        self.assertNotIn("fuel_efficiency", keys)
        self.assertNotIn("lower_impact_meals", keys)
        self.assertNotIn("fly_less", keys)
        self.assertNotIn("buy_less_new_clothing", keys)
        self.assertNotIn("trim_household_waste", keys)

    def test_every_action_carries_trigger_provenance_and_impact_basis(self):
        for action in estimate_profile_actions(HIGH_IMPACT_PROFILE):
            self.assertTrue(action["trigger"])
            self.assertTrue(action["provenance"])
            self.assertTrue(action["impactBasis"])
            self.assertGreaterEqual(action["estimatedReductionKg"], 1.0)


if __name__ == "__main__":
    unittest.main()
