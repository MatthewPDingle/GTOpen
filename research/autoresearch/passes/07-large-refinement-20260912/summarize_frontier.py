"""Summarize completed one-step GPU diagnostics without adding overlapping gains."""
import json
import math
from pathlib import Path

RAW = Path(__file__).resolve().parent / 'raw'

def summarize(name):
    record = json.loads((RAW / f'frontier-{name}-v1-exit.json').read_text())
    assert record['returncode'] == 0 and record['reason'] is None
    report = json.loads((RAW / f'frontier-{name}-v1.json').read_text())
    rows = report['rows']
    assert len(rows) == report['path_count']
    assert len({tuple(row['path']) for row in rows}) == len(rows)
    gaps = report['global_gaps']
    assert len(gaps) == 8 and all(math.isfinite(g) and g >= 0 for g in gaps)
    ranked = []
    for row in rows:
        value = row['full_parent_one_step_gain_bb']
        if value is None:
            continue
        assert math.isfinite(value) and value >= -1e-7
        ranked.append({key: row[key] for key in ('path', 'position',
            'in_selected_subtree', 'strict_ancestor', 'full_parent_one_step_gain_bb')})
    ranked.sort(key=lambda row: row['full_parent_one_step_gain_bb'], reverse=True)
    return dict(input=name, global_gap=sum(gaps), path_count=len(rows), top_decisions=ranked[:12])

if __name__ == '__main__':
    print(json.dumps(dict(scope='Overlapping one-step gains; do not sum as full-BR attribution',
        results=[summarize(name) for name in ('sampled-original', 'sampled-compact',
            'sampled-retained', 'native-retained')]), indent=2))
