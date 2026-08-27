import subprocess

import pytest

from t9x import cli, frontmatter, workspace


@pytest.fixture
def ws(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run('init')
    return tmp_path


def run(*argv):
    code = cli.main(list(argv))
    assert code == 0, f't9x {" ".join(argv)} failed'


def fail(*argv):
    assert cli.main(list(argv)) == 1


def new_task(title, *extra):
    run('task', 'new', title, *extra)
    objects = workspace.scan(workspace.find_root())
    return next(o.id for o in objects.values() if o.title == title)


def get(object_id):
    return workspace.resolve(workspace.find_root(), object_id)


def test_init_creates_skeleton(ws):
    for sub in workspace.TOP_DIRS:
        assert (ws / '.agents' / sub).is_dir()


def test_task_lifecycle(ws):
    a = new_task('Check variance estimator')
    obj = get(a)
    assert obj.meta['status'] == 'open'
    assert obj.path == ws / '.agents' / 'tasks' / f'{a}-check-variance-estimator.md'
    run('close', a)
    assert get(a).status == 'done'
    fail('close', a)
    run('reopen', a)
    run('wontdo', a)
    assert get(a).status == 'wontdo'


def test_block_and_auto_unblock(ws, capsys):
    a, b = new_task('A'), new_task('B')
    run('block', a, b)
    assert get(a).status == 'blocked'
    capsys.readouterr()
    run('ready')
    assert a not in capsys.readouterr().out
    run('close', b)
    capsys.readouterr()
    run('ready')
    out = capsys.readouterr().out
    assert a in out
    assert get(a).status == 'open'
    assert get(a).meta['blocked_by'] == []


def test_unblock_requires_blocked(ws):
    a, b = new_task('A'), new_task('B')
    fail('unblock', a)
    run('block', a, b)
    run('unblock', a)
    assert get(a).status == 'open'


def test_run_backlinks_and_finish(ws):
    a = new_task('A')
    run('run', 'new', a)
    run_obj = next(
        o for o in workspace.scan(ws).values() if o.type == 'run'
    )
    assert a in run_obj.meta['related']
    assert run_obj.id in get(a).meta['related']
    run('run', 'finish', run_obj.id, '--outcome', 'success')
    assert get(run_obj.id).meta['outcome'] == 'success'


def test_note_rename_keeps_id(ws):
    a = new_task('A')
    run('note', 'new', 'Variance decomposition', '--related', a)
    note = next(o for o in workspace.scan(ws).values() if o.type == 'note')
    renamed = note.path.with_name('renamed.md')
    note.path.rename(renamed)
    assert get(note.id).path == renamed


def test_relate_is_symmetric(ws):
    a, b = new_task('A'), new_task('B')
    run('relate', a, b)
    assert b in get(a).meta['related']
    assert a in get(b).meta['related']


def test_unknown_fields_survive_round_trip(ws):
    a = new_task('A')
    obj = get(a)
    text = obj.path.read_text().replace(
        'blocked_by: []',
        'blocked_by: []\ncapabilities: [modeling, math]\nmanuscript:\n  anchor: "@qx3"',
    )
    obj.path.write_text(text)
    run('close', a)
    meta, _ = frontmatter.parse(obj.path.read_text())
    assert meta['capabilities'] == ['modeling', 'math']
    assert meta['manuscript'] == {'anchor': '@qx3'}
    assert meta['status'] == 'done'


def test_origin_is_recorded(ws):
    a = new_task('A', '--origin', 'paper/model.tex:417')
    assert get(a).meta['origin'] == {'file': 'paper/model.tex', 'line': 417}


def test_show_finds_run_directory(ws, capsys):
    run_dir = ws / '.agents' / 'runs' / 'f2m'
    run_dir.mkdir(parents=True)
    (run_dir / 'README.md').write_text(
        '---\nid: f2m\ntype: run\ncreated: 2026-08-27\n---\n# Dir run\n'
    )
    (run_dir / 'output.txt').write_text('data')
    capsys.readouterr()
    run('show', 'f2m')
    out = capsys.readouterr().out
    assert '# Dir run' in out
    assert 'output.txt' in out


def test_skills(ws, capsys):
    run('skill', 'add', 'stata-replication')
    assert (ws / '.agents/skills/stata-replication/SKILL.md').is_file()
    capsys.readouterr()
    run('skill', 'list')
    assert 'stata-replication' in capsys.readouterr().out
    run('skill', 'rm', 'stata-replication')
    assert not (ws / '.agents/skills/stata-replication').exists()


def test_promote_uses_git_mv(ws):
    subprocess.run(['git', 'init', '-q'], cwd=ws, check=True)
    run('note', 'new', 'Identification')
    note = next(o for o in workspace.scan(ws).values() if o.type == 'note')
    subprocess.run(['git', 'add', '-A'], cwd=ws, check=True)
    src = str(note.path.relative_to(ws))
    run('promote', src, 'docs/identification.md')
    assert (ws / 'docs/identification.md').is_file()
    assert not note.path.exists()


def test_ids_are_base36_and_unique(ws):
    ids = {new_task(f'T{i}') for i in range(20)}
    assert len(ids) == 20
    assert all(set(i) <= set(workspace.BASE36) for i in ids)
