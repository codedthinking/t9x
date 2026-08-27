'''Locate the .agents/ workspace, scan structured objects, generate IDs.'''
import random
import re
import string
import sys
from pathlib import Path

from . import frontmatter

AGENTS_DIR = '.agents'
TOP_DIRS = ('tasks', 'notes', 'runs', 'scripts', 'skills')
BASE36 = string.digits + string.ascii_lowercase


class WorkspaceError(Exception):
    pass


class Obj:
    '''One structured object: a markdown file with id/type front matter.'''

    def __init__(self, path, meta, body):
        self.path = path
        self.meta = meta
        self.body = body

    @property
    def id(self):
        return self.meta.get('id')

    @property
    def type(self):
        return self.meta.get('type')

    @property
    def status(self):
        return self.meta.get('status')

    @property
    def title(self):
        for line in self.body.splitlines():
            if line.startswith('# '):
                return line[2:].strip()
        return self.path.stem

    def save(self):
        self.path.write_text(frontmatter.dump(self.meta, self.body))


def find_root(start=None):
    '''Walk up from start looking for a directory containing .agents/.'''
    here = Path(start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / AGENTS_DIR).is_dir():
            return candidate
    raise WorkspaceError(
        f'no {AGENTS_DIR}/ directory found here or above; run `t9x init` first'
    )


def agents_dir(root):
    return root / AGENTS_DIR


def init(root=None):
    base = Path(root or Path.cwd()) / AGENTS_DIR
    for sub in TOP_DIRS:
        (base / sub).mkdir(parents=True, exist_ok=True)
        keep = base / sub / '.gitkeep'
        if not any((base / sub).iterdir()):
            keep.touch()
    return base


def scan(root):
    '''Return {id: Obj} for every markdown file with id front matter.'''
    objects = {}
    for path in sorted(agents_dir(root).rglob('*.md')):
        meta, body = frontmatter.parse(path.read_text())
        if not meta or 'id' not in meta:
            continue
        obj = Obj(path, meta, body)
        if obj.id in objects:
            other = objects[obj.id].path
            print(
                f'warning: duplicate id {obj.id} in {path} and {other}',
                file=sys.stderr,
            )
            continue
        objects[obj.id] = obj
    return objects


def resolve(root, object_id, objects=None):
    objects = objects if objects is not None else scan(root)
    obj = objects.get(object_id)
    if obj is None:
        raise WorkspaceError(f'no object with id {object_id!r} under {AGENTS_DIR}/')
    return obj


def slugify(title, limit=60):
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return slug[:limit].rstrip('-') or 'untitled'


def new_id(existing_ids, length=3):
    '''Random base36 id, retried on collision, widened if the space is tight.'''
    for attempt in range(100):
        width = length + attempt // 20
        candidate = ''.join(random.choices(BASE36, k=width))
        if candidate not in existing_ids:
            return candidate
    raise WorkspaceError('could not generate a fresh id')
