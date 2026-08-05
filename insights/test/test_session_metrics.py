"""The emitted seam document must carry the contract, justify itself, and stay committed fresh."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import session_metrics

HERE = Path(__file__).resolve().parents[1]
ERA = "before-q2-2026"
MEETING = "2026-06-09_roadmap-review"

CONTRACT = [
    "talk_time_balance",
    "questions_vs_assertions",
    "silent_but_engaged",
    "dissent_timing",
    "changed_mind_events",
    "reopened_conflict",
    "interruptions",
    "psych_safety_trend",
]


class SeamDocument(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = session_metrics.build(ERA, MEETING)

    def test_carries_all_eight_contract_metrics(self):
        self.assertEqual(sorted(self.doc["metrics"].keys()), sorted(CONTRACT))

    def test_every_null_metric_states_its_reason(self):
        for metric, value in self.doc["metrics"].items():
            if value is None:
                self.assertIn(metric, self.doc["not_computed"], metric)

    def test_states_its_basis(self):
        self.assertIn(self.doc["basis"], ("content", "all-speech"))

    def test_dana_breaches_the_threshold_here(self):
        balance = self.doc["metrics"]["talk_time_balance"]
        self.assertTrue(balance["breached"])
        self.assertEqual(balance["dominant"]["handle"], "dana")
        self.assertEqual(balance["dominant"]["talk_pct"], 66.2)

    def test_silent_attendees_carry_the_cross_reference(self):
        flagged = self.doc["metrics"]["silent_but_engaged"]["flagged"]
        naomi = [f for f in flagged if f["handle"] == "naomi"]
        self.assertEqual(len(naomi), 1)
        self.assertGreater(naomi[0]["elsewhere"]["messages"], 0)

    def test_evidence_fields_match_the_schema_shape(self):
        for item in self.doc["evidence"]:
            self.assertEqual(
                sorted(item.keys()),
                sorted(["metric", "quote", "source", "speaker", "timestamp_s", "provoked_by"]),
            )
            self.assertTrue(item["quote"])

    def test_required_top_level_keys_match_the_schema(self):
        schema = json.loads(
            (HERE / "schema" / "session_metrics.schema.json").read_text(encoding="utf-8")
        )
        for key in schema["required"]:
            self.assertIn(key, self.doc, key)

    def test_committed_example_is_regenerable(self):
        example = HERE / "examples" / f"{MEETING}.session_metrics.json"
        committed = json.loads(example.read_text(encoding="utf-8"))
        self.assertEqual(committed, self.doc)


if __name__ == "__main__":
    unittest.main()
