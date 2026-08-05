# PRD 04 — Access & Credits Brokering

- **Owner:** Rachel Green (Governance / Access)
- **Origin:** Kevin Osei's idea in #general, 2026-04-09 ("walk-home thought")
- **Status:** In build (design 2026-04-28); needs-board launch targeted Q3
- **Related:** Access design session 2026-04-28, Issue AUR-9

## Problem

The schools that most need Alaska-specific skills are exactly the ones with **no API credits to
build them**. The no-credits problem is mostly solved *upstream* — Claude for Teachers is free for
verified K-12 educators, and Claude Campus and Claude for Good hand out credits — so this program
should **broker builders, not money**.

## Approach — a three-part broker

1. **Needs board.** A teacher posts what they wish existed ("a tides skill for our estuary unit").
2. **Builder pool.** People with spare credits or skills claim needs.
3. **Fallback credits pool.** Seeded from Claude for Good / Campus grants for needs nobody claims.

## Guardrail (from the 2026-04-28 session)

A need that touches Traditional Knowledge (e.g. "a skill about local plants") could pull a
community's knowledge into a build **without consent**. Such needs are **routed to community
review (James) before they become claimable** — category match plus a human check. The routing
rule must be written down, not merely intended (James's request in-session). See PRD 03.

## Metrics

- Needs posted → needs claimed conversion.
- % of TK-touching needs correctly routed to review (target: 100%).
- Districts participating (2 committed via Kevin; pilot pending).

## Non-goals

- Payments, invoicing, or a credits marketplace. This is matchmaking, not commerce.

## Open questions

- Fallback pool sizing and grant sourcing — **UNKNOWN**.
