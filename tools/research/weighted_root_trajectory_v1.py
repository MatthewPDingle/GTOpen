"""CPU-only complete-history coverage/drift diagnostic; never selects a policy."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import concurrent.futures
import json
import math
import multiprocessing
from pathlib import Path
import time
import psutil
from later_action_root_trajectory_20260926 import policy, tv, average
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from weighted_completed_bank_v1 import load_bank
from weighted_training_checkpoint_v1 import model_document
from weighted_training_policy_v1 import probabilities
from preflop_allin_matrix_v1 import AllinMatrix
from showdown_root_trajectory_20260927 import safe_read_only_resources

PREFIX = 'weighted-root-trajectory-v1'
CATALOG = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')


def summarize(policies, counts, importance, mass, expected):
    """All 78 transitions; generation78 is diagnostic, not part of the average."""
    assert len(policies) == len(counts) == len(importance) == 79
    assert len(mass) == 169 and all(math.isfinite(x) and x >= 0 for x in mass)
    assert abs(math.fsum(mass) - 1) < 1e-12
    for g, rows in enumerate(policies):
        assert len(rows) == len(counts[g]) == len(importance[g]) == 169
        assert all(type(n) is int and n >= 0 for n in counts[g])
        assert sum(counts[g]) == g * 512
        assert all(math.isfinite(x) and x >= 0 for x in importance[g])
        for row in rows:
            assert len(row) == 4 and all(math.isfinite(x) and x >= 0 for x in row)
            assert abs(math.fsum(row) - 1) < 1e-12
    assert counts[0] == [0] * 169 and importance[0] == [0.] * 169
    assert len(expected) == 169 and all(len(row) == 4 and all(math.isfinite(x) for x in row) for row in expected)
    complete = average(policies, list(range(78)))
    error = max(abs(x-y) for p,q in zip(complete, expected) for x,y in zip(p,q))
    assert error < 1e-12, 'Played average disagrees with independently checked bank'
    updates = []
    for g in range(1,79):
        increments = [b-a for a,b in zip(counts[g-1], counts[g])]
        added_mass = [b-a for a,b in zip(importance[g-1], importance[g])]
        assert min(increments) >= 3 and sum(increments) == 512
        assert min(added_mass) > 0
        updates.append(dict(generation=g, zero_sample_classes=0,
            minimum_class_deals=min(increments), maximum_class_deals=max(increments),
            source_importance_mass=math.fsum(added_mass),
            weighted_policy_step_tv=tv(policies[g-1], policies[g], mass),
            cumulative_average_tv_to_complete=tv(average(policies,list(range(g))),complete,mass),
            current_action_frequencies=[math.fsum(w*p[a] for w,p in zip(mass,policies[g])) for a in range(4)]))
    windows = [average(policies,list(range(a,b))) for a,b in ((0,26),(26,52),(52,78))]
    return dict(played_average_max_error=error, count_total=sum(counts[-1]),
        counts_min=min(counts[-1]), counts_median=sorted(counts[-1])[84], counts_max=max(counts[-1]),
        mean_zero_sample_classes_per_update=0., mean_zero_sample_entry_mass_per_update=0.,
        first_middle_window_tv=tv(windows[0],windows[1],mass),
        middle_last_window_tv=tv(windows[1],windows[2],mass),
        final_current_vs_played_average_tv=tv(policies[-1],complete,mass),
        mean_step_tv_last_26=math.fsum(x['weighted_policy_step_tv'] for x in updates[52:])/26,
        played_action_frequencies=[math.fsum(w*p[a] for w,p in zip(mass,complete)) for a in range(4)],
        counts_by_generation=counts, updates=updates,
        classes=[dict(native_class_index=c,entry_mass=mass[c],deals=counts[-1][c],
            importance_mass=importance[-1][c],average_deals_per_update=counts[-1][c]/78,
            zero_sample_updates=0,played_probabilities=complete[c],
            final_current_vs_played_average_tv=tv([policies[-1][c]],[complete[c]],[1.])) for c in range(169)])


def inspect_arm(job):
    label, expected_identity, mass, expected = job
    started = time.monotonic()
    def guard():
        assert time.monotonic()-started < 1200 and psutil.virtual_memory().available > 24_000_000_000
    source = (OUT/'bb-context-candidate.json').read_text()
    mp = OUT/'preflop-allin-matrix-control-v1-matrix.json'
    catalog = CATALOG.read_text()
    args = dict(context_source=source,catalog_source=catalog,matrix_sha256=sha(mp),
                entry_mass=AllinMatrix(read(mp),source).btn_mass)
    docs, weights, identity = load_bank(label,bank_args=args,guard=guard)
    assert identity == expected_identity and weights.tolist() == [list(range(1,79))]*2
    reg = read(OUT/'weighted-stratified-study-v1-registration.json')
    objects = Path(reg['store'])/label/'objects'
    docs.append(model_document(objects,identity['unplayed_excluded'],**args))
    root_obs = {r['hand_class']:r['observation'] for r in json.loads(catalog)['native_observations'] if r['player']==0}
    assert set(root_obs) == set(range(169))
    query = dict(context_source=source,observations=[root_obs[c] for c in range(169)])
    policies, counts, importance = [], [], []
    worst = 0.
    for g,doc in enumerate(docs):
        guard()
        assert doc['generation'] == doc['root_state']['completed_updates'] == g
        direct,_ = probabilities(query,doc,device='cpu',**{k:v for k,v in args.items() if k!='context_source'})
        state = doc['root_state']
        fallback = {c:direct[c].tolist() for c,n in enumerate(state['sample_counts']) if not n}
        scalar = policy(state,fallback)
        error = max(abs(x-y) for p,q in zip(scalar,direct) for x,y in zip(p,q))
        worst = max(worst,error)
        assert error < 1e-12
        policies.append(scalar); counts.append(state['sample_counts']); importance.append(state['importance_mass'])
    return dict(arm=label,maximum_policy_readback_error=worst,seconds=time.monotonic()-started,
                **summarize(policies,counts,importance,mass,expected))


def main():
    started = time.monotonic()
    assert safe_read_only_resources() and psutil.cpu_percent(interval=1) < 60
    def guard():
        assert time.monotonic()-started < 1500 and safe_read_only_resources()
    cp = OUT/'weighted-complete-evaluation-control-v1-result.json'
    ap = OUT/'weighted-complete-evaluation-control-v1-independent-review.json'
    result, audit = read(cp), read(ap)
    assert result['passed'] and result['complete'] and audit['passed'] and audit['source_result_sha256']==sha(cp)
    store = Path(result['store']); ip=store/'bank-identities.json'; sp=store/'root-stability.json'
    assert sha(ip)==result['bank_identities_sha256'] and sha(sp)==result['root_stability_sha256']
    identities, roots = read(ip), read(sp)
    oldp = OUT/'showdown-root-trajectory-v1-result.json'; oldreg=OUT/'showdown-root-trajectory-v1-registration.json'
    old = read(oldp)
    assert old['passed'] and old['registration_sha256']==sha(oldreg)
    # Bind the already qualified baseline diagnostics to exactly these banks.
    old_result_path=OUT/'showdown-pipelined-evaluation-study-v1-result.json'
    old_result=read(old_result_path); oldstore=Path(old_result['store'])
    oldip=oldstore/'bank-identities.json'; oldsp=oldstore/'root-stability.json'
    oldids, oldroots = read(oldip), read(oldsp)
    assert sha(oldip)==old_result['bank_identities_sha256'] and sha(oldsp)==old_result['root_stability_sha256']
    for p,h in read(oldreg)['inputs'].items():
        guard(); assert sha(p)==h, p
    assert roots['entry_masses']==oldroots['entry_masses']
    for i in (0,2):
        assert identities[i]['arm']==oldids[i]['arm']==old['findings'][i]['arm']
        assert identities[i]['model_references']==oldids[i]['model_references']
        assert max(abs(a-b) for p,q in zip(roots['root_probabilities'][i],oldroots['root_probabilities'][i]) for a,b in zip(p,q))<1e-12
    helper=OUT/'weighted-root-trajectory-control-v1-result.json'
    assert read(helper)['passed'] and read(helper)['source_sha256']==sha(Path(__file__))
    inputs={str(p):sha(p) for p in [cp,ap,ip,sp,oldp,oldreg,old_result_path,oldip,oldsp,helper,*Path(__file__).parent.glob('*.py')]}
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,workers=2,new_deals=0,gpu_used=False,
        scope='All 78 transitions and all169 classes; complete average only; no checkpoint selection or strength claim.'))
    jobs=[(identities[i]['arm'],identities[i],roots['entry_masses'],roots['root_probabilities'][i]) for i in (1,3)]
    pool=concurrent.futures.ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn'))
    try:
        futures=[pool.submit(inspect_arm,job) for job in jobs]
        candidates=[]
        for future in futures:
            while True:
                guard()
                try: candidates.append(future.result(timeout=5)); break
                except concurrent.futures.TimeoutError: pass
    except BaseException:
        for p in list(pool._processes.values()):
            if p.is_alive(): p.terminate()
        raise
    finally: pool.shutdown(wait=True,cancel_futures=True)
    for p,h in inputs.items():
        guard(); assert sha(p)==h,p
    findings=[old['findings'][0],candidates[0],old['findings'][2],candidates[1]]
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),findings=findings,
        seconds=time.monotonic()-started,gpu_used=False,new_deals=0,production_modified=False,
        final_unplayed_generation_used_only_for_diagnostic=True,accuracy_qualified=False,
        scope='Coverage and root policy movement only; does not establish poker strength.'))


if __name__=='__main__': main()
