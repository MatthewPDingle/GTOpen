"""CPU reconstruction and artifact readback of the completed hybrid GPU control."""
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_batch_model_v1 import predict
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-hybrid-gpu-control-v1'


def main():
    import torch
    torch.set_num_threads(2); started = time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started < 120
        assert psutil.virtual_memory().available >= 20_000_000_000
    guard()
    regpath = OUT/f'{PREFIX}-registration.json'; resultpath = OUT/f'{PREFIX}-result.json'
    reg = json.loads(regpath.read_text()); result = json.loads(resultpath.read_text())
    assert result['passed'] and result['registration_sha256'] == sha(regpath)
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    for p,h in result['artifacts'].items(): assert sha(p) == h,p
    files = {Path(p).name:Path(p) for p in result['artifacts']}
    comparison = json.loads(files['comparison.json'].read_text())
    queries = json.loads(Path(reg['query_fixture']).read_text()); obs = queries['observations']
    documents = json.loads(Path(reg['models']).read_text()); weights = reg['weights']
    per_model = []
    for model in documents:
        guard(); _,p = predict(obs,model['networks'],'cpu')
        tables = [None if t is None else {(int(r['hi']),int(r['lo'])):r for r in t['rows']}
                  for t in model['preflop_tables']]
        for i,o in enumerate(obs):
            table = tables[o['actor']]; key = (int(o['hi']),int(o['lo']))
            if o['phase'] == 0 and table is not None and key in table:
                row = table[key]; values = np.array(row['mean_regret']); positive = np.maximum(values,0.)
                if positive.sum() > 0: p[i] = positive/positive.sum()
                else:
                    p[i] = 0.; p[i,int(np.argmax(values[:o['n']]))] = 1.
        per_model.append(p)
    expected = np.zeros((len(obs),4)); expected_support = []
    for i,o in enumerate(obs):
        factors = []
        for m,p in enumerate(per_model):
            reach = weights[o['actor']][m]
            for depth,(ancestor,action,n) in enumerate(o['own_history']):
                prior = obs[ancestor]
                assert prior['actor'] == o['actor'] and prior['n'] == n and 0 <= action < n
                assert prior['own_history'] == o['own_history'][:depth]
                reach *= p[ancestor,action]
            factors.append(reach)
        support = math.fsum(factors); expected_support.append(support)
        if support:
            for a in range(4): expected[i,a] = math.fsum(f*p[i,a] for f,p in zip(factors,per_model))/support
        else: expected[i,:o['n']] = 1/o['n']
    cpu = np.array(comparison['cpu']); gpu = np.array(comparison['gpu'])
    cpu_support = np.array(comparison['cpu_support']); gpu_support = np.array(comparison['gpu_support'])
    cpu_error = float(np.max(np.abs(expected-cpu))); support_reconstruction_error = float(np.max(np.abs(expected_support-cpu_support)))
    assert cpu_error < 1e-12 and support_reconstruction_error < 1e-12
    policy_error = float(np.max(np.abs(cpu-gpu))); support_error = float(np.max(np.abs(cpu_support-gpu_support)))
    assert policy_error == result['maximum_policy_error'] <= reg['policy_tolerance']
    assert support_error == result['maximum_support_error'] <= reg['support_tolerance']
    assert np.array_equal(cpu_support == 0,gpu_support == 0)
    profiles = json.loads(files['profiles.json'].read_text())
    assert profiles['context_source'] == queries['context_source'] and profiles['batch_source'] == queries['batch_source']
    for profile in profiles['profiles']:
        array = cpu if profile['name'] == 'cpu' else gpu
        assert profile['name'] in ('cpu','gpu') and len(profile['policies']) == len(obs)
        for i,row in enumerate(profile['policies']):
            assert all(row[k] == obs[i][k] for k in ('hi','lo','actor','n'))
            assert np.array_equal(row['probabilities'],array[i])
    native = json.loads(files['native.json'].read_text()); native_profiles = {p['name']:p for p in native['profiles']}
    values = [np.array([d['values'] for d in native_profiles[n]['deals']]) for n in ('cpu','gpu')]
    payoff_error = float(np.max(np.abs(values[0]-values[1])))
    assert payoff_error == result['maximum_payoff_error_bb'] <= reg['payoff_tolerance_bb']
    assert native['maximum_forward_cashflow_error'] < 1e-8 and native['maximum_conservation_error'] < 1e-8
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    for p,h in result['artifacts'].items(): assert sha(p) == h,p
    guard()
    review = dict(passed=True,registration_sha256=sha(regpath),result_sha256=sha(resultpath),
        reviewer_sha256=sha(Path(__file__)),observations=len(obs),played_fixture_models=len(documents),
        independent_cpu_policy_error=cpu_error,independent_cpu_support_error=support_reconstruction_error,
        maximum_cpu_gpu_policy_error=policy_error,maximum_cpu_gpu_payoff_error_bb=payoff_error,
        all_saved_policies_and_artifacts_verified=True,seconds=time.monotonic()-started,
        accuracy_qualified=False,production_modified=False,
        scope='Recomputed CPU neural outputs, manual table regret matching and scalar own-reach averaging. Read back GPU outputs and native payoff evidence; GPU/native execution and chunk variants not rerun. Synthetic fixed-fixture numerical control only.')
    save(OUT/f'{PREFIX}-independent-review.json',review); print(json.dumps(review))


if __name__ == '__main__': main()
