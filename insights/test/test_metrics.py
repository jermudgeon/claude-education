"""The recomputed numbers must match what the dataset publishes, per meeting and per era."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from metrics import DATA, ERAS, elsewhere_counts, measure, meetings, rollup, vtt_drift

ROADMAP = "2026-06-09_roadmap-review"


def roadmap_measure():
    for summary, turns, _ in meetings("before-q2-2026"):
        if summary["id"] == ROADMAP:
            return measure(summary, turns)
    raise AssertionError(f"{ROADMAP} not found")


class MeetingLevel(unittest.TestCase):
    def test_dana_dominates_the_roadmap_review(self):
        m = roadmap_measure()
        self.assertEqual(m["dominant"], "dana")
        self.assertEqual(m["dominant_pct"], 66.2)

    def test_eight_of_twelve_attend_silently(self):
        m = roadmap_measure()
        self.assertEqual(len(m["silent"]), 8)
        self.assertIn("naomi", m["silent"])

    def test_one_seeded_interruption(self):
        m = roadmap_measure()
        self.assertEqual(len(m["interruptions"]), 1)

    def test_recomputed_pct_matches_every_sidecar_summary(self):
        for era in ERAS:
            for summary, turns, _ in meetings(era):
                m = measure(summary, turns)
                for handle, speaker in summary["speakers"].items():
                    self.assertEqual(
                        m["talk_pct"][handle],
                        speaker["talk_pct"],
                        f"{era}/{summary['id']}/{handle}",
                    )


class EraLevel(unittest.TestCase):
    def test_rollups_match_the_published_table(self):
        published = json.loads(
            (DATA / "_comparison" / "before_after.json").read_text(encoding="utf-8")
        )["comparison"]
        for era_key, era_dir in (("before", "before-q2-2026"), ("after", "after-q3-2026")):
            computed = rollup(era_dir)
            for signal, value in computed.items():
                self.assertEqual(
                    value, published[era_key][signal], f"{era_key}/{signal}"
                )

    def test_every_vtt_agrees_with_its_sidecar(self):
        for era in ERAS:
            self.assertEqual(vtt_drift(era), [], era)


class CrossReference(unittest.TestCase):
    def test_naomi_is_silent_in_the_room_and_loud_elsewhere(self):
        counts = elsewhere_counts("before-q2-2026")["naomi"]
        total = counts["messages"] + counts["standups"] + counts["pr_comments"]
        self.assertGreater(total, 0)


if __name__ == "__main__":
    unittest.main()
