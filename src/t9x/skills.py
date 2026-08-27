'''Skills: directories under .agents/skills/ following the SKILL.md convention.'''
import shutil

from .workspace import WorkspaceError, agents_dir

STUB = '''# {name}

Describe the reusable procedure here: when to use it, the steps, and any
scripts or references shipped alongside this file.
'''


def skills_dir(root):
    return agents_dir(root) / 'skills'


def list_skills(root):
    base = skills_dir(root)
    if not base.is_dir():
        return []
    found = [p.parent for p in sorted(base.rglob('SKILL.md'))]
    return [p.relative_to(base) for p in found]


def skill_path(root, name):
    path = skills_dir(root) / name
    if not (path / 'SKILL.md').is_file():
        raise WorkspaceError(f'no skill named {name!r} under .agents/skills/')
    return path


def add(root, name):
    path = skills_dir(root) / name
    if (path / 'SKILL.md').exists():
        raise WorkspaceError(f'skill {name!r} already exists')
    path.mkdir(parents=True, exist_ok=True)
    (path / 'SKILL.md').write_text(STUB.format(name=name))
    return path


def rm(root, name):
    path = skill_path(root, name)
    shutil.rmtree(path)
    return path
