import io
import subprocess
import sys
from pathlib import Path

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


class TtyInput(io.StringIO):
    def isatty(self):
        return True


def fail(*argv):
    assert cli.main(list(argv)) == 1


def deny_replace(monkeypatch, nth):
    replace = workspace.os.replace
    calls = 0

    def denied(source, destination):
        nonlocal calls
        calls += 1
        if calls == nth:
            raise PermissionError(1, 'Operation not permitted', str(destination))
        return replace(source, destination)

    monkeypatch.setattr(workspace.os, 'replace', denied)


def new_task(title, *extra):
    run('task', 'new', title, *extra)
    objects = workspace.scan(workspace.find_root())
    return next(o.id for o in objects.values() if o.title == title)


def get(object_id):
    return workspace.resolve(workspace.find_root(), object_id)


def test_init_creates_skeleton(ws):
    for sub in workspace.TOP_DIRS:
        assert (ws / '.agents' / sub).is_dir()


def test_init_installs_selected_agent_integrations(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run(
        'init',
        '--agent', 'codex',
        '--agent', 'claude',
        '--agent', 'opencode',
        '--agent', 'omp',
        '--agent', 'pi',
        '--agent', 'hermes',
    )
    canonical = tmp_path / '.agents/skills/using-t9x/SKILL.md'
    assert canonical.is_file()
    assert (tmp_path / '.claude/skills/using-t9x/SKILL.md').read_text() == \
        canonical.read_text()
    assert (tmp_path / '.codex/config.toml').read_text() == (
        '[permissions.t9x-workspace]\n'
        'description = "Workspace editing with writable t9x state."\n'
        'extends = ":workspace"\n\n'
        '[permissions.t9x-workspace.filesystem.":workspace_roots"]\n'
        '".git" = "read"\n'
        '".codex" = "read"\n'
        '".agents" = "write"\n'
    )


def test_init_prompts_for_agents_on_a_tty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, 'stdin', TtyInput('4,6\n'))
    run('init')
    assert (tmp_path / '.agents/skills/using-t9x/SKILL.md').is_file()
    assert not (tmp_path / '.codex').exists()
    assert not (tmp_path / '.claude').exists()


def test_init_no_agent_setup_never_prompts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, 'stdin', TtyInput('1\n'))
    run('init', '--no-agent-setup')
    assert not (tmp_path / '.agents/skills/using-t9x/SKILL.md').exists()


def test_init_agent_setup_is_atomic_and_idempotent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run('init', '--agent', 'codex', '--agent', 'claude')
    run('init', '--agent', 'codex', '--agent', 'claude')

    claude_skill = tmp_path / '.claude/skills/using-t9x/SKILL.md'
    claude_skill.write_text('user-authored\n')
    (tmp_path / '.codex/config.toml').unlink()

    fail('init', '--agent', 'codex', '--agent', 'claude')
    assert not (tmp_path / '.codex/config.toml').exists()


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


def test_run_new_rolls_back_if_task_backlink_fails(ws, monkeypatch):
    task_id = new_task('A')
    deny_replace(monkeypatch, 2)

    fail('run', 'new', task_id)

    assert get(task_id).meta['related'] == []
    assert not list((ws / '.agents/runs').glob('*.md'))


def test_permission_error_is_concise_and_non_destructive(
    ws, monkeypatch, capsys
):
    deny_replace(monkeypatch, 1)

    fail('note', 'new', 'Blocked write')

    error = capsys.readouterr().err
    assert 'cannot note new' in error
    assert 'permission denied' in error
    assert 'Traceback' not in error
    assert not list((ws / '.agents/notes').glob('*.md'))


def test_note_rename_keeps_id(ws):
    a = new_task('A')
    run('note', 'new', 'Variance decomposition', '--related', a)
    note = next(o for o in workspace.scan(ws).values() if o.type == 'note')
    renamed = note.path.with_name('renamed.md')
    note.path.rename(renamed)
    assert get(note.id).path == renamed


def test_note_import_copies_body_and_front_matter(ws):
    task_id = new_task('A')
    source = ws / 'docs/source.md'
    source.parent.mkdir()
    source.write_text('---\nauthor: Human\n---\n# Source\n\nBody.\n')

    run(
        'note', 'import', str(source),
        '--title', 'Imported note',
        '--related', task_id,
    )

    note = next(
        obj for obj in workspace.scan(ws).values() if obj.type == 'note'
    )
    assert source.is_file()
    assert note.body == '# Source\n\nBody.\n'
    assert note.meta['author'] == 'Human'
    assert note.meta['related'] == [task_id]
    assert note.title == 'Source'


def test_note_import_move_rolls_back_on_source_failure(ws, monkeypatch):
    source = ws / 'source.md'
    source.write_text('# Source\n')
    original_unlink = Path.unlink

    def deny_source(path, *args, **kwargs):
        if path == source:
            raise PermissionError(1, 'Operation not permitted', str(path))
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'unlink', deny_source)
    fail('note', 'import', str(source), '--title', 'Source', '--move')

    assert source.is_file()
    assert not list((ws / '.agents/notes').glob('*.md'))


def test_promote_rolls_back_on_source_failure(ws, monkeypatch):
    run('note', 'new', 'Identification')
    note = next(obj for obj in workspace.scan(ws).values() if obj.type == 'note')
    destination = ws / 'docs/identification.md'
    original_unlink = Path.unlink

    def deny_source(path, *args, **kwargs):
        if path == note.path:
            raise PermissionError(1, 'Operation not permitted', str(path))
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'unlink', deny_source)
    fail('promote', str(note.path), str(destination))

    assert note.path.is_file()
    assert not destination.exists()


def test_relate_is_symmetric(ws):
    a, b = new_task('A'), new_task('B')
    run('relate', a, b)
    assert b in get(a).meta['related']
    assert a in get(b).meta['related']


def test_relate_rolls_back_if_second_object_fails(ws, monkeypatch):
    a, b = new_task('A'), new_task('B')
    deny_replace(monkeypatch, 2)

    fail('relate', a, b)

    assert get(a).meta['related'] == []
    assert get(b).meta['related'] == []


def test_ready_rolls_back_if_second_unblock_fails(ws, monkeypatch):
    a, b = new_task('A'), new_task('B')
    blocker_a, blocker_b = new_task('Blocker A'), new_task('Blocker B')
    run('block', a, blocker_a)
    run('block', b, blocker_b)
    run('close', blocker_a)
    run('close', blocker_b)
    deny_replace(monkeypatch, 2)

    fail('ready')

    assert get(a).status == 'blocked'
    assert get(b).status == 'blocked'


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
