# ADR-0002 — No arbitrary network egress in skill manifests

- **Status:** Accepted
- **Date:** 2026-04-14 (architecture review)
- **Deciders:** Dana Whitfield, Marcus Bell, Tomás Reyes, Priya Nair
- **Related:** PRD 01, manifest schema (PR #24)

## Context

The manifest capability model needed to decide whether skills could declare their own network
egress (to pull live data — tides, weather). Dana proposed allowing it. Marcus objected **in the
meeting, before the decision was made**: if a skill can declare arbitrary egress, a human reviewer
cannot reason about where it phones home at runtime, which breaks the safety promise that is the
entire product (ADR-0001).

## Decision

Capabilities are an **allow-list, deny-by-default**. **Arbitrary network egress is not a
self-declared capability** in v1. Instead, the platform offers **vetted first-party data sources**
(a hosted, audited tides/weather API) as named capabilities. Revisit in v2 if there is demand.

## Consequences

- Classrooms still get live data, via a bounded, auditable set of endpoints.
- Reviewers audit a handful of first-party sources once, not every skill's sockets.
- Naomi's manifest schema dropped `net.egress` from the capability list (PR #24).

## Notes

This is the canonical example of **healthy dissent timing** on this team: the objection arrived
*before* the decision, the proposal changed *in the room*, and Dana recorded the reversal openly.
Contrast ADR-0003, where an objection was first lodged in a channel after a session (the "hallway").
