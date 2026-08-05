# insights: the measurement layer, and the seam it emits

PRD 05 computes the metric contract once; everything else consumes it. This directory is that
computation as code, plus the two artifacts the integration note
(`docs/superpowers/specs/2026-08-04-facilitator-and-scorer-integration.md`) says gate the rest
of the build:

- **Build-order step 1, done independently.** `verify_ground_truth.py` recomputes the
  before/after table from the raw rows on disk (turn metadata, VTT cue timings, pulse.csv) and
  compares it to `_comparison/before_after.json`. The published numbers were written by
  `generate.py`, the same program that wrote the data; this is a second implementation reading
  the files, so agreement checks the files rather than echoing the generator. It also checks
  every VTT against its metadata sidecar cue by cue.
- **Build-order step 3, the seam.** `schema/session_metrics.schema.json` fixes the shape of the
  one-per-meeting `session_metrics` document, and `session_metrics.py` emits real ones from the
  dataset. The PRD 06 facilitator reads it live; team-assess ingests it as evidence. It carries
  computed metrics and attributed quotes, and nothing scored.

## Run

```bash
python3 insights/verify_ground_truth.py
python3 insights/session_metrics.py --era before-q2-2026 --meeting 2026-06-09_roadmap-review
python3 -m unittest discover -s insights/test
```

Standard library only; no dependencies to audit.

## What is and is not verified

Seven of the eleven ground-truth signals are recomputed from raw rows and asserted, per era.
The four editorial signals (license reopens, regression time to surface, hallway dissent,
changed-mind events) are constants in `generate.py`, grounded in authored content but not
derivable from counts; the verifier reports them as not verified and never blends them with
the computed ones (open question 5).

The metrics that need cross-meeting context or a model (dissent timing, changed-mind detection,
reopened conflict) are null in `session_metrics` documents with the reason stated in
`not_computed`, not silently absent.

## Definitions

Shared with `generate.py` and PRD 05, unchanged: the content basis counts `kind: content` turns
only; a group meeting has more than two attendees; present-but-silent means attended with under
3% of content airtime; the talk-time ceiling is 40%. Every document states its `basis`, because
mixing content-only and all-speech numbers silently is the known failure mode.

`test/test_codebook.py` also enforces the rubric rule that `rubric/obm-behavior-codes.json` is
generated from the markdown, never edited directly.
