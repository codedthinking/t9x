# t9x: Local-First Agent Workspace Specification

## Purpose

t9x is a local-first, file-first workspace for coding and research agents.

Its core purpose is to separate:

* the human-curated scientific/project workspace
* the agent's provisional working state

Most agent-generated material is useful while work is ongoing, but should not
automatically have the same epistemic or editorial status as human-authored
documentation, papers, notes, or production code.

t9x therefore gives agents a dedicated `.agents/` workspace for:

* tasks
* provisional notes
* experimental runs
* scratch and exploratory scripts
* reusable skills

Everything is stored as ordinary files and can be version controlled with Git.

The system is intended especially for scientific work involving software
development, data analysis, statistics, simulations, scripts, papers, reports,
and research notes.

## Core principles

### Human and agent workspaces are separate

The main repository is the human-curated workspace.

```
project/
├── src/
├── scripts/
├── docs/
├── paper/
├── data/
└── .agents/
```

`.agents/` contains lower-trust, provisional agent work.

An agent can edit files outside `.agents/` when explicitly asked to do so. The
boundary is not a security boundary. It is an epistemic and organizational
boundary.

### Files are the interface

A conforming workspace must remain understandable and usable without t9x.

Normal tools must work:

```
cat .agents/tasks/qx3.md
rg "variance" .agents/
find .agents/notes -name '*.md'
git mv ...
rm ...
$EDITOR ...
```

There is no authoritative database, daemon, registry, generated index, or
hidden state.

The CLI is convenience only.

### Git provides history

There is no archive directory.

If an obsolete note, run, or script is deleted, Git retains its history.

Tasks are different: completed and deliberately rejected tasks remain because
they document project decisions.

### Stable IDs, readable filenames

Every structured object has a stable lowercase base36 ID such as:

```
qx3
1v2
k9z
```

The ID is canonical.

Filenames are presentation and may be renamed freely.

Tasks and runs prefix a title slug with the ID so that a plain `ls` gives a
human-readable overview without any tooling.

Notes use date-prefixed descriptive filenames because humans frequently browse
them directly.

### Minimal ontology

The system should model only concepts that have clear semantics.

Semantic operations such as:

```
close
reopen
block
promote
```

are preferable to generic CRUD operations such as `update`.

### Extensible metadata

YAML front matter is intentionally extensible.

Implementations must:

* tolerate unknown fields
* preserve unknown fields when editing an object
* avoid treating the core schema as exhaustive

This allows domain-specific workflows to extend t9x without changing the core
format.

## Name

The project and CLI are called:

```
t9x
```

The name connects naturally to 9X Academic while remaining short,
shell-friendly, and sufficiently abstract.

It deliberately resembles the short base36 identifiers used inside the system.

```
t9x ready
t9x show qx3
t9x close qx3
```

No formal backronym is required.

## Directory structure

```
.agents/
├── tasks/
├── notes/
├── runs/
├── scripts/
└── skills/
```

Subdirectories may appear recursively inside these directories when useful.

```
.agents/
├── tasks/
│   ├── qx3-check-variance-estimator.md
│   └── 1v2-fix-normalization.md
├── notes/
│   ├── 2026-08-27-variance-decomposition.md
│   └── gmrf/
│       ├── 2026-08-28-theta-graph.md
│       └── 2026-09-02-spectral-bound.md
├── runs/
├── scripts/
│   ├── check_variance.jl
│   └── inspect_sample.do
└── skills/
    └── stata-replication/
        └── SKILL.md
```

t9x commands must search recursively.

No mandatory taxonomy below the top-level directories is imposed.

## Ontology

```
TASK   = something that should be done
RUN    = an attempt or investigation
NOTE   = provisional accumulated knowledge
SCRIPT = executable agent working material
SKILL  = reusable procedure or capability
```

The distinction is semantic:

```
task   = intention
run    = activity/history
note   = knowledge
script = executable working material
skill  = reusable method
```

## IDs

