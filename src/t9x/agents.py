'''Install project-local coding-agent integration files.'''
from importlib.resources import files
from pathlib import Path

from .workspace import WorkspaceError, atomic_write_many

AGENTS = ('codex', 'claude', 'opencode', 'omp', 'pi', 'hermes')
LABELS = {
    'codex': 'Codex',
    'claude': 'Claude Code',
    'opencode': 'OpenCode',
    'omp': 'OMP',
    'pi': 'Pi',
    'hermes': 'Hermes',
}
CODEX_CONFIG = '''[permissions.t9x-workspace]
description = "Workspace editing with writable t9x state."
extends = ":workspace"

[permissions.t9x-workspace.filesystem.":workspace_roots"]
".git" = "read"
".codex" = "read"
".agents" = "write"
'''


def skill_text():
    return files('t9x').joinpath(
        'templates', 'using-t9x', 'SKILL.md'
    ).read_text(encoding='utf-8')


def prompt():
    print('Install t9x integration for:')
    for number, name in enumerate(AGENTS, 1):
        print(f'  {number}. {LABELS[name]}')
    answer = input('Select agents (comma-separated, Enter for none): ').strip()
    if not answer:
        return []
    selected = []
    for value in answer.split(','):
        value = value.strip().lower()
        if value.isdigit() and 1 <= int(value) <= len(AGENTS):
            name = AGENTS[int(value) - 1]
        elif value in AGENTS:
            name = value
        else:
            raise WorkspaceError(f'unknown agent selection {value!r}')
        if name not in selected:
            selected.append(name)
    return selected


def install(root, selected):
    root = Path(root)
    selected = tuple(dict.fromkeys(selected))
    unknown = sorted(set(selected) - set(AGENTS))
    if unknown:
        raise WorkspaceError(f'unknown agent {unknown[0]!r}')
    if not selected:
        return []

    skill = skill_text()
    desired = {root / '.agents/skills/using-t9x/SKILL.md': skill}
    if 'claude' in selected:
        desired[root / '.claude/skills/using-t9x/SKILL.md'] = skill
    if 'codex' in selected:
        desired[root / '.codex/config.toml'] = CODEX_CONFIG

    conflicts = [
        path for path, content in desired.items()
        if path.exists() and path.read_text(encoding='utf-8') != content
    ]
    if conflicts:
        paths = ', '.join(str(path.relative_to(root)) for path in conflicts)
        raise WorkspaceError(
            f'refusing to overwrite existing agent configuration: {paths}'
        )

    atomic_write_many({
        path: content for path, content in desired.items() if not path.exists()
    })
    return list(selected)
