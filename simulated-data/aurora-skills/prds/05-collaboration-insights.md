# PRD 05 — Collaboration Insights ("live /insights for teams")

- **Owner:** Dana Whitfield (Platform), with design constraints from James Ahkivgak
- **Origin:** Retro "How We Work Together", 2026-06-02
- **Status:** Prototype (AUR-11); prototype against *our own* data first
- **Related:** healthy-conflict retro 2026-06-02, retro board `retro-howwework-2026-06-02`

> This is the tool the rest of this dataset exists to exercise. It ingests transcripts, chat,
> PRs, issues, standups, retros, and pulse surveys and reports on *how a team is collaborating* —
> live, not a month later in a retro.

## Problem

Teams discover collaboration problems in retros, long after they mattered. In this team:
Dana talked 70–80% in early meetings; Ben stayed silent about a mistake for four days; Naomi
contributes constantly in chat and never in meetings; the license question reopened three times.
None of this was visible in the moment. **All of it is countable from a transcript and a channel.**

## What it measures (the metric contract)

Each metric names the signal, the source, and the *direction* that is healthy.

| Metric | Source | Healthy direction |
|---|---|---|
| **Talk-time balance** | transcript cue durations | No one holds ≳40% of airtime |
| **Questions vs assertions** | `?` vs `.`/`!` per speaker | More questions is participation, **not** low engagement |
| **Silent-but-engaged** | transcript attendance ∧ chat volume | Flag people who attend silently *yet* contribute elsewhere — don't score them zero |
| **Dissent timing** | objection timestamp vs decision | Dissent **before** the decision (healthy) vs in the hallway after (unhealthy) |
| **Changed-mind events** | "I've changed my mind" + stance shift | ≥1 per contested decision means the round moved |
| **Reopened conflict** | same topic across meetings | Reopening a 3rd time w/o new information = suppressed, not settled |
| **Interruptions / overlap** | overlapping cue timing | Prosody matters; volume/intonation are signal, not noise |
| **Psychological safety trend** | pulse survey per sprint | Dips around incidents should recover after blameless changes |

## Design constraints (non-negotiable — from James, 2026-06-02)

1. **Questions count as participation.** A speaker who asks more than they assert is *not* low-value.
2. **Stay humble.** Report patterns, not verdicts about people. It advises; it does not grade humans.
3. **Silence is not absence.** Cross-reference chat before calling anyone disengaged (see Naomi).

## Mechanism (from the brainstorm's final sketch)

A skill declared in `CLAUDE.md` runs in a subagent on a timer (~every 2 minutes through a
session). On each tick it snapshots the discussion, pushes it to a repo, searches the repo for
**similar prior conversations**, and brings them together — plus a knowledge base of what the
team needs to be successful, and **people-matching** (surfacing that Marcus and Lily were building
the same provenance schema independently).

## Non-goals

- Surveillance or individual performance scoring. This is a team mirror, not a manager's dashboard.
- Real-time intervention beyond a gentle facilitator nudge (see PRD 06).

## Open questions

- Prosody: how much of intonation/volume can be recovered from a text transcript alone? The
  transcript metadata sidecars carry interruption/overlap timing, but true prosody needs audio.
  **UNKNOWN** whether audio ingestion is in scope for the prototype.