Structured objects use lowercase base36 identifiers.

```
0123456789abcdefghijklmnopqrstuvwxyz
```

Three characters provide:

```
36^3 = 46,656
```

possible identifiers.

Generation should:

1. generate a random base36 identifier
2. check the entire `.agents/` namespace
3. retry on collision
4. extend beyond three characters if necessary

Example IDs:

```
qx3
1v2
z7k
93a
```

The namespace is global across structured objects. `qx3` identifies exactly one
object anywhere under `.agents/`.

This makes references cheap:

```
related: [qx3, 1v2]
```

## Relationships

Relationships are deliberately weakly typed.

The generic relation is:

```
related:
```

Humans and agents can infer the precise semantic relationship from context.

One relationship is sufficiently operationally important to deserve explicit
structure:

```
blocked_by:
```

This allows `t9x ready` to be computed mechanically.

## Task

A task is a finite piece of work.

Tasks use their ID followed by a slug of the title as filename:

```
.agents/tasks/qx3-check-variance-estimator.md
```

### Task states

```
open
blocked
done
wontdo
```

* `open`: available work
* `blocked`: cannot currently proceed
* `done`: completed
* `wontdo`: explicitly considered and deliberately rejected

`wontdo` tasks remain because the decision itself is project history.

Deletion means the task should not have existed or no longer deserves
representation as an object.

There is deliberately no `in-progress` state. Runs record actual work and do
not become stale when agent sessions disappear.

### Task transitions

```
new       -> open
block     open -> blocked
unblock   blocked -> open
close     open|blocked -> done
wontdo    open|blocked -> wontdo
reopen    done|wontdo -> open
```

### Blocking

```
blocked_by: [1v2, k9z]
```

`t9x ready` returns actionable tasks.

Normally:

```
status == open
```

A blocked task becomes ready once all blockers are resolved. The implementation
may automatically transition such stale blocked tasks back to open.

### Task file

```markdown
---
id: qx3
type: task
status: open
created: 2026-08-27
related: [f2m]
blocked_by: []
---
# Check variance estimator
Determine whether clustering is being applied before or after aggregation.
## Findings
Current implementation appears to aggregate at firm-year level first.
## Next
- inspect estimator implementation
- reproduce behavior on toy data
```

Only the YAML fields carry machine semantics. Markdown structure is
intentionally flexible.

## Run

A run records one concrete attempt, investigation, experiment, or work session.

A run answers:

> What happened when we tried something?

### Lifecycle

```
create
write/update while working
finish
```

`finish` means the record is complete, not necessarily successful.

### Outcomes

A completed run may optionally record:

```
success
failure
inconclusive
abandoned
```

Outcome is descriptive metadata, not workflow state.

### Run file

```markdown
---
id: f2m
type: run
created: 2026-08-27T09:12:00+02:00
related: [qx3]
outcome: inconclusive
---
# Variance estimator simulation
Tested the estimator on a small simulated panel.
## Procedure
Used `.agents/scripts/check_variance.jl`.
## Result
The bias remains after increasing the number of firms.
## Interpretation
The problem is probably not finite-sample noise. The normalization should be
checked next.
```

Runs may use subdirectories when they generate several artifacts:

```
.agents/runs/f2m/
├── README.md
├── output.txt
└── figure.png
```

## Note

A note records provisional accumulated knowledge.

```
run  = what happened
note = what we currently think
```

Notes may synthesize several tasks or runs.

### Note naming

Notes use readable filenames prefixed by an ISO 8601 date:

```
2026-08-27-variance-decomposition.md
2026-08-28-identification-problem.md
```

The date prefix is intentionally redundant with metadata because it remains
useful during ordinary filesystem browsing and survives Git operations better
than filesystem timestamps.

The filename is not canonical.

```
git mv \
  .agents/notes/2026-08-27-variance-decomposition.md \
  .agents/notes/2026-08-27-firm-level-variance.md
```

does not invalidate references to its ID.

### Note file

