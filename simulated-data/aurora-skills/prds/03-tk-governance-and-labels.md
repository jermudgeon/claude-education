# PRD 03 — Traditional Knowledge Governance & Data Labels

- **Owners:** Sarah Kowalski (Governance), James Ahkivgak (Community liaison)
- **Status:** Ratified 2026-06-23 (see ADR-0003)
- **Related:** TK sessions 2026-04-21 / 05-19 / 06-23, ADR-0003, ADR-0004, Issue AUR-8

## Problem

An MIT or Apache license covers **code**. It does not cover place names, subsistence locations,
or traditional knowledge, and **being open source is not consent from a community** (framed by
Sarah, 2026-04-20). If a subsistence hunting location is published under a permissive license,
the license *permits* anyone to redistribute it, and copyright offers the originating community
little recourse (confirmed by Mark, legal, 2026-04-21). The wrong instrument was chosen by
default the moment the container was built to be permissive (James's day-one question).

## Approach

- **Code:** standard permissive license (low adoption friction — Mark's point).
- **TK-referencing skills:** carry **Local Contexts TK / Biocultural (BC) labels** plus a
  community-authored notice. Labels travel with the data as metadata and encode the community's
  authority even where copyright is silent.
- **Provenance:** every artifact carries `author`, `source_community`, `tk_references[]`
  (typed references to label ids, not free text — Naomi's review note on PR #63). One schema,
  jointly owned with Platform (ADR-0004).
- **Routing:** contributions and access-program needs that touch TK route to **community review**
  (James) before they are publishable/claimable.

## Grounded in CARE

Collective benefit · Authority to control · Responsibility · Ethics. Sarah brings the one-pager
to every governance session; CARE is the decision language for *what belongs in the registry at all*.

## The dependency risk (resolved)

Relying on Local Contexts is an external dependency (Mark's standing objection). **Mitigation
(ratified 2026-06-23):** snapshot label definitions into our own repo so an upstream change can't
silently break governance, and review the dependency annually. See ADR-0003 for the full decision
history — this question reopened three times before it was genuinely settled.

## Open questions

- Which specific communities pilot the labels first — **UNKNOWN** (advisory process ongoing, AUR-10).
