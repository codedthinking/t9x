'''Skills: directories under .agents/skills/ following the SKILL.md convention.'''
import shutil
import tempfile
from pathlib import Path

from .workspace import WorkspaceError, agents_dir, atomic_write

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
    created = not path.exists()
    path.mkdir(parents=True, exist_ok=True)
    try:
        atomic_write(path / 'SKILL.md', STUB.format(name=name))
    except OSError:
        if created:
            path.rmdir()
        raise
    return path


def rm(root, name):
    path = skill_path(root, name)
    backup_root = Path(tempfile.mkdtemp(prefix='.t9x-rm-', dir=path.parent))
    backup = backup_root / path.name
    shutil.copytree(path, backup)
    try:
        shutil.rmtree(path)
    except OSError:
        try:
            shutil.copytree(backup, path, dirs_exist_ok=True)
        except OSError as rollback_error:
            raise WorkspaceError(
                f'could not remove {path}; rollback was incomplete: '
                f'{rollback_error}'
            )
        finally:
            shutil.rmtree(backup_root, ignore_errors=True)
        raise
    shutil.rmtree(backup_root, ignore_errors=True)
    return path
