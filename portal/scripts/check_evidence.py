"""Regression checks on identifiers, dimensions, periods and tactical labels."""
from collections import Counter
import gzip
import json
from pathlib import Path

rows = json.loads(gzip.decompress((Path(__file__).resolve().parents[1] / 'lib/evidence.json.gz').read_bytes()))
assert len(rows) == len({r['id'] for r in rows}) == 254
totals = Counter((r['team'], r['p']) for r in rows)
assert totals == {('Maroc', 1): 47, ('Maroc', 2): 33, ('Portugal', 1): 56, ('Portugal', 2): 118}
for r in rows:
    assert 0 <= r['x'] <= 120 and 0 <= r['y'] <= 80
    if 'Perte candidate' in r['tags']:
        assert all(0 <= event['s'] <= 8 for event in r['after'])
    if 'Entrée dans le dernier tiers' in r['tags']:
        assert r['x'] < 80 <= r['end'][0]
    if any('progressive' in t for t in r['tags']):
        assert r['x'] < 80 and r['end'][0] - r['x'] >= 15
    if 'Renversement' in r['tags']:
        assert abs(r['end'][1] - r['y']) >= 35
print('254 situations et géométrie vérifiées.')
