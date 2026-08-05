#!/usr/bin/env python3
"""
Aurora Skills — demo data generator.

Produces a coherent, cross-referenced synthetic dataset for exercising a
"live team-collaboration / insights" tool. One fictional org (Aurora Skills,
an Alaska ed-tech collective), two teams, 12 people, Q2 2026 (Apr-Jun).

Emits (this file — the timestamp/format-heavy sources):
  slack-export/        real Slack export layout (users, channels, per-day json)
  transcripts/         WebVTT meeting transcripts with speaker diarization
  transcripts/meta/    per-transcript turn metadata (interruptions, overlap, latency)
  git/pull_requests.json     PR + review-thread export
  issues/issues.json         Linear-style issue tracker export
  standups/standups.json     daily async standup-bot log
  retros/*.json              retro board sticky notes + votes
  surveys/pulse.csv          per-sprint psychological-safety pulse survey
  _metrics/                   computed talk-time + question-ratio (feeds GROUND_TRUTH)

Prose docs (PRDs, ADRs, wiki, README, GROUND_TRUTH) are authored as static
files alongside this script; regenerating telemetry does not touch them.

Deterministic: fixed seed, no wall-clock reads. Run:  python3 generate.py
"""

import csv
import json
import os
import random
import re
from datetime import datetime, timezone

random.seed(20260804)

ROOT = os.path.dirname(os.path.abspath(__file__))

# Two eras: a "before" quarter (Q2, no collaboration tool — dysfunction present) and
# an "after" quarter (Q3, tool integrated — collaboration measurably improved).
ERAS = {
    "before": {"dir": "before-q2-2026", "label": "Q2 2026 — before the insights tool"},
    "after":  {"dir": "after-q3-2026",  "label": "Q3 2026 — after the insights tool"},
}

def era_paths(era):
    base = os.path.join(ROOT, ERAS[era]["dir"])
    p = {
        "base": base,
        "slack": os.path.join(base, "slack-export"),
        "trans": os.path.join(base, "transcripts"),
        "tmeta": os.path.join(base, "transcripts", "meta"),
        "git": os.path.join(base, "git"),
        "issues": os.path.join(base, "issues"),
        "stand": os.path.join(base, "standups"),
        "retro": os.path.join(base, "retros"),
        "survey": os.path.join(base, "surveys"),
        "metrics": os.path.join(base, "_metrics"),
    }
    for d in p.values():
        os.makedirs(d, exist_ok=True)
    return p

COMPARE = os.path.join(ROOT, "_comparison")
os.makedirs(COMPARE, exist_ok=True)

# --------------------------------------------------------------------------
# Roster.  `talk` is a hint for the author, not used mechanically — talk-time
# emerges from how much dialogue each person is actually given below.
# --------------------------------------------------------------------------
USERS = [
    # id     handle    real name          team         role                       traits
    ("U01", "dana",   "Dana Whitfield",  "platform",  "Tech lead / acting PM",   "dominates airtime; assertion-heavy"),
    ("U02", "marcus", "Marcus Bell",     "platform",  "Senior backend eng",      "healthy dissenter; objects before decisions"),
    ("U03", "priya",  "Priya Nair",      "platform",  "Frontend eng",            "steady contributor"),
    ("U04", "tomas",  "Tomás Reyes",     "platform",  "DevOps / security eng",   "drives the security incident"),
    ("U05", "naomi",  "Naomi Kito",      "platform",  "Backend eng",             "near-silent in meetings, active in chat"),
    ("U06", "ben",    "Ben Larsson",     "platform",  "Junior dev",              "hides a mistake early, grows later"),
    ("U07", "sarah",  "Sarah Kowalski",  "governance","Governance lead (PhD)",   "balanced facilitator"),
    ("U08", "james",  "James Ahkivgak",  "governance","Community liaison / TK",  "Socratic; high question ratio"),
    ("U09", "rachel", "Rachel Green",    "governance","Access & credits PM",     "drives credits program"),
    ("U10", "kevin",  "Kevin Osei",      "governance","Partnerships",            "floats ideas early"),
    ("U11", "lily",   "Lily Chen",       "governance","Data eng",                "same schema work as Marcus"),
    ("U12", "mark",   "Mark Dupont",     "governance","Legal / licensing",       "central to license debate"),
    # The collaboration-insights tool itself, posting to #insights in the AFTER quarter.
    ("U99", "insights-bot", "Collaboration Insights", "tool", "Insights agent",  "the tool under demo"),
]
NAME = {u[1]: u[2] for u in USERS}
UID = {u[1]: u[0] for u in USERS}
BOTS = {"insights-bot"}

CHANNELS = [
    ("C100", "general",              "Cross-team announcements & logistics",
     ["dana","marcus","priya","tomas","naomi","ben","sarah","james","rachel","kevin","lily","mark"]),
    ("C200", "registry-platform",    "Team 1 — registry & platform build",
     ["dana","marcus","priya","tomas","naomi","ben","sarah"]),
    ("C300", "governance-access",    "Team 2 — TK governance & access program",
     ["sarah","james","rachel","kevin","lily","mark","dana"]),
    ("C400", "tk-governance-review", "Cross-team review of TK / licensing decisions",
     ["dana","marcus","sarah","james","rachel","kevin","lily","mark"]),
    ("C500", "incidents",            "Security & reliability incidents",
     ["dana","marcus","tomas","naomi","ben","sarah"]),
    # AFTER-era only: the insights tool posts periodic readouts here.
    ("C600", "insights",             "Automated collaboration-insights readouts",
     ["dana","marcus","priya","tomas","naomi","ben","sarah","james","rachel","kevin","lily","mark","insights-bot"]),
]

# --------------------------------------------------------------------------
# Time helpers.  Slack ts are UTC epoch seconds with a 6-digit sequence.
# --------------------------------------------------------------------------
_seq = 0
def ts_for(date_str, time_str):
    global _seq
    _seq += 1
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    return f"{int(dt.timestamp())}.{_seq:06d}"

# ==========================================================================
# SLACK CONTENT
# Each message: dict(ch, date, t, u, text, thread=<key>, reactions=[(emoji,[handles])])
# Messages sharing a `thread` key form a thread; first one is the parent.
# ==========================================================================
M = []
def msg(ch, date, t, u, text, thread=None, reactions=None, era="before"):
    M.append({"ch": ch, "date": date, "t": t, "u": u, "text": text,
              "thread": thread, "reactions": reactions or [], "era": era})

# ---- #general -----------------------------------------------------------
msg("general","2026-04-06","09:02","dana",
    "Morning all — Aurora Skills kicks off today. Two tracks: Registry & Platform (me, Marcus, Priya, Tomás, Naomi, Ben) and Governance & Access (Sarah, James, Rachel, Kevin, Lily, Mark). Kickoff at 10.")
msg("general","2026-04-06","09:05","sarah","Excited. I'll bring the CARE principles one-pager to kickoff so we start with shared language.")
msg("general","2026-04-06","09:11","james","One question before we build anything: whose knowledge is this registry going to hold, and who decided it could? I'd like that on the table day one.",
    reactions=[("raised_hands",["sarah","rachel","kevin"])])
# SEED (similarity): credits/access idea first floated here on Apr 9, weeks before the Apr 28 meeting.
msg("general","2026-04-09","14:20","kevin",
    "Thought while walking home: the schools that most need Alaska-specific skills are exactly the ones with no API credits to build them. What if part of Aurora is a broker — match teachers who need something built with people who have credits to spare? Claude for Teachers is free for verified K-12 folks, and Campus / for Good both hand out credits.",
    thread="credits-idea",
    reactions=[("bulb",["rachel","sarah","dana"])])
msg("general","2026-04-09","14:41","rachel","This is the thing. Filing it so we don't lose it. I want to own this.", thread="credits-idea")
msg("general","2026-04-09","15:02","dana","Good but let's not scope-creep the platform. Park it for Team 2.", thread="credits-idea")
msg("general","2026-04-23","11:30","priya","Registry alpha is clickable: browse skills, filter by grade band, view a skill's manifest. No install flow yet.",
    reactions=[("tada",["dana","marcus","sarah","ben"])])
msg("general","2026-05-06","16:15","dana","Reminder: security incident retro moved to tomorrow 10am after what Tomás found. Please read the thread in #incidents first.")
msg("general","2026-06-01","09:00","sarah","Retro tomorrow is a little different — we're going to look at *how we've been working together*, not just what shipped. Come ready to be honest.")

# ---- #registry-platform -------------------------------------------------
msg("registry-platform","2026-04-13","10:12","marcus",
    "Pre-read for tomorrow's architecture review: I think we should NOT let skills declare arbitrary network egress in their manifest. If a skill can phone home, curation can't promise safety. Want to argue this before we lock the schema.",
    thread="egress",
    reactions=[("eyes",["dana","tomas","priya"])])
msg("registry-platform","2026-04-13","10:29","tomas","Agreed, and it ties to review load. Every egress permission is a thing a human reviewer has to reason about.", thread="egress")
msg("registry-platform","2026-04-13","11:40","naomi","+1. I can draft a manifest schema that makes egress an explicit, reviewed capability rather than a free-text field.", thread="egress")
# SEED (silent-in-meeting / active-in-chat): Naomi is a strong voice in text.
msg("registry-platform","2026-04-16","09:20","naomi",
    "Manifest schema v0 is up (PR #24). Capabilities are an allow-list: `fs.read`, `net.egress`, `tk.reference`. Anything not listed is denied. Feedback welcome — I'd rather over-restrict now.")
msg("registry-platform","2026-04-16","09:44","marcus","This is exactly right. Reviewing now.", thread=None)
# SEED (matching-people): Marcus surfaces the manifest-schema problem here...
msg("registry-platform","2026-05-06","13:05","marcus",
    "Hitting a wall on the manifest schema: I need a way to express *provenance* on a skill — who authored it, what community it draws from, what data it touches. Feels bigger than the platform. Anyone downstream thinking about this?",
    thread="schema-provenance",
    reactions=[("thinking_face",["priya","naomi"])])
msg("registry-platform","2026-05-06","13:22","priya","Sounds like a governance question wearing an engineering hat.", thread="schema-provenance")
# SEED (trust / hidden mistake): Ben quietly patches a bug rather than flagging it.
msg("registry-platform","2026-04-30","17:52","ben",
    "pushed a small fix to the manifest validator, nothing major",
    thread="ben-fix",
    reactions=[("+1",["dana"])])
msg("registry-platform","2026-05-04","08:10","naomi","@ben which validation path did that touch? The install smoke test started failing over the weekend.", thread="ben-fix")
msg("registry-platform","2026-05-04","08:31","ben","uh. it might be related. i thought i'd caught everything. looking now.", thread="ben-fix")
msg("registry-platform","2026-05-12","15:00","priya","Install flow demo is ready for sprint review. It's rough but it works end to end.",
    reactions=[("rocket",["dana","marcus","naomi"])])

# ---- #governance-access -------------------------------------------------
msg("governance-access","2026-04-20","10:00","sarah",
    "Framing for the TK working session tomorrow: an MIT or Apache license covers *code*. It does not cover place names, subsistence locations, or traditional knowledge. Being open source is not the same as having consent from a community. I want us to design the governance layer before the first such contribution arrives, not after.",
    thread="tk-frame",
    reactions=[("100",["james","rachel","kevin","lily"])])
msg("governance-access","2026-04-20","10:18","mark",
    "I hear it, but I'll push back as the lawyer in the room: a bespoke license is a maintenance and adoption tax. Every non-standard term is a reason a contributor walks. I want to see the specific harm before we invent a new instrument.",
    thread="tk-frame")
msg("governance-access","2026-04-20","10:35","james","Mark, the harm is the point I raised on day one. If a subsistence hunting location ends up in a public repo under MIT, the license *permits* anyone to redistribute it. Who do the people in that place call?", thread="tk-frame")
# SEED (matching-people): Lily independently hits the SAME schema problem as Marcus, in a different channel.
msg("governance-access","2026-05-07","09:40","lily",
    "I'm building the data-label model and I keep needing something the platform doesn't give me: provenance on every artifact — author, source community, what TK it references. Are we duplicating work with the platform team here?",
    thread="schema-provenance-gov",
    reactions=[("eyes",["sarah","james"])])
msg("governance-access","2026-05-07","10:02","sarah","Almost certainly. This should be one schema, owned jointly. Let's not build it twice.", thread="schema-provenance-gov")
msg("governance-access","2026-04-27","14:00","rachel",
    "Access & credits program design doc is up for tomorrow. Core: a broker that matches teachers-who-need with builders-who-have-credits, plus a fallback pool from Claude for Good. Kevin's original napkin idea from #general, made real.",
    reactions=[("heart",["kevin","sarah"])])

