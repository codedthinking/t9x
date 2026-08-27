'''Run objects: records of concrete attempts, tied to tasks via related.'''
import datetime

from .workspace import (
    Obj, WorkspaceError, agents_dir, new_id, resolve, scan, slugify,
)

OUTCOMES = ('success', 'failure', 'inconclusive', 'abandoned')


def now():
    return datetime.datetime.now().astimezone().replace(microsecond=0)


def new(root, task_id=None, title=None):
    objects = scan(root)
    task = None
    if task_id:
        task = resolve(root, task_id, objects)
    run_id = new_id(objects)
    meta = {
        'id': run_id,
        'type': 'run',
        'created': now(),
        'related': [task.id] if task else [],
    }
    heading = title or (f'Run for {task.id}: {task.title}' if task else 'Run')
    path = agents_dir(root) / 'runs' / f'{run_id}-{slugify(heading)}.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    obj = Obj(path, meta, f'# {heading}\n')
    obj.save()
    if task:
        rel = task.meta.setdefault('related', [])
        if run_id not in rel:
            rel.append(run_id)
        task.save()
    return obj


def require_run(root, run_id, objects=None):
    obj = resolve(root, run_id, objects)
    if obj.type != 'run':
        raise WorkspaceError(f'{run_id} is a {obj.type}, not a run')
    return obj


def finish(root, run_id, outcome=None):
    obj = require_run(root, run_id)
    if outcome:
        if outcome not in OUTCOMES:
            raise WorkspaceError(
                f'outcome must be one of {", ".join(OUTCOMES)}, got {outcome!r}'
            )
        obj.meta['outcome'] = outcome
    obj.meta['finished'] = now()
    obj.save()
    return obj
