'''Note objects: provisional accumulated knowledge with readable filenames.'''
import datetime

from .workspace import (
    Obj, WorkspaceError, agents_dir, new_id, resolve, scan, slugify,
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
