"""Old-data diagnosis: exact fold/shove means in counter-strategy fitting.

No fresh confirmation: both old streams have already been inspected. Keep all
ordinary call/raise observations, original support threshold, and deterministic
tie rule. This investigates evaluation reliability, not candidate selection.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import time
from pathlib import Path
import numpy as np
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from root_residual_evaluation_v1 import prepare, residuals
from reboot_research_idle_v1 import idle

PREFIX = 'exact-aware-response-diagnostic-v1'
SOURCE = 'sampled-physical-hybrid-allin-evaluation-v1'


def main():
    started = time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started < 300
    guard()
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists(), 'Preserve registered attempts'
    inputs = {}
    def admit(prefix):
        paths = [OUT/f'{prefix}-{k}.json' for k in ('registration', 'result', 'independent-review')]
        r, p, a = map(read, paths)
        assert a['passed'] and a['result_sha256'] == sha(paths[1]) and a['registration_sha256'] == sha(paths[0])
        inputs.update({str(x):sha(x) for x in paths})
        return r, p
    sr, sp = admit(SOURCE)
    _, bp = admit('bb-fold-jam-response-v3')
    _, ep = admit('exhaustive-btn-response-v2')
    store = Path(sr['store']); response_path = store/'response.json'
    assert sha(response_path) == sp['response_sha256']
    response = read(response_path); threshold = response['minimum_training_deals']
    policy_path = Path(ep['candidates']['combined_269']['policy_artifact'])
    assert sha(policy_path) == ep['candidates']['combined_269']['policy_sha256']
    policy = read(policy_path)
    assert policy['checkpoint'] == sr['checkpoint'] == sp['checkpoint']
    base = np.asarray(policy['root_probabilities'])
    rows = bp['candidates']['combined_269']['classes']
    assert np.max(abs(np.asarray([r['baseline'] for r in rows])-base)) < 1e-12
    mass = np.array([r['entry_probability'] for r in rows])
    fold, jam = [np.array([r[k] for r in rows]) for k in ('fold_value', 'jam_value')]
    for path in (Path(__file__), ROOT/'tools/research/root_residual_evaluation_v1.py', response_path, policy_path, Path(sr['context'])):
        inputs[str(path)] = sha(path)
    streams = {}
    for name, n in [('train',8192), ('test',16384)]:
        cs, qs, bs = [], [], []
        for offset in range(0,n,16):
            folder = store/f'{SOURCE}-{name}-{offset}'; path = folder/'summary.json'; summary = read(path)
            assert sha(path) == sp['batch_summary_hashes'][folder.name]
            assert np.max(abs(np.array(summary['root_probabilities'])-base[summary['classes']])) < 1e-10
            cs.extend(summary['classes']); qs.extend(summary['action_values']); bs.extend(summary['baseline_values'])
            inputs[str(path)] = sha(path)
        streams[name] = (np.array(cs),np.array(qs),np.array(bs))
    save(rp,dict(inputs=inputs,source=SOURCE,minimum_training_deals=threshold,
        change='Replace only class mean fold/shove returns during responder fitting by independently computed exact means; preserve sampled call/raise means and fallback.',
        splits=['all 8192 training deals','first 4096 training deals','last 4096 training deals'],
        scope='Post-hoc descriptive old-data diagnosis; no new confidence claims, current-candidate access, training, native evaluation or production changes.',
        maximum_seconds=300,gpu_used=False,production_modified=False))
    tc,tq,tb = streams['train']; ec,eq,eb = streams['test']
    counts = np.bincount(tc,minlength=169)
    def fit(c,q,exact):
        ns = np.bincount(c,minlength=169); sums = np.zeros((169,4)); np.add.at(sums,c,q)
        means = sums/np.maximum(ns[:,None],1)
        if exact: means[:,0]=fold; means[:,3]=jam
        actions = np.where(ns>=threshold,np.argmax(means,axis=1),-1)
        rho = base.copy(); eligible = actions>=0; rho[eligible] = np.eye(4)[actions[eligible]]
        return actions,rho,ns
    context = read(sr['context']); lo=-context['config']['stack']; hi=context['config']['stack']+context['dead_money']
    output = {}; replay_error=0.
    for label, exact in [('original-sampled',False),('exact-aware',True)]:
        actions,rho,ns = fit(tc,tq,exact)
        if not exact:
            assert actions.tolist() == response['actions'] and ns.tolist() == response['training_counts']
        halves = [fit(tc[s],tq[s],exact) for s in (slice(0,4096),slice(4096,8192))]
        eligible = (halves[0][2]>=threshold)&(halves[1][2]>=threshold)
        disagree = eligible&(halves[0][0]!=halves[1][0])
        prepared=prepare(base,rho,mass,mass*fold,mass*jam,training_classes=tc,training_actions=tq,centre=False,lower=lo,upper=hi)
        estimates={}
        for name,(c,q,b) in streams.items():
            residual=residuals(prepared,c,q)
            raw=np.sum(rho[c]*q,axis=1)-b
            estimates[name]=dict(exact_plus_residual_mean=prepared['total_offset']+float(residual.mean()),
                residual_sample_variance=float(residual.var(ddof=1)),original_sampled_mean=float(raw.mean()))
        if not exact:
            replay_error=abs(estimates['test']['original_sampled_mean']-sp['intervals']['trained-response']['mean'])
        output[label]=dict(actions=actions.tolist(),half_actions=[x[0].tolist() for x in halves],
            half_eligible_classes=int(eligible.sum()),half_disagreeing_classes=int(disagree.sum()),
            half_disagreement_population_mass=float(mass[disagree].sum()),half_eligible_population_mass=float(mass[eligible].sum()),
            selected_population_mass_by_action={str(a):float(mass[actions==a].sum()) for a in (-1,0,1,2,3)},
            exact_fold_jam_offset=prepared['total_offset'],estimates=estimates)
    changes=np.array(output['original-sampled']['actions'])!=np.array(output['exact-aware']['actions'])
    assert replay_error<1e-10
    for p,h in inputs.items(): assert sha(p)==h,p
    guard()
    result=dict(passed=True,registration_sha256=sha(rp),comparisons=output,changed_classes=int(changes.sum()),
        changed_population_mass=float(mass[changes].sum()),maximum_original_replay_error=replay_error,
        training_count_min=int(counts.min()),training_count_median=float(np.median(counts)),training_count_max=int(counts.max()),
        seconds=time.monotonic()-started,gpu_used=False,production_modified=False,accuracy_qualified=False,
        caution='Old inspected data only; train estimates are selected on the same training outcomes and test readback is not fresh confirmation. Half-sample splitting itself reduces support.')
    save(OUT/f'{PREFIX}-result.json',result)
    print({k:v for k,v in result.items() if k!='comparisons'})
    for name, r in output.items(): print(name,{k:v for k,v in r.items() if k not in ('actions','half_actions')})


if __name__=='__main__':main()
