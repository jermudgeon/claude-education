# ADR-0001 — Curate, don't federate

- **Status:** Accepted
- **Date:** 2026-04-07 (kickoff), reinforced 2026-05-05 (incident retro)
- **Deciders:** Dana Whitfield, Tomás Reyes, Sarah Kowalski
- **Related:** PRD 01, PRD 02, incident 2026-05-04

## Context

Skill sharing is already solved — a marketplace is just a git repo, and large public registries
already exist (1,000+ skills catalogued). Distribution is not our differentiator. Meanwhile a
February 2026 Snyk audit found **36% of published skills carried a security flaw** and **76
confirmed malicious payloads**; Tomás later reproduced one that exfiltrates env vars on install.

## Decision

Aurora Skills is a **small, curated, regional registry with a human review pass**. We do **not**
openly federate with external skill ecosystems. Alaska-specific content plus a review pass is the
value; a big firehose is a liability, both security-wise and culturally.

## Consequences

- The **review pipeline is the product** (PRD 02), not a nice-to-have.
- Reviewer capacity becomes a first-order constraint (AUR-5, AUR-16).
- We forgo the network-effects of open federation in exchange for a safety and consent guarantee.

## Notes

This decision was made quickly at kickoff and *validated by evidence* three weeks later when the
external threat and an internal validator regression landed in the same week. The premise held up.
