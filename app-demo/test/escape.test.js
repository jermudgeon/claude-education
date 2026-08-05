import test from "node:test";
import assert from "node:assert/strict";

import { escapeHtml } from "../app.js";

test("escaping neutralizes a script tag typed into the notes field", () => {
  assert.equal(
    escapeHtml('<script>alert("x")</script>'),
    "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;",
  );
});

test("escaping covers both quote characters, so an attribute cannot be broken out of", () => {
  assert.equal(escapeHtml(`" onmouseover="steal()`), "&quot; onmouseover=&quot;steal()");
  assert.equal(escapeHtml("' onfocus='steal()"), "&#39; onfocus=&#39;steal()");
});

test("escaping runs the ampersand first, so an entity is not double decoded", () => {
  assert.equal(escapeHtml("&lt;b&gt;"), "&amp;lt;b&amp;gt;");
});

test("escaping leaves ordinary prose alone", () => {
  assert.equal(escapeHtml("Priya reproduces the step on a fresh account."), "Priya reproduces the step on a fresh account.");
});

test("escaping accepts an empty string and a missing value", () => {
  assert.equal(escapeHtml(""), "");
  assert.equal(escapeHtml(undefined), "");
  assert.equal(escapeHtml(null), "");
});

test("escaping coerces a number rather than throwing", () => {
  assert.equal(escapeHtml(12), "12");
});
