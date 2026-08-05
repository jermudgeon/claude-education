/*
 * The conversation state machine. No DOM, no network, no clock of its own.
 * Every function takes a session and returns a new one, so the render layer
 * can diff, and so the whole flow is testable without a browser.
 */

const PHASE = { idle: "idle", roster: "roster", live: "live", distill: "distill" };

const RESEARCH_CADENCE = 2;

export function createSession(script) {
  return {
    script,
    phase: PHASE.idle,
    turn: 0,
    seat: 0,
    overlay: false,
    findings: 0,
    searching: false,
    notes: "",
    startedAt: null,
  };
}

export function start(session, now) {
  if (session.phase !== PHASE.idle) return session;
  return { ...session, phase: PHASE.roster, startedAt: now };
}

export function seatRoster(session) {
  if (session.phase !== PHASE.roster) return session;
  return { ...session, phase: PHASE.live, turn: 0, seat: 0 };
}

export function handoff(session) {
  if (session.phase !== PHASE.live) return session;
  const seats = session.script.roster.length;
  return {
    ...session,
    turn: session.turn + 1,
    seat: (session.seat + 1) % seats,
    overlay: true,
  };
}

export function clearOverlay(session) {
  if (!session.overlay) return session;
  return { ...session, overlay: false };
}

export function setSpeaker(session, seat) {
  const seats = session.script.roster.length;
  const valid = Number.isInteger(seat) && seat >= 0 && seat < seats;
  if (!valid) return session;
  return { ...session, seat };
}

export function setNotes(session, notes) {
  return { ...session, notes: String(notes ?? "") };
}

export function beginResearch(session) {
  if (session.searching) return session;
  if (session.findings >= session.script.findings.length) return session;
  return { ...session, searching: true };
}

export function dockFinding(session) {
  if (session.findings >= session.script.findings.length) {
    return session.searching ? { ...session, searching: false } : session;
  }
  return { ...session, searching: false, findings: session.findings + 1 };
}

export function distill(session) {
  return { ...session, phase: PHASE.distill, overlay: false };
}

export function resume(session) {
  if (session.phase !== PHASE.distill) return session;
  return { ...session, phase: PHASE.live };
}

export function reset(session) {
  return createSession(session.script);
}

export function currentSpeaker(session) {
  return session.script.roster[session.seat];
}

export function nextSpeaker(session) {
  const seats = session.script.roster.length;
  return session.script.roster[(session.seat + 1) % seats];
}

export function previousSpeaker(session) {
  const seats = session.script.roster.length;
  return session.script.roster[(session.seat - 1 + seats) % seats];
}

export function goalVersion(session) {
  return Math.min(session.turn, session.script.goals.length - 1);
}

export function goal(session) {
  return session.script.goals[goalVersion(session)];
}

export function goalHistory(session) {
  return session.script.goals.slice(0, goalVersion(session));
}

export function sharpness(session) {
  const reached = goalVersion(session) + 1;
  return Math.round((reached / session.script.goals.length) * 100);
}

export function prompt(session) {
  const prompts = session.script.prompts;
  return prompts[session.turn % prompts.length];
}

export function findings(session) {
  return session.script.findings.slice(0, session.findings);
}

export function researchIsDue(session) {
  if (session.searching) return false;
  if (session.turn === 0) return false;
  if (session.turn % RESEARCH_CADENCE !== 0) return false;
  return session.findings < session.script.findings.length;
}

/*
 * The distilled document, derived from what the session reached. It never
 * reports a goal version, a finding, or a next action the room did not get to.
 */
export function digest(session) {
  const versions = goalVersion(session) + 1;
  const evidence = findings(session);
  const complete = versions === session.script.goals.length;
  const counted = [
    `${session.script.roster.length} speakers`,
    `${versions} ${versions === 1 ? "restatement" : "restatements"}`,
    evidence.length === 0
      ? "no findings yet"
      : `${evidence.length} ${evidence.length === 1 ? "finding" : "findings"}`,
  ].join(", ");

  return {
    goal: goal(session),
    trail: [...goalHistory(session), goal(session)],
    evidence,
    complete,
    ruledOut: complete ? session.script.document.ruledOut : [],
    next: complete ? session.script.document.next : [],
    notes: session.notes.trim(),
    summary: complete
      ? `${counted}. The goal moved from a wish to one change with an owner and a date.`
      : `${counted}.`,
  };
}

export function elapsed(session, now) {
  if (session.startedAt === null) return "00:00";
  const seconds = Math.max(0, Math.floor((now - session.startedAt) / 1000));
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(Math.floor(seconds / 60))}:${pad(seconds % 60)}`;
}

export { PHASE };