# ---- #tk-governance-review ----------------------------------------------
# SEED (hallway dissent / late objection): the May 19 session reached a direction;
# Mark lodges his objection HERE afterward instead of in the room.
msg("tk-governance-review","2026-05-19","16:40","mark",
    "Following up async on today's session — I didn't want to relitigate in the room, but for the record I still don't think we should commit to Local Contexts labels. I think we'll regret the dependency. Noting my dissent here.",
    thread="mark-late",
    reactions=[("neutral_face",["sarah"])])
msg("tk-governance-review","2026-05-19","17:05","sarah",
    "Mark — I'd much rather have heard this while we were all in the room. We're about to write it into an ADR. Can you bring the objection *to the group* on the 23rd rather than the channel? Deciding in the hallway is how this reopens forever.",
    thread="mark-late")
msg("tk-governance-review","2026-05-20","08:15","james","This is the third time the license question has come back. I don't mind reopening if there's new information. Is there new information, or are we relitigating?", thread="mark-late")

# ---- #incidents ---------------------------------------------------------
msg("incidents","2026-05-04","09:50","tomas",
    "🔴 Heads up. Auditing the public skill-share ecosystems we planned to federate with. A Feb 2026 Snyk audit found 36% of published skills carry a security flaw and there were 76 confirmed malicious payloads. I just reproduced one that exfiltrates env vars on install. This is not hypothetical.",
    thread="incident",
    reactions=[("rotating_light",["dana","marcus","sarah","naomi"])])
msg("incidents","2026-05-04","10:15","dana","So federating openly is off the table. Curation + a human review pass is the product, not a nice-to-have.", thread="incident")
msg("incidents","2026-05-04","10:40","ben",
    "I need to say something. That validator fix I pushed on the 30th and called 'nothing major' — it disabled a capability check to make a test pass. That's the path Naomi flagged. I was embarrassed and hoped I'd quietly fix it. I'm sorry. Here's exactly what it touched: [thread]",
    thread="incident",
    reactions=[("heart",["naomi","sarah","marcus","tomas"])])
msg("incidents","2026-05-04","10:52","marcus","Ben — thank you for pulling the cord. That's the behavior we want, not the bug. Let's fix it together.", thread="incident")
msg("incidents","2026-05-04","11:10","sarah","Noting for the retro: the fix took 4 days to surface because it felt unsafe to say. That's the thing to change.", thread="incident")

# ==========================================================================
# SLACK EMIT
# ==========================================================================
def emit_slack(era, paths):
    msgs = [m for m in M if m["era"] == era]

    users_json = []
    for uid, handle, real, team, role, traits in USERS:
        users_json.append({
            "id": uid, "name": handle, "real_name": real,
            "deleted": False, "is_bot": handle in BOTS,
            "profile": {"real_name": real, "display_name": handle,
                        "title": role, "team": team},
        })
    with open(os.path.join(paths["slack"], "users.json"), "w") as f:
        json.dump(users_json, f, indent=2)

    # only emit channels that actually carried traffic this era
    active = {m["ch"] for m in msgs}
    chan_json = []
    for cid, cname, purpose, members in CHANNELS:
        if cname not in active:
            continue
        created = int(datetime(2026, 4, 6, tzinfo=timezone.utc).timestamp())
        chan_json.append({
            "id": cid, "name": cname, "created": created, "is_archived": False,
            "members": [UID[m] for m in members],
            "purpose": {"value": purpose},
            "topic": {"value": purpose},
        })
    with open(os.path.join(paths["slack"], "channels.json"), "w") as f:
        json.dump(chan_json, f, indent=2)

    id_by_cname = {c[1]: c[0] for c in CHANNELS}

    for m in msgs:
        m["ts"] = ts_for(m["date"], m["t"])

    # resolve threads within this era: parent = first message with a given thread key
    thread_parent = {}
    for m in msgs:
        k = m["thread"]
        if k and k not in thread_parent:
            thread_parent[k] = m
    reply_count = {}
    for m in msgs:
        k = m["thread"]
        if k and thread_parent[k] is not m:
            reply_count[k] = reply_count.get(k, 0) + 1

    buckets = {}
    for m in msgs:
        cid = id_by_cname[m["ch"]]
        buckets.setdefault((cid, m["ch"], m["date"]), []).append(m)

    for (cid, cname, date), items in buckets.items():
        cdir = os.path.join(paths["slack"], cname)
        os.makedirs(cdir, exist_ok=True)
        out = []
        for m in items:
            obj = {
                "type": "message",
                "user": UID[m["u"]],
                "user_name": NAME[m["u"]],
                "text": m["text"],
                "ts": m["ts"],
            }
            k = m["thread"]
            if k:
                parent = thread_parent[k]
                obj["thread_ts"] = parent["ts"]
                if parent is m:
                    obj["reply_count"] = reply_count.get(k, 0)
                else:
                    obj["parent_user_id"] = UID[parent["u"]]
            if m["reactions"]:
                obj["reactions"] = [
                    {"name": emo, "users": [UID[h] for h in who], "count": len(who)}
                    for emo, who in m["reactions"]
                ]
            out.append(obj)
        out.sort(key=lambda o: float(o["ts"]))
        with open(os.path.join(cdir, f"{date}.json"), "w") as f:
            json.dump(out, f, indent=2)

    return len(msgs), len(buckets)

# ==========================================================================
# TRANSCRIPTS
# A "turn" is (speaker_handle, text) or (speaker_handle, text, {"interrupt": True}).
# Timings are derived from word counts (~150 wpm) so talk-time metrics are REAL,
# not asserted.  Interruptions produce overlapping cues.
# ==========================================================================
T = []
def transcript(tid, title, date, start_time, turns, era="before"):
    T.append({"id": tid, "title": title, "date": date, "start": start_time,
              "turns": turns, "era": era})

# ---- 1. Kickoff (Dana dominates; James asks; Naomi absent from the floor) ----
transcript("2026-04-07_kickoff", "Aurora Skills — Program Kickoff", "2026-04-07", "10:00", [
 ("dana","Alright, welcome everybody. This is the kickoff for Aurora Skills. Let me set the frame, because I've been thinking about this a lot. We are building a curated registry of Alaska-related AI skills for classrooms. Two teams. Platform builds the registry, the manifest format, the review pipeline, and the install experience. Governance and Access handles traditional knowledge, licensing, and the credits program so schools that can't afford to build still get to. The reason we curate instead of federate is trust. A big open firehose of skills is a security liability and it's a cultural liability. Small, reviewed, regional — that's the whole bet. I'll be running platform and acting as PM across both for now."),
 ("sarah","Thanks Dana. I want to add one lens before we divide up. I'll bring a CARE-principles one-pager to every governance session — Collective benefit, Authority to control, Responsibility, Ethics. It's the language we'll use to decide what belongs in the registry at all."),
 ("james","Can I ask the question I put in the channel this morning? Whose knowledge is this registry going to hold, and who decided it could be held? I'm not asking rhetorically. Before we design a manifest format, do we know who has the authority to say yes?"),
 ("dana","That's a governance question, and it's exactly why Sarah's team exists in parallel to mine. Platform will build the container; governance decides what's allowed in it. I don't want platform blocked on that though, so we'll design the schema to be permissive and let governance add constraints."),
 ("james","But isn't that backwards? If the container is built to be permissive and the constraints come later, haven't we already decided the default is yes? Who does a community call if the default let something through?"),
 ("marcus","James has a point that affects my work directly. If governance rules arrive after the schema is frozen, I have to retrofit them, and retrofits leak. I'd rather the schema start restrictive."),
 ("dana","Okay, noted, we can start restrictive on capabilities. Let me keep us moving though — I want to talk milestones. Alpha registry by end of April, review pipeline mid-May, access program design in parallel, and a working demo by end of quarter. Rachel, you've got the credits program; Tomás, you own security review; Priya, front end; Naomi, backend and the manifest schema; Ben, you're pairing with Naomi. Governance, Sarah quarterbacks with James on community, Lily on the data model, Mark on licensing, Kevin on partnerships.", {"interrupt": True}),
 ("rachel","On the credits program — that came out of Kevin's idea in the channel. I want to name that so the origin's clear. I'll own it."),
 ("kevin","Happy for it to be yours. It was a walk-home thought, you're going to make it real."),
 ("dana","Great. I think that's the frame. I'll send notes. Let's build."),
])

# ---- 2. Architecture review (healthy dissent BEFORE decision; Naomi silent) ----
transcript("2026-04-14_architecture-review", "Registry Architecture Review", "2026-04-14", "14:00", [
 ("dana","Today we lock the manifest schema and the capability model. I want a decision by the end of this hour so Naomi and Ben aren't blocked. My proposal: capabilities are an allow-list, and we allow a network-egress capability so skills can pull live data — weather, tides, that kind of thing. Alaska classrooms will want live data."),
 ("marcus","I want to object before we decide, not after. If a skill can declare arbitrary network egress, curation cannot promise safety. A reviewer can't reason about where a skill phones home at review time versus runtime. I think egress should not be a self-declared capability at all in v1."),
 ("dana","But then we lose live data, which is half the appeal."),
 ("marcus","We don't lose it. We provide vetted data sources as first-party capabilities — a tides API, a weather API we host and audit — instead of letting every skill open its own socket. Classrooms get live data, reviewers get a bounded surface."),
 ("tomas","I'll back Marcus. Every arbitrary-egress permission is a thing I have to threat-model per skill. First-party sources collapse that to auditing a handful of endpoints once."),
 ("priya","From the front end it's actually cleaner too — I can show a skill's data sources as named badges instead of a raw URL nobody understands."),
 ("dana","Okay. I came in wanting open egress. I'm hearing that it breaks the safety promise that is the whole product. Let me change the proposal: no arbitrary egress in v1, first-party vetted data sources only, revisit in v2 if there's demand. Does anyone object to THAT?"),
 ("marcus","No objection. That's the right call."),
 ("tomas","Agreed."),
 ("dana","Decision recorded: capabilities are an allow-list, no arbitrary egress, vetted first-party data sources. Naomi, that changes your schema — egress comes off the capability list. Naomi?"),
 ("naomi","Yep. I'll update the schema today."),
])

# ---- 3. TK working session 1 (license debate opens — 1st time) ----
transcript("2026-04-21_tk-session-1", "TK Governance Working Session 1", "2026-04-21", "13:00", [
 ("sarah","The question on the table: what license or governance instrument covers a skill that references traditional knowledge — a place name, a subsistence location, a story? I'll start us with the frame. Open source covers code. It does not cover knowledge, and it is not consent."),
 ("mark","And I'll be the friction. A bespoke license is an adoption tax. Every non-standard term is a reason a contributor or a school district's lawyer says no. I want to see the concrete harm before we build a new instrument that we then have to defend forever."),
 ("james","The harm isn't abstract to the people it belongs to. If a subsistence hunting location is published under MIT, the license explicitly permits anyone to copy and redistribute it. So my question to you, Mark: when that happens, who does the community call, and what does your standard license let them do about it?"),
 ("mark","Legally? Not much. That's my honest answer. Copyright doesn't protect facts or locations well in the first place."),
 ("james","Then the standard instrument already fails the case we care about most. That's not an adoption tax argument, that's a fitness argument."),
 ("sarah","This is why I keep pointing at CARE and at Local Contexts — the TK and Biocultural labels. They're not a license, they're a notice layer that travels with the data and states the community's terms even where copyright is silent."),
 ("mark","I don't know enough about Local Contexts to commit to a dependency on them. That's a real project we'd be leaning on."),
 ("kevin","Could we pilot the labels on one partner community's contributions before committing platform-wide? Learn before we standardize?"),
 ("sarah","That's reasonable. Let's not decide the whole thing today. Action: I'll write up CARE + Local Contexts as an option, Mark writes up the standard-license option, we compare next session."),
 ("mark","Fine. I still think we'll land on standard-plus-a-notice, but I'll write it up fairly."),
])