```markdown
---
id: k9z
type: note
created: 2026-08-27
related: [qx3, f2m]
---
# Variance estimator normalization
The current evidence suggests that the observed bias is caused by
normalization rather than finite-sample behavior.
```

Notes have no workflow status.

Obsolete notes may simply be deleted.

## Script

Scripts are ordinary executable files written during agent work.

```
.agents/scripts/check_variance.jl
.agents/scripts/reproduce_bug.py
.agents/scripts/inspect_sample.do
.agents/scripts/query_data.sh
```

t9x imposes no metadata schema on them.

They may contain normal comments, shebangs, language-specific metadata, or
nothing at all.

Runs and notes can reference scripts by path.

If a script becomes useful project code, it can be explicitly promoted into
the human workspace.

## Skill

Skills are reusable agent procedures or capabilities.

They live under:

```
.agents/skills/
```

and should follow the existing SKILL.md convention.

```
.agents/skills/stata-replication/
├── SKILL.md
├── scripts/
└── references/
```

Skills use human-readable names.

Harness-specific discovery and execution remain outside the core t9x
specification.

## Origin

A structured object may optionally record where it originated in the human
workspace.

This is particularly useful when tasks are extracted from manuscripts, source
code, reports, notebooks, or other human-authored material.

Example:

```yaml
origin:
  file: paper/model.tex
  line: 417
```

A more complete task might therefore contain:

```yaml
---
id: qx3
type: task
status: open
created: 2026-08-27
related: []
blocked_by: []
origin:
  file: paper/model.tex
  line: 417
---
```

`origin` is optional.

The file path should normally be repository-relative.

The line number is a useful locator but should not be treated as a stable
identifier: normal editing may move the relevant text.

Future extensions may therefore add additional fields such as an anchor or
source-specific locator without changing the core schema:

```yaml
origin:
  file: paper/model.tex
  line: 417
  anchor: "@qx3"
```

Implementations must preserve such unknown extension fields.

## Manuscript task integration

t9x itself does not define how tasks are authored inside manuscripts.

A separate skill or workflow may extract embedded instructions and create
normal t9x tasks.

For example, a manuscript could initially contain a structured instruction
requesting:

* writing
* mathematical derivation
* literature search
* empirical analysis
* editing

The extraction layer could replace that instruction with a short stable
reference:

```
@qx3
```

and create:

```
.agents/tasks/qx3.md
```

The task's origin records where it came from.

The manuscript syntax, extraction process, and reinsertion process are
intentionally outside the core specification.

This lets different users adopt different annotation conventions without
changing t9x.

## Capabilities

Task kinds such as:

```
writing
literature
modeling
math
empirical
editing
```

should not become subclasses of task.

A task remains:

```
type: task
```

A workflow may optionally add capability metadata:

```
capabilities: [writing, literature]
```

or:

```
capabilities: [modeling, math]
```

This is an extension field, not part of the required core schema.

## Promotion

Promotion is the explicit crossing of the agent-human workspace boundary.

```
.agents/notes/2026-08-27-identification.md
        ->
docs/identification.md
```

or:

```
.agents/scripts/check_estimator.jl
        ->
scripts/check_estimator.jl
```

Possible CLI:

```
t9x promote \
  .agents/notes/2026-08-27-identification.md \
  docs/identification.md
```

Promotion means that provisional agent material has been accepted into the
curated project workspace.

t9x need not enforce trust mechanically. Promotion expresses the intended
workflow.

## YAML front matter

The required core schema is deliberately small.

### Common fields

```yaml
---
id:
type:
created:
related:
---
```

### Task-specific fields

```yaml
status:
blocked_by:
```

### Run-specific fields

```yaml
outcome:
```

### Optional cross-cutting fields

```yaml
origin:
```

### Extension fields

Workflows may add arbitrary fields, for example:

```yaml
capabilities:
manuscript:
anchor:
experiment:
dataset:
```

Implementations must preserve fields they do not understand.

### id

Stable canonical base36 identifier.

