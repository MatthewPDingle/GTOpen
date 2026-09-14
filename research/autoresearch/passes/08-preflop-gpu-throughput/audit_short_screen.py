"""Host-only retrospective of shorter LARGE benchmark screens.

Subtract omitted measured sweeps/checks from each completed six-row run.
Keep every other measured cost. This is a timing proxy, not a new run:
initialization, clocks and final synchronization may behave differently.
Never use it to replace correctness tests or final paired retention timing.
"""
import hashlib
import json
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / 'raw'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def proxy(record, count):
    rows = record['rows']
    assert len(rows) == 6
    assert [r['index'] for r in rows] == list(range(6))
    assert [r['warmup'] for r in rows] == [True, True, False, False, False, False]
    omitted = sum(r['iteration_seconds'] + r['check_seconds'] for r in rows[count:])
    remaining = record['complete_seconds'] - omitted
    assert remaining > 0
    return remaining


def main():
    experiments = {}
    sources = {}
    for candidate in sorted(RAW.glob('c*-large-candidate-*-bench.json')):
        match = re.fullmatch(r'(c\d+)-large-candidate-(\d+)-bench.json', candidate.name)
        if not match:
            continue
        control = RAW / candidate.name.replace('-candidate-', '-control-')
        if not control.exists():
            continue
        a, b = read(control), read(candidate)
        for key in ['input', 'nodes', 'initial_iteration', 'iteration']:
            assert a[key] == b[key], (candidate.name, key)
        for path in [control, candidate]:
            sources[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        row = {'pair': int(match[2]), 'full_ratio': b['complete_seconds'] / a['complete_seconds']}
        row['proxies'] = {str(n): {
            'ratio': proxy(b, n) / proxy(a, n),
            'pair_seconds': proxy(a, n) + proxy(b, n),
            'pair_time_fraction': (proxy(a, n) + proxy(b, n)) / (a['complete_seconds'] + b['complete_seconds']),
        } for n in [3, 4, 5]}
        experiments.setdefault(match[1], []).append(row)

    summaries = {}
    for name, pairs in experiments.items():
        receipt = RAW / (name + '-verified.json')
        summaries[name] = {
            'pairs': len(pairs), 'retained': receipt.exists() and read(receipt).get('retained', False),
            'full_ratio': statistics.median(p['full_ratio'] for p in pairs),
            'proxies': {str(n): {
                'ratio': statistics.median(p['proxies'][str(n)]['ratio'] for p in pairs),
                'pair_time_fraction': statistics.median(p['proxies'][str(n)]['pair_time_fraction'] for p in pairs),
            } for n in [3, 4, 5]},
        }
        if receipt.exists():
            sources[receipt.name] = hashlib.sha256(receipt.read_bytes()).hexdigest()
    retained = sorted(k for k, v in summaries.items() if v['retained'])
    assert retained == ['c01', 'c07', 'c09', 'c14']
    gates = {}
    for n in [3, 4, 5]:
        gates[str(n)] = {
            'missed_retained_at_one_percent_gate': [k for k in retained if summaries[k]['proxies'][str(n)]['ratio'] > .99],
            'disagreements_with_full_one_percent_gate': [k for k, v in summaries.items()
                if (v['full_ratio'] <= .99) != (v['proxies'][str(n)]['ratio'] <= .99)],
            'median_pair_time_fraction': statistics.median(v['proxies'][str(n)]['pair_time_fraction'] for v in summaries.values()),
        }
    result = {
        'kind': 'retrospective_timing_proxy', 'verified': True,
        'scope': 'Existing large fixture, two warmup rows and one/two/three measured rows; no GPU run.',
        'limitations': 'Post-hoc proxy, selected historical candidates, no independent held-out validation. Omits no compilation cost and does not measure early-stop synchronization or clock effects. No change to current C23 protocol or final retention gates.',
        'experiments': summaries, 'gates': gates, 'pairs': experiments, 'sources': sources,
    }
    destination = RAW / 'short-screen-audit.json'
    if destination.exists():
        assert read(destination) == result
    else:
        destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'experiments': summaries, 'gates': gates}, indent=2))


if __name__ == '__main__':
    main()
