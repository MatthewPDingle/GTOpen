"""Fixed old deals/policy: isolate opponent-action sampling variance at BB root."""
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-action-noise-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX


def main():
    started = time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started < 180
        assert psutil.virtual_memory().available >= 20_000_000_000
        assert psutil.disk_usage(str(STORE.parent)).free >= 40_000_000_000
    guard(); assert not STORE.exists()
    parentpath = OUT/'sampled-physical-gpu-bank-v1-result.json'; parent = json.loads(parentpath.read_text())
    assert parent['passed']
    for p,h in parent['artifacts'].items(): assert sha(p) == h,p
    base = Path('S:/GTOpen-research/sampled-physical-gpu-bank-v1')
    fixture = json.loads((base/'profiles.json').read_text())
    query = json.loads((base/'queries.json').read_text()); obs = query['observations']
    batch = json.loads(fixture['batch_source']); n = len(batch['deals']); assert n == 16
    policy = next(p['policies'] for p in fixture['profiles'] if p['name'] == 'cpu')
    assert len(policy) == len(obs)
    context = OUT/'bb-context-candidate.json'; assert context.read_text() == fixture['context_source']
    exe = ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe'
    native = json.loads((base/'native.json').read_text()); profiles = {p['name']:p for p in native['profiles']}
    assert native['maximum_forward_cashflow_error'] < 1e-8 and native['maximum_conservation_error'] < 1e-8
    expected = np.array([[d['values'][0] for d in profiles[f'cpu-{a}']['deals']] for a in range(4)]).T
    assert expected.shape == (n,4) and np.max(np.abs(expected[:,0]+1)) < 1e-10
    reg = dict(inputs={str(p):sha(p) for p in [parentpath,context,exe,Path(__file__),
        base/'profiles.json',base/'queries.json',base/'native.json']},repetitions=64,
        action_seeds=list(range(710000,710064)),maximum_seconds=180,
        scope='Repeated opponent-action sampling on 16 unchanged old deals with a fixed full-bank policy. CPU native correctness/variance diagnosis only. No fresh physical deals, fitting, candidate selection or held-out test.',production_modified=False)
    regpath = OUT/f'{PREFIX}-registration.json'; assert not regpath.exists(); save(regpath,reg)
    STORE.mkdir(); samples = []; identities = []; maximum_fold_error = 0.
    for seed in reg['action_seeds']:
        guard(); folder = STORE/str(seed); folder.mkdir()
        trial = dict(batch,seed=seed,batch_id=f'{PREFIX}-{seed}'); batchpath = folder/'batch.json'; save(batchpath,trial)
        policypath = folder/'policies.json'; save(policypath,dict(format=2,context_source=fixture['context_source'],
            batch_source=batchpath.read_text(),policies=policy))
        updatepath = folder/'updates.json'
        done = subprocess.run([str(exe),'verify',str(context),str(batchpath),str(policypath),str(updatepath)],
            cwd=ROOT,capture_output=True,text=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
        assert done.returncode == 0,done.stderr[-2000:]
        updates = json.loads(updatepath.read_text())
        assert updates['verified_traversals'] == 2*n and updates['maximum_reference_error'] == 0
        roots = [r for r in updates['roots'] if r[1] == 0]
        assert [r[0] for r in roots] == list(range(n))
        rows = [(i,v) for i,u,tag,v in updates['records'] if u == 0 and tag == 4 and int(obs[i]['hi']) == 1]
        assert len(rows) == n
        # Records are appended in deal order. Each first updater starts at BB's
        # root; adding back its sampled value recovers all four action returns.
        values = np.array([v for _,v in rows])+np.array([r[2] for r in roots])[:,None]
        fold_error = float(np.max(np.abs(values[:,0]+1)))
        assert fold_error < 1e-10; maximum_fold_error = max(maximum_fold_error,fold_error)
        for (index,_),deal in zip(rows,trial['deals']):
            # Root key validation already occurs in the native query lookup.
            assert obs[index]['actor'] == 0 and obs[index]['phase'] == 0
        samples.append(values)
        identities.append(dict(action_seed=seed,artifacts={str(p):sha(p) for p in (batchpath,policypath,updatepath)}))
    samples = np.array(samples); variance = samples.var(axis=0,ddof=1)
    mean = samples.mean(axis=0); difference = mean-expected
    # Fixture-level total-variance decomposition: exact conditional expectations
    # remove the action-sampling component, but leave card/deal uncertainty.
    within = variance.mean(axis=0); between = expected.var(axis=0,ddof=0)
    # Fold pays exactly -1; discard only its measured floating-point residue.
    within[0] = 0.; between[0] = 0.
    reduction = np.divide(within,within+between,out=np.zeros(4),where=within+between>0)
    samplepath = STORE/'root-samples.json'
    save(samplepath,dict(exact_conditional_values_bb=expected.tolist(),sampled_values_bb=samples.tolist()))
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    for row in identities:
        for p,h in row['artifacts'].items(): assert sha(p) == h,p
    guard()
    result = dict(passed=True,registration_sha256=sha(regpath),source_fixture_deals=n,repetitions=len(samples),
        verified_traversals=2*n*len(samples),maximum_fold_identity_error_bb=maximum_fold_error,
        action_order=['fold','call','raise','jam'],
        action_sampling_variance_bb2=within.tolist(),between_fixture_deal_variance_bb2=between.tolist(),
        estimated_fixture_variance_fraction_removable=reduction.tolist(),
        rms_sample_mean_minus_exact_bb=np.sqrt((difference**2).mean(0)).tolist(),
        artifacts={str(samplepath):sha(samplepath)},repeated_batches=identities,
        seconds=time.monotonic()-started,accuracy_qualified=False,production_modified=False,
        scope=reg['scope']+' Variance fractions describe this finite fixed fixture and sampled action seeds, not a population speedup, unbiasedness proof, training improvement or convergence guarantee.')
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','repeated_batches')}))


if __name__ == '__main__': main()
