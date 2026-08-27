'''t9x command line interface: semantic verbs over the .agents/ workspace.'''
import argparse
import sys

from . import notes, promote, runs, skills, tasks, workspace
from .workspace import WorkspaceError, find_root


def print_obj(obj):
    print(obj.path.read_text(), end='')
    if obj.path.name == 'README.md':
        artifacts = [p.name for p in sorted(obj.path.parent.iterdir())
                     if p.name != 'README.md']
        if artifacts:
            print('\n[artifacts] ' + ', '.join(artifacts))


def print_task_line(obj):
    print(f'{obj.id}  {obj.status:<7}  {obj.title}')


def parse_origin(text):
    if text is None:
        return None
    file, _, line = text.partition(':')
    origin = {'file': file}
    if line:
        origin['line'] = int(line)
    return origin


def cmd_init(args):
    base = workspace.init()
    print(f'initialized {base}')


def cmd_show(args):
    root = find_root()
    print_obj(workspace.resolve(root, args.id))


def cmd_ready(args):
    root = find_root()
    actionable, unblocked = tasks.ready(root)
    for task_id in unblocked:
        print(f'unblocked: {task_id} (all blockers resolved)', file=sys.stderr)
    for obj in actionable:
        print(f'{obj.id}  {obj.title}')


def cmd_transition(args):
    root = find_root()
    obj = tasks.transition(root, args.verb, args.id)
    print_task_line(obj)


def cmd_block(args):
    root = find_root()
    obj = tasks.block(root, args.id, args.blocker)
    blockers = ', '.join(obj.meta.get('blocked_by', []))
    print(f'{obj.id}  blocked by [{blockers}]')


def cmd_relate(args):
    root = find_root()
    a, b = tasks.relate(root, args.id, args.other)
    print(f'related {a.id} <-> {b.id}')


def cmd_task_new(args):
    root = find_root()
    obj = tasks.new(root, args.title, related=args.related,
                    origin=parse_origin(args.origin))
    print(f'{obj.id}  {obj.path.relative_to(root)}')


def cmd_task_list(args):
    root = find_root()
    listed = sorted(tasks.all_tasks(workspace.scan(root)), key=lambda o: o.id)
    if args.status:
        listed = [o for o in listed if o.status == args.status]
    for obj in listed:
        print_task_line(obj)


def cmd_task_show(args):
    root = find_root()
    print_obj(tasks.require_task(root, args.id))


def cmd_run_new(args):
    root = find_root()
    obj = runs.new(root, task_id=args.task, title=args.title)
    print(f'{obj.id}  {obj.path.relative_to(root)}')


def cmd_run_show(args):
    root = find_root()
    print_obj(runs.require_run(root, args.id))


def cmd_run_finish(args):
    root = find_root()
    obj = runs.finish(root, args.id, outcome=args.outcome)
    outcome = obj.meta.get('outcome', 'no outcome recorded')
    print(f'{obj.id}  finished  ({outcome})')


def cmd_note_new(args):
    root = find_root()
    obj = notes.new(root, args.title, related=args.related)
    print(f'{obj.id}  {obj.path.relative_to(root)}')


def cmd_note_list(args):
    root = find_root()
    found = [o for o in workspace.scan(root).values() if o.type == 'note']
    for obj in sorted(found, key=lambda o: str(o.path)):
        print(f'{obj.id}  {obj.path.relative_to(root)}')


def cmd_note_show(args):
    root = find_root()
    print_obj(notes.require_note(root, args.id))


def cmd_skill_list(args):
    root = find_root()
    for name in skills.list_skills(root):
        print(name)


def cmd_skill_show(args):
    root = find_root()
    print((skills.skill_path(root, args.name) / 'SKILL.md').read_text(), end='')


def cmd_skill_add(args):
    root = find_root()
    path = skills.add(root, args.name)
    print(f'created {path.relative_to(root)}/SKILL.md')


def cmd_skill_rm(args):
    root = find_root()
    path = skills.rm(root, args.name)
    print(f'removed {path.relative_to(root)}')


def cmd_promote(args):
    dst = promote.promote(args.src, args.dst)
    print(f'promoted {args.src} -> {dst}')


