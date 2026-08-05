import test from "node:test";
import assert from "node:assert/strict";

import {
  createSession,
  start,
  seatRoster,
  handoff,
  clearOverlay,
  setNotes,
  dockFinding,
  digest,
} from "../session.js";

const SCRIPT = {
  roster: [{ name: "Ann" }, { name: "Bo" }, { name: "Cy" }],
  goals: ["Rough goal.", "Sharper goal.", "Sharp goal with an owner and a date."],
  prompts: [{ question: "Q?", tip: "T.", framing: "F." }],
  findings: [
    { headline: "First finding", detail: "First detail.", source: "Invented sample" },
    { headline: "Second finding", detail: "Second detail.", source: "Invented sample" },
  ],
  document: {
    ruledOut: ["A path nobody wanted."],
    next: ["Ann does the thing, by Thursday."],
  },
};

const live = () => seatRoster(start(createSession(SCRIPT), 0));
const turn = (session) => clearOverlay(handoff(session));

test("the document names the goal the session actually reached", () => {
  assert.equal(digest(live()).goal, "Rough goal.");
  assert.equal(digest(turn(live())).goal, "Sharper goal.");
});

test("the trail holds every version reached and nothing beyond it", () => {
  assert.deepEqual(digest(live()).trail, ["Rough goal."]);
  assert.deepEqual(digest(turn(live())).trail, ["Rough goal.", "Sharper goal."]);
  assert.deepEqual(digest(turn(turn(live()))).trail, SCRIPT.goals);
});

test("the evidence list holds only the findings the research agent docked", () => {
  assert.deepEqual(digest(live()).evidence, []);
  assert.deepEqual(digest(dockFinding(live())).evidence, [SCRIPT.findings[0]]);
});

test("the summary counts what happened rather than what the script holds", () => {
  assert.equal(digest(live()).summary, "3 speakers, 1 restatement, no findings yet.");
  assert.equal(
    digest(dockFinding(turn(live()))).summary,
    "3 speakers, 2 restatements, 1 finding.",
  );
  assert.equal(
    digest(dockFinding(dockFinding(turn(turn(live()))))).summary,
    "3 speakers, 3 restatements, 2 findings. The goal moved from a wish to one change with an owner and a date.",
  );
});

test("an unfinished conversation has ruled nothing out and owes nobody an action", () => {
  const early = digest(turn(live()));
  assert.equal(early.complete, false);
  assert.deepEqual(early.ruledOut, []);
  assert.deepEqual(early.next, []);
});

test("a conversation that reached the last version reports what it ruled out and what is next", () => {
  const done = digest(turn(turn(live())));
  assert.equal(done.complete, true);
  assert.deepEqual(done.ruledOut, SCRIPT.document.ruledOut);
  assert.deepEqual(done.next, SCRIPT.document.next);
});

test("notes reach the document trimmed, and an empty field leaves no section", () => {
  assert.equal(digest(setNotes(live(), "   ")).notes, "");
  assert.equal(digest(setNotes(live(), "  kept  ")).notes, "kept");
});
