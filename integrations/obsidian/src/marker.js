// Locate the outermost @(word ...) marker enclosing a text offset.
// Nested markers stay inside the returned span; the delegated agent
// interprets them (see .agents/skills/manuscript-tasks).

/**
 * @param {string} text
 * @param {number} offset
 * @returns {{start: number, end: number, text: string} | null}
 *   end is exclusive; null when the offset is not inside a balanced marker.
 */
export function findMarkerAt(text, offset) {
  let i = 0;
  while ((i = text.indexOf("@(", i)) !== -1) {
    const end = matchParen(text, i + 1);
    if (end === -1) {
      i += 2;
      continue;
    }
    if (offset >= i && offset <= end) {
      return { start: i, end, text: text.slice(i, end) };
    }
    i = end; // skip the whole marker: only top-level markers are candidates
  }
  return null;
}

/** @param {string} text @param {number} open index of "(" @returns {number} */
function matchParen(text, open) {
  let depth = 0;
  for (let j = open; j < text.length; j++) {
    if (text[j] === "(") depth++;
    else if (text[j] === ")") {
      depth--;
      if (depth === 0) return j + 1;
    }
  }
  return -1;
}