```yaml
id: qx3
```

### type

Core structured object type:

```
task
run
note
```

Scripts and skills are identified structurally and do not require this
metadata.

### created

ISO 8601 date or timestamp.

```yaml
created: 2026-08-27
```

or:

```yaml
created: 2026-08-27T09:12:00+02:00
```

### related

Zero or more stable object IDs.

```yaml
related: [qx3, f2m]
```

### origin

Optional reference to material outside `.agents/`.

Minimum useful form:

```yaml
origin:
  file: paper/model.tex
  line: 417
```

## CLI design

The CLI uses semantic verbs rather than generic CRUD terminology.

### Generic

```
t9x show qx3
t9x ready
```

`show` resolves an ID recursively anywhere under `.agents/`.

`ready` returns actionable tasks.

### Tasks

```
t9x task new "Check variance estimator"
t9x task list
t9x task show qx3
t9x close qx3
t9x wontdo qx3
t9x reopen qx3
t9x block qx3 1v2
t9x unblock qx3
t9x relate qx3 f2m
```

There is no `start` or `stop`.

### Runs

```
t9x run new qx3
t9x run show f2m
t9x run finish f2m
```

### Notes

```
t9x note new "Variance decomposition"
t9x note list
t9x note show k9z
```

Editing and renaming remain ordinary filesystem operations.

### Scripts

Scripts fundamentally remain ordinary files.

Possible convenience commands may exist, but t9x must not impose a script
object model.

### Skills

```
t9x skill list
t9x skill show stata-replication
t9x skill add ...
t9x skill rm ...
```

Execution remains harness-specific.

## Example workflow

Discover available work:

```
t9x ready
```

Suppose:

```
qx3  Check variance estimator
```

Inspect it:

```
t9x show qx3
```

Create a run:

```
t9x run new qx3
```

Suppose this creates `f2m`.

The agent writes:

```
.agents/scripts/check_variance.jl
```

The run records the experiment.

The agent develops a more durable interpretation and creates:

```
.agents/notes/2026-08-27-variance-normalization.md
```

related to `qx3` and `f2m`.

Finally:

```
t9x close qx3
```

After review, useful material can cross into the human workspace.

## Key design decisions

### No AGENTS.md dependency

Long-lived instruction documents tend to become stale.

t9x instead emphasizes concrete persistent state:

* current tasks
* past runs
* provisional notes
* scripts
* reusable skills

### No JSONL as the primary representation

Separate files are easier to browse, review, diff, edit, link, and reference
directly from coding-agent interfaces.

Tracing can exist independently.

### No database

Scientific repositories are expected to contain hundreds rather than millions
of these objects.

Filesystem search, rg, Git, and normal agent file tools are sufficient.

### No mandatory plugin

Any coding agent capable of reading and writing files can use the workspace.

Harness integrations may improve ergonomics later but must remain optional.

### No archive

Git is the archive.

### No in-progress

Runs represent actual activity without introducing stale session state.

### No complicated relation graph

`related` handles ordinary cross-object relationships.

`blocked_by` exists because blocking has operational semantics.

### No task subclasses

Writing, literature search, modeling, mathematical derivation, empirical work,
and editing are capabilities or workflow metadata, not separate object types.

### No metadata for everything

Tasks, runs, and notes are structured objects.

Scripts remain scripts.

Skills follow the existing skills convention.

### Extensibility is part of the format

Unknown YAML fields must survive round trips through t9x.

This allows manuscript integration and other domain-specific workflows to
evolve independently of the core system.

## Conceptual summary

```
TASK     What remains to be done?
RUN      What did we try?
NOTE     What do we currently think we know?
SCRIPT   What executable working material did the agent create?
SKILL    What reusable procedure does the agent know?
ORIGIN   Where did this work come from?
PROMOTE  What has crossed from provisional agent work into the curated human
         project?
```

The central implementation invariant is:

> Files are the interface. IDs provide stable identity. The CLI provides
> optional convenience. Git provides history.
