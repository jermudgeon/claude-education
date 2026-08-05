"""Recompute the before/after table from the raw rows and compare it to the published one.

This is build-order step 1 done independently: the numbers in _comparison/before_after.json
were written by generate.py, the same program that wrote the data. Reproducing them from the
files on disk is the accuracy test GROUND_TRUTH.md asks any consumer to pass, and it is what
the integration note says must exist before any scorer's trend output is believed.

Four signals in the published table are editorial constants in generate.py, grounded in
authored content but not derivable from counts. They are reported here as not verified,
never blended with the computed ones (open question 5).

Exit status is 0 only when every computed signal matches and every VTT agrees with its
metadata sidecar.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from metrics import DATA, rollup, vtt_drift

ERA_DIRS = {"before": "before-q2-2026", "after": "after-q3-2026"}

EDITORIAL = (
    "license_conflict_reopens",
    "regression_time_to_surface_days",
    "hallway_dissent_events",
    "changed_mind_in_room_events",
)


def main():
    published = json.loads(
        (DATA / "_comparison" / "before_after.json").read_text(encoding="utf-8")
    )["comparison"]
    failures = []

    for era_key, era_dir in ERA_DIRS.items():
        drift = vtt_drift(era_dir)
        for problem in drift:
            print(f"DRIFT   {problem}")
        failures.extend(drift)

        computed = rollup(era_dir)
        for signal, value in computed.items():
            want = published[era_key][signal]
            status = "ok" if value == want else "MISMATCH"
            print(f"{era_key:<7} {signal:<32} computed {value!s:>7}  published {want!s:>7}  {status}")
            if value != want:
                failures.append(f"{era_key} {signal}: computed {value}, published {want}")

    print()
    for signal in EDITORIAL:
        pair = f"{published['before'][signal]} -> {published['after'][signal]}"
        print(f"editorial {signal:<34} {pair:>12}  set in generate.py, not verified here")

    print()
    if failures:
        print(f"FAILED: {len(failures)} disagreement(s) between the files and the published table")
        sys.exit(1)
    computed_count = len(rollup(ERA_DIRS["before"]))
    print(
        f"OK: {computed_count} signals per era recomputed from raw rows match "
        f"_comparison/before_after.json; every VTT agrees with its sidecar"
    )


if __name__ == "__main__":
    main()
