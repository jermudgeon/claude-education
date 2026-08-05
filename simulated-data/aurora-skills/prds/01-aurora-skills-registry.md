# PRD 01 — Aurora Skills Registry (Core Platform)

- **Owner:** Dana Whitfield (Platform)
- **Status:** In build (alpha shipped 2026-04-23; install flow 2026-05-13)
- **Related:** ADR-0001 (curate not federate), ADR-0002 (no arbitrary egress), ADR-0004 (joint provenance schema), Issues AUR-1..AUR-4

## Problem

Alaska classrooms need AI skills grounded in local context — tides, weather, place-based
science, Native languages — but the general skill ecosystems are a firehose. A February 2026
Snyk audit found 36% of published skills carried a security flaw and 76 confirmed malicious
payloads (see PRD 02 and the 2026-05-04 incident). Distribution is not the differentiator;
skill-sharing is already a git repo. **A small, curated, regional registry with a human review
pass is worth more than a big open one.**

## Goals

- Browse and filter skills by grade band and subject.
- Every skill carries a machine-readable **manifest** declaring its capabilities.
- Capabilities are an **allow-list, deny-by-default** (`fs.read`, `tk.reference`, vetted
  first-party data sources). No arbitrary network egress (ADR-0002).
- Install flow surfaces a **consent screen** that reflects the *enforced* capability set —
  denied capabilities cannot run (not cosmetic). Shipped in PR #77.
- Skills that reference Traditional Knowledge carry provenance + Local Contexts labels
  (PRD 03, ADR-0003).

## Non-goals

- Open federation with external skill ecosystems (rejected — see ADR-0001).
- A payments/marketplace layer. The access program brokers builders, not money (PRD 04).

## Key decisions (traceable)

| Decision | Where it was made | Outcome |
|---|---|---|
| Curate, don't federate | Kickoff 2026-04-07; incident retro 2026-05-05 | ADR-0001 |
| No self-declared egress | Architecture review 2026-04-14 | ADR-0002 |
| One provenance schema, jointly owned | Chat 2026-05-06/07; PR #63 | ADR-0004 |

## Open questions

- Second human reviewer to remove Tomás as a single point of failure (AUR-5, raised in
  standup 2026-05-05). **UNKNOWN:** hiring vs. training an existing team member.
- Beta partner districts: two committed via Kevin (partnerships); a third is **UNKNOWN**.

## Milestones

- ✅ Registry alpha (browse/filter/manifest view) — 2026-04-23
- ✅ Install flow + enforced consent — 2026-05-13
- ⬜ Beta with 3 partner districts — Q3 (see roadmap review 2026-06-09)
