# Assessments — the Q2 → feedback → Q3 loop

These are the in-world outputs of the `team-assess` tool (Five Dysfunctions rubric) run against
each quarter. They are what makes the dataset a **closed loop**, not just a before/after:

```
Q2 data ──assess──▶ report-Q2-2026  ──the team acts on the recommendations──▶ Q3 data
                                                                                 │
Q3 data ──assess──▶ report-Q3-2026 ◀─────────────────────────────────────────── ┘
   (trend vs Q2 shows the recommendations worked)
```

| File | What it is |
|---|---|
| `report-Q2-2026.md` | Human-readable Q2 assessment. Its **Priority Actions** are the feedback the team enacts in Q3. |
| `snapshot-Q2-2026.json` | Machine-readable Q2 snapshot (tool schema). |
| `report-Q3-2026.md` | Q3 assessment with trend vs Q2 — the validation. |
| `snapshot-Q3-2026.json` | Machine-readable Q3 snapshot + `trend_vs` block. |

## Status

- **Scores/confidence are provisional** against rubric **v0.8** and will be re-pinned when the
  refined rubric lands. The `run_date` / `rubric_version` fields mark this.
- **Recommendations are stable** — they follow from Q2's fixed dysfunction signals and the five
  Lencioni dimensions, and are the actual driver of the Q3 content.

## How to reproduce with the real tool

```
team-assess --input ../before-q2-2026 --period Q2-2026
team-assess --input ../after-q3-2026  --period Q3-2026 --compare Q2-2026
```

The tool's output should approximate these files. Where the transcripts are `.vtt`, the tool needs
a WebVTT reader (or point it at a text rendering); see the workflow spec.

## Which Q3 artifacts enact each recommendation

See `../ground_truth.json` → `five_dysfunctions_loop` for the exact file+location mapping of every
Q2 recommendation to the Q3 meetings, PRs, issues, and chat that implement it.
