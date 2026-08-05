# Team Health Assessment — aurora-q3-2026
Overall Health: 4.31 / 5  (↑ +0.9 from aurora-q2-2026)

## Dimension Scores

Accountability   ████░  4.1  ↑ +0.9
Conflict         ████░  4.2  ↑ +1.2  ⚠
Trust            ████░  4.4  ↑ +1.0  ⚠
Commitment       ████░  4.4  ↑ +0.8
Results          ████░  4.4  ↑ +0.4

## Priority Actions

1. Accountability is the lowest dimension at ~4.0 and the team's own self-identified next focus — invest in strengthening peer-to-peer accountability specifically. Introduce a lightweight rotating 'accountability partner' pattern where each engineer names one commitment weekly to a specific peer (not upward to Dana or Sarah), with a check-in at the next standup.
2. Content-speech time remains a small share of total speech (~10% in most meetings) despite excellent participation balance. Pilot a 'decision density' target — e.g., in decision meetings, aim for at least 2 explicit decisions with owner+date stated aloud before close — to convert healthy debate into more concrete closure.
3. Roll the insights tool out to the two partner districts' teams as agreed in retro, but pair it with the humility guardrails you built (patterns not rankings, questions=participation). Document the anti-surveillance constraints as a required part of adoption so other teams don't skip the guardrail that made it safe here.
4. Publish the before/after Q2->Q3 case study externally as Dana proposed, but include the tool's own failure modes (the over-flagged 'quiet week', threshold tuning) — this reinforces the 'mirror not target' norm James articulated and prevents cargo-culting the metrics.
5. Guard against tool dependency: schedule at least one meeting per sprint where the insights bot is intentionally off, and retro on whether the team still practices round-robin, blameless disclosure, and dissent-before-decision unaided. This tests whether the norms are internalized or only tool-scaffolded.

## Evidence Highlights

### Accountability
- "Marcus challenged Naomi's PR #92 (peer, not manager) — 'I want the humility constraint enforced in code, not just documented'"
- "Insights bot flags duplicate work between Marcus and Lily; Marcus accepts the nudge peer-to-peer"
- "Ben's blameless note filed to peer channels rather than escalated upward only"
- "Q3 assessment: Accountability at 4.0, team's self-identified next-quarter focus per Sarah's message"

### Conflict
- "Insights readout 2026-08-04: 'Dissent timing — Beta Arch Review: 3 objections detected, all raised before the decision point. 0 hallway/after-decision objections this sprint'"
- "Marcus raised surveillance concern on PR #92 as changes_requested — surfaced early, in-band"
- "Ben standup 2026-07-16: 'Defended my caching approach in review, Marcus pushed hard... that felt good instead of scary'"
- "Retro quote from Marcus: 'Dissent lands in the room before decisions now — the tool shows the timing.'"

### Trust
- "Ben Larsson self-disclosed a regression 41 minutes after commit: 'heads up: I introduced a regression in the label renderer this morning. test went red, I'm on it... flagging now rather than sitting on it.'"
- "Dana admits her own talk-time issue publicly in retro: 'My talk-time dropped from ~66% to under 40% once the tool started nudging me.'"
- "Naomi's Q2->Q3 talk-time went 6%->28% under round-robin; standup: 'the round-robin format actually works for me'"
- "Pulse survey psych_safety at 5/5 across nearly all respondents in S10-S12"

### Commitment
- "Sarah 2026-07-01: 'Overall 2.7/5; lowest dimensions... owners assigned in today's review: Trust → Tomás+me, Conflict → Dana+Naomi, Commitment → me, Accountability → Tomás, Results → Dana+Rachel'"
- "Every issue in AUR tracker has a named assignee and priority (P0/P1/P2)"
- "Dana's Q3 kickoff message: 'Q3 is live. Insights tool goes on for our team today; beta rollout to 3 districts staggered per the arch review. Round-robin is the default meeting format now.'"
- "ADR-0003 ratified with explicit mitigation"

### Results
- "Q4 Planning meeting titled 'Outcome Over Optics' (AUR/meeting 2026-08-11)"
- "Insights bot rule 'reports patterns, never ranks individuals, and questions count toward participation' — designed against individual status"
- "James: 'Change the behavior, not the number' — collective-outcome framing"
- "Sarah's summary: 'every collaboration metric improved vs Q2' — references shared scoreboard"

