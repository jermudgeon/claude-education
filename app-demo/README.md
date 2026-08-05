# ~~Claude~~ Team Insights

A conversation guide you run on the screen in the room. One button starts it, the app takes the speaking order, and between each speaker it puts one question on the full screen until a rough goal becomes one somebody can act on Monday. The session document writes itself.

This is a **demo**, not the product. Nothing is recorded, no microphone is opened, no model is called, and every word of the sample conversation is invented. What it demonstrates is the technique: how a turn-taking structure plus one sharp question per handoff moves a team from a wish to a commitment.

## Where it sits in this repository

This is a working surface for **PRD 06, the classroom and group agent facilitator**. PRD 06 names four behaviors and each one is on the screen here:

| PRD 06 behavior | What you see |
|---|---|
| "Let me say that back so we both understand" | Every restatement is a new goal version, introduced with "let me re-state," and the old versions stay visible |
| Balances voices, notices who has not spoken | The speaker rail shows who holds the floor and who is next, and a tap corrects it |
| A source, not an answer | One question per handoff, taking the full screen, never an answer |
| Encourages antithetical thinking | Every question forces a choice between two real paths, and the canonical tip is "say no" |

`demo/` is the other half. It computes PRD 05's metric contract over the Aurora Skills dataset, which measures collaboration after the fact. This demo participates in it. In PRD 06's words, 05 is the mirror and 06 is the extra chair at the table.

**The two demos differ in provenance, and the difference is deliberate.** `demo/` invents nothing: every name and number there is read from `simulated-data/aurora-skills`. This demo invents its whole conversation, because the facilitator's output, the restated goals and the questions, exists in no dataset. Porting the roster, the meeting, and the evidence rail onto `simulated-data/aurora-skills` while keeping the facilitator's lines authored and labeled is tracked as follow-up work.

## Run it

```bash
cd app-demo
npm start          # serves on http://localhost:4173
npm test           # 34 tests, no dependencies
```

`npm start` is `python3 -m http.server 4173`. Any static server works. Opening `index.html` straight off disk does not, because the app uses ES modules and browsers block module loading over `file://`.

There is nothing to install. The dependency tree is empty on purpose, so the tests run on Node's built-in runner and the supply chain surface is zero.

## What to look at

Press Start and hand the baton around four times. Five things are happening.

**The goal stacks instead of replacing itself.** Each restatement is a new version and the old ones stay on screen, greyed out. Watching "get more people using the reporting product" become "remove the re-authentication step that blocks report two" is the whole value of the exercise, and hiding the history throws it away.

**The question takes the entire screen at each handoff.** A question in a sidebar gets read by one person. A question filling the display gets read by the room, which is the point of a shared framing. The overlay also restates the current goal so the question lands in context.

**Every question forces a choice.** "Are you trying to solve for more signups, or for the teams you already have?" has no agreeable answer. Each one carries a coaching tip, and the canonical tip is "say no." A rejected framing sharpens a goal faster than a nod does, so the app is teaching a behavior rather than decorating the screen.

**Research arrives without interrupting.** Findings dock into the side rail with a source line, on a two turn cadence. An agent that talked over people would get the app switched off in one meeting.

**The document reports only what happened.** Distill at turn two and the document says the room has not ruled anything out and nobody owns an action yet, because at turn two that is true. It never lists a finding the research agent did not dock or a goal version the conversation did not reach. A document that flatters the meeting is worse than no document.

## What is faked, and what a real build needs

Being explicit about the gap matters more than the demo looking finished.

| In this demo | In a real build |
|---|---|
| The roster is a scripted list, and the names animate in as though heard | Voice capture, with each name bound to a voice profile as it is spoken |
| You press "hand off" to change speakers | Speaker diarization from the audio stream, with the tap-a-name correction kept as the manual override |
| Questions, restatements, and the document come from `sample.js` | Anthropic API calls over the running transcript |
| The research rail replays three invented findings on a timer | A real research agent with real sources |
| Nothing persists past a page reload | Session storage, and a retention decision about the audio |

The hard parts are speaker separation and question quality. Everything in this repository is the easy half.

## Files

| File | What it holds |
|---|---|
| `index.html` | The page shell, and the banner that labels the content invented |
| `insights.css` | The whole design system: dark first, PT Serif headings, Inter body, aurora as the only accent |
| `session.js` | The conversation state machine. No DOM, no network, no clock of its own |
| `app.js` | The render layer. Reads a session, writes the screen, turns clicks into transitions |
| `sample.js` | The invented sample conversation. Swap this one file to run the demo on a different one |
| `test/` | Node's built-in test runner against `session.js` and the HTML escaping |

Conversation logic lives in `session.js` as pure functions that take a session and return a new one, which is why the whole flow is testable without a browser. To change what the demo says, edit `sample.js` and nothing else.

## Accessibility and safety notes

The handoff overlay is a real dialog: it takes focus, closes on Escape, and returns focus to the control that opened it. Tap targets clear 44px at every width tested, focus is always visible, and `prefers-reduced-motion` turns off every animation. The notes field is the only user input and the only trust boundary, so its escaping has its own test file.

Below 640px the sticky header and footer would each wrap to three rows and leave the conversation a slit to live in, so the speaker rail scrolls horizontally in one row, card headings drop their badge to a second line rather than being squeezed to one word per line, and the presenter hint gives up its space to the buttons.

One external request exists: the Google Fonts stylesheet. Everything else is local.

## Known gaps

- The conversation is invented, while `demo/` reads the Aurora Skills dataset. Porting the roster, the meeting, and the evidence rail onto that dataset is the next change worth making.
- A phone is not the target. The layout is verified to hold at 375px and 320px, but the app is built for one shared display a room reads from six feet away, so a phone gets a working screen rather than a considered one.
- Research does not start a second run while one is in flight, so clicking through handoffs quickly docks fewer findings than a real conversation would.
- PRD 06's open design tension is not solved here. Slowing a group down while staying useful, and knowing when the facilitator is confidently wrong, are unanswered. This demo shows the shape of the intervention, not a measurement of whether the intervention read the room correctly.
