/*
 * The render layer. Reads a session, writes the screen, and turns clicks back
 * into transitions. All conversation logic lives in session.js.
 */

import { SAMPLE } from "./sample.js";
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
  goal,
  goalVersion,
  goalHistory,
  sharpness,
  prompt,
  findings,
  digest,
  researchIsDue,
  elapsed,
  PHASE,
} from "./session.js";

const ENTITIES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

export function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value).replace(/[&<>"']/g, (character) => ENTITIES[character]);
}

const SEARCH_MS = 2200;
const NAME_MS = 550;

export function mount() {
  let session = createSession(SAMPLE);
  const timers = new Set();
  let returnFocusTo = null;

  const el = (id) => document.getElementById(id);

  function after(ms, run) {
    const id = setTimeout(() => {
      timers.delete(id);
      run();
    }, ms);
    timers.add(id);
    return id;
  }

  function clearTimers() {
    for (const id of timers) clearTimeout(id);
    timers.clear();
  }

  function update(next) {
    session = next;
    render();
  }

  /* ---------- chrome ---------- */

  function renderPhase() {
    const label =
      session.phase === PHASE.idle
        ? "Ready"
        : session.phase === PHASE.roster
          ? "Setting the order"
          : session.phase === PHASE.distill
            ? "Distilled"
            : `Turn ${session.turn + 1}`;
    el("phase").textContent = label;
    el("recording").hidden = session.phase === PHASE.idle;
  }

  function renderSeats() {
    const rail = el("seats");
    if (session.phase === PHASE.idle || session.phase === PHASE.roster) {
      rail.innerHTML = "";
      return;
    }
    rail.innerHTML = SAMPLE.roster
      .map((person, index) => {
        const speaking = index === session.seat;
        const upNext = index === (session.seat + 1) % SAMPLE.roster.length;
        const state = speaking ? "speaking" : upNext ? "up next" : "";
        return `
          <button class="chip ${speaking ? "on" : ""}" data-seat="${index}"
                  aria-pressed="${speaking}"
                  aria-label="${escapeHtml(person.name)}${state ? `, ${state}` : ""}. Set as the current speaker.">
            <span class="dot" aria-hidden="true"></span>${escapeHtml(person.name)}
            ${state ? `<small>${state}</small>` : ""}
          </button>`;
      })
      .join("");
    for (const button of rail.querySelectorAll("[data-seat]")) {
      button.addEventListener("click", () => update(setSpeaker(session, Number(button.dataset.seat))));
    }
  }

  /* ---------- screens ---------- */

  function renderIdle(main) {
    main.innerHTML = `
      <div class="idle">
        <span class="eyebrow">One button, then talk</span>
        <h1>Turn a rough goal into one the team can act on.</h1>
        <p>Press start. Team Insights takes the speaking order, then drops one question between each speaker until the goal is sharp enough to hand to someone.</p>
        <button class="orb" id="start">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/>
            <path d="M19 11a7 7 0 0 1-14 0M12 18v4"/>
          </svg>
          Start
        </button>
        <span class="hint">Opens the session document and arms the research agent</span>
      </div>`;
    el("start").addEventListener("click", beginRoster);
  }

  function renderRoster(main) {
    main.innerHTML = `
      <div class="roster">
        <div class="wave" aria-hidden="true">${"<span></span>".repeat(7)}</div>
        <p class="ask">Who is here, and who speaks first?</p>
        <ol class="order" id="order" aria-label="Speaking order"></ol>
        <span class="dim small">In the real app each name binds to a voice as it is spoken. Here the order is scripted.</span>
      </div>`;

    const order = el("order");
    SAMPLE.roster.forEach((person, index) => {
      after(300 + index * NAME_MS, () => {
        const seat = document.createElement("li");
        seat.className = "seat";
        seat.innerHTML = `<span class="num" aria-hidden="true">${index + 1}</span><b>${escapeHtml(person.name)}</b><span class="dim small">${escapeHtml(person.role)}</span>`;
        order.appendChild(seat);
        if (index === SAMPLE.roster.length - 1) after(900, openFirstTurn);
      });
    });
  }

  function renderLive(main) {
    const version = goalVersion(session);
    const question = prompt(session);
    const percent = sharpness(session);
    const docked = findings(session);

    main.innerHTML = `
      <div class="grid">
        <div class="column">
          <section class="card goal" aria-labelledby="goal-heading">
            <div class="cardhead">
              <div>
                <span class="eyebrow">The goal</span>
                <h2 id="goal-heading">What the room is actually after</h2>
              </div>
              <span class="badge">${version + 1} of ${SAMPLE.goals.length} restatements</span>
            </div>
            <div class="stack" aria-live="polite">
              ${goalHistory(session)
                .map((text, index) => `<p class="version"><span class="tag">v${index + 1}</span>${escapeHtml(text)}</p>`)
                .join("")}
              <p class="version now"><span class="tag">v${version + 1} &middot; let me re-state</span>${escapeHtml(goal(session))}</p>
            </div>
            <div class="growth">
              <span>Sharpness</span>
              <span class="bar" role="img" aria-label="Goal sharpness ${percent} percent"><i style="width:${percent}%"></i></span>
              <span>${percent}%</span>
            </div>
          </section>

          <section class="card notes" aria-labelledby="notes-heading">
            <div class="cardhead">
              <div>
                <span class="eyebrow">Optional</span>
                <h2 id="notes-heading">Notes</h2>
              </div>
              <span class="dim small">Anyone can type, nobody has to</span>
            </div>
            <textarea id="notes" aria-labelledby="notes-heading"
              placeholder="Whiteboard, links, the thing nobody said out loud">${escapeHtml(session.notes)}</textarea>
          </section>
        </div>

        <div class="column">
          <section class="card prompt" aria-labelledby="question-heading">
            <div class="cardhead">
              <div>
                <span class="eyebrow">Question on the table</span>
                <h2 id="question-heading">For ${escapeHtml(currentSpeaker(session).name)}</h2>
              </div>
            </div>
            <p class="question" aria-live="polite">${escapeHtml(question.question)}</p>
            <p class="tip"><b>Tip</b><span>${escapeHtml(question.tip)}</span></p>
            <p class="framing">Directional framing: ${escapeHtml(question.framing)}</p>
          </section>

          <section class="card research" aria-labelledby="research-heading">
            <div class="cardhead">
              <div>
                <span class="eyebrow">Research agent</span>
                <h2 id="research-heading">Found while you talk</h2>
              </div>
              <span class="badge ${docked.length ? "go" : ""}">${docked.length ? `${docked.length} found` : "idle"}</span>
            </div>
            <div aria-live="polite">
              ${session.searching ? '<p class="working"><span class="spin" aria-hidden="true"></span>Checking product analytics and the support queue</p>' : ""}
              ${
                docked.length
                  ? docked
                      .map(
                        (item) => `
                        <div class="find">
                          <b>${escapeHtml(item.headline)}</b>
                          <span class="muted">${escapeHtml(item.detail)}</span>
                          <span class="source">${escapeHtml(item.source)}</span>
                        </div>`,
                      )
                      .join("")
                  : session.searching
                    ? ""
                    : '<p class="dim small leading">Runs on its own every couple of turns, and whenever the goal changes shape. Findings land here, never in the middle of a sentence.</p>'
              }
            </div>
          </section>
        </div>
      </div>`;

    const notes = el("notes");
    notes.addEventListener("input", (event) => {
      session = setNotes(session, event.target.value);
    });
  }

  function renderDistill(main) {
    const doc = digest(session);

    const row = (inner) => `<li><span>${inner}</span></li>`;
    const list = (items, render) =>
      items.length ? `<ul>${items.map(render).join("")}</ul>` : "";
    const nothingYet = (text) => `<p class="dim small leading">${text}</p>`;

    main.innerHTML = `
      <article class="doc">
        <div class="sheet">
          <span class="eyebrow">Session document, written by the app</span>
          <h1>${escapeHtml(doc.goal)}</h1>
          <p>${escapeHtml(doc.summary)}</p>

          <section class="section">
            <h2>How the goal moved</h2>
            ${
              doc.trail.length > 1
                ? `<ul>${doc.trail
                    .map((text, index) =>
                      index === doc.trail.length - 1
                        ? row(`<b>${escapeHtml(text)}</b>`)
                        : row(`<span class="struck">${escapeHtml(text)}</span>`),
                    )
                    .join("")}</ul>`
                : nothingYet("The goal has not been restated yet. It moves on the next handoff.")
            }
          </section>

          <section class="section">
            <h2>What the room ruled out</h2>
            ${
              list(doc.ruledOut, (item) => row(escapeHtml(item))) ||
              nothingYet("Nothing yet. The room rules a path out by saying no to a framing.")
            }
          </section>

          <section class="section">
            <h2>Evidence pulled during the conversation</h2>
            ${
              list(
                doc.evidence,
                (item) =>
                  row(
                    `${escapeHtml(item.headline)}. <span class="muted">${escapeHtml(item.detail)}</span> <span class="source">${escapeHtml(item.source)}</span>`,
                  ),
              ) || nothingYet("The research agent has not docked a finding yet.")
            }
          </section>

          <section class="section">
            <h2>Next</h2>
            ${
              list(doc.next, (item) => row(escapeHtml(item))) ||
              nothingYet("Nobody owns an action yet. The goal needs a change, an owner, and a date first.")
            }
          </section>

          ${doc.notes ? `<section class="section"><h2>Notes from the room</h2><p>${escapeHtml(doc.notes)}</p></section>` : ""}
        </div>
      </article>`;
  }

  /* ---------- footer ---------- */

  function renderControls() {
    const footer = el("controls");

    if (session.phase === PHASE.idle) {
      footer.innerHTML = `<span class="dim small">Nothing to press until the conversation starts</span>`;
      return;
    }

    if (session.phase === PHASE.roster) {
      footer.innerHTML = `<button class="btn btn-ghost" id="skip">Start the first turn</button>`;
      el("skip").addEventListener("click", () => {
        clearTimers();
        openFirstTurn();
      });
      return;
    }

    if (session.phase === PHASE.distill) {
      footer.innerHTML = `
        <button class="btn btn-ghost" id="back">Back to the conversation</button>
        <span class="spacer"></span>
        <button class="btn btn-primary" id="again">New session</button>`;
      el("back").addEventListener("click", () => update(resume(session)));
      el("again").addEventListener("click", startOver);
      return;
    }

    footer.innerHTML = `
      <button class="btn btn-primary" id="hand">Hand off to ${escapeHtml(nextSpeaker(session).name)}</button>
      <button class="btn btn-ghost" id="research">Run research now</button>
      <span class="spacer"></span>
      <span class="dim small">The real app detects the speaker change. Tap a name above to correct it.</span>
      <button class="btn btn-ghost" id="wrap">Distill</button>`;
    el("hand").addEventListener("click", handOff);
    el("research").addEventListener("click", runResearch);
    el("wrap").addEventListener("click", () => update(distill(session)));
  }

  /* ---------- the handoff takeover ---------- */

  function renderOverlay() {
    const host = el("overlay");
    if (!session.overlay) {
      host.innerHTML = "";
      return;
    }
    const question = prompt(session);
    host.innerHTML = `
      <div class="overlay" role="dialog" aria-modal="true" aria-labelledby="takeover-question">
        <p class="who">
          <span>${escapeHtml(previousSpeaker(session).name)}</span>
          <span class="arrow" aria-hidden="true">&rarr;</span>
          <span class="to">${escapeHtml(currentSpeaker(session).name)}</span>
        </p>
        <span class="eyebrow">Let me re-state</span>
        <p class="restate">${escapeHtml(goal(session))}</p>
        <h2 id="takeover-question">${escapeHtml(question.question)}</h2>
        <p class="tip"><b>Tip</b><span>${escapeHtml(question.tip)}</span></p>
        <button class="btn btn-primary" id="go">${escapeHtml(currentSpeaker(session).name)}, go</button>
      </div>`;

    const go = el("go");
    go.focus();
    go.addEventListener("click", closeOverlay);
    host.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeOverlay();
      if (event.key === "Tab") event.preventDefault();
    });
  }

  /* ---------- actions ---------- */

  function beginRoster() {
    returnFocusTo = null;
    update(start(session, Date.now()));
  }

  function openFirstTurn() {
    update(seatRoster(session));
  }

  function handOff() {
    returnFocusTo = "hand";
    const next = handoff(session);
    update(next);
    if (researchIsDue(next)) runResearch();
  }

  function closeOverlay() {
    update(clearOverlay(session));
    const restore = el(returnFocusTo ?? "");
    if (restore) restore.focus();
  }

  function runResearch() {
    const searching = beginResearch(session);
    if (searching === session) return;
    update(searching);
    after(SEARCH_MS, () => update(dockFinding(session)));
  }

  function startOver() {
    clearTimers();
    update(reset(session));
    el("clock").textContent = "00:00";
  }

  /* ---------- clock ---------- */

  setInterval(() => {
    if (session.startedAt === null) return;
    el("clock").textContent = elapsed(session, Date.now());
  }, 1000);

  /* ---------- theme ---------- */

  const theme = el("theme");
  theme.addEventListener("click", () => {
    const dark = document.documentElement.dataset.theme === "dark";
    document.documentElement.dataset.theme = dark ? "light" : "dark";
    theme.textContent = dark ? "Dark" : "Light";
    theme.setAttribute("aria-label", dark ? "Switch to the dark theme" : "Switch to the light theme");
  });

  /* ---------- render ---------- */

  function render() {
    const main = el("main");
    renderPhase();
    renderSeats();
    if (session.phase === PHASE.idle) renderIdle(main);
    else if (session.phase === PHASE.roster) renderRoster(main);
    else if (session.phase === PHASE.distill) renderDistill(main);
    else renderLive(main);
    renderControls();
    renderOverlay();
  }

  render();
}
