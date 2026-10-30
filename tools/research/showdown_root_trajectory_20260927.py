"""Read-only coverage/drift diagnosis of four audited completed showdown arms."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
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
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
from composite_showdown_bank_v1 import Objects, training_gates
from preflop_allin_matrix_v1 import AllinMatrix
from exact_initial_single_policy64_v1 import predict
from reboot_research_idle_v1 import idle

PREFIX='showdown-root-trajectory-v1'


def safe_read_only_resources():
    # No app calls or mutations are needed by this CPU-only saved-file analysis.
    # A present app must still pass its original activity checks; a demonstrably
    # closed port is allowed without starting/restarting the user's application.
    listening=any(c.status==psutil.CONN_LISTEN and c.laddr.port==56708
        for c in psutil.net_connections(kind='tcp'))
    return (not listening or idle()) and psutil.virtual_memory().available>20_000_000_000


def inspect_arm(job):
    index,identity,original_store,continuation_store,source = job
    start=time.monotonic()
    def guard():
        assert time.monotonic()-start<600
        assert psutil.virtual_memory().available>20_000_000_000
    label=identity['arm'];old=Path(original_store)/label/'objects'
    objects=ReadOnlyCheckpointObjects(old,guard=guard) if index<3 else Objects(
        Path(continuation_store)/label/'objects',old,guard)
    checkpoint=json.loads(objects.read(identity['checkpoint']))
    assert checkpoint['completed_iterations']==78
    assert checkpoint['played_bank']==identity['model_references']
    context=(OUT/'bb-context-candidate.json').read_text()
    catalog=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json').read_text()
    matrix_path=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    entry_mass=AllinMatrix(read(matrix_path),context).btn_mass
    root_obs={r['hand_class']:r['observation'] for r in json.loads(catalog)['native_observations'] if r['player']==0}
    policies=[];counts=[]
    for generation,reference in enumerate([*checkpoint['played_bank'],checkpoint['next_model']]):
        guard();doc=json.loads(objects.read(reference))
        assert doc['generation']==reference['generation']==generation
        assert doc['format']==(7 if index in (0,2) else 8)
        state=doc['integrated_root']['state']
        assert state['completed_updates']==generation and len(state['sample_counts'])==len(state['regret_sums'])==169
        assert sum(state['sample_counts'])==512*generation
        missing=[c for c,n in enumerate(state['sample_counts']) if not n]
        fallback={}
        if missing:
            _,p,_=predict(dict(context_source=context,observations=[root_obs[c] for c in missing]),
                doc['exact_model'],catalog_source=catalog,matrix_sha256=sha(matrix_path),
                entry_mass=entry_mass,device='cpu')
            fallback={c:row.tolist() for c,row in zip(missing,p)}
        policies.append(policy(state,fallback));counts.append(state['sample_counts'])
    mass=source['entry_masses'];complete=average(policies,list(range(78)))
    error=max(abs(a-b) for x,y in zip(complete,source['root_probabilities'][index]) for a,b in zip(x,y))
    assert error<1e-12
    updates=[]
    for g in range(1,79):
        increments=[b-a for a,b in zip(counts[g-1],counts[g])]
        assert min(increments)>=0 and sum(increments)==512
        updates.append(dict(generation=g,zero_sample_classes=sum(n==0 for n in increments),
            zero_sample_entry_mass=math.fsum(w for w,n in zip(mass,increments) if n==0),
            weighted_policy_step_tv=tv(policies[g-1],policies[g],mass),
            cumulative_average_tv_to_complete=tv(average(policies,list(range(g))),complete,mass)))
    windows=[average(policies,list(range(a,b))) for a,b in ((0,26),(26,52),(52,78))]
    per_class=[]
    for c in range(169):
        increments=[counts[g][c]-counts[g-1][c] for g in range(1,79)]
        per_class.append(dict(native_class_index=c,entry_mass=mass[c],deals=counts[-1][c],
            average_deals_per_update=counts[-1][c]/78,zero_sample_updates=sum(n==0 for n in increments),
            final_current_vs_played_average_tv=tv([policies[-1][c]],[complete[c]],[1.])))
    return dict(arm=label,counts_min=min(counts[-1]),counts_median=sorted(counts[-1])[84],
        counts_max=max(counts[-1]),count_total=sum(counts[-1]),played_average_max_error=error,
        mean_zero_sample_classes_per_update=math.fsum(x['zero_sample_classes'] for x in updates)/78,
        mean_zero_sample_entry_mass_per_update=math.fsum(x['zero_sample_entry_mass'] for x in updates)/78,
        first_middle_window_tv=tv(windows[0],windows[1],mass),middle_last_window_tv=tv(windows[1],windows[2],mass),
        final_current_vs_played_average_tv=tv(policies[-1],complete,mass),
        mean_step_tv_last_26=math.fsum(x['weighted_policy_step_tv'] for x in updates[52:])/26,
        counts_by_generation=counts,updates=updates,classes=per_class,seconds=time.monotonic()-start)


def main():
    start=time.monotonic();assert safe_read_only_resources()
    available=psutil.virtual_memory().available
    assert available>24_000_000_000
    cpu=psutil.cpu_percent(interval=1);assert cpu<70
    rp=OUT/'showdown-pipelined-evaluation-study-v1-result.json';result=read(rp)
    audit_path=OUT/'showdown-parallel-readback-v1-independent-review.json';audit=read(audit_path)
    assert result['passed'] and result['complete'] and audit['passed'] and audit['source_result_sha256']==sha(rp)
    store=Path(result['store']);ip=store/'bank-identities.json';sp=store/'root-stability.json'
    assert sha(ip)==result['bank_identities_sha256'] and sha(sp)==result['root_stability_sha256']
    identities=read(ip);source=read(sp)
    trial=read(OUT/'showdown-matched-training-v1-registration.json')
    continuation=read(OUT/'showdown-fourth-arm-continuation-v1-registration.json')
    bindings={str(p):sha(p) for p in [rp,audit_path,ip,sp,*training_gates(),*Path(__file__).parent.glob('*.py')]}
    registration=OUT/f'{PREFIX}-registration.json'
    save(registration,dict(inputs=bindings,workers=4,maximum_seconds=900,cpu_percent_before=cpu,
        available_memory_before=available,new_deals=0,training=False,production_modified=False,
        scope='Exploratory coverage and policy movement; all four complete arms and all classes, no checkpoint selection.'))
    jobs=[(i,identity,trial['store'],continuation['store'],source) for i,identity in enumerate(identities)]
    pool=concurrent.futures.ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn'))
    try:
        futures=[pool.submit(inspect_arm,job) for job in jobs];findings=[]
        for future in futures:
            while True:
                assert time.monotonic()-start<900 and safe_read_only_resources()
                try: row=future.result(timeout=5);break
                except concurrent.futures.TimeoutError:pass
            findings.append(row)
            print(json.dumps({k:v for k,v in row.items() if k not in ('counts_by_generation','updates','classes')}),flush=True)
    except BaseException:
        for p in list(pool._processes.values()):
            if p.is_alive():p.terminate()
        raise
    finally:pool.shutdown(wait=True,cancel_futures=True)
    assert findings[0]['counts_by_generation']==findings[1]['counts_by_generation']
    assert findings[2]['counts_by_generation']==findings[3]['counts_by_generation']
    for p,h in bindings.items():assert sha(p)==h
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,exploratory=True,registration_sha256=sha(registration),
        findings=findings,matched_class_counts_identical=True,seconds=time.monotonic()-start,
        new_deals=0,gpu_used=False,production_modified=False,
        final_unplayed_generation_used_only_for_diagnostic=True,
        scope='Coverage and changing root policies only; no variance attribution or strength claim.'))


if __name__=='__main__':main()
