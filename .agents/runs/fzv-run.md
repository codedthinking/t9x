---
id: fzv
type: run
created: 2026-08-29T08:53:53+02:00
related: []
outcome: success
finished: 2026-08-29T08:54:45+02:00
---
# Run: compare human vs agent markdown, extract formatting preferences

Corpora defined by the t9x boundary, per Miklos: human = `docs/`
(spec.md, 970 lines), agent = `.agents/notes/` (3 notes, all written by
Claude 2026-08-27/28).

Counts per file (grep/awk):

```
                     spec.md   obsidian-plan  slash-plan  design-interp
star bullets (*)        24          0             0            0
dash bullets (-)         2         19             8            7
bold spans (**)          0         10             4            0
em dashes                0         26            10            0
table rows               0          7             6            0
lines > 80 chars         0          1             3            0
markdown links           0          n/a           n/a          n/a
horizontal rules         0          0             0            0
```

The 10 `^---$` lines in spec.md are YAML fences inside ```markdown
example blocks, not horizontal rules.

Qualitative reading of spec.md: sentence-case ATX headers, shallow
nesting; one idea per paragraph, often single-sentence paragraphs;
lists introduced by a colon sentence; numbered lists only for ordered
procedures (4 uses); fenced code blocks instead of tables for aligned
structure (ontology, id math, file trees); inline code for every path,
command, and identifier; normative must/should/may prose.

Durable output: note on markdown preferences (see related).
