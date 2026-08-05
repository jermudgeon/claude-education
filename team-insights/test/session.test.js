import test from "node:test";
import assert from "node:assert/strict";

import {
  createSession,
  start,
  seatRoster,
  handoff,
  clearOverlay,
  setSpeaker,
  setNotes,
  beginResearch,
  dockFinding,
  distill,
  resume,
  reset,
  currentSpeaker,
  nextSpeaker,
  previousSpeaker,
  goalVersion,
  goalHistory,
  sharpness,
  prompt,
  researchIsDue,
} from "../session.js";

const SCRIPT = {
  roster: [
    { name: "Ann", role: "Product" },
    { name: "Bo", role: "Support" },
    { name: "Cy", role: "Engineering" },
  ],
  goals: ["Rough goal.", "Sharper goal.", "Sharp goal with an owner and a date."],
  prompts: [
    { question: "First question?", tip: "First tip.", framing: "First framing." },
    { question: "Second question?", tip: "Second tip.", framing: "Second framing." },
  ],
  findings: [
    { headline: "First finding", detail: "First detail.", source: "Invented sample" },
    { headline: "Second finding", detail: "Second detail.", source: "Invented sample" },
  ],
};

const fresh = () => createSession(SCRIPT);

test("a new session is idle with nothing recorded", () => {
  const s = fresh();
  assert.equal(s.phase, "idle");
  assert.equal(s.turn, 0);
  assert.equal(s.seat, 0);
  assert.equal(s.overlay, false);
  assert.equal(s.findings, 0);
  assert.equal(s.searching, false);
  assert.equal(s.notes, "");
  assert.equal(s.startedAt, null);
});

test("start moves idle to roster and stamps the clock", () => {
  const s = start(fresh(), 1000);
  assert.equal(s.phase, "roster");
  assert.equal(s.startedAt, 1000);
});

test("start refuses to restart a session already under way", () => {
  const live = seatRoster(start(fresh(), 0));
  assert.equal(start(live, 500).startedAt, 0);
  assert.equal(start(live, 500).phase, "live");
});

test("seating the roster opens the first turn", () => {
  const s = seatRoster(start(fresh(), 0));
  assert.equal(s.phase, "live");
  assert.equal(s.turn, 0);
  assert.equal(s.seat, 0);
});

test("the speaker rail names who is up and who is next, and wraps", () => {
  let s = seatRoster(start(fresh(), 0));
  assert.equal(currentSpeaker(s).name, "Ann");
  assert.equal(nextSpeaker(s).name, "Bo");

  s = clearOverlay(handoff(s));
  s = clearOverlay(handoff(s));
  assert.equal(currentSpeaker(s).name, "Cy");
  assert.equal(nextSpeaker(s).name, "Ann");
  assert.equal(previousSpeaker(s).name, "Bo");
});

test("a handoff raises the full screen question for the incoming speaker", () => {
  const s = handoff(seatRoster(start(fresh(), 0)));
  assert.equal(s.overlay, true);
  assert.equal(currentSpeaker(s).name, "Bo");
  assert.equal(previousSpeaker(s).name, "Ann");
  assert.equal(clearOverlay(s).overlay, false);
});

test("a handoff outside a live turn changes nothing", () => {
  const idle = fresh();
  assert.deepEqual(handoff(idle), idle);
});

test("each turn advances the goal version, and the last version holds", () => {
  let s = seatRoster(start(fresh(), 0));
  assert.equal(goalVersion(s), 0);

  s = clearOverlay(handoff(s));
  assert.equal(goalVersion(s), 1);

  s = clearOverlay(handoff(s));
  assert.equal(goalVersion(s), 2);

  s = clearOverlay(handoff(s));
  assert.equal(goalVersion(s), 2, "the goal stops sharpening once the script runs out");
});

test("prior goal versions stay visible so the room sees the goal sharpen", () => {
  let s = seatRoster(start(fresh(), 0));
  assert.deepEqual(goalHistory(s), []);

  s = clearOverlay(handoff(s));
  assert.deepEqual(goalHistory(s), ["Rough goal."]);

  s = clearOverlay(handoff(s));
  assert.deepEqual(goalHistory(s), ["Rough goal.", "Sharper goal."]);
});

