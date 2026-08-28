import test from "node:test";
import assert from "node:assert/strict";
import { findMarkerAt } from "./marker.js";

test("simple marker", () => {
  const text = "before @(write add a paragraph) after";
  const m = findMarkerAt(text, text.indexOf("add"));
  assert.equal(m.text, "@(write add a paragraph)");
});

test("cursor in nested marker returns outermost", () => {
  const text = "x @(write do this @(model verify the proposition)) y";
  const m = findMarkerAt(text, text.indexOf("verify"));
  assert.equal(m.text, "@(write do this @(model verify the proposition))");
});

test("cursor outside any marker", () => {
  const text = "before @(write a) after";
  assert.equal(findMarkerAt(text, 0), null);
  assert.equal(findMarkerAt(text, text.length - 1), null);
});

test("unclosed marker is ignored", () => {
  const text = "@(write never closed";
  assert.equal(findMarkerAt(text, 5), null);
});

test("second of two markers", () => {
  const text = "@(write one) mid @(edit two)";
  const m = findMarkerAt(text, text.indexOf("two"));
  assert.equal(m.text, "@(edit two)");
});

test("balanced parens inside description", () => {
  const text = "@(model check f(x) = y) tail";
  const m = findMarkerAt(text, text.indexOf("check"));
  assert.equal(m.text, "@(model check f(x) = y)");
});
