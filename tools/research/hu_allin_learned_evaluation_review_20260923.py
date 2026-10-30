"""Saved-artifact audit of the learned-bank conditional evaluation diagnostic."""
import hashlib
import json
from pathlib import Path
import statistics
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-allin-learned-evaluation-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    began = time.monotonic()
    rp = OUT/f'{PREFIX}-result.json'; gp = OUT/f'{PREFIX}-registration.json'
    result, reg = read(rp), read(gp)
    assert result['passed'] and result['registration_sha256'] == sha(gp)
    checked = {}
    for group in (reg['inputs'], result['artifacts']):
        for path, digest in group.items():
            assert sha(path) == digest, path
            checked[path] = digest
    rows = read(STORE/'rows.json')
    bykey = {(r['replicate'], r['pair'], r['profile']): r for r in rows}
    assert len(bykey) == len(rows) == result['profile_deals'] == 1280
    names = ['baseline']+[f'action-{i}' for i in range(4)]
    max_mixture_error = 0.
    for rep in range(16):
        folder = STORE/f'runout-{rep:02d}'
        batch, labelled = read(folder/'batch.json'), read(folder/'conditional-batch.json')
        original, conditional = read(folder/'profiles.json'), read(folder/'conditional-profiles.json')
        assert batch['deals'] == labelled['deals']
        assert original['profiles'] == conditional['profiles']
        assert original['context_source'] == conditional['context_source']
        assert original['batch_source'] == (folder/'batch.json').read_text()
        assert conditional['batch_source'] == (folder/'conditional-batch.json').read_text()
        sources = [('original',read(folder/'native.json')),('conditional',read(folder/'conditional-native.json'))]
        summary = read(folder/'summary.json')
        for kind, native in sources:
            assert [p['name'] for p in native['profiles']] == names
            assert native['maximum_forward_cashflow_error'] < 1e-10
            assert native['maximum_conservation_error'] < 1e-10
            for p in native['profiles']:
                assert len(p['deals']) == 16
                for pair,d in enumerate(p['deals']):
                    assert d['deal_index'] == pair
                    assert bykey[rep,pair,p['name']][kind] == d['values']
                    assert abs(d['terminal_mass']-1) < 1e-12
            for pair in range(16):
                mix = summary['root_probabilities'][pair]
                value = sum(mix[a]*bykey[rep,pair,f'action-{a}'][kind][0] for a in range(4))
                max_mixture_error = max(max_mixture_error, abs(value-bykey[rep,pair,'baseline'][kind][0]))
                assert bykey[rep,pair,'action-0'][kind][0] == -1
        for name in ('action-0','action-1'):
            for pair in range(16):
                r = bykey[rep,pair,name]
                assert r['allin_mass'] == 0 and r['original'] == r['conditional']
    assert max_mixture_error < 1e-9
    variances = []
    for reported in result['variance']:
        name = reported['profile']; v = [0.,0.]; m = [[],[]]
        for pair in range(16):
            for k,kind in enumerate(('original','conditional')):
                series = [bykey[rep,pair,name][kind][0] -
                          (bykey[rep,pair,'baseline'][kind][0] if name != 'baseline' else 0.)
                          for rep in range(16)]
                v[k] += statistics.variance(series); m[k].append(statistics.mean(series))
        for k,suffix in enumerate(('original','conditional')):
            assert abs(v[k]-reported[f'summed_within_pair_variance_{suffix}']) < 1e-8
            assert abs(statistics.mean(m[k])-reported[f'diagnostic_mean_{suffix}']) < 1e-10
        ratio = v[1]/v[0] if v[0] else None
        assert (ratio is None and reported['ratio'] is None) or abs(ratio-reported['ratio']) < 1e-12
        variances.append(dict(profile=name,ratio=ratio))
    audit = dict(passed=True, source_result_sha256=sha(rp),registration_sha256=sha(gp),
                 reviewer_sha256=sha(Path(__file__)),checked_file_count=len(checked),
                 profile_deals=1280,maximum_root_mixture_error_bb=max_mixture_error,
                 variance_ratios=variances,seconds=time.monotonic()-began,
                 scope='Saved input/artifact identities, same policies and deals, native accounting checks, root mixtures and independent standard-library paired-variance recomputation. Does not repeat neural inference, native execution or equity enumeration; no population accuracy claim.',
                 production_modified=False)
    dest = OUT/f'{PREFIX}-independent-review.json'
    with dest.open('x') as f: json.dump(audit,f,indent=2); f.write('\n')
    print(json.dumps(audit,indent=2))


if __name__ == '__main__':
    main()