test("sharpness reads as a percentage and reaches full on the last version", () => {
  let s = seatRoster(start(fresh(), 0));
  assert.equal(sharpness(s), 33);

  s = clearOverlay(handoff(s));
  s = clearOverlay(handoff(s));
  assert.equal(sharpness(s), 100);
});

test("the question cycles through the prompt script", () => {
  let s = seatRoster(start(fresh(), 0));
  assert.equal(prompt(s).question, "First question?");

  s = clearOverlay(handoff(s));
  assert.equal(prompt(s).question, "Second question?");

  s = clearOverlay(handoff(s));
  assert.equal(prompt(s).question, "First question?", "the prompt list wraps");
});

test("tapping a name corrects the speaker without rewinding the goal", () => {
  let s = clearOverlay(handoff(seatRoster(start(fresh(), 0))));
  const version = goalVersion(s);

  s = setSpeaker(s, 2);
  assert.equal(currentSpeaker(s).name, "Cy");
  assert.equal(goalVersion(s), version);
  assert.equal(s.turn, 1);
});

test("a speaker correction outside the roster is rejected", () => {
  const s = seatRoster(start(fresh(), 0));
  assert.equal(setSpeaker(s, 3).seat, 0);
  assert.equal(setSpeaker(s, -1).seat, 0);
  assert.equal(setSpeaker(s, 1.5).seat, 0);
  assert.equal(setSpeaker(s, "1").seat, 0);
  assert.equal(setSpeaker(s, NaN).seat, 0);
});

test("research runs on a two turn cadence and stops when the findings run out", () => {
  let s = seatRoster(start(fresh(), 0));
  assert.equal(researchIsDue(s), false, "nothing is due before anyone has spoken");

  s = clearOverlay(handoff(s));
  assert.equal(researchIsDue(s), false, "one turn is too early");

  s = clearOverlay(handoff(s));
  assert.equal(researchIsDue(s), true);

  s = dockFinding(beginResearch(s));
  s = clearOverlay(handoff(s));
  s = clearOverlay(handoff(s));
  s = dockFinding(beginResearch(s));
  assert.equal(s.findings, 2);
  assert.equal(researchIsDue(s), false, "every finding in the script is already docked");
});

test("research shows it is working, then docks one finding", () => {
  let s = seatRoster(start(fresh(), 0));
  s = beginResearch(s);
  assert.equal(s.searching, true);
  assert.equal(s.findings, 0);

  s = dockFinding(s);
  assert.equal(s.searching, false);
  assert.equal(s.findings, 1);
});

test("research never docks more findings than the script holds", () => {
  let s = seatRoster(start(fresh(), 0));
  s = dockFinding(dockFinding(dockFinding(s)));
  assert.equal(s.findings, 2);
});

test("research does not start twice at once", () => {
  const searching = beginResearch(seatRoster(start(fresh(), 0)));
  assert.equal(beginResearch(searching), searching);
});

test("notes are optional and never block the turn", () => {
  let s = seatRoster(start(fresh(), 0));
  s = setNotes(s, "the thing nobody said out loud");
  assert.equal(s.notes, "the thing nobody said out loud");

  s = clearOverlay(handoff(s));
  assert.equal(s.notes, "the thing nobody said out loud", "a handoff keeps the notes");
  assert.equal(currentSpeaker(s).name, "Bo");
});

test("distill opens the document and resume returns to the conversation", () => {
  let s = clearOverlay(handoff(seatRoster(start(fresh(), 0))));
  s = setNotes(s, "kept");
  s = distill(s);
  assert.equal(s.phase, "distill");
  assert.equal(s.turn, 1, "distilling does not disturb the conversation behind it");

  s = resume(s);
  assert.equal(s.phase, "live");
  assert.equal(s.notes, "kept");
});

test("reset returns an idle session and keeps nothing from the last one", () => {
  let s = clearOverlay(handoff(seatRoster(start(fresh(), 1000))));
  s = setNotes(s, "gone");
  s = dockFinding(beginResearch(s));

  assert.deepEqual(reset(s), fresh());
});

test("every transition returns a new object rather than mutating the old one", () => {
  const before = seatRoster(start(fresh(), 0));
  const snapshot = structuredClone(before);
  handoff(before);
  setNotes(before, "x");
  setSpeaker(before, 1);
  dockFinding(beginResearch(before));
  assert.deepEqual(before, snapshot);
});
