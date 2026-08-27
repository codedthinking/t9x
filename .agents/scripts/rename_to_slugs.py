'''One-off: rename .agents/{tasks,runs}/<id>.md to <id>-<slug>.md via git mv.'''
import subprocess

from t9x import workspace

root = workspace.find_root()
for obj in workspace.scan(root).values():
    if obj.type not in ('task', 'run'):
        continue
    target = obj.path.with_name(f'{obj.id}-{workspace.slugify(obj.title)}.md')
    if obj.path != target:
        subprocess.run(['git', 'mv', str(obj.path), str(target)], check=True)
        print(f'{obj.path.name} -> {target.name}')
