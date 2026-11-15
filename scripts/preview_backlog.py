"""Affiche le backlog prévu sans publier sur GitHub."""
from pathlib import Path
import json
items=json.loads((Path(__file__).resolve().parents[1]/'backlog/issues.json').read_text(encoding='utf-8'))
for i in items:
    print(f"{i['id']} | {i['priority']} | {i['target_date']} | {i['module']:<10} | {i['title']}")