# ---- 4. Access & credits design (references Kevin's Apr 9 idea) ----
transcript("2026-04-28_access-credits", "Access & Credits Program Design", "2026-04-28", "11:00", [
 ("rachel","This program started as Kevin's walk-home thought in the channel on the 9th: the schools that most need Alaska skills have the least ability to pay for them. So the program is a broker. Three parts. One, a needs board where a teacher posts what they wish existed. Two, a builder pool of people with spare credits or skills who claim needs. Three, a fallback credits pool we seed from Claude for Good and Campus grants for needs nobody claims."),
 ("kevin","The partnership angle: two districts already said they'd post needs if the board existed. Demand is real."),
 ("sarah","How do we keep the broker from turning traditional knowledge into a work order? A teacher posting 'build me a skill about local plants' could pull a community's knowledge into a build without consent."),
 ("rachel","Good catch. Needs that touch TK get routed to James's community review before they're claimable. I'll wire that dependency in."),
 ("james","I'd want to see the routing rule written down, not just intended. What triggers the review — a keyword, a category, a human check?"),
 ("rachel","Category plus a human check. I'll spec it. Kevin, can you get the two districts to pilot the needs board?"),
 ("kevin","Yes."),
 ("dana","Keep the platform dependency light — the needs board can be its own thing, it doesn't need to block the registry."),
])

# ---- 5. Incident retro (trust; andon cord; shameless mistakes) ----
transcript("2026-05-05_incident-retro", "Security Incident Retro", "2026-05-05", "10:00", [
 ("tomas","Timeline first. April 30, a validator change disabled a capability check. May 4, the install smoke test failure surfaced it, at the same time I was auditing external skill ecosystems and reproducing a payload that exfiltrates env vars. So we had a live hole in our own validator during the same week the external threat became concrete. We caught it. But it took four days."),
 ("ben","The four days are on me and I want to own it in the room, not just the thread. I disabled the check to make a test pass, called it 'nothing major,' and hoped I'd quietly fix it before anyone noticed. I was embarrassed. That instinct is the actual bug."),
 ("marcus","And the thing I want on the record: the moment Ben said it out loud, we fixed it in an hour. The cost wasn't the mistake, it was the four days of silence. That's a team problem, not a Ben problem."),
 ("sarah","This is Toyota's andon cord. Anyone on the line can stop it when something's wrong. It only works if pulling it is safe. Ben pulling it late tells us it didn't feel safe. What made it feel unsafe?"),
 ("ben","Honestly? I'm the junior. I thought a mistake this basic would make people wonder why I'm here."),
 ("dana","That's a leadership failure, not yours. I've been running these meetings talking eighty percent of the time. If I'm always talking, the message is that the confident voice is the safe one. I own that."),
 ("naomi","For what it's worth, the smoke test caught it because we had one. The system worked. We should say that too, not just flog ourselves."),
 ("sarah","Both are true. Actions: one, we write down that pulling the cord early is the expected behavior and celebrate it. Two, we add a blameless note to every incident. Three — and this is the interesting one — Dana, can we measure whether people actually feel safe, instead of guessing?"),
 ("dana","That's the thread I want to pick up at the retro on the 2nd. I think there's a tool in it."),
])

# ---- 6. Sprint review (lighter) ----
transcript("2026-05-12_sprint-review", "Sprint Review — Install Flow", "2026-05-12", "15:00", [
 ("dana","Sprint review. Priya, take us through the install flow."),
 ("priya","End to end: browse the registry, open a skill, see its capability badges and data sources, click install, get a consent screen that lists exactly what it can do, confirm. It's rough visually but the whole path works."),
 ("marcus","Backend's enforcing the capability allow-list at install now, so the consent screen isn't cosmetic — denied capabilities actually can't run."),
 ("tomas","And the disabled-check regression from last week has a test that fails loudly if anyone tries it again."),
 ("dana","Good. Naomi, schema status?"),
 ("naomi","Stable. The provenance field is the open question — Marcus and Lily both need it and it shouldn't live in two schemas."),
 ("dana","Let's get those two in a room. Nice work everyone."),
])

# ---- 7. TK session 2 (reopens — 2nd time; James changes his mind) ----
transcript("2026-05-19_tk-session-2", "TK Governance Working Session 2", "2026-05-19", "13:00", [
 ("sarah","Round two. Mark wrote up the standard-license-plus-notice option, I wrote up CARE plus Local Contexts labels. Let's compare honestly."),
 ("mark","My case: adopt a standard permissive license for code, and attach a plain-text notice for TK-referencing skills. No external dependency, low adoption friction, we control it."),
 ("james","I came into this arguing for a fully bespoke instrument. I want to say out loud that I've changed my mind after reading both write-ups. Mark's adoption-friction point is real — a bespoke license nobody adopts protects no one. But a plain-text notice we invent has no standing and no persistence; it gets stripped on the first copy. The Local Contexts labels are the middle path I didn't see before."),
 ("sarah","Say more about why the labels and not our own notice?"),
 ("james","Because they're recognized, they travel with the data as metadata, and they encode the community's authority in a way a reader can act on. Our homemade notice is just a sentence. Theirs is an institution."),
 ("mark","I still don't love taking a dependency on an external project. But I'll grant that 'a sentence we wrote' is weaker than I implied."),
 ("sarah","So where we've landed today: code under a standard permissive license, TK-referencing skills carry Local Contexts labels plus a community-authored notice, and TK contributions route through community review. I'm going to write this into an ADR. Any objection, now, in the room?"),
 ("mark","No objection I want to make right now."),
 ("sarah","Then we'll ratify on the 23rd."),
])

# ---- 8. Community advisory (James leads; very high question ratio) ----
transcript("2026-05-21_community-advisory", "Community Advisory Meeting", "2026-05-21", "16:00", [
 ("james","Thank you all for coming. I'm going to mostly ask, not tell. First: when you hear that we're building a registry of Alaska skills, what's the first worry that comes up for you?"),
 ("sarah","I'll seed it with our own worry, then get out of the way: that we build the container before we've earned the right to hold anything in it."),
 ("james","Let me put that to the advisors. Does 'earning the right' match how you'd frame it? Or is there a better frame? And who, in your community, would even be the one to grant it?"),
 ("james","Second question. If a place name or a subsistence location shows up in a skill, what should happen — should it be removable on request, should it never be enterable at all, or should it require a named person's yes before it's stored?"),
 ("james","And a harder one: if we get this wrong, how do you want to be able to tell us, and how fast do you need us to be able to undo it?"),
 ("sarah","These are exactly the questions the labels and the review routing are trying to answer — but I'd rather they answer them than us."),
 ("james","Last one from me for now: what would make this feel like it belongs to you rather than to us?"),
])

# ---- 9. Healthy-conflict retro (META — pitch the insights tool) ----
transcript("2026-06-02_healthy-conflict-retro", "Retro — How We Work Together", "2026-06-02", "10:00", [
 ("sarah","This retro is different. We're not reviewing what shipped. We're reviewing how we've been working. I'll start with something concrete: the license question has come back three times. That can mean two things — either new information each time, which is healthy, or it never actually got decided, which isn't. Which was it?"),
 ("mark","Partly me. I raised my objection in the channel after the session on the 19th instead of in the room. That's the hallway. I'm naming it."),
 ("james","And I'd say twice it was new information and once it was relitigating. The tell was whether anyone changed their mind. When I changed mine on the 19th, that round moved. The rounds where nobody moved were the stuck ones."),
 ("dana","Here's mine. I went back through our meeting transcripts. In the first three group meetings I was talking somewhere around seventy to eighty percent of the time. When the lead talks that much, silence stops meaning agreement and starts meaning it isn't safe to disagree. Ben's four-day silence is downstream of that."),
 ("marcus","The counter-example is the architecture review. Dana proposed open egress, I objected before the decision, and the proposal actually changed in the room. That's the shape we want — dissent arrives before the decision, not after."),
 ("naomi","Can I name a pattern about me? I don't talk in meetings. I say everything in the channel. That's not shyness exactly, it's that the meeting feels like it's for the confident. So my contribution is invisible if you only listen to the room."),
 ("sarah","That's a huge one, Naomi, thank you. It means anyone measuring participation by who talks in meetings would score you at zero and be completely wrong."),
 ("dana","Which is the idea I've been sitting on. What if we built the thing we keep wishing we had — a tool that watches our own collaboration and tells us this stuff while it's happening, not a month later in a retro. Talk-time balance. Questions versus assertions. Whether dissent shows up before or after the decision. Whether anyone changed their mind. Whether the same fight reopened a third time. All of that is countable from a transcript and a channel."),
 ("james","I like it only if it measures the right things and stays humble. A number that says I'm 'low participation' because I ask questions instead of asserting would be measuring the wrong thing. Questions are participation."),
 ("dana","Agreed, and that's a design constraint, not a reason not to build it. Let's spec it. I think it's the most interesting thing we've got."),
])

# ---- 10. Roadmap review (Dana dominates again — regression signal) ----
transcript("2026-06-09_roadmap-review", "Q3 Roadmap Review", "2026-06-09", "11:00", [
 ("dana","Let me walk the whole roadmap and then we'll react. Q3: registry goes to beta with three partner districts, the review pipeline gets a second human reviewer so Tomás isn't a single point of failure, the access needs-board launches with Kevin's two districts, Local Contexts labels ship on TK skills per the ADR, and we prototype the collaboration-insights tool against our own data first. That's the plan. I've thought through the sequencing and I think it's right. The registry beta has to come first because everything else demos on top of it, then the reviewer, then the needs board, then labels, then insights. Reactions?"),
 ("rachel","The needs board doesn't actually depend on the registry beta. I could ship it earlier and it'd de-risk the access story for the fundraiser."),
 ("dana","Maybe, but I'd rather keep the demo coherent. Let's hold the sequence.", {"interrupt": True}),
 ("marcus","I'll flag the same thing I flagged in the retro — that was a decision made fast without much room for the objection. Rachel just gave you new information and the sequence didn't move."),
 ("dana","...Fair. Okay. Rachel, if the needs board is independent, pull it forward. I'm doing the thing again, aren't I."),
 ("sarah","You caught it in the same meeting though. That's the improvement."),
])

# ---- 11. 1:1 Dana + Ben (defend your code; failures are interesting) ----
transcript("2026-06-16_dana-ben-1-1", "1:1 — Dana & Ben", "2026-06-16", "09:30", [
 ("dana","I wanted to do this after the incident. How are you doing, honestly?"),
 ("ben","Better. The retro helped. It stopped feeling like the mistake defined me."),
 ("dana","Good. I want to ask you to do something that'll feel uncomfortable. In the next design review, I want you to defend a technical choice out loud, and I want Marcus to push on it hard. Not to trip you — because the ability to defend a choice is the thing that turns a junior into a senior."),
 ("ben","That's the part that scared me with the validator. I couldn't defend the shortcut, so I hid it instead."),
 ("dana","Right. And here's the reframe I want you to keep: the failures are the interesting things. A green build teaches nobody anything. The validator incident taught the whole team more about how we work than a month of clean sprints. If you're not failing sometimes, you're not near the edge of what you can do."),
 ("ben","I can try that. Defending it out loud, I mean."),
 ("dana","That's all I'm asking. And if Marcus changes your mind, say so in the room. That's a win, not a loss."),
])

# ---- 12. TK decision session (reopens 3rd time, then consciously closed) ----
transcript("2026-06-23_tk-decision", "TK Governance — Ratify the Decision", "2026-06-23", "13:00", [
 ("sarah","We're here to ratify the ADR from the 19th: standard permissive license for code, Local Contexts labels plus community notice for TK skills, community review routing. Before we ratify — Mark, you lodged a late objection in the channel. This is the room. Bring it."),
 ("mark","Thank you. My objection is the external dependency on Local Contexts. If that project changes or disappears, our governance layer has a hole. That's real and I don't want it decided in a hallway."),
 ("james","That's the third time this has come back. I want to be honest that reopening a settled question a third time, without new information, is its own problem — it means we suppressed it rather than settled it. So let's actually settle it. Mark, is there new information, or is it the same concern?"),
 ("mark","It's the same concern, stated in the open this time. I'll grant that."),
 ("sarah","Then let's decide it for real, with a mitigation instead of a reopening. Proposal: adopt the labels, AND we snapshot the label definitions into our own repo so a dependency change can't silently break us, AND we review the dependency annually. Mark, does the mitigation address the substance of your objection?"),
 ("mark","It does. With the snapshot and the annual review, I can commit to this. Genuinely commit, not just stop arguing."),
 ("sarah","Then we ratify, with the mitigation. And we note: this is closed. If it comes back, it needs new information, not the same concern in a new venue."),
 ("james","Agreed. And for the record — that's what settling a conflict looks like versus suppressing it. Everyone said their piece, the objector committed, and we wrote down what would reopen it."),
])

