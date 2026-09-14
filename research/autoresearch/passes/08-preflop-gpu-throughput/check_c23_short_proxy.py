"""Prospective candidate check of the previously recorded short timing proxy.

The proxy recipe and historical audit were committed at 03eb8aa, before C23
timing. C23 is held out from that audit. This still does not measure an actual
shortened executable, which requires a separate validation run.
"""
import hashlib
import json
import statistics
import subprocess
from pathlib import Path
from audit_short_screen import HERE, RAW, read, proxy


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    lab = HERE.parents[3]
    for path in [HERE/'audit_short_screen.py', RAW/'short-screen-audit.json']:
        relative = path.relative_to(lab).as_posix()
        registered = subprocess.check_output(['git', 'show', '03eb8aa:'+relative], cwd=lab)
        assert registered == path.read_bytes(), relative
    history = read(RAW/'short-screen-audit.json')
    assert 'c23' not in history['experiments']
    qualified = read(RAW/'c23-large-repeats-verified.json')
    assert qualified['verified'] and qualified['passed_timing']
    sources = {str(p.relative_to(HERE)): sha(p) for p in
        [HERE/'audit_short_screen.py', RAW/'short-screen-audit.json', RAW/'c23-large-repeats-verified.json']}
    pairs = []
    for pair in [2, 3, 4]:
        paths = [RAW/f'c23-large-{role}-{pair}-bench.json' for role in ['control', 'candidate']]
        a, b = map(read, paths)
        for p in paths:
            sources[str(p.relative_to(HERE))] = sha(p)
        full = b['complete_seconds']/a['complete_seconds']
        estimate = proxy(b, 3)/proxy(a, 3)
        pairs.append({'pair': pair, 'full_ratio': full, 'three_row_proxy_ratio': estimate,
            'proxy_pair_seconds': proxy(a, 3)+proxy(b, 3),
            'full_pair_seconds': a['complete_seconds']+b['complete_seconds'],
            'one_percent_gate_agrees': (full <= .99) == (estimate <= .99)})
    full = statistics.median(x['full_ratio'] for x in pairs)
    estimate = statistics.median(x['three_row_proxy_ratio'] for x in pairs)
    assert full == qualified['fixtures']['large']['median_ratio']
    result = {'verified': True, 'kind': 'prospective_candidate_timing_proxy',
        'candidate': 'c23', 'recipe_registered_commit': '03eb8aa',
        'all_pair_screen_decisions_agree': all(p['one_percent_gate_agrees'] for p in pairs),
        'full_median_ratio': full, 'proxy_median_ratio': estimate,
        'ratio_difference_percentage_points': 100*(estimate-full),
        'median_proxy_pair_seconds': statistics.median(x['proxy_pair_seconds'] for x in pairs),
        'median_full_pair_seconds': statistics.median(x['full_pair_seconds'] for x in pairs),
        'pairs': pairs, 'sources': sources,
        'limitation': 'One prospective candidate, far from threshold. Subtraction from six-row timing, not actual three-row runs. Does not validate close decisions, early sync cost, compilation savings or deployment.'}
    out = RAW/'c23-short-proxy-verified.json'
    if out.exists():
        assert read(out) == result
    else:
        out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