## Facet Detail

### Accountability (4.1)
  peer_to_peer_accountability  ████░  4.0  (medium confidence)
    - "Marcus challenged Naomi's PR #92 (peer, not manager) — 'I want the humility constraint enforced in code, not just documented'"
    - "Insights bot flags duplicate work between Marcus and Lily; Marcus accepts the nudge peer-to-peer"
    - "Ben's blameless note filed to peer channels rather than escalated upward only"
    - "Q3 assessment: Accountability at 4.0, team's self-identified next-quarter focus per Sarah's message"
  expectation_setting_antecedents  ████░  4.0  (medium confidence)
    - "PR #115 ways-of-working codifies blameless notes and reopening bar as antecedents"
    - "AUR issues carry explicit priority, labels, and description of definition of done"
    - "PR body norms (e.g., #92, #101) state what the change does and what evidence supports it up front"
    - "Team-health rec owners assigned with due-by-Q3 expectations"
  performance_monitoring  ████░  4.0  (medium confidence)
    - "Insights bot posts weekly readouts of talk-time, dissent timing, incident time-to-surface"
    - "AUR-19 tracker keeps 5 recommendations visible to closure across the quarter"
    - "Time-to-surface metric: 4 days (Q2) -> 41 minutes (Q3) tracked and reported"
    - "Q3 retro references specific metrics rather than vague impressions"
  consequences_feedback_delivery  ████░  4.0  (medium confidence)
    - "Marcus's specific-act feedback on Ben's regression: 'This is the exact situation that took four days in Q2. 40 minutes now. Growth.' — tied to a specific observed act"
    - "Insights bot delivers behavior-linked positive feedback promptly (weekly cadence)"
    - "PR review comments target specific design elements (surveillance risk, questions-as-participation)"
    - "Retro reactions (👍, 🎉, ❤️) tied to specific milestones rather than generic praise"
  ownership_vs_blame_shifting  █████  4.5  (high confidence)
    - "Ben: 'INC note: label-renderer regression, self-introduced, self-disclosed 41 min after commit.' — plainly owns miss without qualification"
    - "Dana publicly owned her 66% talk-time via PR #101 dogfooding"
    - "Naomi accepted Marcus's PR critique without defense and rebuilt design"
    - "Blameless template (PR #115) codifies diagnosis separated from fault"

### Conflict (4.2)
  surfacing_disagreement  █████  4.5  (high confidence)
    - "Insights readout 2026-08-04: 'Dissent timing — Beta Arch Review: 3 objections detected, all raised before the decision point. 0 hallway/after-decision objections this sprint'"
    - "Marcus raised surveillance concern on PR #92 as changes_requested — surfaced early, in-band"
    - "Ben standup 2026-07-16: 'Defended my caching approach in review, Marcus pushed hard... that felt good instead of scary'"
    - "Retro quote from Marcus: 'Dissent lands in the room before decisions now — the tool shows the timing.'"
  quality_of_debate  ████░  4.0  (medium confidence)
    - "PR #92 review chain: Marcus states specific concern, Naomi supplies concrete design change (guard, metric), James verifies the fix — evidence-based back-and-forth"
    - "Insights bot presents observable facts (talk-time %, dissent timing) before conclusions"
    - "Sarah PR #115 codifies reopening bar to force explicit reasoning on ADRs"
    - "Content-speech ratio remains low (~10% of speech time in most meetings), some debate quality still lean"
  tension_management_repair  ████░  4.0  (medium confidence)
    - "Ben framed post-challenge experience positively: 'that felt good instead of scary' — indicates recovery norms working"
    - "Marcus after Ben's incident: 'This is the exact situation that took four days in Q2. 40 minutes now. Growth.' — expresses support alongside the critique"
    - "Blameless practice working session (2026-07-10) explicitly institutionalizes repair"
    - "No interruptions recorded across 15 tracked meetings"
  destructive_conflict_aggression  █████  4.5  (high confidence)
    - "Zero interruptions across all 15 meetings in the metrics data"
    - "No demeaning language observed in Slack across #general, #incidents, #registry-platform, #team-health"
    - "Marcus's pushback on PR #92 attacks the proposal (surveillance risk), not the author"
  destructive_conflict_withdrawal_incivility  █████  4.5  (high confidence)
    - "No 'present but silent' attendees across all tracked meetings"
    - "Naomi (previously silent) now speaks in every meeting she attends; standup: 'Spoke up twice in the arch review'"
    - "Insights bot flagged silent-but-present went from 3 -> 0 across the quarter"
    - "Ben continued engaging after Marcus's tough review, per his own standup entry"
  resolution_closure  ████░  4.0  (medium confidence)
    - "AUR-18 'Written reopening bar standard on ADRs' explicitly institutionalizes closure"
    - "Insights bot 2026-08-18: 'Reopened-conflict watch: the licensing question (3 reopens in Q2) has not reopened... Marking it settled, not suppressed.'"
    - "Q3 retro produced two owned 'try_next' items with implicit ownership"
    - "Q2 recs all closed with checkmarks and dates in #team-health thread"

