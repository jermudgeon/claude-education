/*
 * INVENTED SAMPLE SESSION.
 *
 * Every name, quote, number, finding, and source below is made up for the
 * demo. None of it is real product data, real analytics, or a real person.
 * The page says so in a banner at the top, and that banner stays.
 *
 * Swap this one file to run the demo on a different conversation.
 */

export const SAMPLE = {
  roster: [
    { name: "Sam", role: "Product" },
    { name: "Dana", role: "Support" },
    { name: "Priya", role: "Engineering" },
    { name: "Marcus", role: "Sales" },
  ],

  goals: [
    "Get more people using the reporting product.",
    "Increase weekly active teams on the reporting product.",
    "Get teams who ran one report to run a second one.",
    "Get the 12 teams that ran exactly one report in 90 days to a second report within 7 days.",
    "Remove the re-authentication step that blocks report two, so the 12 one-report teams reach a second report within 7 days.",
  ],

  prompts: [
    {
      question: "Are you trying to solve for more signups, or for the teams you already have?",
      tip: "Say no. Rejecting a framing sharpens the goal faster than agreeing with it.",
      framing: "Forces a choice between two real paths.",
    },
    {
      question: "Who feels the pain first when the second report never happens?",
      tip: "Name one person, not a segment.",
      framing: "Moves an abstraction to a witness.",
    },
    {
      question: "Is the blocker that the teams forgot, or that something stopped them?",
      tip: "Say no if neither is true, then say what is.",
      framing: "Separates motivation from mechanics.",
    },
    {
      question: "What would you stop doing if the second report happened on its own?",
      tip: "An answer of nothing means the goal is not load bearing yet.",
      framing: "Tests whether the goal has a cost.",
    },
  ],

  findings: [
    {
      headline: "12 of 44 teams ran exactly one report in the last 90 days",
      detail: "Nine of the twelve stopped inside the same session as their first report.",
      source: "Invented sample: product analytics",
    },
    {
      headline: "The median gap between report one and report two is 34 days",
      detail: "Of the teams that ever reach report two, 80 percent get there in the first week or never.",
      source: "Invented sample: product analytics",
    },
    {
      headline: "Support logged 7 tickets naming the second connection step",
      detail: "Every ticket came from a team on its first report.",
      source: "Invented sample: support queue",
    },
  ],

  document: {
    ruledOut: [
      "More signups. Nobody in the room could name a person who wanted them.",
      "A reminder email. The blocker is mechanical, not memory.",
    ],
    next: [
      "Priya reproduces the second connection step on a fresh account, by Thursday.",
      "Dana pulls the 7 tickets into one thread for the fix, by Wednesday.",
    ],
  },
};
