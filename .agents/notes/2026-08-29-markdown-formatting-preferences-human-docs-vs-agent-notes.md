---
id: ixa
type: note
created: 2026-08-29
related: [fzv]
---
# Markdown formatting preferences (human docs/ vs agent notes)

Superseded 2026-08-29 by the curated skill in
`.agents/skills/markdown-formatting/`, which is authoritative where the
two differ (it prefers `-` bullets, unwrapped paragraphs, and allows
genuinely tabular tables). This note remains as the empirical record.

Extracted by contrasting `docs/spec.md` (human-curated) with the three
agent-written files in `.agents/notes/` (evidence: run fzv). Written in
the preferred style itself.

## Preferences

* Bullets are `*`, not `-`.
* No bold for emphasis. spec.md has zero `**` spans in 970 lines; agent
  notes average one per ten lines. If something matters, give it a
  header, a code span, or a plain declarative sentence.
* No em dashes. Zero in the human corpus. Use short sentences, commas,
  or parentheses.
* No markdown tables. Aligned or structured material goes in fenced
  code blocks (ontology listings, file trees, small ledgers).
* No horizontal rules. A `---` line outside YAML front matter reads as
  an AI tell.
* Hard wrap at 80 characters.
* Sentence-case ATX headers, shallow nesting: `##` and `###`, rarely
  deeper.
* One idea per paragraph; single-sentence paragraphs are normal.
* Introduce every list with a full sentence ending in a colon.
* Numbered lists only for genuinely ordered procedures.
* Inline code for every path, command, flag, and identifier.
* Plain prose over decorated prose: no emoji, no bold-led bullet
  patterns like `- **Thing** — explanation`.

## How to apply

When writing anywhere in the human workspace (`docs/`, `README.md`,
paper text), follow the list above strictly. Agent-space records
(`.agents/`) should follow it too, so promotion needs no reformatting.
