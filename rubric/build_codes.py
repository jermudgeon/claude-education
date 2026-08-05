"""Generate obm-behavior-codes.json from obm-behavior-codes.md.

The markdown file is the single source of truth for Team Insights behavior coding: a `##`
heading opens a dimension, a `###` heading opens a cluster, and every line starting with
`+ ` or `- ` is one code. IDs are assigned as <DIM>-<cluster index>-<valence><sequence>,
so they stay stable while entry text is edited and while clusters gain or lose entries.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "obm-behavior-codes.md"
TARGET = HERE / "obm-behavior-codes.json"
EXPECTED = 120

DIMENSIONS = {
    "TRUST": "TRU",
    "CONFLICT": "CON",
    "COMMITMENT": "COM",
    "ACCOUNTABILITY": "ACC",
    "RESULTS": "RES",
}

ENTRY = re.compile(r"^([+−-])\s+(.*\S)\s*$")


def parse(text):
    """Walk the markdown once, emitting one record per coded behavior."""
    codes = []
    dimension = prefix = cluster = None
    cluster_index = 0
    counters = {}

    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            dimension = line[3:].strip()
            prefix = DIMENSIONS.get(dimension.upper())
            if prefix is None:
                sys.exit(f"line {number}: unknown dimension {dimension!r}")
            cluster_index = 0
            print(f"dimension      {dimension} -> {prefix}")
            continue

        if line.startswith("### "):
            if prefix is None:
                sys.exit(f"line {number}: cluster before any dimension")
            cluster = line[4:].strip()
            cluster_index += 1
            continue

        match = ENTRY.match(line)
        if not match or prefix is None:
            continue

        valence = "positive" if match.group(1) == "+" else "negative"
        key = (prefix, cluster_index, valence)
        counters[key] = counters.get(key, 0) + 1
        code = f"{prefix}-{cluster_index:02d}-{'P' if valence == 'positive' else 'N'}{counters[key]}"
        codes.append(
            {
                "id": code,
                "dimension": dimension.title(),
                "cluster": cluster,
                "valence": valence,
                "behavior": match.group(2),
            }
        )

    return codes


def main():
    codes = parse(SOURCE.read_text(encoding="utf-8"))

    duplicates = {c["id"] for c in codes if sum(1 for d in codes if d["id"] == c["id"]) > 1}
    if duplicates:
        sys.exit(f"duplicate ids: {sorted(duplicates)}")
    if len(codes) != EXPECTED:
        sys.exit(f"parsed {len(codes)} codes, expected {EXPECTED}")

    TARGET.write_text(
        json.dumps(
            {
                "name": "OBM Behavior Coding Reference",
                "version": "1.0",
                "source": "rubric/obm-behavior-codes.md",
                "count": len(codes),
                "codes": codes,
            },
            indent=2,
        )
        + "\n"
    )

    for prefix in DIMENSIONS.values():
        group = [c for c in codes if c["id"].startswith(prefix)]
        positive = sum(1 for c in group if c["valence"] == "positive")
        clusters = len({c["cluster"] for c in group})
        print(f"{prefix:<14} {len(group):>3} codes  {positive} positive  {len(group) - positive} negative  {clusters} clusters")

    print(f"total          {len(codes)} codes")
    print(f"wrote          {TARGET.name} ({TARGET.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
