"""Read-only evidence coverage; no fitting, prediction or acceptance changes."""
import collections
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from continuation_checkpoint import same_job

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'research/preflop-evolution/continuation'
RANKS = '23456789TJQKA'
LABELS = [RANKS[max(i//13, i%13)] + RANKS[min(i//13, i%13)]
          + ('' if i//13 == i%13 else 's' if i//13 > i%13 else 'o')
          for i in range(169)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def effective_count(weights):
    assert weights and all(math.isfinite(w) and w > 0 for w in weights)
    value = math.fsum(weights)**2 / math.fsum(w*w for w in weights)
    assert 1 - 1e-9 <= value <= len(weights) + 1e-9
    return value


def summarize(case, rows):
    assert len(case['weights']) == 2 and all(len(w) == 169 for w in case['weights'])
    assert all(math.isfinite(w) and w >= 0 for side in case['weights'] for w in side)
    assert all(any(w > 0 for w in side) for side in case['weights'])
    evidence = [collections.defaultdict(list), collections.defaultdict(list)]
    boards = set()
    for row in rows:
        job = row['job']
        assert job['case'] == case['id'] and job['board'] not in boards
        boards.add(job['board'])
        assert row['target_met'] is True and len(row['hands']) == 2
        scale = job['iso_weight'] / job['inclusion_probability']
        assert math.isfinite(scale) and scale > 0
        for p in range(2):
            seen = set()
            for hand in row['hands'][p]:
                label = hand['hand']
                assert label in LABELS and label not in seen
                seen.add(label)
                mass = hand['pair_mass']
                assert math.isfinite(mass) and mass >= 0
                assert all(math.isfinite(hand[k]) for k in ['ev_bb', 'equity', 'br_ev_bb'])
                assert -1e-6 <= hand['equity'] <= 1 + 1e-6
                if mass > 0:
                    evidence[p][label].append((job['board'], job['stratum'], scale*mass))
    positions = []
    for p in range(2):
        hands = []
        missing = []
        for label, range_weight in zip(LABELS, case['weights'][p]):
            if range_weight <= 0:
                continue
            observed = evidence[p][label]
            if not observed:
                missing.append(label)
                continue
            hands.append(dict(hand=label, range_weight=range_weight, observed_boards=len(observed),
                              observed_strata=len({r[1] for r in observed}),
                              effective_weight_count=effective_count([r[2] for r in observed])))
        positions.append(dict(position=['OOP', 'IP'][p], positive_classes=sum(w > 0 for w in case['weights'][p]),
                              missing_classes=missing, hands=hands,
                              minimum_observed_boards=min((h['observed_boards'] for h in hands), default=None),
                              minimum_effective_weight_count=min((h['effective_weight_count'] for h in hands), default=None),
                              median_effective_weight_count=statistics.median(h['effective_weight_count'] for h in hands) if hands else None))
    return dict(case=case['id'], boards=len(boards), positions=positions,
                all_positive_classes_observed=all(not p['missing_classes'] for p in positions))


def run(name):
    assert name in ['N15', 'N20']
    directory = BASE / ('shrunk-residual-20260916' if name == 'N15' else 'policy-transfer-optimized-20260916/N20')
    evaluation = directory / 'evaluation.json'
    assert evaluation.exists(), 'Only audit completed evaluations'
    manifest_path = directory / 'prospective/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    payload = {k: v for k, v in manifest.items() if k != 'id'}
    assert hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest() == manifest['id']
    bycase = collections.defaultdict(list)
    references = {}
    for job in manifest['jobs']:
        path = directory / 'prospective/jobs' / (job['id']+'.json')
        row = json.loads(path.read_text())
        assert row['manifest_id'] == manifest['id'] and same_job(row['job'], job)
        references[str(path.relative_to(ROOT)).replace('\\', '/')] = sha(path)
        bycase[job['case']].append(row)
    assert len(references) == len(manifest['jobs'])
    assert set(bycase) == {c['id'] for c in manifest['cases']}
    cases = [summarize(c, bycase[c['id']]) for c in manifest['cases']]
    assert all(c['boards'] == len(manifest['boards']) for c in cases)
    result = dict(checked_at=dt.datetime.now(dt.timezone.utc).isoformat(), model=name,
                  references=len(references), reference_hashes=references, cases=cases,
                  all_positive_classes_observed=all(c['all_positive_classes_observed'] for c in cases),
                  manifest_sha256=sha(manifest_path), evaluation_sha256=sha(evaluation), source_sha256=sha(__file__),
                  job_comparison_sha256=sha(Path(__file__).with_name('continuation_checkpoint.py')),
                  production_enabled=False,
                  caveat='Descriptive coverage only; no model, labels or gates changed. Effective weight count is (sum weights)^2/sum squared weights using isomorphism/inclusion/pair-mass weights. It is not an independent sample size, confidence interval or convergence measure. Positive class coverage does not imply precise values or coverage of unseen scenarios.')
    (directory/'coverage-audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    lines = ['# Reference coverage: '+name, '', result['caveat'], '',
             '| Case | Position | Positive classes | Missing classes | Minimum boards | Minimum effective weight count | Median effective weight count |',
             '|---|---|---:|---:|---:|---:|---:|']
    for c in cases:
        for p in c['positions']:
            show = lambda value: 'n/a' if value is None else f'{value:.2f}'
            lines.append(f"| {c['case']} | {p['position']} | {p['positive_classes']} | {len(p['missing_classes'])} | {p['minimum_observed_boards']} | {show(p['minimum_effective_weight_count'])} | {show(p['median_effective_weight_count'])} |")
    (directory/'COVERAGE.md').write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')
    print(name, 'references:', len(references), 'all positive classes observed:', result['all_positive_classes_observed'])


if __name__ == '__main__':
    run(sys.argv[1])
