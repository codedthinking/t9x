'''Promotion: move provisional agent material into the human workspace.'''
import os
import shutil
import subprocess
import tempfile
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
    if not src.is_file():
        raise WorkspaceError(f'source {src} is not a regular file')
    if dst.exists():
        raise WorkspaceError(f'destination {dst} already exists')
    dst.parent.mkdir(parents=True, exist_ok=True)
    if in_git_repo(src.parent):
        moved = subprocess.run(
            ['git', 'mv', str(src), str(dst)], capture_output=True, text=True
        )
        if moved.returncode == 0:
            return dst

    handle = tempfile.NamedTemporaryFile(dir=dst.parent, delete=False)
    temporary = Path(handle.name)
    handle.close()
    try:
        shutil.copy2(src, temporary)
        os.replace(temporary, dst)
        try:
            src.unlink()
        except OSError:
            try:
                dst.unlink()
            except OSError as rollback_error:
                raise WorkspaceError(
                    f'could not remove source {src}; rollback also failed '
                    f'for {dst}: {rollback_error}'
                )
            raise
    finally:
        temporary.unlink(missing_ok=True)
    return dst
