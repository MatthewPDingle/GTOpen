"""Independent artifact/statistic readback of the fixed-deal action-noise probe."""
import json
import math
from pathlib import Path
import numpy as np
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-action-noise-control-v1'


def main():
    regpath = OUT/f'{PREFIX}-registration.json'; resultpath = OUT/f'{PREFIX}-result.json'
    reg = json.loads(regpath.read_text()); result = json.loads(resultpath.read_text())
    assert result['passed'] and result['registration_sha256'] == sha(regpath)
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    for p,h in result['artifacts'].items(): assert sha(p) == h,p
    base = Path('S:/GTOpen-research/sampled-physical-gpu-bank-v1')
    fixture = json.loads((base/'profiles.json').read_text()); profiles = {p['name']:p['policies'] for p in fixture['profiles']}
    query = json.loads((base/'queries.json').read_text()); original_batch = json.loads(fixture['batch_source'])
    for action in range(4):
        for src,dst in zip(profiles['cpu'],profiles[f'cpu-{action}']):
            assert all(src[k] == dst[k] for k in ('hi','lo','actor','n'))
            expected = [float(i == action) for i in range(4)] if int(src['hi']) == 1 and src['actor'] == 0 else src['probabilities']
            assert dst['probabilities'] == expected
    native = json.loads((base/'native.json').read_text()); outputs = {p['name']:p['deals'] for p in native['profiles']}
    expected = [[outputs[f'cpu-{a}'][i]['values'][0] for a in range(4)] for i in range(16)]
    samples = []
    assert len(result['repeated_batches']) == 64
    for record,seed in zip(result['repeated_batches'],reg['action_seeds']):
        assert record['action_seed'] == seed
        for p,h in record['artifacts'].items(): assert sha(p) == h,p
        files = {Path(p).name:Path(p) for p in record['artifacts']}
        batch = json.loads(files['batch.json'].read_text()); policy = json.loads(files['policies.json'].read_text())
        assert batch['seed'] == seed and batch['deals'] == original_batch['deals']
        assert policy['context_source'] == fixture['context_source'] and policy['batch_source'] == files['batch.json'].read_text()
        assert policy['policies'] == profiles['cpu']
        updates = json.loads(files['updates.json'].read_text())
        assert updates['verified_traversals'] == 32 and updates['maximum_reference_error'] == 0
        root_values = [r[2] for r in updates['roots'] if r[1] == 0]
        advantages = [v for i,u,tag,v in updates['records'] if u == 0 and tag == 4 and int(query['observations'][i]['hi']) == 1]
        assert len(advantages) == len(root_values) == 16
        samples.append([[v[a]+value for a in range(4)] for v,value in zip(advantages,root_values)])
    stored = json.loads(Path(next(iter(result['artifacts']))).read_text())
    assert stored['sampled_values_bb'] == samples and stored['exact_conditional_values_bb'] == expected
    def mean(x): return math.fsum(x)/len(x)
    def variance(x,ddof):
        m = mean(x); return math.fsum((v-m)**2 for v in x)/(len(x)-ddof)
    within = [mean([variance([samples[r][d][a] for r in range(64)],1) for d in range(16)]) for a in range(4)]
    between = [variance([expected[d][a] for d in range(16)],0) for a in range(4)]
    assert max(abs(samples[r][d][0]+1) for r in range(64) for d in range(16)) < 1e-10
    within[0] = between[0] = 0.
    fractions = [w/(w+b) if w+b else 0. for w,b in zip(within,between)]
    rms = [math.sqrt(mean([(mean([samples[r][d][a] for r in range(64)])-expected[d][a])**2 for d in range(16)])) for a in range(4)]
    errors = {name:max(abs(x-y) for x,y in zip(actual,result[name])) for name,actual in (
        ('action_sampling_variance_bb2',within),('between_fixture_deal_variance_bb2',between),
        ('estimated_fixture_variance_fraction_removable',fractions),('rms_sample_mean_minus_exact_bb',rms))}
    assert max(errors.values()) < 1e-9
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    review = dict(passed=True,registration_sha256=sha(regpath),result_sha256=sha(resultpath),
        reviewer_sha256=sha(Path(__file__)),repeated_batches=64,verified_traversals=2048,
        fixed_deals_and_policy_verified=True,root_only_forced_action_profiles_verified=True,
        sample_arrays_exact=True,statistic_readback_errors=errors,production_modified=False,
        scope='Independent artifact and fsum statistic reconstruction. Native execution not rerun; no training improvement or population-variance claim.')
    save(OUT/f'{PREFIX}-independent-review.json',review); print(json.dumps(review))


if __name__ == '__main__': main()
