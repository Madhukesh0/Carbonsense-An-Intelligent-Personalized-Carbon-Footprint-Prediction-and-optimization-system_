import unittest
from pathlib import Path


class OrganizationSummariesContractTests(unittest.TestCase):
    def test_aggregate_summary_endpoint_is_role_gated_and_excludes_individual_identity_fields(self):
        source = (Path(__file__).resolve().parents[1] / "app" / "routers" / "organization.py").read_text()
        endpoint = source[source.index('@router.get("/summaries")'):source.index('@router.get("/quests")')]

        self.assertIn('require_roles("org_viewer", "org_admin", "super_admin")', endpoint)
        self.assertIn('{"organization_id": 1, "share_aggregates": 1}', endpoint)
        self.assertIn('"organizationId"', endpoint)
        self.assertIn('"consentingMembers"', endpoint)
        self.assertNotIn('"email"', endpoint)
        self.assertNotIn('"name"', endpoint)


if __name__ == "__main__":
    unittest.main()