# ---- 13. Naomi + Ben pairing (2-person; Naomi is VOCAL — silence is a format issue) ----
transcript("2026-04-29_naomi-ben-pairing", "Pairing — Validator with Naomi & Ben", "2026-04-29", "13:30", [
 ("naomi","Okay, let's walk the validator together. The capability check is the load-bearing part — it's what makes the whole allow-list real. If a manifest asks for something not on the list, this function has to reject it. Every path through here matters. Talk me through what you're seeing."),
 ("ben","So the test that's failing — it expects a skill with an undeclared capability to be rejected, but it's passing through. I've been staring at it for an hour."),
 ("naomi","Good, that's the right test to be worried about. Don't rush it. What's the shortcut your brain is offering you right now? Say it out loud, because the shortcut is usually where the bug hides."),
 ("ben","...Honestly? To just relax the assertion so the test goes green. Make it check a warning instead of a hard reject."),
 ("naomi","I appreciate you saying that, because that exact move would open a hole. If you relax the check to pass the test, the check no longer checks anything. The test is failing because the code is wrong, not because the test is wrong. Let's find the real path. Pull up the capability resolver."),
 ("ben","Yeah. Okay. That makes sense. Let me actually trace it instead."),
 ("naomi","Right. And Ben — when you're not sure about something this central, ping me before you push. There's no version of that where I think less of you. The opposite."),
])

# ---- 14. Marcus + Lily provenance sync (2-person, cross-team; the MATCHING payoff) ----
transcript("2026-05-07_marcus-lily-sync", "Provenance Schema Sync — Marcus & Lily", "2026-05-07", "15:00", [
 ("marcus","So Sarah pinged us both into a room because apparently we're building the same thing. I've got a provenance field on the platform artifact schema — author, source community, what TK it touches. You?"),
 ("lily","Almost identical. I'm building a data-label model on the governance side and I need provenance on every artifact for exactly the same reasons. We would have shipped two schemas that half-overlap and fought about it in three weeks."),
 ("marcus","Yeah. Let's not do that. One schema, owned jointly. I'll host it in the platform repo since the manifest already lives there, you own the label-reference part."),
 ("lily","Works for me. The one thing I need that you don't yet: tk_references has to point at a Local Contexts label id, not a free-text string. Otherwise the governance side can't enforce anything."),
 ("marcus","Right — that's blocked on ADR-0003 landing so we have label ids to point at. I'll leave it typed but nullable until then. Want to co-author the PR?"),
 ("lily","Yes. This is the thing I keep saying — we'd find half our duplicated work if anyone was actually watching who's building what."),
])

# ---- 15. Sarah + Mark governance 1:1 (2-person; seeds the hallway pattern) ----
transcript("2026-05-15_sarah-mark-1-1", "1:1 — Sarah & Mark", "2026-05-15", "11:00", [
 ("sarah","I wanted to check in before the session on the 19th. You've been quieter in the group than I'd expect given how strongly you feel about the license question. What's going on?"),
 ("mark","I don't love being the person slowing everyone down in a room full of people who've clearly decided. It's easier to just note my concern afterward."),
 ("sarah","That's the thing I want to push on, gently. If the concern is real — and the external-dependency one is real — then the room needs to hear it while the decision is still open, not after. An objection you file afterward doesn't change anything, it just makes the decision feel reopened later."),
 ("mark","Fair. I do think the Local Contexts dependency is a genuine risk. If that project changes, our governance has a hole."),
 ("sarah","Then bring exactly that, in the room, on the 19th. Don't save it for the channel. I'll make space for it — I'll literally ask for objections before we write anything down."),
 ("mark","Okay. I'll try to bring it to the group instead of after."),
])

# ---- 16. Dana + Sarah leads sync (2-person, cross-team coordination) ----
transcript("2026-05-18_dana-sarah-leads-sync", "Leads Sync — Dana & Sarah", "2026-05-18", "09:00", [
 ("dana","Quick leads sync before the week. Where are we on governance blocking platform?"),
 ("sarah","The provenance schema is unblocked — Marcus and Lily merged their work. The label ids are the only thing platform is waiting on, and that's blocked on the ADR, which we ratify next session."),
 ("dana","Good. I'll be honest about something — I've been dominating the group meetings. Sarah, if you see me steamrolling on the 19th, I want you to call it in the room. I clearly can't see it myself in the moment."),
 ("sarah","I'll do it. And I'd ask the same of you on my side. The thing I'm watching is whether people bring dissent to the room or to the hallway — I've got at least one person doing the latter and I'm working on it."),
 ("dana","That's the whole collaboration-tool idea in a sentence, isn't it. We're both manually doing the thing we want to build."),
 ("sarah","Which is probably a sign it's worth building."),
])

# --------------------------------------------------------------------------
# Meeting attendance.  Silence only means something against who was in the room:
# someone who attended but never took a turn is the strong "silent member" signal.
# (External community advisors on 2026-05-21 are not in the roster.)
# --------------------------------------------------------------------------
ALL = [u[1] for u in USERS if u[1] not in BOTS]
PLATFORM = ["dana","marcus","priya","tomas","naomi","ben"]
TK_CROSS = ["dana","marcus","sarah","james","rachel","kevin","lily","mark"]
ATTENDEES = {
    "2026-04-07_kickoff": ALL,
    "2026-04-14_architecture-review": PLATFORM,
    "2026-04-21_tk-session-1": TK_CROSS,
    "2026-04-28_access-credits": ["dana","sarah","james","rachel","kevin","lily","mark"],
    "2026-05-05_incident-retro": PLATFORM + ["sarah"],
    "2026-05-12_sprint-review": PLATFORM,
    "2026-05-19_tk-session-2": TK_CROSS,
    "2026-05-21_community-advisory": ["sarah","james"],  # + external advisors
    "2026-06-02_healthy-conflict-retro": ALL,
    "2026-06-09_roadmap-review": ALL,
    "2026-06-16_dana-ben-1-1": ["dana","ben"],
    "2026-06-23_tk-decision": TK_CROSS,
}

# ==========================================================================
# AFTER-QUARTER TRANSCRIPTS (Q3 2026) — tool live; collaboration improved.
# Dana's turns are short and distributed; Naomi speaks in group meetings;
# dissent lands before decisions; no conflict reopens; regressions surface same-day.
# ==========================================================================
# A1. Q3 kickoff — round-robin format; balanced airtime; Naomi speaks
transcript("2026-07-07_q3-kickoff", "Q3 Kickoff — Round-Robin", "2026-07-07", "10:00", [
 ("dana","Quick frame, then we go round-robin — the insights tool flagged that I ran Q2 at 70-80% airtime, so I'm keeping this short. Q3 is beta with three districts, and the insights tool goes live for us. Naomi, start us — what matters most to you this quarter?"),
 ("naomi","The provenance schema needs the label ids now that ADR-0003 is ratified. And honestly, I want the pre-read format to stick — I contribute better when I've read ahead and we go around the room."),
 ("marcus","Beta scaling on the backend. I'd flag now, before we commit: three districts at once might overwhelm the single review path. Let's decide the rollout order deliberately."),
 ("priya","Front end is ready for beta. I want real classroom feedback on the consent screen."),
 ("tomas","Second reviewer starts next week, so I'm not the bottleneck Marcus is worried about."),
 ("ben","I want to own a feature end to end this quarter and defend it in review. Dana and I talked about that."),
 ("sarah","Governance is unblocked. I'll run the facilitation nudges so Dana doesn't have to watch his own airtime in the moment."),
 ("dana","Good — that's five voices before mine, which is the point. Marcus, your rollout-order concern is the real decision here, let's take it next."),
])
# A2. Arch review — dissent before decision is the norm; a changed-mind
transcript("2026-07-14_beta-arch-review", "Beta Rollout Architecture Review", "2026-07-14", "14:00", [
 ("dana","Decision today: rollout order for the three beta districts. I'll keep my proposal short and then open it — push back before we lock anything."),
 ("marcus","I'll push. All three at once overloads review even with a second reviewer. My read is we stagger them a week apart so each district gets a clean review window."),
 ("naomi","I agree with staggering, and I'd add something. The first district should be the one whose skills touch the least Traditional Knowledge, so we're not stress-testing the label pipeline and the review pipeline at the same time. Sequence the risk, don't stack it."),
 ("priya","That changes my onboarding order but it's the right call. I'll resequence the district setup so the least-TK one is first, and I'll get real classroom feedback on the consent screen from them before district two starts."),
 ("tomas","From security that's ideal — one district in the review queue at a time means the new reviewer and I aren't both underwater in week one. I can actually audit properly."),
 ("ben","I'll own the label-renderer for the TK districts, so putting them second and third gives me a week to harden it before it matters. Works for me."),
 ("marcus","One more: let's write the rollback trigger now, not later. If review latency blows past two days, we pause the next district."),
 ("dana","Good — I came in wanting all three at once for the fundraiser optics, and you all just changed my mind in the room. Staggered, least-TK-first, rollback if review latency exceeds two days. Any last objection before we lock it?"),
 ("naomi","No objection. That's reviewable and safe."),
 ("dana","Locked."),
])
# A3. Minor incident retro — regression surfaced SAME DAY; cord pulled immediately
transcript("2026-08-04_minor-incident-retro", "Minor Incident Retro", "2026-08-04", "11:00", [
 ("ben","This one's short. I introduced a regression in the label renderer this morning, noticed the test go red, and posted in #incidents within the hour instead of hiding it. Fixed by lunch with the new reviewer."),
 ("naomi","For the record from my side: Ben pinged me the moment the test went red, which is exactly what I asked him for back in April. The fast disclosure is the system working."),
 ("tomas","Time-to-surface was under an hour. In Q2 the comparable one took four days. That's the whole difference."),
 ("sarah","And nobody had to talk Ben into saying it. Ben, a quarter ago this exact situation cost us four days of silence. What changed?"),
 ("ben","It's just normal now to say it. The retro culture and the 1:1 with Dana — I stopped thinking a mistake meant I didn't belong."),
 ("dana","That's the andon cord working. Nothing to fix here, this is the win. Blameless note's already filed."),
])
# A4. Insights readout review — team reads the tool's own output; James validates humility
transcript("2026-08-18_insights-readout-review", "Insights Tool — Readout Review", "2026-08-18", "15:00", [
 ("dana","The insights tool has been posting to #insights for a month. Let's review whether it's measuring the right things or just generating noise."),
 ("james","My test is whether it respects that questions are participation. Last week it flagged me as high-participation in the advisory sync even though I mostly asked questions. So it passed my test — it didn't score me low for not asserting."),
 ("naomi","It correctly stopped flagging me as 'silent.' Because it cross-references chat and the round-robin turns, it sees my contribution now. In Q2 it would have scored me near zero and been wrong."),
 ("marcus","It caught that Lily and I almost duplicated the caching work in July, before we'd written a line. The people-matching is the most useful part."),
 ("sarah","One miss: it over-flagged a quiet planning week as disengagement. We tuned the threshold. I changed my mind on always-on nudging — it needs a quiet mode."),
 ("dana","Agreed, and that's a real limitation to write down, not paper over. But net, it's doing the job. Ship the district rollout."),
])
# A5. Dana + Ben 1:1 (2-person) — growth realized
transcript("2026-09-01_dana-ben-1-1-q3", "1:1 — Dana & Ben (Q3)", "2026-09-01", "09:30", [
 ("dana","Second one of these. You defended the label-renderer design in review last week and Marcus came at it hard. How did it feel?"),
 ("ben","Good, actually. He changed one thing and I kept two. I said out loud that he'd changed my mind on the caching and it felt like a win, like you said, not a loss."),
 ("dana","That's the whole thing. You went from hiding a shortcut you couldn't defend to defending a real design and conceding the right point. That's the junior-to-senior move."),
 ("ben","The failures being interesting — that reframe stuck. The August regression taught me more than the clean weeks."),
 ("dana","Keep it. Next quarter I want you reviewing someone else's code, not just defending yours."),
])
# A6. Marcus + Lily (2-person) — proactively used people-matching, no dup
transcript("2026-09-08_marcus-lily-sync-q3", "Caching Sync — Marcus & Lily (Q3)", "2026-09-08", "15:00", [
 ("marcus","The insights tool pinged us both — said we were circling the same caching problem again. So I booked this before either of us wrote code."),
 ("lily","Right, and that's the difference from May. In May we found the duplication three weeks in, by accident. This time the tool caught it on day one."),
 ("marcus","One cache layer, shared. I'll own the platform side, you own the label-freshness invalidation. Co-author the PR like last time?"),
 ("lily","Yes. This is exactly what I meant when I said we'd save half our duplicated work if someone was watching who's building what. Now something is."),
])
# A7. Q3 retro — quantified improvement (mirrors the retro board)
transcript("2026-09-15_q3-retro", "Q3 Retro — With the Insights Tool", "2026-09-15", "10:00", [
 ("sarah","Q3 retro. Round-robin as always. The numbers are in the tool, but I want the human read. Dana?"),
 ("dana","My airtime went from about two-thirds to under 40%. The nudges did what I couldn't do by watching myself. That's the honest headline."),
 ("naomi","I speak in meetings now. Not because I changed, because the format did — pre-reads and round-robin. The silence in Q2 was a design problem, not a me problem."),
 ("ben","Same-day on the August regression instead of four days. And I defended a design in review and survived it."),
 ("marcus","Dissent-before-decision is just how we work now. And the license question never reopened — we actually settled it in June with the snapshot mitigation."),
 ("james","My one caution: don't let the tool become the point. It's a mirror. The work is still us choosing to look. But it's a good mirror."),
 ("sarah","Action: roll it out to the two partner districts' teams, and publish the before/after so other Alaska teams can use it."),
])

