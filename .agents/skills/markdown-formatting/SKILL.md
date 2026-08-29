---
name: markdown-formatting
description: Format GitHub Flavored Markdown for human-facing documentation that should render cleanly in both GitHub and Obsidian. Use when creating, editing, rewriting, or reformatting Markdown documents, README files, specifications, research notes, or agent notes where consistent structure, restrained typography, ASCII source, and portable math formatting matter.
---

# Markdown formatting

Apply these rules whenever this skill is active. Preserve the author's meaning and existing document organization unless the task explicitly asks for structural editing.

## Structure

- Make document structure explicit through headings and paragraphs, not typographic emphasis.
- Use headings aggressively enough that the document structure is clear from the heading outline alone.
- Use sentence-case ATX headings with `#`, `##`, and `###`. Keep nesting shallow when possible.
- Do not use boldface, italics, labels, callouts, blockquotes, or other inline formatting to create implicit sections or pseudo-structure.
- If material needs a structural label such as "Assumption", "Result", "Interpretation", or "Caveat", use a real heading when it represents a genuine structural unit.
- Removing all emphasis formatting should not damage the document's structure or readability.
- Do not use horizontal rules. A line containing `---` is allowed only as YAML front matter when the file requires it.
- Do not use raw HTML for layout or formatting.

## Paragraphs

- Do not hard-wrap prose. Keep each paragraph on one source line, followed by a blank line.
- Use one idea per paragraph.
- Single-sentence paragraphs are fine when they form a genuine unit of thought.
- Prefer paragraphs over fragmented notes.
- Do not create manual line breaks with trailing spaces, backslashes, or HTML.

## Emphasis

- Prefer plain declarative prose over decorated prose.
- Use `*italic*` and `**bold**` sparingly and only for genuine local emphasis.
- Do not use emphasis to encode hierarchy or labels.
- Do not create pseudo-definition patterns such as `**Key term:** definition`.
- Do not create bold-led bullets such as `- **Thing:** explanation`.
- Use inline code for literal syntax, never as rhetorical emphasis.

## Lists

Use lists only when the items are genuinely parallel, short, and scannable.

- Use `-` for unordered list items.
- Introduce a nontrivial list with a complete sentence explaining what the items represent.
- Move paragraph-length or independently argued items out of a list and into prose with headings where appropriate.
- Use numbered lists only when order, sequence, ranking, or explicit enumeration matters.
- Avoid deeply nested lists. Prefer at most one nested level unless the hierarchy is intrinsic.

## Tables

Use Markdown tables when the information is genuinely tabular.

- Do not use tables for page layout or pseudo-columns.
- Prefer prose when relationships are conceptual rather than tabular.
- Do not repeat the same information in both a table and surrounding prose unless the repetition serves a clear purpose.

## Code and literal identifiers

- Give every fenced code block a language identifier.
- Use inline code for filenames, paths, commands, flags, package names, function names, code identifiers, configuration keys, and literal syntax.
- Examples include `README.md`, `docs/spec.md`, `git status`, `--force`, `DataFrame`, and `fit()`.
- Distinguish code identifiers from mathematical quantities. A data column named `y` is code; the model quantity `$y$` is mathematics.

## Character set and punctuation

- Use plain ASCII text only.
- Do not use emojis.
- Use `-`, not an em dash or en dash.
- Use straight quotes such as `"text"` and `'text'`, not curly quotes.
- Use `...`, not a Unicode ellipsis.
- Write mathematical symbols as ASCII LaTeX commands inside math delimiters, never as literal Unicode symbols.

## Math

Use the conservative MathJax subset that renders correctly in both GitHub and Obsidian.

- Use `$...$` for inline math.
- Use `$$...$$` for display math.
- Do not use `\(...\)`, `\[...\]`, standalone LaTeX, or fenced `math` code blocks.
- Put display math in its own paragraph, with `$$` on separate source lines from the expression.
- Wrap every mathematical parameter, variable, index, and symbol in math delimiters when it appears in prose.
- Write `$\rho$`, `$\sigma_a$`, `$\sigma_z$`, `$\Omega_i$`, `$a_i$`, `$z_m$`, `$\varepsilon_{im}$`, and `$y$` rather than bare names when they refer to model quantities.
- Do not write bare `rho`, `sigma`, `epsilon`, `a`, `z`, or `y` in prose when they denote mathematical quantities.
- Keep ordinary prose outside math mode when possible.
- Use LaTeX commands rather than Unicode symbols, for example `$\rho$`, `$\leq$`, `$\times$`, and `$\infty$`.
- Use standard LaTeX operators such as `\log`, `\exp`, `\max`, and `\operatorname{Var}`.
- For multiline display equations, use standard MathJax environments such as `aligned` inside `$$...$$`.
- Avoid custom macros, `\newcommand`, package imports, document-level LaTeX commands, equation labels, and cross-reference machinery unless compatibility with both renderers has been explicitly verified.
- Prefer conservative, standard MathJax constructs over renderer-specific features.
- Treat mathematical expressions grammatically as part of the surrounding sentence.
- Distinguish mathematical notation from literal code. Use `$y$` for the mathematical variable and `y` in inline code when referring to a program variable or data column.

For example, write display math as follows:

```markdown
$$
y = a_i + z_m + \varepsilon_{im}
$$
```

## Links and quotations

- Use descriptive link text instead of bare URLs where practical.
- Use blockquotes only for actual quotations or semantically quoted material.
- Do not use blockquotes as callout boxes or visual decoration.

## Editing existing Markdown

When reformatting an existing file, prioritize semantic preservation over cosmetic normalization.

- Preserve valid YAML front matter unless the task explicitly asks to change it.
- Preserve code, equations, links, citations, identifiers, and file paths exactly unless they are themselves being edited.
- Replace typographic pseudo-structure with headings or prose when doing so preserves the intended hierarchy.
- Remove unnecessary emphasis, horizontal rules, decorative formatting, and AI-style bold-led list patterns.
- Normalize unordered list markers to `-`.
- Remove hard wraps inside prose paragraphs.
- Check that math delimiters and LaTeX constructs remain portable between GitHub and Obsidian.
