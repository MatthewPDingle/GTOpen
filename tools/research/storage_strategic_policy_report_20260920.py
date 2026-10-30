"""Compare root policies under the frozen common entry prior, never their EVs.

Usage: OUTPUT_PREFIX --source NAME RESULT_JSON ITERATION [--source ...]
Only read completed/frozen result artifacts. Does not inspect heldout results.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from storage_phase_run_20260920 import ROOT, OUT, SUB, read, sha


def hand_label(index):
    a, b = divmod(int(index), 13)
    ranks = '23456789TJQKA'
    return ranks[max(a,b)]+ranks[min(a,b)]+('' if a == b else 's' if a > b else 'o')


def check_policy(policy):
    p = np.asarray(policy, dtype=float)
    assert p.shape == (4,1326) and np.all(np.isfinite(p))
    assert p.min() >= -1e-12 and p.max() <= 1+1e-12
    assert np.max(abs(p.sum(0)-1)) < 1e-10
    return p


def summarize(policies, prior):
    w = np.asarray(prior['combo_prior'][0], dtype=float)
    classes = np.asarray(prior['combo_classes'], dtype=int)
    assert w.shape == classes.shape == (1326,)
    assert np.all(np.isfinite(w)) and w.min() >= 0 and abs(w.sum()-1) < 1e-12
    assert classes.min() >= 0 and classes.max() < 169
    cp = np.bincount(classes, weights=w, minlength=169)
    assert np.max(abs(cp-np.asarray(prior['class_prior'][0]))) < 1e-12
    policies = {name:check_policy(p) for name,p in policies.items()}
    sources = []
    for name, p in policies.items():
        rows = []
        for c in np.flatnonzero(cp > 0):
            mask = classes == c
            rows.append(dict(hand=hand_label(c), prior=float(cp[c]),
                             frequencies=(p[:,mask]@w[mask]/cp[c]).tolist()))
        freq = p@w
        reconstructed = sum(row['prior']*np.asarray(row['frequencies']) for row in rows)
        assert np.max(abs(freq-reconstructed)) < 1e-12
        sources.append(dict(name=name, standardized_root_frequencies=freq.tolist(), hands=rows))
    comparisons = []
    for a,b in itertools.combinations(policies,2):
        # Measure differences per physical combo before combining into classes:
        # opposite changes across suits must not cancel in the distance.
        tv = abs(policies[b]-policies[a]).sum(0)/2
        contribution = np.bincount(classes, weights=w*tv, minlength=169)
        total = float(tv@w)
        assert abs(total-contribution.sum()) < 1e-12 and -1e-12 <= total <= 1+1e-12
        rows = [dict(hand=hand_label(c), prior=float(cp[c]), policy_tv=float(contribution[c]/cp[c]),
                     weighted_contribution=float(contribution[c])) for c in np.flatnonzero(cp > 0)]
        rows.sort(key=lambda r:r['weighted_contribution'],reverse=True)
        comparisons.append(dict(a=a,b=b,prior_weighted_root_policy_tv=total,
                                standardized_frequency_delta=((policies[b]-policies[a])@w).tolist(),hands=rows))
    return dict(sources=sources,comparisons=comparisons)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_prefix', type=Path)
    parser.add_argument('--source', nargs=3, action='append', required=True, metavar=('NAME','RESULT','ITERATION'))
    args = parser.parse_args()
    assert len(args.source) >= 2 and len({s[0] for s in args.source}) == len(args.source)
    prior_path = OUT/'strategic-common-prior-v1.json'
    prior = read(prior_path)
    registration = read(OUT/'strategic-segments-v1-registration.json')
    assert sha(prior_path) == registration['inputs_sha256'][str(prior_path.relative_to(ROOT))]
    for path,digest in prior['inputs_sha256'].items():
        assert sha(ROOT/path) == digest, path
    tree = read(SUB)
    assert tree['nodes'][0]['actor'] == 0
    assert [a['kind'] for a in tree['nodes'][0]['actions']] == ['fold','call','raise','jam']
    actions = [a['label'] for a in tree['nodes'][0]['actions']]
    policies = {}; metadata = []
    for name,path,iteration in args.source:
        path = Path(path).resolve(); raw = path.read_bytes(); result = json.loads(raw)
        assert result['entry_cutoff'] == prior['entry_cutoff'] and result['suit_orbits'] is True
        matches = [r for r in result['records'] if r['iteration'] == int(iteration)]
        assert len(matches) == 1
        e = matches[0]['evaluation']; policies[name] = e['preflop_policy'][0]
        metadata.append(dict(name=name,path=str(path),sha256=hashlib.sha256(raw).hexdigest(),iteration=int(iteration),
                             training_panel_root_frequencies=e['root_frequencies'],within_training_panel_gap=e['gap_total']))
    report = summarize(policies,prior)
    report.update(actions=actions,source_artifacts=metadata,common_prior_sha256=sha(prior_path),
                  subtree_sha256=sha(SUB),reporter_sha256=sha(Path(__file__)),accuracy_claim=False,
                  scope='Root action policies only, standardized to the same two-live-player entry prior. Distances do not establish strategic quality. Later-node arrival frequencies and heldout EV/deviation require separate accounting. Earlier folds remain omitted.')
    dest = args.output_prefix
    assert not dest.with_suffix('.json').exists() and not dest.with_suffix('.md').exists()
    with dest.with_suffix('.json').open('x') as f:
        json.dump(report,f,indent=2,allow_nan=False)
    lines = ['# Root range comparison','',report['scope'],'',
             '| Source | '+ ' | '.join(actions)+' |','|---|'+'---:|'*4]
    for source in report['sources']:
        lines.append('| '+source['name']+' | '+' | '.join(f'{100*x:.3f}%' for x in source['standardized_root_frequencies'])+' |')
    lines += ['','Policy distance measures how much action probability changes for the same physical hands. It is not an EV loss or an accuracy score.','']
    for c in report['comparisons']:
        lines.append(f"- {c['a']} → {c['b']}: {100*c['prior_weighted_root_policy_tv']:.3f}% prior-weighted root policy distance.")
    lines += ['', 'Source iterations and training-panel gaps are retained in the JSON evidence. Different training-panel gaps are not directly comparable quality scores.']
    with dest.with_suffix('.md').open('x',encoding='utf-8') as f:
        f.write('\n'.join(lines)+'\n')
    print(json.dumps(dict(outputs=[str(dest.with_suffix(s)) for s in ['.json','.md']],comparisons=len(report['comparisons']))))


if __name__ == '__main__':
    main()