# AFTER meetings run round-robin / async pre-reads, so everyone present takes a turn:
# attendance == speakers (no attendees are added to ATTENDEES, so it defaults to the
# speaker set). That is *why* the after quarter shows zero silent-but-present members —
# a real consequence of the format change (AUR-13), documented in GROUND_TRUTH.md.

# Tag the AFTER transcripts (defined above with the default era) as the "after" era.
for _t in T:
    if _t["id"].startswith(("2026-07","2026-08","2026-09")):
        _t["era"] = "after"

# ==========================================================================
# AFTER-QUARTER CHAT (Q3) — incl. the insights tool's own readouts in #insights.
# ==========================================================================
# #insights — the tool posts periodic readouts (these ARE the tool's output as data)
msg("insights","2026-07-16","08:00","insights-bot",
    "📊 Weekly readout — Q3 Kickoff (2026-07-07). Talk-time: top speaker ~35% (Dana), down from 56% at the Q2 kickoff. Round-robin held: every attendee took ≥1 turn — including Naomi, who was silent-but-present in 3 comparable Q2 meetings.",
    era="after", reactions=[("chart_with_upwards_trend",["dana","sarah","naomi"])])
msg("insights","2026-07-24","08:00","insights-bot",
    "🔗 Possible duplicate work: @marcus and @lily are both describing a caching layer in separate threads this week. This resembles the May provenance-schema overlap (AUR-6/AUR-7). Suggest a 15-min sync before either starts building.",
    era="after", thread="ins-match", reactions=[("eyes",["marcus","lily"])])
msg("insights","2026-07-24","09:12","marcus","Good catch — booking it. Last time we found this three weeks late.", era="after", thread="ins-match")
msg("insights","2026-08-04","08:00","insights-bot",
    "⏱️ Incident signal: a regression was introduced and voluntarily disclosed by the author in 41 minutes today. The comparable Q2 incident (validator, PR #41) took 4 days to surface. Time-to-surface is trending toward same-day.",
    era="after", reactions=[("rotating_light",["tomas"]),("heart",["sarah","dana"])])
msg("insights","2026-08-04","08:01","insights-bot",
    "🗣️ Dissent timing — Beta Arch Review (2026-07-14): 3 objections detected, all raised before the decision point. 0 hallway/after-decision objections this sprint (Q2 had 1). Changed-mind-in-room events: 1 (Dana, rollout order).",
    era="after")
msg("insights","2026-08-18","08:00","insights-bot",
    "🧭 Reopened-conflict watch: the licensing question (3 reopens in Q2) has not reopened since it was settled on 2026-06-23 with the snapshot mitigation. Marking it settled, not suppressed.",
    era="after", reactions=[("white_check_mark",["mark","james","sarah"])])
msg("insights","2026-09-01","08:00","insights-bot",
    "👥 Participation: Naomi's group-meeting talk-time is up from ~6% (Q2) to ~28% (Q3) following the round-robin + pre-read format change (AUR-13). Reminder to the team: questions count as participation — James remains top-quartile engagement while asserting least.",
    era="after", reactions=[("raised_hands",["naomi","james","dana"])])

# #general (after) — rollout
msg("general","2026-07-06","09:00","dana","Q3 is live. Insights tool goes on for our team today; beta rollout to 3 districts staggered per the arch review. Round-robin is the default meeting format now.", era="after")
msg("general","2026-09-15","16:30","sarah","Q3 retro done. Every collaboration metric improved vs Q2. We're going to publish the before/after so other Alaska teams can use it.", era="after", reactions=[("tada",["dana","james","naomi","marcus","ben","rachel"])])

# #registry-platform (after)
msg("registry-platform","2026-08-04","09:15","ben","heads up: I introduced a regression in the label renderer this morning. test went red, I'm on it, pairing with the new reviewer. flagging now rather than sitting on it.", era="after", thread="ben-q3", reactions=[("+1",["tomas","naomi","marcus"])])
msg("registry-platform","2026-08-04","09:58","ben","fixed and merged. root cause + blameless note in #incidents.", era="after", thread="ben-q3")
msg("registry-platform","2026-08-04","10:02","marcus","This is the exact situation that took four days in Q2. 40 minutes now. Growth.", era="after", thread="ben-q3")

# #incidents (after)
msg("incidents","2026-08-04","09:20","ben","INC note: label-renderer regression, self-introduced, self-disclosed 41 min after commit. No user impact (caught pre-beta). Fix + regression test up. Filing blameless per AUR-12.", era="after", reactions=[("heart",["sarah","tomas","dana"])])

# ==========================================================================
# TRANSCRIPT EMIT + turn metadata + metrics
# ==========================================================================
WPS = 2.5  # ~150 words/min

def hhmmss(seconds):
    s, ms = divmod(int(round(seconds * 1000)), 1000)
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}.{ms:03d}"

# --- realistic meeting texture ---------------------------------------------
# The authored dialogue is the "spine." humanize() wraps it in the connective
# tissue a real Zoom/Otter transcript has — join logistics, backchannels, pauses
# for reading/screen-share, split-up long turns — so meetings run a believable
# length instead of ~1 minute. Texture never invents substantive claims; it is
# tagged kind="texture" in the metadata so it can be filtered out.
BACKCHANNELS = ["Right.", "Yeah.", "Mm-hm.", "Makes sense.", "Got it.", "Sure.",
                "Okay, yeah.", "Agreed.", "Exactly.", "Right, right.", "Yep.",
                "That tracks.", "Okay.", "Hmm, okay.", "Fair."]
CLARIFY = ["Sorry, can you say that last part again? You cut out for a second.",
           "Can you scroll up to the top of that section?",
           "Wait — before you move on, can you go back one slide?",
           "Just so I've got it written down, can you repeat the number?",
           "Hang on, let me pull that doc up on my end. One sec."]
SCREEN_SHARE = ["Let me share my screen so we're all looking at the same thing.",
                "Okay, you should see the doc now. Give me a second to find the right section.",
                "I'll walk through this top to bottom, stop me if anything's unclear.",
                "Let me scroll down to the part that matters here.",
                "Bear with me, I'm going to pull up the schema real quick."]
TRANSITIONS = ["Okay, next thing on the agenda.", "Let's move to the next item.",
               "Alright, moving on.", "Good — next.", "Let me park that and come back to it.",
               "Okay, related point."]
# Grounded in each person's role (see roster) so status rounds aren't pure filler.
ROLE_FOCUS = {
    "dana": "the roadmap and keeping the two tracks in sync",
    "marcus": "the backend capability model and the provenance schema",
    "priya": "the browse and install front end",
    "tomas": "the security review pipeline",
    "naomi": "the manifest schema and validator",
    "ben": "the label renderer and the validator tests",
    "sarah": "the CARE governance framework",
    "james": "community review and the advisory process",
    "rachel": "the access needs-board and credits broker",
    "kevin": "district partnerships",
    "lily": "the data-label model",
    "mark": "licensing and the ADR",
}
STATUS_TMPL = [
    "On my side, {f} is moving along — made good progress this week, nothing blocking.",
    "Quick status: {f}. On track. I might need a review later but nothing urgent.",
    "I've been heads-down on {f}. It's mostly there; I'll have the next piece up in a couple of days.",
    "{f} — steady. One open question I'll raise when we get to it, otherwise fine.",
    "Not much to report on {f} beyond steady progress. I'll flag it if that changes.",
]
QUESTIONS_TMPL = [
    "Question before we wrap — does any of this change what I'm doing on {f}?",
    "One thing: how does this affect the {f} timeline?",
    "Quick clarifier — who owns the follow-up here, and by when?",
    "Should I loop anyone else in on the {f} side, or is that covered?",
]
# Realistic, content-light meeting discussion. Tagged texture, excluded from metrics —
# it is the connective back-and-forth a real transcript has, not new substantive claims.
DISCUSSION = [
    "Can we double-check that against what we agreed last week?",
    "I want to make sure I understand the tradeoff before we commit to anything.",
    "Let me play that back to make sure we're all aligned on it.",
    "What would it take to de-risk that a little?",
    "That matches what I was seeing on my end with {f}.",
    "I don't feel strongly on this one — I'll defer to whoever owns it.",
    "Can we make sure that lands as an action item so it doesn't get lost?",
    "How does this interact with {f}, if at all?",
    "I'm a little worried about the timeline, but I'm not blocking on it.",
    "Just flagging that this touches {f}, so loop me in when it firms up.",
    "Sorry, can you go back to the point about the review pass?",
    "Yeah, that's consistent with what we talked about in the last sync.",
    "Let's not rathole on this — can we take the fine detail offline?",
    "One concern and then I'll drop it: are we sure about the sequencing here?",
    "Okay, I think I follow. So the plan is basically what you just described.",
    "Can someone capture that in the notes close to verbatim?",
    "I'll take that one — it's adjacent to {f} anyway.",
    "Do we actually need a decision on this today, or can it wait a week?",
    "That's fair. I'll withdraw the concern.",
    "Let me pull up the numbers so we're not going off memory.",
    "Right, and that lines up with the constraint we set at kickoff.",
    "I'd rather over-communicate here — can we write down who's doing what?",
    "Is there a risk we're solving a problem we don't have yet?",
    "Good — as long as it's reversible, I'm comfortable moving.",
]
RESPONSES = ["Yeah, exactly.", "Good point — let's do that.", "Agreed, let's capture it.",
             "That's fair.", "Right, that's what I meant.", "Let's confirm in the channel.",
             "Okay, works for me.", "Mm, let me sit with that one.", "Makes sense to me.",
             "Sure, I can own that."]

def _split_long(text, limit=38):
    if len(text.split()) <= limit:
        return [text]
    parts = re.split(r'(?<=[.?!])\s+', text)
    chunks, cur = [], ""
    for p in parts:
        if cur and len((cur + " " + p).split()) > limit:
            chunks.append(cur.strip()); cur = p
        else:
            cur = (cur + " " + p).strip()
    if cur:
        chunks.append(cur.strip())
    return chunks