def build_parser():
    parser = argparse.ArgumentParser(
        prog='t9x', description='Local-first, file-first agent workspace.'
    )
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('init', help='create the .agents/ directory skeleton') \
        .set_defaults(func=cmd_init)
    show = sub.add_parser('show', help='print an object by id')
    show.add_argument('id')
    show.set_defaults(func=cmd_show)
    sub.add_parser('ready', help='list actionable tasks') \
        .set_defaults(func=cmd_ready)

    for verb, help_text in (
        ('close', 'mark a task done'),
        ('wontdo', 'reject a task deliberately'),
        ('reopen', 'reopen a done or wontdo task'),
        ('unblock', 'clear blockers and reopen a blocked task'),
    ):
        p = sub.add_parser(verb, help=help_text)
        p.add_argument('id')
        p.set_defaults(func=cmd_transition, verb=verb)

    block = sub.add_parser('block', help='mark a task blocked by another object')
    block.add_argument('id')
    block.add_argument('blocker')
    block.set_defaults(func=cmd_block)

    relate = sub.add_parser('relate', help='link two objects symmetrically')
    relate.add_argument('id')
    relate.add_argument('other')
    relate.set_defaults(func=cmd_relate)

    task = sub.add_parser('task', help='task commands').add_subparsers(
        dest='subcommand', required=True)
    t_new = task.add_parser('new', help='create an open task')
    t_new.add_argument('title')
    t_new.add_argument('--related', nargs='*', default=[], metavar='ID')
    t_new.add_argument('--origin', metavar='FILE[:LINE]')
    t_new.set_defaults(func=cmd_task_new)
    t_list = task.add_parser('list', help='list tasks')
    t_list.add_argument('--status', choices=('open', 'blocked', 'done', 'wontdo'))
    t_list.set_defaults(func=cmd_task_list)
    t_show = task.add_parser('show', help='print a task')
    t_show.add_argument('id')
    t_show.set_defaults(func=cmd_task_show)

    run = sub.add_parser('run', help='run commands').add_subparsers(
        dest='subcommand', required=True)
    r_new = run.add_parser('new', help='create a run, optionally for a task')
    r_new.add_argument('task', nargs='?', help='task id this run works on')
    r_new.add_argument('--title')
    r_new.set_defaults(func=cmd_run_new)
    r_show = run.add_parser('show', help='print a run')
    r_show.add_argument('id')
    r_show.set_defaults(func=cmd_run_show)
    r_finish = run.add_parser('finish', help='mark a run record complete')
    r_finish.add_argument('id')
    r_finish.add_argument('--outcome', choices=runs.OUTCOMES)
    r_finish.set_defaults(func=cmd_run_finish)

    note = sub.add_parser('note', help='note commands').add_subparsers(
        dest='subcommand', required=True)
    n_new = note.add_parser('new', help='create a dated note')
    n_new.add_argument('title')
    n_new.add_argument('--related', nargs='*', default=[], metavar='ID')
    n_new.set_defaults(func=cmd_note_new)
    note.add_parser('list', help='list notes').set_defaults(func=cmd_note_list)
    n_show = note.add_parser('show', help='print a note')
    n_show.add_argument('id')
    n_show.set_defaults(func=cmd_note_show)

    skill = sub.add_parser('skill', help='skill commands').add_subparsers(
        dest='subcommand', required=True)
    skill.add_parser('list', help='list skills').set_defaults(func=cmd_skill_list)
    s_show = skill.add_parser('show', help='print a SKILL.md')
    s_show.add_argument('name')
    s_show.set_defaults(func=cmd_skill_show)
    s_add = skill.add_parser('add', help='scaffold a new skill')
    s_add.add_argument('name')
    s_add.set_defaults(func=cmd_skill_add)
    s_rm = skill.add_parser('rm', help='remove a skill directory')
    s_rm.add_argument('name')
    s_rm.set_defaults(func=cmd_skill_rm)

    prom = sub.add_parser('promote', help='move agent material into the '
                          'human workspace')
    prom.add_argument('src')
    prom.add_argument('dst')
    prom.set_defaults(func=cmd_promote)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except WorkspaceError as error:
        print(f't9x: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
