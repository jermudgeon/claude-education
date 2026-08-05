# Ground Truth — Aurora Skills Demo Dataset

This is the human-readable key to the seeded collaboration signals. The machine-readable version
(for scoring) is **`ground_truth.json`**; the computed numbers live in
**`_comparison/before_after.json`** and **`<era>/_metrics/talk_time.json`**.

> **How metrics are computed.** Each transcript is an authored substantive spine wrapped in
> realistic procedural texture (roll call, status rounds, backchannels, Q&A, wrap-up) so meetings
> reach believable length. Every cue is tagged `kind: content` or `kind: texture` in the metadata
> sidecars, and **all metrics below are computed from `content` turns only**, so the signals are
> exact regardless of filler.

## The before → after story (computed)

Same team, two quarters. Q2 has no insights tool; Q3 has it. Every number below is computed by
`generate.py` from the data, not asserted.

| Signal | Before (Q2) | After (Q3) | Direction |
|---|---|---|---|
| Peak dominant talk-time (group mtg) | 66.2% | 40.1% | ↓ better |
| Dana peak talk-time (group mtg) | 66.2% | 35.1% | ↓ better |
| Naomi avg talk-time (group mtg) | 6.3% | 18.9% | ↑ better |
| Naomi "silent-but-present" meetings | 3 | 0 | ↓ better |
| Interruptions (total) | 2 | 0 | ↓ better |
| License conflict — times reopened | 3 | 0 | ↓ better |
| Regression time-to-surface | 4 days | same-day | ↓ better |
| Hallway (post-decision) dissent events | 1 | 0 | ↓ better |
| Changed-mind-in-room events | 1 | 3 | ↑ better |
| Avg psychological safety (1–5) | 3.75 | 4.74 | ↑ better |
| Avg conflict-health (1–5) | 3.68 | 4.65 | ↑ better |

A tool that ingests this dataset should be able to reproduce this table and tell the story:
**the team went from lead-dominated, silence-hiding, and conflict-reopening to balanced,
psychologically safe, and decisive — after adopting the tool.**

## Seeded signals (catalog)

Each signal below has full file+location detail in `ground_truth.json`.

1. **Talk-time dominance** — Dana dominates Q2 group meetings (kickoff 56%, roadmap 66%); drops
   under 40% in Q3 after facilitation nudges + round-robin.
2. **Silent-but-engaged (Naomi)** — attends Q2 meetings, never speaks, yet is the top contributor
   in chat/standups/PRs. A naive airtime metric scores her ~0 and is *wrong*. Resolved in Q3 by a
   format change (round-robin + pre-reads), not by pressuring her. She is talkative in the
   2-person pairing (2026-04-29) — proof the silence was a *format* effect.
3. **Dissent timing** — healthy: Marcus objects *before* the egress decision (arch review,
   ADR-0002). Unhealthy: Mark lodges a license objection in a channel *after* the session (the
   "hallway"), 2026-05-19.
4. **Changed-mind events** — James changes his mind in-room (2026-05-19). Three such events in Q3.
5. **Reopened conflict** — the MIT-vs-CARE license question reopens **3 times** (ADR-0003) before
   being consciously settled 2026-06-23; never reopens in Q3.
6. **Trust / hidden mistake** — Ben hides a disabled capability check for 4 days (PR #41 "small
   fix, nothing major") until an incident. In Q3 he discloses a regression in 41 minutes.
7. **People-matching** — Marcus & Lily build the same provenance schema independently (found by
   luck week 3 in Q2, ADR-0004); the tool flags the same pattern on day 1 in Q3 (#insights).
8. **Similar conversation** — the credits idea is floated in `#general` (2026-04-09) then becomes
   a design meeting (2026-04-28), 19 days apart.
9. **Questions are participation** — James asks far more than he asserts (esp. the community
   advisory, almost all questions). Must not be scored low.
10. **Interruptions / prosody** — turn metadata carries interruption/overlap/latency; 2 seeded
    interruptions in Q2, 0 in Q3.
11. **Psychological-safety trend** — pulse survey dips at the Q2 incident and recovers; Q3 stays
    high.
12. **Two-person meetings** — multiple 1:1s and pair syncs per quarter, a distinct meeting shape.

## Where the non-computed numbers come from

Four comparison signals are **editorial** (not derivable from counts alone) and are set as
constants in `generate.py` → `main()`, grounded in the authored content:

- `license_conflict_reopens` (3 → 0) — see the three TK sessions + ADR-0003.
- `regression_time_to_surface_days` (4 → 0) — PR #41 + incident retro vs the 2026-08-04 disclosure.
- `hallway_dissent_events` (1 → 0) — Mark's post-session channel objection.
- `changed_mind_in_room_events` (1 → 3) — the explicit "changed my mind" moments in transcripts.

Everything else in the table is computed directly from the transcripts and surveys.