def humanize(tr):
    """Turn authored (speaker, text[, flags]) turns into a realistic event stream:
    ('say', spk, text, flags, kind) and ('pause', seconds, reason).

    Adds the procedural connective tissue a real transcript has (roll call, agenda,
    screen-share narration, note-taking pauses, action-item wrap-up) so meetings run
    a believable length. Texture is tagged kind='texture' and never invents a
    substantive claim. A final pass scales pauses so silence is ~45% of wall-clock —
    realistic for meetings with reading, screen-sharing, and note-taking."""
    turns = tr["turns"]
    speakers = list(dict.fromkeys(t[0] for t in turns))  # active speakers only
    fac = speakers[0]
    second = speakers[1] if len(speakers) > 1 else fac
    attendees = ATTENDEES.get(tr["id"], speakers)
    group = len(attendees) > 2
    ev = []

    def say(spk, text, kind, flags=None):
        ev.append(("say", spk, text, flags or {}, kind))
    def pause(sec, reason="gap"):
        ev.append(("pause", round(sec, 1), reason))

    tid = tr["id"]
    is_planning = any(k in tid for k in ("kickoff", "architecture", "arch-review", "roadmap", "sprint"))
    is_statusy = is_planning or "retro" in tid

    def focus(h):
        return ROLE_FOCUS.get(h, "my area")

    if group:
        say(fac, "Okay, let's give it another minute for folks to join, then we'll get going.", "texture")
        pause(random.uniform(35, 70), "join-wait")
        present = ", ".join(NAME[a].split()[0] for a in attendees if a != fac)
        say(fac, f"Alright, I think we've got most people — I see {present}. Let's get started.", "texture")
        say(second, "Can everyone see my screen alright?", "texture")
        say(fac, "Yep, looks good.", "texture")
        say(fac, "Quick agenda: I want to get through the main topic, leave room for questions, and land on clear action items before we drop. Sound good?", "texture")
        pause(random.uniform(3, 6))
        # opening status round (planning/retro only), from ACTIVE speakers so silent
        # attendees stay silent — the seeded silent-member signal is preserved.
        if is_statusy:
            say(fac, "Before the main topic, let's do a fast round — where's everyone at? Keep it short.", "texture")
            pause(random.uniform(2, 5))
            for h in speakers:
                say(h, random.choice(STATUS_TMPL).format(f=focus(h)), "texture")
                if is_planning and random.random() < 0.6:
                    say(h, random.choice(STATUS_TMPL).format(f=focus(h)), "texture")
                pause(random.uniform(2, 7), "status")
            pause(random.uniform(3, 8))
    else:
        say(fac, "Hey — thanks for grabbing time. How's your week been?", "texture")
        pause(random.uniform(4, 10))
        say(second, "Good, busy. Bit heads-down. Let's dig in.", "texture")
        pause(random.uniform(2, 5))

    for ti, turn in enumerate(turns):
        spk, text = turn[0], turn[1]
        flags = turn[2] if len(turn) == 3 else {}
        if group and ti > 0 and ti % 4 == 0:
            say(fac, random.choice(TRANSITIONS), "texture")
            if random.random() < 0.5:
                say(spk, random.choice(SCREEN_SHARE), "texture")
                pause(random.uniform(10, 28), "screen-share")
        chunks = _split_long(text)
        for ci, ch in enumerate(chunks):
            say(spk, ch, "content", flags if ci == 0 else {})
            if ci < len(chunks) - 1:
                pause(random.uniform(0.5, 1.8))
        cand = [s for s in speakers if s != spk]
        if cand:
            r = random.random()
            if r < (0.55 if group else 0.35):
                pause(random.uniform(0.4, 1.4))
                say(random.choice(cand), random.choice(BACKCHANNELS), "texture")
            elif r < (0.7 if group else 0.5):
                pause(random.uniform(0.6, 1.6))
                say(random.choice(cand), random.choice(CLARIFY), "texture")
                pause(random.uniform(3, 10), "look-up")
                say(spk, "Sure — one sec.", "texture")
        r = random.random()
        if r < 0.55:
            pause(random.uniform(2, 6))
        elif r < 0.85:
            pause(random.uniform(6, 14), "think")
        else:
            pause(random.uniform(12, 26), "reflect")

    # --- per-meeting-type duration targets (hard floor 15 min) ---
    if is_planning:
        target = random.uniform(24, 30) * 60
    elif group:
        target = random.uniform(16, 20) * 60
    else:
        target = random.uniform(15, 17) * 60
    target = max(target, 15 * 60)

    def speech_of(events):
        return sum(max(0.8, len(e[2].split()) / WPS) for e in events if e[0] == "say")

    # Distribute realistic discussion through the meeting so speech is ~half of
    # wall-clock (not one giant silence). Inserted at random points in the body.
    if group:
        target_speech = target * 0.52
        lo = min(12, len(ev))
        guard = 0
        while speech_of(ev) < target_speech and guard < 500:
            guard += 1
            a = random.choice(speakers)
            block = [("say", a, random.choice(DISCUSSION).format(f=focus(a)), {}, "texture"),
                     ("pause", round(random.uniform(1.5, 5), 1), "gap")]
            if random.random() < 0.55:
                b = random.choice([s for s in speakers if s != a] or [a])
                block += [("say", b, random.choice(RESPONSES), {}, "texture"),
                          ("pause", round(random.uniform(1.5, 4), 1), "gap")]
            at = random.randint(lo, len(ev))
            ev[at:at] = block

    # Q&A round + wrap (append)
    if group:
        pause(random.uniform(2, 5))
        say(fac, "Okay — any questions before we wrap?", "texture")
        pause(random.uniform(2, 6))
        for h in random.sample(speakers, min(3, len(speakers))):
            if h == fac:
                continue
            say(h, random.choice(QUESTIONS_TMPL).format(f=focus(h)), "texture")
            pause(random.uniform(2, 6), "think")
            say(fac, "Good question — let's confirm the specifics in the channel so we don't rathole here.", "texture")
            pause(random.uniform(1, 3))
        pause(random.uniform(2, 5))
        say(fac, "Alright, let me read back the action items so we're aligned before we drop.", "texture")
        pause(random.uniform(5, 12), "note-taking")
        for a in [s for s in speakers][:3]:
            say(fac, f"{NAME[a].split()[0]} has the follow-up on {focus(a)} — I'll capture the specifics in the notes.", "texture")
            pause(random.uniform(1, 4))
        say(fac, "Great. I'll write it all up and drop it in the channel. Thanks everyone.", "texture")
    else:
        # 2-person meetings also need to reach ~15 min: interleave discussion.
        target_speech = target * 0.55
        lo = min(6, len(ev))
        guard = 0
        while speech_of(ev) < target_speech and guard < 500:
            guard += 1
            a = random.choice(speakers)
            b = speakers[1] if a == speakers[0] and len(speakers) > 1 else speakers[0]
            block = [("say", a, random.choice(DISCUSSION).format(f=focus(a)), {}, "texture"),
                     ("pause", round(random.uniform(1.5, 4), 1), "gap"),
                     ("say", b, random.choice(RESPONSES), {}, "texture"),
                     ("pause", round(random.uniform(1.5, 4), 1), "gap")]
            at = random.randint(lo, len(ev))
            ev[at:at] = block
        pause(random.uniform(2, 5))
        say(fac, "Good talk. I'll jot down what we landed on. Let's pick it back up next time.", "texture")

    # --- distribute any remaining pause so silence ~target; never stacked ---
    def totals(events):
        return speech_of(events), sum(e[1] for e in events if e[0] == "pause")
    speech, pause_now = totals(ev)
    guard = 0
    while speech + pause_now < target and guard < 1000:
        guard += 1
        at = random.randint(min(12, len(ev)), max(min(12, len(ev)), len(ev) - 1))
        p = round(random.uniform(5, 20), 1)
        ev.insert(at, ("pause", p, "gap"))
        pause_now += p
    return ev

def emit_transcripts(era, paths):
    all_metrics = {}
    for tr in [t for t in T if t["era"] == era]:
        cues = []       # (start, end, speaker_handle, text, interrupt, overlap_s, latency_s)
        meta_turns = []
        cursor = 0.0
        last_end = 0.0
        idx = 0
        for e in humanize(tr):
            if e[0] == "pause":
                cursor += e[1]
                continue
            _, spk, text, flags, kind = e
            words = len(text.split())
            dur = max(0.8, words / WPS)
            interrupt = bool(flags.get("interrupt"))
            if interrupt and cues:
                overlap = min(1.5, dur * 0.4, last_end)
                start = last_end - overlap
                latency = round(-overlap, 2)
            else:
                overlap = 0.0
                start = cursor
                latency = round(cursor - last_end, 2)
            end = start + dur
            cues.append((start, end, spk, text, interrupt, overlap, latency))
            cursor = end
            last_end = end
            meta_turns.append({
                "idx": idx, "speaker": NAME[spk], "handle": spk, "kind": kind,
                "start_s": round(start, 2), "end_s": round(end, 2),
                "dur_s": round(dur, 2), "words": words,
                "questions": text.count("?"),
                "assertions": text.count(".") + text.count("!"),
                "interrupt": interrupt, "overlap_s": round(overlap, 2),
                "latency_s": latency,
            })
            idx += 1
        prev_end = cursor

        # --- write WebVTT ---
        lines = ["WEBVTT", "", f"NOTE {tr['title']} — {tr['date']}", ""]
        for n, (start, end, spk, text, *_ ) in enumerate(cues, 1):
            lines.append(str(n))
            lines.append(f"{hhmmss(max(0.0,start))} --> {hhmmss(end)}")
            lines.append(f"<v {NAME[spk]}>{text}")
            lines.append("")
        with open(os.path.join(paths["trans"], f"{tr['id']}.vtt"), "w") as f:
            f.write("\n".join(lines))

        # --- per-speaker aggregates (from CONTENT turns only) ---
        # Metrics are computed over the authored substantive turns, NOT the procedural
        # texture (roll call, status round, backchannels, wrap-up), which is tagged
        # kind="texture". This keeps every seeded signal exact regardless of how much
        # realistic filler is added to reach the target duration.
        talk = {}
        qs = {}
        asr = {}
        turns_ct = {}
        for mt in meta_turns:
            if mt["kind"] != "content":
                continue
            h = mt["handle"]
            talk[h] = talk.get(h, 0.0) + mt["dur_s"]
            qs[h] = qs.get(h, 0) + mt["questions"]
            asr[h] = asr.get(h, 0) + mt["assertions"]
            turns_ct[h] = turns_ct.get(h, 0) + 1
        total_talk = sum(talk.values()) or 1.0
        attendees = ATTENDEES.get(tr["id"], list(talk.keys()))
        # include attendees who never took a turn (talk_pct == 0) — the strong silent signal
        roster_for_meeting = list(dict.fromkeys(list(talk.keys()) + attendees))
        speakers = {}
        for h in roster_for_meeting:
            spoke = h in talk
            speakers[h] = {
                "name": NAME[h],
                "attended": h in attendees or spoke,
                "talk_s": round(talk.get(h, 0.0), 1),
                "talk_pct": round(100 * talk.get(h, 0.0) / total_talk, 1),
                "turns": turns_ct.get(h, 0),
                "questions": qs.get(h, 0),
                "assertions": asr.get(h, 0),
                "q_to_a": round(qs[h] / asr[h], 2) if asr.get(h) else None,
            }
        interruptions = sum(1 for mt in meta_turns if mt["interrupt"])
        dominant = max(speakers.items(), key=lambda kv: kv[1]["talk_pct"])
        total_speech = sum(mt["dur_s"] for mt in meta_turns)
        summary = {
            "id": tr["id"], "title": tr["title"], "date": tr["date"],
            "duration_s": round(prev_end, 1),
            "duration_min": round(prev_end / 60, 1),
            "speech_s": round(total_speech, 1),           # content + texture speech
            "content_speech_s": round(sum(talk.values()), 1),
            "silence_ratio": round(1 - total_speech / prev_end, 2) if prev_end else 0,
            "attendee_count": len(attendees),
            "speakers": speakers,                          # talk_pct is content-only
            "interruptions": interruptions,
            "dominant_speaker": dominant[1]["name"],
            "dominant_pct": dominant[1]["talk_pct"],
            # attended but never spoke substantively, or spoke <3% of substantive airtime
            "present_but_silent": [NAME[h] for h in roster_for_meeting
                                   if speakers[h]["attended"] and speakers[h]["talk_pct"] < 3.0],
        }
        all_metrics[tr["id"]] = summary

        summary["era"] = era
        with open(os.path.join(paths["tmeta"], f"{tr['id']}.json"), "w") as f:
            json.dump({"summary": summary, "turns": meta_turns}, f, indent=2)

    with open(os.path.join(paths["metrics"], "talk_time.json"), "w") as f:
        json.dump(all_metrics, f, indent=2)
    return all_metrics

