'''Promotion: move provisional agent material into the human workspace.'''
import shutil
import subprocess
from pathlib import Path

from .workspace import WorkspaceError


def in_git_repo(path):
    result = subprocess.run(
        ['git', '-C', str(path), 'rev-parse', '--is-inside-work-tree'],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == 'true'


def promote(src, dst):
    src, dst = Path(src), Path(dst)
    if not src.exists():
        raise WorkspaceError(f'source {src} does not exist')
    if dst.exists():
        raise WorkspaceError(f'destination {dst} already exists')
    dst.parent.mkdir(parents=True, exist_ok=True)
    if in_git_repo(src.parent):
        moved = subprocess.run(
            ['git', 'mv', str(src), str(dst)], capture_output=True, text=True
        )
        if moved.returncode == 0:
            return dst
    shutil.move(str(src), str(dst))
    return dst
