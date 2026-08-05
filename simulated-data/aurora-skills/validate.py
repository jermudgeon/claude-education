"""Validate every VTT against the WebVTT spec and its metadata sidecar.

Exists because malformed timestamps (milliseconds >= 1000, a missing carry in hhmmss)
have now shipped twice. Run standalone or in CI; exits nonzero on the first bad file.

Checks per transcript: every cue matches the strict HH:MM:SS.mmm --> HH:MM:SS.mmm form,
cue count equals the sidecar turn count, and cue timings agree with the sidecar's
start_s/end_s within rounding tolerance.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CUE = re.compile(
    r"^(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)\s*$\n<v ([^>]+)>(.*)$",
    re.MULTILINE,
)
LOOSE = re.compile(r"-->")


def seconds(stamp):
    h, m, s = stamp.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def check(vtt):
    meta_path = vtt.parent / "meta" / (vtt.stem + ".json")
    if not meta_path.exists():
        return [f"no metadata sidecar at {meta_path}"]

    text = vtt.read_text(encoding="utf-8")
    cues = CUE.findall(text)
    arrows = len(LOOSE.findall(text))
    turns = json.loads(meta_path.read_text())["turns"]
    problems = []

    if len(cues) != arrows:
        problems.append(f"{arrows - len(cues)} of {arrows} cues are malformed (spec requires exactly 3 millisecond digits)")
    if len(cues) != len(turns):
        problems.append(f"{len(cues)} parseable cues vs {len(turns)} sidecar turns")

    for i, ((start, end, _, _), turn) in enumerate(zip(cues, turns), start=1):
        for label, stamp, key in (("start", start, "start_s"), ("end", end, "end_s")):
            if abs(seconds(stamp) - turn[key]) > 0.002:
                problems.append(f"cue {i} {label} {stamp} disagrees with sidecar {key}={turn[key]}")

    return problems


def main():
    failures = 0
    vtts = sorted(ROOT.rglob("*.vtt"))
    for vtt in vtts:
        problems = check(vtt)
        if problems:
            failures += 1
            print(f"FAIL {vtt.relative_to(ROOT)}")
            for p in problems[:5]:
                print(f"     {p}")
    print(f"{len(vtts) - failures} of {len(vtts)} transcripts valid")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
