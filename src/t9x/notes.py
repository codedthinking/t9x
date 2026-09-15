'''Note objects: provisional accumulated knowledge with readable filenames.'''
import datetime
from pathlib import Path

from . import frontmatter
from .workspace import (
    Obj, WorkspaceError, agents_dir, atomic_write, new_id, resolve, scan, slugify,
)


def new(root, title, related=None):
    objects = scan(root)
    note_id = new_id(objects)
    date = datetime.date.today()
    meta = {
        'id': note_id,
        'type': 'note',
        'created': date,
        'related': list(related or []),
    }
    notes = agents_dir(root) / 'notes'
    notes.mkdir(parents=True, exist_ok=True)
    path = notes / f'{date}-{slugify(title)}.md'
    counter = 2
    while path.exists():
        path = notes / f'{date}-{slugify(title)}-{counter}.md'
        counter += 1
    obj = Obj(path, meta, f'# {title}\n')
    obj.save()
    return obj


def require_note(root, note_id, objects=None):
    obj = resolve(root, note_id, objects)
    if obj.type != 'note':
        raise WorkspaceError(f'{note_id} is a {obj.type}, not a note')
    return obj


def import_file(root, source, title, related=None, move=False):
    source = Path(source)
    if not source.is_file():
        raise WorkspaceError(f'source {source} is not a file')

    objects = scan(root)
    related = list(related or [])
    for object_id in related:
        resolve(root, object_id, objects)

    source_meta, body = frontmatter.parse(
        source.read_text(encoding='utf-8')
    )
    note_id = new_id(objects)
    date = datetime.date.today()
    meta = dict(source_meta or {})
    meta.update({
        'id': note_id,
        'type': 'note',
        'created': date,
        'related': related,
    })

    notes = agents_dir(root) / 'notes'
    path = notes / f'{date}-{slugify(title)}.md'
    counter = 2
    while path.exists():
        path = notes / f'{date}-{slugify(title)}-{counter}.md'
        counter += 1
    obj = Obj(path, meta, body)
    atomic_write(path, frontmatter.dump(meta, body))

    if move:
        try:
            source.unlink()
        except OSError:
            try:
                path.unlink()
            except OSError as rollback_error:
                raise WorkspaceError(
                    f'could not remove source {source}; rollback also failed '
                    f'for {path}: {rollback_error}'
                )
            raise
    return obj