### Trust (4.4)
  vulnerability_psychological_safety  █████  4.5  (high confidence)
    - "Ben Larsson self-disclosed a regression 41 minutes after commit: 'heads up: I introduced a regression in the label renderer this morning. test went red, I'm on it... flagging now rather than sitting on it.'"
    - "Dana admits her own talk-time issue publicly in retro: 'My talk-time dropped from ~66% to under 40% once the tool started nudging me.'"
    - "Naomi's Q2->Q3 talk-time went 6%->28% under round-robin; standup: 'the round-robin format actually works for me'"
    - "Pulse survey psych_safety at 5/5 across nearly all respondents in S10-S12"
  contractual_trust_reliability_of_character  █████  4.5  (high confidence)
    - "All five Q2 assessment recommendations tracked to closure in AUR-19 with named owners and dates (Trust->Tomás+Sarah, Conflict->Dana+Naomi, etc.)"
    - "AUR-16 second security reviewer onboarded on time; Tomás: 'no longer a SPOF'"
    - "Ben reported back on regression: 'fixed and merged. root cause + blameless note in #incidents'"
    - "ADR-0003 written reopening bar (AUR-18) completed one day after creation"
  communication_trust_disclosure  █████  4.5  (high confidence)
    - "Ben's proactive incident disclosure in #registry-platform and #incidents without being asked"
    - "Marcus's PR #92 review: 'what stops this from becoming surveillance? I want the humility constraint enforced in code, not just documented.' — direct feedback to peer"
    - "Naomi's PR #92 response accepted feedback: 'Fair — added a guard... Marcus changed my design for the better here'"
    - "Insights bot dissent-timing readout: 3 objections raised before decision point in Beta Arch Review"
  competence_trust_capability  ████░  4.0  (medium confidence)
    - "Insights tool caught duplicate work: Marcus deferred to sync — 'Good catch — booking it. Last time we found this three weeks late.'"
    - "Marcus/Lily caching sync shows Marcus asking for Lily's expert judgment (46/54 talk split, Marcus led but Lily dominant speaker)"
    - "AUR-13 Round-robin/pre-reads designed with Naomi's input — deferring to her on how she thinks"
    - "Second reviewer onboarding (AUR-5, AUR-16) explicitly to reduce SPOF"
  humility_status_behavior  █████  4.5  (high confidence)
    - "Dana's PR #101 body: 'Dogfooded on our own Q2 data first — it correctly flags my 66% talk-time in the roadmap review' — public self-attribution of a fault"
    - "Naomi credits Marcus in PR #92: 'Marcus changed my design for the better here'"
    - "AUR-13 description names Naomi's pattern by name; Sarah at Q3 retro credits Naomi's work"
    - "James: 'Reminder as we act on this: it's a mirror, not a target' — deflecting toward collective learning"

