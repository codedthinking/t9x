'''Task objects and their semantic state transitions.'''
import datetime

from .workspace import (
    Obj, WorkspaceError, agents_dir, new_id, resolve, scan, slugify,
)

RESOLVED = ('done', 'wontdo')
TRANSITIONS = {
    'close': (('open', 'blocked'), 'done'),
    'wontdo': (('open', 'blocked'), 'wontdo'),
    'reopen': (('done', 'wontdo'), 'open'),
    'unblock': (('blocked',), 'open'),
}


def today():
    return datetime.date.today()


def new(root, title, related=None, origin=None):
    objects = scan(root)
    task_id = new_id(objects)
    meta = {
        'id': task_id,
        'type': 'task',
        'status': 'open',
        'created': today(),
        'related': list(related or []),
        'blocked_by': [],
    }
    if origin:
        meta['origin'] = origin
    path = agents_dir(root) / 'tasks' / f'{task_id}-{slugify(title)}.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    obj = Obj(path, meta, f'# {title}\n')
    obj.save()
    return obj


def require_task(root, task_id, objects=None):
    obj = resolve(root, task_id, objects)
    if obj.type != 'task':
        raise WorkspaceError(f'{task_id} is a {obj.type}, not a task')
    return obj


def transition(root, verb, task_id):
    allowed, target = TRANSITIONS[verb]
    obj = require_task(root, task_id)
    if obj.status not in allowed:
        raise WorkspaceError(
            f'cannot {verb} {task_id}: status is {obj.status!r}, '
            f'expected one of {", ".join(allowed)}'
        )
    obj.meta['status'] = target
    if verb == 'unblock':
        obj.meta['blocked_by'] = []
    obj.save()
    return obj


def block(root, task_id, blocker_id):
    objects = scan(root)
    obj = require_task(root, task_id, objects)
    resolve(root, blocker_id, objects)
    if obj.status not in ('open', 'blocked'):
        raise WorkspaceError(
            f'cannot block {task_id}: status is {obj.status!r}, expected open'
        )
    blockers = obj.meta.setdefault('blocked_by', [])
    if blocker_id not in blockers:
        blockers.append(blocker_id)
    obj.meta['status'] = 'blocked'
    obj.save()
    return obj


def relate(root, id_a, id_b):
    objects = scan(root)
    a, b = resolve(root, id_a, objects), resolve(root, id_b, objects)
    for src, dst in ((a, b), (b, a)):
        rel = src.meta.setdefault('related', [])
        if dst.id not in rel:
            rel.append(dst.id)
        src.save()
    return a, b


def all_tasks(objects):
    return [o for o in objects.values() if o.type == 'task']


def ready(root):
    '''Actionable tasks. Auto-unblocks tasks whose blockers are all resolved.'''
    objects = scan(root)
    unblocked = []
    for obj in all_tasks(objects):
        if obj.status != 'blocked':
            continue
        blockers = obj.meta.get('blocked_by') or []
        done = all(
            b in objects and objects[b].status in RESOLVED for b in blockers
        )
        if blockers and done:
            obj.meta['status'] = 'open'
            obj.meta['blocked_by'] = []
            obj.save()
            unblocked.append(obj.id)
    actionable = [o for o in all_tasks(objects) if o.status == 'open']
    return sorted(actionable, key=lambda o: o.id), unblocked
