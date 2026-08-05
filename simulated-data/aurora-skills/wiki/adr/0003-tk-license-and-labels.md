# ADR-0003 — TK licensing: standard code license + Local Contexts labels

- **Status:** Accepted (ratified 2026-06-23)
- **Date:** opened 2026-04-21, revisited 2026-05-19, ratified 2026-06-23
- **Deciders:** Sarah Kowalski, Mark Dupont, James Ahkivgak (+ community advisors)
- **Related:** PRD 03, TK sessions (3), #tk-governance-review

## Context

An MIT/Apache license covers code, not place names, subsistence locations, or Traditional
Knowledge, and open source is not community consent. A permissive license *permits* redistribution
of a subsistence location, and copyright offers little recourse (confirmed by Mark, legal). Mark
countered that a bespoke instrument is an adoption tax and wanted to see concrete harm first.

## Decision

- **Code:** standard permissive license (low friction).
- **TK-referencing skills:** carry **Local Contexts TK / BC labels** plus a community-authored
  notice; labels travel with the data as metadata and encode community authority where copyright
  is silent.
- **Provenance:** typed `tk_references[]` pointing at label ids (not free text) — see ADR-0004.
- **Routing:** TK contributions and TK-touching access needs route through community review.

## Mitigation for the external-dependency risk

Mark's standing objection was the dependency on Local Contexts. Resolved 2026-06-23: **snapshot
the label definitions into our own repo** so an upstream change can't silently break governance,
and **review the dependency annually** (AUR-17).

## Decision history (this is the point)

| Date | Event | Outcome |
|---|---|---|
| 2026-04-21 | Session 1 | Opened. No decision; write up both options. |
| 2026-05-19 | Session 2 | James **changed his mind** in the room → labels. Direction reached. |
| 2026-05-19 (after) | #tk-governance-review | Mark lodged a **late objection in the channel** (the "hallway"). |
| 2026-06-23 | Session 3 | Objection reopened a **third time**; settled for real with the snapshot mitigation. Mark committed. |

This question **reopened three times**. Twice with new information (healthy), once as the same
concern in a new venue (unhealthy — suppressed, not settled). It was consciously closed on
2026-06-23 with a written reopening bar: *new information required, not the same concern restated.*
