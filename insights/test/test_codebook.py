"""The committed codebook JSON must be exactly what build_codes.py generates from the markdown.

The rubric spec says editing the JSON directly is a bug; this is what makes it one.
"""

import importlib.util
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

RUBRIC = Path(__file__).resolve().parents[2] / "rubric"

spec = importlib.util.spec_from_file_location("build_codes", RUBRIC / "build_codes.py")
build_codes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_codes)


class Codebook(unittest.TestCase):
    def test_committed_json_matches_the_markdown(self):
        with redirect_stdout(io.StringIO()):
            codes = build_codes.parse(
                (RUBRIC / "obm-behavior-codes.md").read_text(encoding="utf-8")
            )
        committed = json.loads(
            (RUBRIC / "obm-behavior-codes.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(codes), build_codes.EXPECTED)
        self.assertEqual(committed["count"], len(codes))
        self.assertEqual(committed["codes"], codes)

    def test_ids_are_unique(self):
        with redirect_stdout(io.StringIO()):
            codes = build_codes.parse(
                (RUBRIC / "obm-behavior-codes.md").read_text(encoding="utf-8")
            )
        ids = [c["id"] for c in codes]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
