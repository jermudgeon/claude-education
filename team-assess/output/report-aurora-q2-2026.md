# Team Health Assessment — aurora-q2-2026
Overall Health: 3.44 / 5

## Dimension Scores

Conflict         ███░░  3.0
Accountability   ███░░  3.2
Trust            ███░░  3.4
Commitment       ████░  3.6
Results          ████░  4.0

## Priority Actions

1. Address decision closure and buy-in discipline: adopt a standing meeting-close ritual where the facilitator restates the decision, names owner and date, and asks each attendee (by name) whether they can commit. The license question reopening three times and Mark's post-meeting dissent (5-19) are the flagship symptoms; closing the loop in-room will prevent hallway relitigation.
2. Break Dana's talk-time dominance and the withdrawal pattern it produces. Dana averaged 56–78% of airtime in meetings she led, with 6–8 attendees silent; Naomi named this explicitly ('invisible if you only count the room'). Rotate facilitation, cap lead talk-time to <30%, and adopt round-robin or written-first formats so Naomi, Ben, Priya, Tomás, Lily and Mark contribute in the room, not only in chat.
3. Institutionalize peer-to-peer accountability in the moment rather than saving it for retros. Sarah's direct message to Mark (5-19) and Naomi's to Ben (5-04) are the model; feedback about Dana's dominance, by contrast, only surfaced upward through pulse surveys and retros. Set a norm that concerns are raised directly to the person within one working day, with retros for patterns not first mentions.
4. Tighten review standards for security-critical code and set explicit 'definition of done' up front. Ben's PR #41 shipped with 'small fix, nothing major' and 'lgtm, ship it' — no acceptance criteria examined, capability check disabled, four-day silence followed. Require named test evidence and a second reviewer for any change touching the capability system, and state acceptance criteria before work starts.
5. Preserve and codify what is working: cross-team dedup (Marcus/Lily provenance schema), blameless incident handling (Ben's disclosure + Marcus's 'thank you for pulling the cord'), and converting failures into named process changes (AUR-12 template, regression test in PR #77). Make these explicit team norms in an onboarding doc so they survive new joiners and don't depend on individual heroics.

## Evidence Highlights

### Conflict
- "Marcus surfaced dissent pre-arch-review in #registry-platform 2026-04-13: 'I think we should NOT let skills declare arbitrary network egress... Want to argue this before we lock the schema.'"
- "Sarah surfaced TK/licensing tension day one in #governance-access 2026-04-20: 'Being open source is not the same as having consent from a community.'"
- "Mark did NOT surface his license objection in the 2026-05-19 session — took it to channel after. James in #tk-governance-review 2026-05-20: 'This is the third time the license question has come back.'"
- "Kickoff had 6 present-but-silent members including Priya, Tomás, Naomi, Ben, Lily, Mark — dissent not invited from most attendees"

### Accountability
- "Naomi to Ben in #registry-platform 2026-05-04: '@ben which validation path did that touch? The install smoke test started failing over the weekend.' — direct, specific, to the person"
- "Sarah to Mark 2026-05-19: 'Can you bring the objection to the group on the 23rd rather than the channel?' — peer holding peer to standard"
- "James to Mark in #tk-governance-review 2026-05-20: 'Is there new information, or are we relitigating?' — direct challenge on process"
- "But: took 4 days for validator regression to surface; Sarah retro item votes=6 'Dana talks ~80% of the time... hard to disagree' raised upward via retro, not peer-to-peer to Dana in the moment"

### Trust
- "Ben in #incidents 2026-05-04: 'I need to say something. That validator fix I pushed on the 30th and called "nothing major" — it disabled a capability check... I was embarrassed and hoped I'd quietly fix it. I'm sorry.'"
- "Ben in retro: 'It took me 4 days to admit the validator fix broke something.' — vulnerability arrived, but only after 4 days of silence"
- "Naomi in retro: 'I say everything in chat, nothing in meetings — invisible if you only count the room.' — safety in writing but not in the room"
- "Pulse survey S2 Ben psych_safety=2, S3 Ben=2, Naomi consistently 3 — safety uneven, concentrated on governance side"

### Commitment
- "Dana at kickoff: 'Two tracks: Registry & Platform (me, Marcus, Priya, Tomás, Naomi, Ben) and Governance & Access (Sarah, James, Rachel, Kevin, Lily, Mark)' — clear roles and owners"
- "Issue tracker AUR-1 through AUR-12 all have named assignees and priorities (P0/P1/P2)"
- "AUR-2 'Decide capability model' resolved explicitly at arch review 2026-04-14 with named decision: 'no arbitrary egress, vetted first-party sources'"
- "AUR-6/AUR-7 merged as joint ownership after Sarah stated: 'This should be one schema, owned jointly.'"

### Results
- "Marcus/Lily merged parallel work into joint schema (AUR-6/AUR-7) instead of shipping duplicates for own-team credit"
- "Sarah: 'This should be one schema, owned jointly. Let's not build it twice.'"
- "James refers to shared customer stake: 'Who do the people in that place call?'"
- "Dana's talk-time dominance (56-78% in her meetings) is the main countervailing signal — argues from position/leader-role rather than shared metric"

## Facet Detail

### Conflict (3.0)
  surfacing_disagreement  ███░░  3.0  (high confidence)
    - "Marcus surfaced dissent pre-arch-review in #registry-platform 2026-04-13: 'I think we should NOT let skills declare arbitrary network egress... Want to argue this before we lock the schema.'"
    - "Sarah surfaced TK/licensing tension day one in #governance-access 2026-04-20: 'Being open source is not the same as having consent from a community.'"
    - "Mark did NOT surface his license objection in the 2026-05-19 session — took it to channel after. James in #tk-governance-review 2026-05-20: 'This is the third time the license question has come back.'"
    - "Kickoff had 6 present-but-silent members including Priya, Tomás, Naomi, Ben, Lily, Mark — dissent not invited from most attendees"
  quality_of_debate  ████░  4.0  (high confidence)
    - "Marcus arch-review PR #24 review: 'Exactly right. The deny-by-default posture is what makes review tractable.' — reasoned proposal linked to stated principle"
    - "James in #governance-access: 'Mark, the harm is the point I raised on day one. If a subsistence hunting location ends up in a public repo under MIT, the license permits anyone to redistribute it.' — concrete factual harm"
    - "Mark: 'a bespoke license is a maintenance and adoption tax. Every non-standard term is a reason a contributor walks. I want to see the specific harm before we invent a new instrument.' — reasoned, not personal"
    - "TK session 2 transcript shows Sarah, Mark, James in genuine back-and-forth (James 43.6%, Mark 24.1%, Sarah 32.4%)"
  tension_management_repair  ███░░  3.0  (medium confidence)
    - "Sarah's message to Mark 2026-05-19 was firm and direct but supportive — did not attack the person, named the process problem ('Deciding in the hallway is how this reopens forever')"
    - "Marcus: 'Ben — thank you for pulling the cord.' — supported Ben while diagnosing the failure"
    - "No observed explicit apology-with-named-act; Ben's #incidents post ('I'm sorry') is the closest and it worked"
    - "Retro 2026-06-02 named tension explicitly with james vote=6 'The license question has reopened 3 times' — repair via retro rather than in-moment"
  destructive_conflict_aggression  ████░  4.0  (high confidence)
    - "Only 2 interruptions across all 17 meetings (kickoff, roadmap review — both by Dana)"
    - "No demeaning remarks, no reprimands in front of the group observed in any transcript or Slack thread"
    - "Dana's interruption of Rachel in roadmap review is a clear signal but singular"
    - "Pulse S2 psych_safety scores for Ben and Naomi (2, 3) suggest felt aggression is low but dominance-based silencing exists"
  destructive_conflict_withdrawal_incivility  ██░░░  2.0  (high confidence)
    - "Kickoff: 6 attendees silent (Priya, Tomás, Naomi, Ben, Lily, Mark); roadmap review: 8 attendees silent; healthy-conflict retro: 6 silent"
    - "Naomi retro item votes=8: 'I say everything in chat, nothing in meetings — invisible if you only count the room.' — explicit withdrawal pattern"
    - "Ben went silent for 4 days on validator regression until Naomi asked him directly"
    - "Mark's post-hoc dissent in channel after the room is a withdrawal-then-relitigate pattern"
  resolution_closure  ██░░░  2.0  (high confidence)
    - "James in retro went_poorly (votes=6): 'The license question has reopened 3 times.'"
    - "James in #tk-governance-review 2026-05-20: 'I don't mind reopening if there's new information. Is there new information, or are we relitigating?'"
    - "TK Session 2 on 5-19 did not close the license question — required a separate ratification meeting on 6-23"
    - "Kickoff transcript ends with Dana monologue for the last 6 turns; no explicit decision restated"

### Accountability (3.2)
  peer_to_peer_accountability  ███░░  3.0  (high confidence)
    - "Naomi to Ben in #registry-platform 2026-05-04: '@ben which validation path did that touch? The install smoke test started failing over the weekend.' — direct, specific, to the person"
    - "Sarah to Mark 2026-05-19: 'Can you bring the objection to the group on the 23rd rather than the channel?' — peer holding peer to standard"
    - "James to Mark in #tk-governance-review 2026-05-20: 'Is there new information, or are we relitigating?' — direct challenge on process"
    - "But: took 4 days for validator regression to surface; Sarah retro item votes=6 'Dana talks ~80% of the time... hard to disagree' raised upward via retro, not peer-to-peer to Dana in the moment"
  expectation_setting_antecedents  ███░░  3.0  (medium confidence)
    - "Naomi PR #24 states standard in advance: 'Anything not listed is denied. I'd rather over-restrict now and loosen later.'"
    - "Tomas post-incident added regression test as an explicit standard: 'fails loudly if the capability check is ever disabled again'"
    - "Ben's #41 body was 'small fix, nothing major' and Dana approved with 'lgtm, ship it' — no 'done' criteria set for a change to security-critical code"
    - "AUR issues have assignees and priorities but few state explicit acceptance criteria"
  performance_monitoring  ███░░  3.0  (medium confidence)
    - "Standups exist and are used consistently (see 04-15, 05-01, 05-05, 05-08, 06-03)"
    - "Naomi caught #41 regression via smoke test — automated monitoring worked"
    - "Tomas 2026-05-04 audit of ecosystems ('Auditing the public skill-share ecosystems') is proactive evidence-seeking"
    - "Ben's fix approved without examining actual work product ('lgtm, ship it'); regression only caught 4 days later when it broke prod"
  consequences_feedback_delivery  ███░░  3.0  (medium confidence)
    - "Marcus to Ben in #incidents same-day: 'Ben — thank you for pulling the cord. That's the behavior we want, not the bug.' — specific positive feedback tied to specific act"
    - "Sarah to Mark same-week: named specific act ('deciding in the hallway')"
    - "Retro 2026-06-02 delivered feedback about Dana's dominance and Naomi's silence — but only monthly, in retrospect, not in the moment"
    - "Sarah S3 pulse notes: 'Dana talks ~80% of the time in meetings; hard to disagree.' — this feedback appears in retro not directly to Dana"
  ownership_vs_blame_shifting  ████░  4.0  (high confidence)
    - "Ben #incidents: 'That validator fix I pushed on the 30th and called nothing major — it disabled a capability check to make a test pass... I'm sorry.' — plain ownership, no counter-accusation"
    - "Marcus PR #63 review: 'Good catch Naomi — changed my mind on the free-text approach... Updated.' — ownership of change of mind"
    - "Tomas: 'I'm a single point of failure on security review' — ownership of a systemic gap"
    - "Retro items are largely 'I' statements (mark, james, naomi own their own patterns) rather than finger-pointing"

### Trust (3.4)
  vulnerability_psychological_safety  ███░░  3.0  (high confidence)
    - "Ben in #incidents 2026-05-04: 'I need to say something. That validator fix I pushed on the 30th and called "nothing major" — it disabled a capability check... I was embarrassed and hoped I'd quietly fix it. I'm sorry.'"
    - "Ben in retro: 'It took me 4 days to admit the validator fix broke something.' — vulnerability arrived, but only after 4 days of silence"
    - "Naomi in retro: 'I say everything in chat, nothing in meetings — invisible if you only count the room.' — safety in writing but not in the room"
    - "Pulse survey S2 Ben psych_safety=2, S3 Ben=2, Naomi consistently 3 — safety uneven, concentrated on governance side"
  contractual_trust_reliability_of_character  ████░  4.0  (high confidence)
    - "Naomi followed through on manifest schema v0 (PR #24) on committed date; standups show consistent 'yesterday/today' delivery"
    - "Marcus renegotiated position on PR #63 openly: 'Good catch Naomi — changed my mind on the free-text approach, now it's a typed label reference. Updated.'"
    - "Tomas: 'Added a regression test that fails loudly if the capability check is ever disabled again' — reliable follow-through post-incident"
    - "AUR-2 P0 decision completed on time; AUR-12 blameless template shipped 3 days after retro commitment"
  communication_trust_disclosure  ███░░  3.0  (high confidence)
    - "Sarah in tk-governance-review 2026-05-19: 'Mark — I'd much rather have heard this while we were all in the room... Deciding in the hallway is how this reopens forever.' — direct feedback to a person's face"
    - "Mark lodged license objection in channel AFTER the meeting rather than in the room (retro item, votes=5)"
    - "Naomi's comment on PR #41 4 days late: 'This is the change that disabled the capability check... Flagging for the incident retro — not to pile on Ben, who surfaced it himself.'"
    - "Ben's standup blocker 2026-04-15: 'not sure I understand the capability model fully' — willing to state what he doesn't know"
  competence_trust_capability  ████░  4.0  (high confidence)
    - "Marcus deferred to Naomi's expertise on PR #63: 'Good catch Naomi — changed my mind on the free-text approach'"
    - "Sarah sought James's input at kickoff on TK questions; James: 'whose knowledge is this registry going to hold, and who decided it could?'"
    - "Lily/Marcus co-owned provenance schema after realizing duplication — mutual deference across teams"
    - "Dana approved Ben's #41 with just 'lgtm, ship it' — insufficient review of a junior's change to security-critical code (competence-trust gap in review rigor)"
  humility_status_behavior  ███░░  3.0  (high confidence)
    - "Marcus in retro went_well: 'Arch review: I dissented BEFORE the decision and it actually changed.' — credits the process rather than himself"
    - "Marcus in #incidents: 'Ben — thank you for pulling the cord. That's the behavior we want, not the bug.' — attributes healthy behavior to Ben by name"
    - "Dana dominant_pct 56.3% at kickoff, 66.2% at roadmap review, 78.2% in 1:1 with Ben, 37.6% in retro when Sarah led — repeatedly redirects airtime to self; interrupted Rachel in the roadmap review"
    - "Rachel filed Kevin's #general napkin idea and credited him in the AUR-9 description ('Origin: Kevin's idea in #general 2026-04-09')"

### Commitment (3.6)
  clarity_of_mission_goals_roles  ████░  4.0  (high confidence)
    - "Dana at kickoff: 'Two tracks: Registry & Platform (me, Marcus, Priya, Tomás, Naomi, Ben) and Governance & Access (Sarah, James, Rachel, Kevin, Lily, Mark)' — clear roles and owners"
    - "Issue tracker AUR-1 through AUR-12 all have named assignees and priorities (P0/P1/P2)"
    - "AUR-2 'Decide capability model' resolved explicitly at arch review 2026-04-14 with named decision: 'no arbitrary egress, vetted first-party sources'"
    - "AUR-6/AUR-7 merged as joint ownership after Sarah stated: 'This should be one schema, owned jointly.'"
  strategy_planning  ████░  4.0  (high confidence)
    - "Naomi's manifest schema PR #24 concrete plan: 'Capabilities are an allow-list: fs.read, net.egress, tk.reference. Anything not listed is denied.'"
    - "Rachel #governance-access 2026-04-27: 'a broker that matches teachers-who-need with builders-who-have-credits, plus a fallback pool from Claude for Good' — concrete plan with sequence"
    - "Sarah: blameless incident note template shipped 3 days after retro commitment (AUR-12 done 2026-05-08)"
    - "Roadmap review meeting exists but Dana dominates 66.2% — planning done TO the team by Dana, not with them"
  buy_in_decision_closure  ██░░░  2.0  (high confidence)
    - "Mark's #tk-governance-review 2026-05-19 post-meeting: 'I still don't think we should commit to Local Contexts labels. Noting my dissent here.' — publicly agreed in room, dissented after (classic Lack of Commitment)"
    - "License question reopened 3 times per James retro item — decisions not committed to"
    - "TK Session 2 required a separate 'Ratify the Decision' meeting on 6-23; healthy but symptomatic of unclosed prior decisions"
    - "Kickoff has 6 silent attendees — no explicit commitment check per person"
  shared_vision_meaning  ████░  4.0  (high confidence)
    - "Sarah at kickoff: 'CARE principles one-pager to kickoff so we start with shared language'"
    - "James kickoff: 'whose knowledge is this registry going to hold, and who decided it could?' — surfaces meaning early"
    - "Kevin's #general 2026-04-09: 'the schools that most need Alaska-specific skills are exactly the ones with no API credits' — states customer consequence"
    - "Tomas #incidents: '36% of published skills carry a security flaw and there were 76 confirmed malicious payloads... This is not hypothetical' — states organizational consequence"
  discretionary_engagement  ████░  4.0  (high confidence)
    - "Kevin (Partnerships) proposed access broker idea outside his lane in #general 2026-04-09"
    - "Marcus #registry-platform 2026-05-06: 'I need a way to express provenance on a skill... Feels bigger than the platform. Anyone downstream thinking about this?' — raised cross-team problem"
    - "Lily #governance-access 2026-05-07: 'Are we duplicating work with the platform team here?' — cross-boundary flag"
    - "Dana proposing insights tool (AUR-11) from retro is discretionary meta-work"

### Results (4.0)
  collective_goal_focus_vs_individual_status  ████░  4.0  (high confidence)
    - "Marcus/Lily merged parallel work into joint schema (AUR-6/AUR-7) instead of shipping duplicates for own-team credit"
    - "Sarah: 'This should be one schema, owned jointly. Let's not build it twice.'"
    - "James refers to shared customer stake: 'Who do the people in that place call?'"
    - "Dana's talk-time dominance (56-78% in her meetings) is the main countervailing signal — argues from position/leader-role rather than shared metric"
  dependability_delivery  ████░  4.0  (high confidence)
    - "PR #24 merged next day, #63 within a week, #77 within 2 days of creation"
    - "AUR-1, AUR-2, AUR-3, AUR-4, AUR-6, AUR-7, AUR-12 all completed on planned dates"
    - "Priya's clickable alpha announced on time in #general 2026-04-23; install flow demo ready for sprint review"
    - "Ben's #41 shipped but broke smoke test — one delivery miss, promptly owned"
  coordination_backup_behavior  ████░  4.0  (high confidence)
    - "Marcus + Lily paired to dedupe provenance schema (AUR-6 co-owned)"
    - "Naomi paired with Ben on validator tests (standup 2026-04-15: 'Paired with Naomi on validator tests')"
    - "Tomas flagged incident and offered to harden pipeline; Ben and Marcus paired on the fix"
    - "Marcus in retro on incident: 'Once Ben spoke up we fixed it in an hour.' — team backed each other quickly"
  progress_monitoring_adaptation  ████░  4.0  (high confidence)
    - "Sprint retro post-incident produced 3 named try-nexts including blameless template (all shipped)"
    - "Tomas #incidents: escalated federation plan change: 'So federating openly is off the table. Curation + a human review pass is the product, not a nice-to-have' — plan revised on new evidence"
    - "AUR-5 security review escalated after 2026-05-04 incident"
    - "Standups report real progress including bad news (Ben 5-01: 'the weekend smoke test is red and I'm not sure why')"
  recognition_collective_motivation  ███░░  3.0  (medium confidence)
    - "Marcus named Ben's andon-cord behavior explicitly in-thread"
    - "Rachel credited Kevin ('Kevin's original napkin idea from #general, made real')"
    - "Emoji reactions on many announcements (tada, rocket, heart, raised_hands) show peer recognition"
    - "Dana closes several meetings with monologue rather than naming contributors; kickoff summary of team work missing named credit for many"
  continuous_improvement_learning_from_failure  █████  5.0  (high confidence)
    - "Sarah #incidents same day of incident: 'Noting for the retro: the fix took 4 days to surface because it felt unsafe to say. That's the thing to change.' — reframes failure as information"
    - "AUR-12 blameless incident note template shipped as named, owned process change"
    - "Retro 2026-06-02 produced AUR-11 (collaboration insights tool) as a named change against the team's own dysfunction"
    - "Tomas added regression test 'so #41 never repeats' — failure converted to a specific control"


*Inputs: *
*Run date: 2026-08-04*