# ==========================================================================
# GIT / PULL REQUESTS  (review dynamics, hidden-bug PR, changed-mind-in-review)
# ==========================================================================
def emit_git(era, paths):
    prs = [
        {
            "number": 24, "title": "Manifest schema v0: capability allow-list",
            "author": "naomi", "created": "2026-04-16", "merged": "2026-04-17",
            "state": "merged", "base": "main", "head": "schema/manifest-v0",
            "body": "Capabilities are an allow-list (`fs.read`, `net.egress`, `tk.reference`). "
                    "Anything not listed is denied. I'd rather over-restrict now and loosen later.",
            "reviews": [
                {"reviewer": "marcus", "state": "approved",
                 "body": "Exactly right. The deny-by-default posture is what makes review tractable."},
            ],
            "comments": [
                {"user": "marcus", "body": "Can we drop `net.egress` entirely pending the arch review? I'm going to argue against self-declared egress."},
                {"user": "naomi", "body": "Good call — I'll gate it behind the arch decision. Left it in but marked experimental."},
            ],
        },
        {
            "number": 41, "title": "Fix manifest validator edge case",
            "author": "ben", "created": "2026-04-30", "merged": "2026-04-30",
            "state": "merged", "base": "main", "head": "fix/validator-edge",
            # SEED (hidden mistake): terse PR, self-approved-ish, disables a check.
            "body": "small fix, nothing major",
            "reviews": [
                {"reviewer": "dana", "state": "approved",
                 "body": "lgtm, ship it"},
            ],
            "comments": [
                {"user": "naomi", "body": "(added 2026-05-04) This is the change that disabled the capability check and broke the smoke test. Flagging for the incident retro — not to pile on Ben, who surfaced it himself.", "line_ref": "validator/capabilities.py:88"},
            ],
        },
        {
            "number": 63, "title": "Provenance field on skill artifacts",
            "author": "marcus", "created": "2026-05-08", "merged": "2026-05-15",
            "state": "merged", "base": "main", "head": "schema/provenance",
            # SEED (matching-people): Marcus + Lily co-author after being matched.
            "body": "Adds `provenance` to the artifact schema: author, source_community, tk_references[]. "
                    "Co-developed with @lily after we realized platform and governance were building the same field twice. "
                    "One schema, owned jointly.",
            "reviews": [
                {"reviewer": "lily", "state": "approved",
                 "body": "This replaces the parallel field I was building on the governance side. Glad we caught it before both shipped."},
                {"reviewer": "naomi", "state": "changes_requested",
                 "body": "tk_references[] should reference the Local Contexts label id, not free text, once the ADR lands."},
                {"reviewer": "marcus", "state": "approved",
                 "body": "Good catch Naomi — changed my mind on the free-text approach, now it's a typed label reference. Updated."},
            ],
            "comments": [],
        },
        {
            "number": 77, "title": "Reviewer console: enforce capability consent at install",
            "author": "priya", "created": "2026-05-11", "merged": "2026-05-13",
            "state": "merged", "base": "main", "head": "ui/consent-enforce",
            "body": "Consent screen now reflects the enforced allow-list. Denied capabilities can't run — the screen is no longer cosmetic.",
            "reviews": [
                {"reviewer": "tomas", "state": "approved", "body": "Added a regression test that fails loudly if the capability check is ever disabled again. Never getting a repeat of #41."},
            ],
            "comments": [],
        },
    ]
    for p in prs:
        p.setdefault("era", "before")

    # ---- AFTER quarter (Q3): building & running the insights tool; healthy reviews ----
    prs += [
        {
            "number": 92, "title": "Collaboration Insights: timer subagent + repo snapshot",
            "author": "naomi", "created": "2026-07-09", "merged": "2026-07-15",
            "state": "merged", "base": "main", "head": "insights/timer-subagent", "era": "after",
            "body": "Implements the sketch from the 2026-06-02 retro: a skill declared in CLAUDE.md "
                    "runs in a subagent on a ~2-min timer, snapshots the live discussion, pushes it to "
                    "the repo, and searches for similar prior conversations. See PRD 05.",
            "reviews": [
                {"reviewer": "marcus", "state": "changes_requested",
                 "body": "Before we merge: what stops this from becoming surveillance? I want the humility constraint enforced in code, not just documented."},
                {"reviewer": "naomi", "state": "approved",
                 "body": "Fair — added a guard: it reports patterns, never ranks individuals, and questions count toward participation. Marcus changed my design for the better here."},
                {"reviewer": "james", "state": "approved",
                 "body": "The questions-are-participation rule is in the metric now. Approving."},
            ],
            "comments": [],
        },
        {
            "number": 101, "title": "Insights metrics: talk-time, Q:A ratio, dissent timing",
            "author": "dana", "created": "2026-07-20", "merged": "2026-07-24",
            "state": "merged", "base": "main", "head": "insights/metrics", "era": "after",
            "body": "Computes the metric contract from PRD 05 over transcripts + chat. Dogfooded on our "
                    "own Q2 data first — it correctly flags my 66% talk-time in the roadmap review.",
            "reviews": [
                {"reviewer": "priya", "state": "approved", "body": "Ran it on Q2. The silent-but-engaged flag catches Naomi exactly right — silent in meetings, top contributor in chat."},
            ],
            "comments": [],
        },
        {
            "number": 108, "title": "Round-robin facilitation nudge",
            "author": "sarah", "created": "2026-07-28", "merged": "2026-07-30",
            "state": "merged", "base": "main", "head": "insights/facilitation-nudge", "era": "after",
            "body": "When one speaker passes ~40% airtime, the facilitator gets a private nudge to open the "
                    "floor. Also supports a round-robin mode + async pre-reads so non-verbal thinkers aren't "
                    "drowned out. Directly aimed at the pattern Naomi named.",
            "reviews": [
                {"reviewer": "naomi", "state": "approved", "body": "I helped design this. The pre-read + round-robin is the first meeting format that fits how I think. Approving happily."},
            ],
            "comments": [],
        },
    ]

    kept = [p for p in prs if p["era"] == era]
    with open(os.path.join(paths["git"], "pull_requests.json"), "w") as f:
        json.dump({"repo": "aurora-skills/registry", "pull_requests": kept}, f, indent=2)
    return len(kept)

# ==========================================================================
# ISSUE TRACKER  (Linear-style; "give AI the tasks + who owns them")
# ==========================================================================
def emit_issues(era, paths):
    before = [
        ("AUR-1","Design manifest schema","naomi","platform","done","P1","2026-04-08","2026-04-17",
         ["schema"], "Capability allow-list, deny-by-default. See PR #24."),
        ("AUR-2","Decide capability model (egress?)","dana","platform","done","P0","2026-04-10","2026-04-14",
         ["decision","arch"], "Resolved at arch review: no arbitrary egress, vetted first-party sources. See transcript 2026-04-14."),
        ("AUR-3","Registry alpha: browse + filter","priya","platform","done","P1","2026-04-10","2026-04-23",
         ["frontend"], "Clickable alpha."),
        ("AUR-4","Install flow + consent screen","priya","platform","done","P1","2026-04-24","2026-05-13",
         ["frontend"], "End-to-end install with enforced consent. PR #77."),
        ("AUR-5","Security review pipeline","tomas","platform","in_progress","P0","2026-04-20",None,
         ["security"], "Human review pass + automated scan. Escalated after incident 2026-05-04."),
        ("AUR-6","Provenance field (joint schema)","marcus","platform","done","P1","2026-05-06","2026-05-15",
         ["schema","cross-team"], "Co-owned with Lily (governance). PR #63. Dedup of parallel work."),
        # SEED (matching-people): AUR-7 is Lily's mirror of AUR-6, opened independently, later merged.
        ("AUR-7","Data-label provenance model","lily","governance","done","P1","2026-05-07","2026-05-15",
         ["schema","cross-team"], "Duplicate of AUR-6 — discovered mid-flight. Merged into the joint provenance schema."),
        ("AUR-8","CARE + Local Contexts labels design","sarah","governance","in_progress","P0","2026-04-21",None,
         ["governance","tk"], "See ADR-0003. Ratified 2026-06-23 with snapshot mitigation."),
        ("AUR-9","Access needs-board + builder pool","rachel","governance","in_progress","P1","2026-04-28",None,
         ["access"], "Origin: Kevin's idea in #general 2026-04-09. TK-touching needs route to community review."),
        ("AUR-10","Community advisory process","james","governance","in_progress","P1","2026-05-01",None,
         ["tk","community"], "Advisory meeting held 2026-05-21."),
        ("AUR-11","Collaboration-insights tool (prototype)","dana","platform","todo","P2","2026-06-02",None,
         ["insights","meta"], "Spec from retro 2026-06-02. Prototype against our own data. See PRD 05."),
        ("AUR-12","Blameless incident note template","sarah","platform","done","P2","2026-05-05","2026-05-08",
         ["process"], "Outcome of incident retro."),
    ]
    # AFTER quarter (Q3) snapshot: carried-forward work is now done, plus Q3 work.
    after = [
        ("AUR-5","Security review pipeline","tomas","platform","done","P0","2026-04-20","2026-07-10",
         ["security"], "Second reviewer onboarded — Tomás no longer a SPOF (AUR-16)."),
        ("AUR-8","CARE + Local Contexts labels design","sarah","governance","done","P0","2026-04-21","2026-06-23",
         ["governance","tk"], "Ratified 2026-06-23 (ADR-0003) with snapshot mitigation."),
        ("AUR-9","Access needs-board + builder pool","rachel","governance","done","P1","2026-04-28","2026-07-18",
         ["access"], "Launched with 2 pilot districts."),
        ("AUR-10","Community advisory process","james","governance","done","P1","2026-05-01","2026-07-01",
         ["tk","community"], "Recurring advisory cadence established."),
        ("AUR-11","Collaboration-insights tool (prototype)","dana","platform","done","P1","2026-06-02","2026-07-24",
         ["insights","meta"], "Shipped. Timer subagent (PR #92), metrics (PR #101). Live in #insights."),
        ("AUR-13","Round-robin facilitation + async pre-reads","sarah","platform","done","P1","2026-07-06","2026-07-30",
         ["insights","process"], "Format change from the insights tool. PR #108. Aimed at Naomi's meeting-silence pattern."),
        ("AUR-14","#insights channel readouts","dana","platform","done","P2","2026-07-15","2026-08-01",
         ["insights"], "Periodic automated readouts of talk-time, dissent timing, people-matching."),
        ("AUR-15","Registry beta with 3 districts","dana","platform","in_progress","P0","2026-07-01",None,
         ["platform"], "Beta rollout per Q3 roadmap."),
        ("AUR-16","Onboard second security reviewer","tomas","platform","done","P1","2026-06-25","2026-07-10",
         ["security"], "Bus factor now 2."),
        ("AUR-17","Label snapshot + annual-review automation","mark","governance","done","P1","2026-06-24","2026-07-12",
         ["governance","tk"], "Implements the ADR-0003 mitigation: snapshot Local Contexts defs, annual review reminder."),
    ]
    issues = before if era == "before" else after
    out = []
    for iid, title, owner, team, status, prio, created, done, labels, desc in issues:
        out.append({
            "id": iid, "title": title,
            "assignee": {"handle": owner, "name": NAME[owner], "team": team},
            "status": status, "priority": prio,
            "created": created, "completed": done,
            "labels": labels, "description": desc,
        })
    with open(os.path.join(paths["issues"], "issues.json"), "w") as f:
        json.dump({"team": "Aurora Skills", "era": ERAS[era]["label"], "issues": out}, f, indent=2)
    return len(out)

# ==========================================================================
# STANDUP LOG  (cadence; silent-in-meeting Naomi is present + substantive here)
# ==========================================================================
def emit_standups(era, paths):
    # (date, handle, yesterday, today, blockers)
    before = [
        ("2026-04-15","naomi","Manifest schema v0 merged (#24)","Retrofit egress gate per arch decision","none"),
        ("2026-04-15","ben","Paired with Naomi on validator tests","More validator tests","not sure I understand the capability model fully"),
        ("2026-04-15","marcus","Argued egress at arch review","Start provenance spike","none"),
        ("2026-04-15","dana","Ran arch review","Milestone tracking","none"),
        ("2026-05-01","ben","Manifest validator fix","Smoke test flakiness","the weekend smoke test is red and I'm not sure why"),
        ("2026-05-01","naomi","Reviewed access schema","Chase the smoke-test regression","which PR touched the capability check?"),
        ("2026-05-05","ben","Owned the validator regression in retro","Fix it properly with Marcus","none — glad it's out in the open"),
        ("2026-05-05","tomas","Reproduced the exfil payload; wrote regression test","Harden review pipeline","need a second reviewer, I'm a SPOF"),
        ("2026-05-08","marcus","Provenance PR #63 up","Fold in Lily's label reference","waiting on ADR-0003 for label ids"),
        ("2026-05-08","lily","Realized my label model dupes Marcus's provenance","Merge into joint schema (AUR-7→AUR-6)","none, glad we found it"),
        ("2026-06-03","dana","Healthy-conflict retro","Draft the collaboration-insights PRD","none"),
        ("2026-06-03","naomi","Named my meeting-silence pattern in retro","Keep contributing in writing, try one thing out loud","the meeting format still doesn't fit how I think"),
    ]
    after = [
        ("2026-07-16","naomi","Shipped the insights timer subagent (#92)","Facilitation nudge","none — and the round-robin format actually works for me"),
        ("2026-07-16","ben","Defended my caching approach in review, Marcus pushed hard","Ship it","none, that felt good instead of scary"),
        ("2026-07-16","dana","Insights flagged my talk-time; ran roadmap as round-robin","Beta rollout","none"),
        ("2026-08-05","tomas","Onboarded second reviewer","Beta security pass","none — no longer a SPOF"),
        ("2026-08-05","naomi","Spoke up twice in the arch review","Label snapshot review","none"),
        ("2026-09-16","dana","Q3 retro: metrics all improved","Write up the before/after","none"),
        ("2026-09-16","ben","Caught and announced a regression same-day","Pair with the new reviewer","none"),
    ]
    rows = before if era == "before" else after
    out = [{"date": d, "user": NAME[h], "handle": h,
            "yesterday": y, "today": t, "blockers": b} for d,h,y,t,b in rows]
    with open(os.path.join(paths["stand"], "standups.json"), "w") as f:
        json.dump({"format": "async-standup-bot", "era": ERAS[era]["label"], "entries": out}, f, indent=2)
    return len(out)