### Commitment (4.4)
  clarity_of_mission_goals_roles  █████  4.5  (high confidence)
    - "Sarah 2026-07-01: 'Overall 2.7/5; lowest dimensions... owners assigned in today's review: Trust → Tomás+me, Conflict → Dana+Naomi, Commitment → me, Accountability → Tomás, Results → Dana+Rachel'"
    - "Every issue in AUR tracker has a named assignee and priority (P0/P1/P2)"
    - "Dana's Q3 kickoff message: 'Q3 is live. Insights tool goes on for our team today; beta rollout to 3 districts staggered per the arch review. Round-robin is the default meeting format now.'"
    - "ADR-0003 ratified with explicit mitigation"
  strategy_planning  █████  4.5  (high confidence)
    - "PRD 05 referenced in PR #92; PR bodies contain concrete plans (metrics contract, snapshot mitigation)"
    - "Beta rollout staggered per architecture review (AUR-15)"
    - "Q2 rec tracker AUR-19 lists 5 named owners with sequenced completion"
    - "Insights channel readouts (AUR-14) set up as recurring cadence"
  buy_in_decision_closure  ████░  4.0  (medium confidence)
    - "PR #115 codifies decision reopening bar — explicit commit mechanism"
    - "Q3 retro try_next items have visible vote counts (6, 7)"
    - "AUR-18 completed one day after creation shows fast decision closure"
    - "Marcus's PR #92 review: changes_requested then approved after design change — buy-in earned through debate"
  shared_vision_meaning  █████  4.5  (high confidence)
    - "James: 'it's a mirror, not a target. Change the behavior, not the number.' — articulates purpose"
    - "Sarah's retro Slack: 'We're going to publish the before/after so other Alaska teams can use it.' — connects work to broader community"
    - "AUR-9/AUR-10 tie work to community advisory and access — customer-facing purpose"
    - "PR #108 body explicitly frames facilitation nudge as 'aimed at the pattern Naomi named'"
  discretionary_engagement  █████  4.5  (high confidence)
    - "Naomi authored PR #92 (insights tool) — engaged with meta-work outside her core backend role"
    - "Sarah authored PR #115 codifying ways-of-working — governance lead taking on process for platform team"
    - "James (governance/TK) actively participates in platform retros and cautions on tool interpretation"
    - "Ben (junior dev) proactively disclosed incident and volunteered pairing with new reviewer"

### Results (4.4)
  collective_goal_focus_vs_individual_status  █████  4.5  (high confidence)
    - "Q4 Planning meeting titled 'Outcome Over Optics' (AUR/meeting 2026-08-11)"
    - "Insights bot rule 'reports patterns, never ranks individuals, and questions count toward participation' — designed against individual status"
    - "James: 'Change the behavior, not the number' — collective-outcome framing"
    - "Sarah's summary: 'every collaboration metric improved vs Q2' — references shared scoreboard"
  dependability_delivery  █████  4.5  (high confidence)
    - "12 of 13 Q3 issues closed on time; only AUR-15 (Beta rollout, P0) still in_progress as expected"
    - "AUR-19 assessment tracker closed at Q3 readout — loop closed"
    - "PRs merged within days of opening (PR #92: 6 days, PR #101: 4 days, PR #115: 1 day)"
    - "Ben delivered incident fix + regression test same-hour"
  coordination_backup_behavior  ████░  4.0  (medium confidence)
    - "Insights bot flagged Marcus/Lily duplicate caching work — coordination emerging via tool"
    - "Second reviewer onboarding explicitly framed as reducing bus factor (AUR-16)"
    - "Ben pairing with new reviewer on incident fix"
    - "Round-robin format ensures orientation of quieter members (Naomi, Priya) — helps new/underrepresented voices"
  progress_monitoring_adaptation  █████  4.5  (high confidence)
    - "James flagged tool over-triggering: 'The tool over-flagged one quiet week as low engagement — we tuned the threshold' — plan adapted"
    - "Insights bot 2026-09-15 quarter summary reports actual metric changes including bad news options"
    - "Q3 retro includes 'went_poorly' column with two accepted items"
    - "Dana's talk-time behavior changed in response to nudges, monitored across meetings"
  recognition_collective_motivation  █████  4.5  (high confidence)
    - "11 :tada: reactions on Sarah's Q3 assessment result post; 6 on general channel announcement"
    - "Naomi's contribution named by Marcus, Sarah, and in AUR-13 description"
    - "Retro 'went_well' column votes recognize specific individuals' improvements (Naomi 9, Dana 8, Ben 8, Marcus 7)"
    - "James's 'mirror, not a target' framing defuses potential anxiety about metrics"
  continuous_improvement_learning_from_failure  █████  4.5  (high confidence)
    - "Blameless template (PR #115) codifies learning from failure"
    - "Q2 incident (validator, 4-day surface time) explicitly compared to Q3 (41 min) as learning benchmark"
    - "James: 'it's a mirror, not a target' converts failure into information"
    - "Threshold-tuning after false positive shows retrospective loop working end-to-end"


*Inputs: *
*Run date: 2026-08-04*