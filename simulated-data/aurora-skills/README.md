# Aurora Skills — Collaboration Demo Dataset

Synthetic, internally-consistent demo data for exercising a **live team-collaboration /
insights tool** (the concept from the Team 1 brainstorm: a timed subagent that snapshots a
team's discussions, finds similar past conversations, matches people doing similar work, and
measures collaboration health).

One fictional org — **Aurora Skills**, an Alaska ed-tech collective building a curated registry
of Alaska-related AI skills, a Traditional-Knowledge governance layer, and a no-credits access
program. 12 people, two teams. The dataset spans **two quarters**:

- **`before-q2-2026/`** — Q2 2026, *before* the insights tool. Dysfunction present.
- **`after-q3-2026/`** — Q3 2026, *after* the tool is adopted. Collaboration measurably improved.

The whole point is the **before → after delta** on the same team: it is the story a scoring
rubric can verify. See `_comparison/before_after.json`.

## What's in each quarter

| Source | Format | Path |
|---|---|---|
| Slack export | real export layout (`users.json`, `channels.json`, per-channel per-day JSON, threads, reactions) | `slack-export/` |
| Meeting transcripts | WebVTT with speaker diarization (`<v Name>`) | `transcripts/*.vtt` |
| Transcript turn metadata | per-turn interruptions, overlap, latency, `kind` (content vs texture) | `transcripts/meta/*.json` |
| Pull requests | review threads, changed-mind-in-review, hidden-bug PR | `git/pull_requests.json` |
| Issue tracker | Linear-style issues + assignees | `issues/issues.json` |
| Standups | daily async standup-bot log | `standups/standups.json` |
| Retro boards | sticky notes + votes (the "post-it notes") | `retros/*.json` |
| Pulse survey | per-sprint psychological-safety Likert CSV | `surveys/pulse.csv` |
| Computed metrics | talk-time, question ratio, silent members per meeting | `_metrics/talk_time.json` |

The **after** quarter also has a `#insights` Slack channel containing the tool's own periodic
readouts (`insights-bot`) — the tool's output as data, cross-referencing the before quarter.

Top level also has:

- **`prds/`** — 6 PRDs (registry, security pipeline, TK governance, access, the insights tool
  itself, and the classroom facilitator).
- **`wiki/`** — team directory, glossary, ways-of-working, decision log, and `wiki/adr/` (4 ADRs).
- **`ground_truth.json`** — machine-readable key: every seeded signal, where it lives, and the
  expected detection. For the scoring rubric.
- **`GROUND_TRUTH.md`** — the same, narrated, with the computed before/after table.
- **`_comparison/before_after.json`** — computed before-vs-after metrics.
- **`generate.py`** — regenerates everything (deterministic). `python3 generate.py`.

## The cast (both quarters)

**Registry & Platform:** Dana Whitfield (lead/PM), Marcus Bell (backend), Priya Nair (frontend),
Tomás Reyes (security), Naomi Kito (backend), Ben Larsson (junior).
**Governance & Access:** Sarah Kowalski (governance lead), James Ahkivgak (community/TK), Rachel
Green (access), Kevin Osei (partnerships), Lily Chen (data), Mark Dupont (legal).
Full details in `wiki/team-directory.md`.

## Dataset size

|  | Before (Q2) | After (Q3) |
|---|---|---|
| Meetings (transcripts) | 16 | 7 |
| Slack messages | 34 | 13 |
| Pull requests | 4 | 3 |
| Issues | 12 | 10 |
| Standup entries | 12 | 7 |
| Retro boards | 2 | 1 |
| Survey rows | 72 | 72 |

Meetings run **15–30 minutes** (planning meetings longer), with realistic rhythm — join
logistics, roll call, status rounds, screen-share pauses, Q&A, wrap-up.

## Important: how the transcripts are built

Each transcript has an authored **substantive spine** (the real dialogue that carries the seeded
signals) wrapped in realistic procedural **texture** (roll call, status updates, backchannels,
Q&A, action-item wrap-up) so meetings reach a believable length. Every VTT cue is tagged in the
metadata sidecar as `kind: "content"` or `kind: "texture"`.

**All seeded metrics are computed from `content` turns only.** This keeps every signal exact no
matter how much realistic filler is added. A scorer can reproduce the content-only numbers or
measure over the full transcript, as it prefers (see `ground_truth.json` → `metrics_note`).

## Regenerating

```bash
python3 generate.py
```

Deterministic (fixed seed, no wall-clock reads) — same output every run. To scale volume, add
more `msg(...)` / `transcript(...)` entries or bump the per-meeting duration targets in
`humanize()`. Prose docs (`prds/`, `wiki/`) are static and not touched by the generator.

## Not included (say the word to add)

Calendar/attendance metadata, email/mbox threads, Miro/FigJam board exports.
