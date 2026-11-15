"""Vérifie uniquement le référentiel ; pas l'application ni les ressources GitHub distantes."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
required = [
    'README.md', '.gitignore', '.env.example', 'docs/product.md',
    'docs/architecture.md', 'docs/roadmap.md', 'docs/data-sources.md',
    'docs/video-decision.md', 'docs/security.md', 'docs/quality.md',
    'docs/risks.md', 'docs/demo.md', 'docs/github-operations.md',
    'backlog/issues.json', 'backlog/labels.json', 'backlog/project.json',
    '.github/workflows/scaffold-check.yml', '.github/PULL_REQUEST_TEMPLATE.md',
]
errors = [f'Missing {p}' for p in required if not (ROOT / p).is_file()]
issues = json.loads((ROOT / 'backlog/issues.json').read_text(encoding='utf-8'))
labels = json.loads((ROOT / 'backlog/labels.json').read_text(encoding='utf-8'))
project = json.loads((ROOT / 'backlog/project.json').read_text(encoding='utf-8'))
ids = [x['id'] for x in issues]
if len(ids) != len(set(ids)):
    errors.append('Duplicated issue IDs')
label_names = {x['name'] for x in labels}
for i in issues:
    for dep in i['depends_on']:
        if dep not in ids:
            errors.append(f"{i['id']} has unknown dependency {dep}")
    if not i['acceptance']:
        errors.append(f"{i['id']} without acceptance criteria")
    if i['priority'] not in project['priority_options']:
        errors.append(f"{i['id']} invalid priority")
    if i['module'] not in project['module_options']:
        errors.append(f"{i['id']} invalid module")
    for label in ['priority:'+i['priority'], 'module:'+i['module'].lower(), 'type:'+i['type']]:
        if label not in label_names:
            errors.append(f"{i['id']} missing label {label}")
if sorted(project['status_options']) != sorted(['Backlog','Ready','In Progress','In Review','Blocked','Done']):
    errors.append('Project statuses differ from plan')
if len(issues) < 16:
    errors.append('Insufficient backlog coverage')
if 'OPEN' not in (ROOT / 'docs/decisions/0003-video-open.md').read_text(encoding='utf-8'):
    errors.append('Video must remain undecided')
if errors:
    for e in errors:
        print('ERROR:', e, file=sys.stderr)
    sys.exit(1)
print(f'OK — {len(required)} fichiers requis, {len(issues)} issues, {len(labels)} labels, vidéo ouverte.')
print('NOTE: application, publication GitHub et Project non vérifiés par ce script.')