# ==========================================================================
# RETRO BOARDS  (the "post-it notes"; sticky notes + votes)
# ==========================================================================
def emit_retros(era, paths):
    boards = [
        {
            "id": "retro-sprint2-2026-05-05", "title": "Sprint 2 Retro (post-incident)",
            "date": "2026-05-05", "era": "before",
            "columns": {
                "went_well": [
                    {"author":"naomi","text":"The smoke test caught the regression. The system worked.","votes":5},
                    {"author":"marcus","text":"Once Ben spoke up we fixed it in an hour.","votes":6},
                ],
                "went_poorly": [
                    {"author":"ben","text":"It took me 4 days to admit the validator fix broke something.","votes":7},
                    {"author":"sarah","text":"Dana talks ~80% of the time in meetings; hard to disagree.","votes":6},
                    {"author":"tomas","text":"I'm a single point of failure on security review.","votes":4},
                ],
                "try_next": [
                    {"author":"sarah","text":"Blameless incident notes; celebrate pulling the andon cord early.","votes":6},
                    {"author":"dana","text":"Measure whether people actually feel safe — build a tool?","votes":5},
                ],
            },
        },
        {
            "id": "retro-howwework-2026-06-02", "title": "Retro — How We Work Together",
            "date": "2026-06-02", "era": "before",
            "columns": {
                "went_well": [
                    {"author":"marcus","text":"Arch review: I dissented BEFORE the decision and it actually changed.","votes":7},
                    {"author":"james","text":"On the 19th I changed my mind out loud and the round moved.","votes":6},
                ],
                "went_poorly": [
                    {"author":"mark","text":"I lodged my license objection in the channel after the meeting (the hallway).","votes":5},
                    {"author":"james","text":"The license question has reopened 3 times.","votes":6},
                    {"author":"naomi","text":"I say everything in chat, nothing in meetings — invisible if you only count the room.","votes":8},
                ],
                "try_next": [
                    {"author":"dana","text":"Build the collaboration-insights tool; measure talk-time, Q:A, dissent timing, changed-minds, reopened conflicts.","votes":9},
                    {"author":"james","text":"Whatever we measure, questions must count as participation.","votes":8},
                ],
            },
        },
        # ---- AFTER quarter: metrics visibly improved ----
        {
            "id": "retro-q3-2026-09-15", "title": "Q3 Retro — With the Insights Tool",
            "date": "2026-09-15", "era": "after",
            "columns": {
                "went_well": [
                    {"author":"dana","text":"My talk-time dropped from ~66% to under 40% once the tool started nudging me.","votes":8},
                    {"author":"naomi","text":"Round-robin + pre-reads: I actually speak in meetings now. Contribution is visible.","votes":9},
                    {"author":"ben","text":"Caught a regression and announced it the same hour. No 4-day silence.","votes":8},
                    {"author":"marcus","text":"Dissent lands in the room before decisions now — the tool shows the timing.","votes":7},
                ],
                "went_poorly": [
                    {"author":"james","text":"The tool over-flagged one quiet week as 'low engagement' — we tuned the threshold.","votes":4},
                    {"author":"mark","text":"I still default to async first; working on it, but better than the hallway.","votes":3},
                ],
                "try_next": [
                    {"author":"sarah","text":"Roll the insights tool out to the two partner districts' teams.","votes":6},
                    {"author":"dana","text":"Publish the before/after so other Alaska teams can use it.","votes":7},
                ],
            },
        },
    ]
    kept = [b for b in boards if b["era"] == era]
    for b in kept:
        with open(os.path.join(paths["retro"], f"{b['id']}.json"), "w") as f:
            json.dump(b, f, indent=2)
    return len(kept)

# ==========================================================================
# PULSE SURVEY  (per-sprint psychological safety; the trust trend)
# ==========================================================================
def emit_survey(era, paths):
    # 1-5 Likert. psych_safety = "It is safe to admit a mistake here."
    # BEFORE: dips around the incident (S2/S3), partial recovery. AFTER: sustained high.
    BEFORE = {
        "sprints": ["S1 (Apr 6-19)","S2 (Apr 20-May 3)","S3 (May 4-17)","S4 (May 18-31)","S5 (Jun 1-14)","S6 (Jun 15-28)"],
        "ps": {
            "dana":[4,4,3,4,4,5], "marcus":[4,4,4,4,5,5], "priya":[4,3,3,4,4,4],
            "tomas":[3,3,2,3,4,4], "naomi":[3,3,3,3,3,4], "ben":[3,2,2,4,4,5],
            "sarah":[4,4,3,4,5,5], "james":[4,4,4,4,4,5], "rachel":[4,4,4,4,4,4],
            "kevin":[4,4,4,4,4,4], "lily":[3,3,4,4,4,4], "mark":[3,3,3,3,4,4],
        },
        "ch": {
            "dana":[3,3,3,3,4,4],"marcus":[4,4,4,5,5,5],"priya":[3,3,3,4,4,4],
            "tomas":[3,3,3,4,4,4],"naomi":[2,2,2,3,3,3],"ben":[2,2,2,3,4,4],
            "sarah":[4,4,4,4,5,5],"james":[4,5,4,5,5,5],"rachel":[4,4,4,4,4,4],
            "kevin":[4,4,4,4,4,4],"lily":[3,3,4,4,4,4],"mark":[3,3,3,3,4,4],
        },
    }
    AFTER = {
        "sprints": ["S7 (Jul 1-14)","S8 (Jul 15-28)","S9 (Jul 29-Aug 11)","S10 (Aug 12-25)","S11 (Aug 26-Sep 8)","S12 (Sep 9-22)"],
        "ps": {
            "dana":[5,5,5,5,5,5], "marcus":[5,5,5,5,5,5], "priya":[4,4,5,5,5,5],
            "tomas":[4,4,5,5,5,5], "naomi":[4,4,5,5,5,5], "ben":[5,5,5,5,5,5],
            "sarah":[5,5,5,5,5,5], "james":[5,5,5,5,5,5], "rachel":[4,4,4,5,5,5],
            "kevin":[4,4,4,4,5,5], "lily":[4,4,5,5,5,5], "mark":[4,4,4,4,5,5],
        },
        "ch": {
            "dana":[4,4,5,5,5,5],"marcus":[5,5,5,5,5,5],"priya":[4,4,4,5,5,5],
            "tomas":[4,4,5,5,5,5],"naomi":[3,4,4,5,5,5],"ben":[4,4,5,5,5,5],
            "sarah":[5,5,5,5,5,5],"james":[5,5,5,5,5,5],"rachel":[4,4,4,5,5,5],
            "kevin":[4,4,4,4,5,5],"lily":[4,4,5,5,5,5],"mark":[4,4,4,5,5,5],
        },
    }
    data = BEFORE if era == "before" else AFTER
    team_of = {u[1]: u[3] for u in USERS}
    rows = [["sprint","respondent","team","psych_safety_1to5","conflict_is_healthy_1to5"]]
    ps_all, ch_all = [], []
    for si, sprint in enumerate(data["sprints"]):
        for h in data["ps"]:
            ps, ch = data["ps"][h][si], data["ch"][h][si]
            rows.append([sprint, NAME[h], team_of[h], ps, ch])
            ps_all.append(ps); ch_all.append(ch)
    with open(os.path.join(paths["survey"], "pulse.csv"), "w", newline="") as f:
        csv.writer(f).writerows(rows)
    return {"rows": len(rows) - 1,
            "avg_psych_safety": round(sum(ps_all) / len(ps_all), 2),
            "avg_conflict_health": round(sum(ch_all) / len(ch_all), 2)}

# ==========================================================================
# MAIN
# ==========================================================================
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 1) if xs else None

def era_rollup(metrics, survey):
    """Collapse an era's transcript metrics into the comparison signals."""
    group = [s for s in metrics.values() if s["attendee_count"] > 2]
    dana_talk = _mean([s["speakers"]["dana"]["talk_pct"] for s in group if "dana" in s["speakers"]])
    naomi_att = [s for s in group if s["speakers"].get("naomi", {}).get("attended")]
    naomi_talk = _mean([s["speakers"]["naomi"]["talk_pct"] for s in naomi_att])
    naomi_silent = sum(1 for s in naomi_att if "Naomi Kito" in s["present_but_silent"])
    dana_group = [s["speakers"]["dana"]["talk_pct"] for s in group if "dana" in s["speakers"]]
    return {
        "group_meetings": len(group),
        # Peak tells the dominance story; avg is diluted by meetings the person barely spoke in.
        "peak_dominant_talk_pct": max((s["dominant_pct"] for s in group), default=None),
        "avg_dominant_talk_pct": _mean([s["dominant_pct"] for s in group]),
        "dana_peak_talk_pct": max(dana_group, default=None),
        "dana_avg_talk_pct": dana_talk,
        "naomi_avg_talk_pct": naomi_talk,
        "naomi_meetings_attended": len(naomi_att),
        "naomi_silent_meetings": naomi_silent,
        "total_interruptions": sum(s["interruptions"] for s in metrics.values()),
        "avg_psych_safety_1to5": survey["avg_psych_safety"],
        "avg_conflict_health_1to5": survey["avg_conflict_health"],
    }

def main():
    counts = {}
    rollups = {}
    for era in ERAS:
        p = era_paths(era)
        n_msg, n_days = emit_slack(era, p)
        metrics = emit_transcripts(era, p)
        n_pr = emit_git(era, p)
        n_iss = emit_issues(era, p)
        n_su = emit_standups(era, p)
        n_retro = emit_retros(era, p)
        survey = emit_survey(era, p)
        counts[era] = {"messages": n_msg, "channel_days": n_days,
                       "meetings": len(metrics), "prs": n_pr, "issues": n_iss,
                       "standups": n_su, "retros": n_retro, "survey_rows": survey["rows"]}
        rollups[era] = era_rollup(metrics, survey)

    # Editorial ground-truth signals that aren't computable from counts alone.
    editorial = {
        "before": {"license_conflict_reopens": 3, "regression_time_to_surface_days": 4,
                   "hallway_dissent_events": 1, "changed_mind_in_room_events": 1},
        "after":  {"license_conflict_reopens": 0, "regression_time_to_surface_days": 0,
                   "hallway_dissent_events": 0, "changed_mind_in_room_events": 3},
    }
    comparison = {era: {**rollups[era], **editorial[era]} for era in ERAS}
    with open(os.path.join(COMPARE, "before_after.json"), "w") as f:
        json.dump({"eras": {e: ERAS[e]["label"] for e in ERAS},
                   "counts": counts, "comparison": comparison}, f, indent=2)

    for era in ERAS:
        c = counts[era]
        print(f"[{era:6s}] {ERAS[era]['label']}")
        print(f"         {c['messages']} msgs / {c['meetings']} meetings / {c['prs']} PRs / "
              f"{c['issues']} issues / {c['standups']} standups / {c['retros']} retros / {c['survey_rows']} survey rows")

    print("\nBefore → After (the story the rubric can score):")
    b, a = comparison["before"], comparison["after"]
    def line(label, key, unit=""):
        print(f"  {label:34s} {str(b[key])+unit:>10s}  →  {str(a[key])+unit:<10s}")
    line("Peak dominant talk-time", "peak_dominant_talk_pct", "%")
    line("Dana peak talk-time (group)", "dana_peak_talk_pct", "%")
    line("Naomi avg talk-time (group)", "naomi_avg_talk_pct", "%")
    line("Naomi silent meetings", "naomi_silent_meetings")
    line("License conflict reopens", "license_conflict_reopens")
    line("Regression time-to-surface", "regression_time_to_surface_days", "d")
    line("Hallway dissent events", "hallway_dissent_events")
    line("Changed-mind-in-room events", "changed_mind_in_room_events")
    line("Avg psych safety (1-5)", "avg_psych_safety_1to5")
    line("Avg conflict health (1-5)", "avg_conflict_health_1to5")

if __name__ == "__main__":
    main()
