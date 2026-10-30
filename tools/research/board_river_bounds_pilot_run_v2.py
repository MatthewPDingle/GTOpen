"""Unchanged fixed pilot; v2 admission caps CUDA allocation for desktop sharing."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',
    CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
import json
import math
from pathlib import Path
import time
import traceback
import uuid
import numpy as np
import psutil
from board_river_bounds_pilot_support_v2 import (PREFIX,STORE,CONTROL_STORE,CONTEXT,LIMIT_BYTES,SEED,DEALS,
    ROOT,OUT,LOCK,OTHER,Guard,inputs,load,Adapter,read,sha,verify,CUDA_BUDGET_BYTES,CUDA_HEADROOM_BYTES)
from board_later_fit_holdout_train_v1 import configure
from board_prefix_publication_v1 import atomic_json
from global_research_inventory_v2 import measure as global_measure
from board_study_storage_v1 import measure as study_measure
from later_average_support_v1 import load_complete_cache
from crossed_complete_policy_batch_v1 import evaluate_batch
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison,differences,PROFILE_NAMES
from owned_columnar_evaluation_archive_v1 import OwnedColumnarEvaluationArchive,ColumnarEvaluationReader
from bounded_parallel_evaluation_archive_v2 import ParallelArchives
from weighted_evaluation_checkpoint_v1 import publish,restore_latest,committed
from sampled_physical_deals_v1 import PhysicalDeals

CP=OUT/(PREFIX+'-transport-result.json');CR=OUT/(PREFIX+'-transport-registration.json')
RP=OUT/(PREFIX+'-registration.json');RESULT=OUT/(PREFIX+'-result.json')


def immutable(path,value):
    if path.exists():assert read(path)==value,'Changed immutable artifact: '+str(path)
    else:atomic_json(path,value)


def status(value):atomic_json(OUT/(PREFIX+'-status.json'),value,replace=True)


def native_values(document):
    assert [x['name'] for x in document['profiles']]==list(PROFILE_NAMES)
    flat=np.array([[d['values'] for d in p['deals']] for p in document['profiles']],dtype=np.float64)
    return flat.transpose(1,0,2).reshape(-1,2,4,2)


def execute(batch,folder,banks,cache,guard):
    return evaluate_batch(batch=batch,folder=folder,context_path=CONTEXT,banks=banks,cache=cache,guard=guard,
        query_executable=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
        evaluation_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe')


def transport(paths,qualified,inventory,guard):
    assert not CR.exists() and not CP.exists() and not CONTROL_STORE.exists()
    original=OUT/'weighted-complete-board-root-study-v1-result.json';old=read(original)
    name='test-000000';route=old['routes'][name];source=Path(old['store'])/route['attempt']
    reader=ColumnarEvaluationReader(source,{name:route['manifest_sha256']},guard=guard)
    batch=reader.read_json(source/name/'query-batch.json');query=reader.read_json(source/name/'queries.json')
    expected=native_values(reader.read_json(source/name/'native.json'))
    assert len(batch['deals'])==32 and len(query['observations'])==14547
    paths.update({str(p):sha(p) for p in (original,source/(name+'.manifest.json'),source/(name+'.xz'))})
    reg=dict(inputs=paths,source_route=route,source_store=str(source),source_name=name,source_result_sha256=sha(original),
        batch_sha256=reader.sha256(source/name/'query-batch.json'),query_sha256=reader.sha256(source/name/'queries.json'),
        existing_unique_physical_deals=32,new_deals=0,native_payoff_tolerance_bb=1e-7,transport_policy_tolerance=1e-12,
        modes=['disabled','bounded'],purpose='Transport/accounting controls only; not pilot evidence.',storage_admission=inventory,
        maximum_new_bytes=LIMIT_BYTES,maximum_seconds=7200,production_modified=False)
    atomic_json(CR,reg);CONTROL_STORE.mkdir();guard.roots=[CONTROL_STORE]
    banks,shared,identity=load(guard,qualified);cache=load_complete_cache()
    atomic_json(CONTROL_STORE/'bank-identities.json',identity)
    archive=OwnedColumnarEvaluationArchive.create(CONTROL_STORE/('attempt-'+uuid.uuid4().hex),guard=guard)
    pool=ParallelArchives(archive,guard=guard,maximum_workers=2);records=[]
    try:
        for i,mode in enumerate(('disabled','bounded')):
            t=time.monotonic();name=f'test-{i*32:06d}';folder=archive.begin(name)
            policies=([Adapter(shared,j,False) for j in (0,0,1,1)] if mode=='disabled' else banks)
            summary=execute(batch,folder,policies,cache,guard)
            q=read(folder/'queries.json');assert q['observations']==query['observations'] and q['context_source']==query['context_source']
            got=np.asarray(summary['values']);payoff_error=None
            if mode=='disabled':
                reference=np.repeat(expected[:,:,3:4,:],4,axis=2)
                payoff_error=float(np.max(abs(got-reference)));assert payoff_error<1e-7
                assert np.max(abs(differences(got)))<1e-12
            transport_doc=read(folder/'profiles.json');probabilities=[p.average(q,guard=guard)[0] for p in policies]
            maximum=0.;actors=np.array([o['actor'] for o in q['observations']])
            for seed in range(2):
                for pair,(bb,btn) in enumerate(((0,0),(0,1),(1,0),(1,1))):
                    rows=transport_doc['profiles'][seed*4+pair]['policies']
                    correct=np.where((actors==0)[:,None],probabilities[2*seed+bb],probabilities[2*seed+btn])
                    actual=np.array([x['probabilities'] for x in rows])
                    error=float(np.max(abs(actual-correct)));assert error<1e-12;maximum=max(maximum,error)
                    assert [(x['hi'],x['lo'],x['actor'],x['n']) for x in rows]==[(o['hi'],o['lo'],o['actor'],o['n']) for o in q['observations']]
            raw_bytes=sum(p.stat().st_size for p in folder.iterdir());summary_hash=sha(folder/'summary.json')
            pool.submit(name)
            records.append(dict(mode=mode,name=name,source_deals_identical=True,source_queries_identical=True,
                maximum_disabled_payoff_difference_bb=payoff_error,maximum_transport_policy_difference=maximum,
                zero_disabled_replacement_gain=mode=='disabled',maximum_cashflow_error=summary['maximum_forward_cashflow_error'],
                maximum_conservation_error=summary['maximum_conservation_error'],raw_bytes=raw_bytes,summary_sha256=summary_hash,
                measured_batch_seconds=time.monotonic()-t))
        manifests=pool.drain();pool.close();pool=None
        for row in records:
            row['manifest_sha256']=manifests[row['name']];row['packed_bytes']=(archive.root/(row['name']+'.xz')).stat().st_size
        verify(paths);storage=study_measure(CONTROL_STORE,guard)
        result=dict(passed=True,complete=True,registration_sha256=sha(CR),records=records,
            store=str(CONTROL_STORE),archive=str(archive.root),owner_sha256=archive.owner_sha256,cache_sha256=cache.sha256,
            bank_identities_sha256=sha(CONTROL_STORE/'bank-identities.json'),storage=storage,
            seconds=time.monotonic()-guard.started,new_deals=0,accuracy_qualified=False,production_modified=False)
        atomic_json(CP,result)
        print(json.dumps(dict(transport_passed=True,seconds=result['seconds'],records=records)),flush=True)
    finally:
        if pool is not None:pool.close()


def study(paths,qualified,inventory,guard,resume,max_batches):
    control=read(CP);assert control['passed'] and control['complete'] and control['registration_sha256']==sha(CR)
    verify(read(CR)['inputs']);paths.update({str(CP):sha(CP),str(CR):sha(CR)})
    paths[str(CONTROL_STORE/'bank-identities.json')]=sha(CONTROL_STORE/'bank-identities.json')
    projection=4*max(r['packed_bytes'] for r in control['records'])*(DEALS//32)+4*max(r['raw_bytes'] for r in control['records'])+10_000_000
    assert projection<LIMIT_BYTES,'Rework execution storage before sampling'
    if resume:
        reg=read(RP);assert reg['inputs']==paths
    else:
        assert not RP.exists() and not STORE.exists() and not RESULT.exists()
        reg=dict(inputs=paths,prefix=PREFIX,store=str(STORE),deals=DEALS,test_seed=SEED,batch_size=32,checkpoint_batches=8,archive_workers=4,
            maximum_output_bytes=LIMIT_BYTES,projected_output_bytes=projection,maximum_invocation_seconds=7200,storage_admission=inventory,
            arms=['A-original','A-bounded','B-original','B-bounded'],stopping='One final look at 4096; no outcome-dependent stopping or tuning.',
            statistics='Eight paired player replacement gains; 5% family-error bounded empirical Bernstein; descriptive mean +/-1.96 SE clearly approximate.',
            next_budget_estimate='ceil((3*max paired standard deviation/0.01)^2), approximate planning only.',
            production_modified=False,accuracy_qualified=False,training_performed=False,created_unix=time.time(),
            execution_version=2,cuda_allocator_budget_bytes=CUDA_BUDGET_BYTES,cuda_headroom_bytes=CUDA_HEADROOM_BYTES,
            resource_only_change='Same qualified policies and fixed chance; adaptive free-memory check with hard allocator cap.')
        atomic_json(RP,reg);STORE.mkdir()
    assert reg['deals']==DEALS and reg['test_seed']==SEED and reg['store']==str(STORE) and reg['checkpoint_batches']==8
    assert not RESULT.exists();verify(reg['inputs']);guard.roots=[STORE]
    banks,shared,identity=load(guard,qualified)
    assert identity==read(CONTROL_STORE/'bank-identities.json')
    immutable(STORE/'bank-identities.json',identity);bank_hash=sha(STORE/'bank-identities.json')
    context_source=CONTEXT.read_text();context=json.loads(context_source);cache=load_complete_cache()
    assert cache.sha256==control['cache_sha256']
    common=dict(registration_sha256=sha(RP),bank_identities_sha256=bank_hash,context_source=context_source,guard=guard)
    if committed(STORE):
        sampler,comparison,routes,checkpoint=restore_latest(STORE,total_deals=DEALS,seed=SEED,**common)
    else:
        sampler=PhysicalDeals(context_source,mode='full_deck',seed=SEED)
        comparison=CompletePolicyComparison(stack=context['config']['stack'],dead_money=context['dead_money'],deals=DEALS)
        routes={};checkpoint=publish(STORE,sampler=sampler,comparison=comparison,routes=routes,**common)
    immutable(STORE/'sampler-initial.json',PhysicalDeals(context_source,mode='full_deck',seed=SEED).checkpoint())
    before=sampler.draws;stop=DEALS if max_batches is None else min(DEALS,before+32*max_batches)
    archive=OwnedColumnarEvaluationArchive.create(STORE/('attempt-'+uuid.uuid4().hex),guard=guard)
    pool=ParallelArchives(archive,guard=guard,maximum_workers=4);metadata={}
    atomic_json(archive.root/'invocation.json',dict(pid=os.getpid(),process_created=psutil.Process().create_time(),resumed=resume,
        registration_sha256=sha(RP),initial_completed=before,storage_admission=inventory))
    try:
        for offset in range(before,stop,32):
            guard();pool.wait_slot();name=f'test-{offset:06d}'
            batch=dict(format=2,batch_id=f'{PREFIX}-{name}',seed=0,query_limit=100000,deals=sampler.sample(32)['deals'])
            folder=archive.begin(name);summary=execute(batch,folder,banks,cache,guard)
            comparison.add(summary['values'])
            metadata[name]=dict(attempt=archive.root.name,owner_sha256=archive.owner_sha256,summary_sha256=sha(folder/'summary.json'))
            pool.submit(name)
            if ((offset-before)//32+1)%8==0 or offset+32==stop:
                for key,value in pool.drain().items():routes[key]=dict(metadata[key],manifest_sha256=value)
                checkpoint=publish(STORE,sampler=sampler,comparison=comparison,routes=routes,**common)
                progress=dict(state='running',pid=os.getpid(),completed_deals=sampler.draws,total_deals=DEALS,
                    checkpoint=checkpoint,seconds=time.monotonic()-guard.started)
                status(progress);print(json.dumps(progress),flush=True)
        pool.close();pool=None
        if sampler.draws<DEALS:
            status(dict(state='checkpointed',completed_deals=sampler.draws,total_deals=DEALS,checkpoint=checkpoint))
            return
        analysis=comparison.finish();immutable(STORE/'analysis.json',analysis)
        immutable(STORE/'sampler-final.json',sampler.checkpoint());verify(reg['inputs'])
        storage=study_measure(STORE,guard);assert storage['logical_bytes']<LIMIT_BYTES and storage['allocated_file_bytes']<LIMIT_BYTES
        result=dict(passed=True,complete=True,registration_sha256=sha(RP),store=str(STORE),deals=DEALS,test_seed=SEED,
            checkpoint=checkpoint,routes=routes,analysis_sha256=sha(STORE/'analysis.json'),bank_identities_sha256=bank_hash,
            sampler_initial_sha256=sha(STORE/'sampler-initial.json'),sampler_final_sha256=sha(STORE/'sampler-final.json'),
            storage=storage,seconds_this_invocation=time.monotonic()-guard.started,independent_review_required=True,
            peak_cuda_allocated_bytes=__import__('torch').cuda.max_memory_allocated(),
            peak_cuda_reserved_bytes=__import__('torch').cuda.max_memory_reserved(),
            accuracy_qualified=False,production_modified=False,training_performed=False)
        atomic_json(RESULT,result);status(dict(state='complete; independent readback pending',deals=DEALS))
        print(json.dumps(dict(complete=True,deals=DEALS,seconds_this_invocation=result['seconds_this_invocation'],storage=storage)),flush=True)
    finally:
        if pool is not None:pool.close()


def main(mode,resume,max_batches):
    paths,qualified=inputs()
    if mode=='ready':print(json.dumps(dict(ready=True,planned_deals=DEALS,transport_complete=CP.exists(),new_work_started=False)));return
    assert not LOCK.exists() and not OTHER.exists();guard=Guard();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();assert psutil.cpu_percent(interval=1)<50
        import torch
        configure();torch.use_deterministic_algorithms(True)
        inventory=global_measure();guard()
        already=study_measure(STORE,guard)['allocated_file_bytes'] if resume and STORE.exists() else 0
        assert sum(v['allocated_file_bytes'] for v in inventory)+max(0,LIMIT_BYTES-already)<800_000_000_000
        if mode=='control':transport(paths,qualified,inventory,guard)
        else:study(paths,qualified,inventory,guard,resume,max_batches)
    except Exception as e:
        failure=OUT/(PREFIX+f'-{mode}-failure-'+uuid.uuid4().hex+'.json')
        atomic_json(failure,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-guard.started,
            instruction='Preserve evidence. Inspect failure; if external interruption, resume longest committed prefix unchanged.'))
        status(dict(state='interrupted',error=repr(e),failure=str(failure)));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('ready','control','study'),default='ready')
    p.add_argument('--resume',action='store_true');p.add_argument('--max-batches',type=int);a=p.parse_args()
    assert (not a.resume and a.max_batches is None) or a.mode=='study'
    assert a.max_batches is None or a.max_batches>0
    main(a.mode,a.resume,a.max_batches)
