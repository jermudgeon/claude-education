# Glossary — Aurora Skills

**Andon cord.** From Toyota's lean manufacturing: any worker on the line can pull a cord to stop
production when something is wrong. It only works if pulling it is *safe*. We use it as shorthand
for surfacing a mistake or risk early. See ways-of-working.md.

**CARE Principles.** Indigenous data governance framework: **C**ollective benefit, **A**uthority to
control, **R**esponsibility, **E**thics. Our decision language for *what belongs in the registry at
all*. Complements FAIR (which is about data mechanics, not authority).

**Capability.** A permission a skill declares in its manifest (`fs.read`, `tk.reference`, a vetted
data source). Allow-list, deny-by-default (ADR-0002).

**Confidently wrong.** An AI failure mode the team names repeatedly: fluent, plausible output that
is incorrect. A core risk the collaboration tools (PRD 05/06) must not reproduce.

**Local Contexts / TK & BC Labels.** An external framework of Traditional Knowledge (TK) and
Biocultural (BC) labels that travel with data as metadata and encode a community's terms even where
copyright is silent. Adopted in ADR-0003; snapshotted locally to manage the dependency risk.

**Manifest.** The machine-readable declaration accompanying each skill: capabilities, data sources,
provenance. Schema owned by Naomi (PR #24) + joint provenance (ADR-0004).

**Provenance.** `author`, `source_community`, `tk_references[]` on every artifact. One schema,
jointly owned by Platform and Governance (ADR-0004).

**Traditional Knowledge (TK).** Knowledge held by a community — place names, subsistence locations,
stories. Not covered by code licenses; governed via ADR-0003.

**Silent-but-engaged.** A person who is quiet in meetings yet contributes heavily elsewhere (chat,
PRs). Naomi is the canonical case. A metric that counts only meeting airtime scores them wrongly at
zero — a design constraint on PRD 05.
