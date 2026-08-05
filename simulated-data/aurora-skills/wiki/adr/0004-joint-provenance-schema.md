# ADR-0004 — One provenance schema, jointly owned

- **Status:** Accepted
- **Date:** 2026-05-15 (merged PR #63)
- **Deciders:** Marcus Bell, Lily Chen, Naomi Kito, Sarah Kowalski
- **Related:** PRD 01, PRD 03, PR #63, Issues AUR-6 / AUR-7

## Context

Marcus (Platform) needed provenance on skill artifacts — author, source community, TK references.
Lily (Governance) independently needed the *same* thing for the data-label model. They were
building it twice, in two schemas, in two repos, and would have collided weeks later. Sarah pulled
them into a 2-person sync (2026-05-07) after spotting the overlap in two channels.

## Decision

**One `provenance` schema, owned jointly.** Fields: `author`, `source_community`,
`tk_references[]`. It lives in the platform repo (next to the manifest); Governance owns the
label-reference semantics. `tk_references[]` is a **typed reference to a Local Contexts label id**,
not free text (Naomi's review note on PR #63; Marcus changed his design in response).

## Consequences

- AUR-7 (Lily's duplicate) was merged into AUR-6 (Marcus's) rather than shipped separately.
- `tk_references[]` was left typed-but-nullable until ADR-0003 provided label ids.

## Notes

This is the canonical **people-matching** case in the dataset: two people doing the same work in
different teams, discovered by a human (Sarah) in Q2 by luck, and later (Q3) surfaced automatically
by the insights tool on day one (see #insights, 2026-07-24). The delta between "found by accident
in week three" and "flagged on day one" is a core before/after signal.
