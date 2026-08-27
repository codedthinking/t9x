---
id: ohc
type: task
status: open
created: 2026-08-27
related: []
blocked_by: []
---
# Add --capabilities passthrough to task new
`capabilities: [writing, literature]` is an extension field per the spec.
The CLI could accept `t9x task new "..." --capabilities writing literature`
so workflows do not have to edit front matter by hand. Must remain an
extension: no validation of capability names, no task subclasses.
