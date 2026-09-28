"""Export frozen complete-bank preflop policies; no training or fresh evaluation."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import argparse
from concurrent.futures import ThreadPoolExecutor
import gc
import json
from pathlib import Path
import sys
import threading
import time
import traceback
import uuid
import numpy as np
import river_matched_training_pilot_v1 as pilot
import sampled_visible_hybrid_checkpoint_v1 as storage

ROOT=pilot.ROOT; OUT=pilot.OUT
NAME='complete-preflop-bank-export-control-v1'
REG=OUT/(NAME+'-registration.json'); RESULT=OUT/(NAME+'-result.json')
STATUS=OUT/(NAME+'-status.json'); PLAN=OUT/'COMPLETE-PREFLOP-BANK-EXPORT-PLAN.md'
STORE=Path('S:/GTOpen-research')/NAME
SOURCE=Path('S:/GTOpen-research/weighted-complete-river-continuation-v1')
CONT='river-matched-continuation-v1'
QUERY='complete-preflop-query-catalog-control-v3'
LIMIT=16_000_000; RESERVE=16_000_000; SECONDS=1800
COUNT=110; POLICY_TOL=1e-10; REACH_TOL=1e-8
ORDER=('A-baseline','A-river','B-baseline','B-river')


def specification():
    source_reg=OUT/(CONT+'-registration.json')
    source_result=OUT/(CONT+'-result.json')
    review_path=OUT/(CONT+'-independent-review-v1.json')
    identities_path=SOURCE/'bank-identities.json'
    expected={source_reg:'6b4b4dec4d0580d3aed5b3c2a38361eb91a58ab5dee778d929b919408ebbf14a',
              source_result:'e0a81a258b3189047c3cfee9581a0ef6496eacdddc686b2c4f15c32dea1eaf95',
              review_path:'8676d3ae76e0c3d026fecc468b3052278dd8ff06a6816463a16049bc3bede5fb',
              identities_path:'4b9d3c61e2f0bc168367f3bdbc122429a827ea9b2f9b592355069b160f1c5539'}
    pilot.verify(expected)
    old=pilot.read(source_reg); result=pilot.read(source_result); review=pilot.read(review_path)
    assert result['passed'] and result['complete'] and result['registration_sha256']==pilot.sha(source_reg)
    assert result['final_iteration']==COUNT and result['evaluation']['bank_identities_sha256']==pilot.sha(identities_path)
    assert review['passed'] and review['source_result_sha256']==pilot.sha(source_result)
    review_reg=OUT/(CONT+'-review-v1-registration.json')
    assert review['readback_registration_sha256']==pilot.sha(review_reg)
    query_reg=OUT/(QUERY+'-registration.json'); query_result=OUT/(QUERY+'-result.json')
    query_path=OUT/(QUERY+'-catalog.json'); qproof=pilot.read(query_result)
    assert qproof['passed'] and qproof['registration_sha256']==pilot.sha(query_reg)
    assert qproof['catalog_sha256']==pilot.sha(query_path)=='903dab1aecf7c73045eca272d27d1d49cf53ee6821337ffe2fdd8103468ba38b'
    assert qproof['query_rows']==699 and qproof['native_own_history_links_compared']==220
    pilot.verify(pilot.read(query_reg)['inputs'])
    paths=[Path(__file__),PLAN,*expected,review_reg,query_reg,query_result,query_path,
           pilot.CONTEXT,pilot.MATRIX,pilot.CATALOG]
    for path in (pilot.CONTEXT,pilot.MATRIX,pilot.CATALOG):
        assert pilot.sha(path)==old['inputs'][str(path)]
    source=pilot.CONTEXT.read_text(); matrix=pilot.AllinMatrix(pilot.read(pilot.MATRIX),source)
    args=dict(context_source=source,catalog_source=pilot.CATALOG.read_text(),
              matrix_sha256=pilot.sha(pilot.MATRIX),entry_mass=matrix.btn_mass)
    queries=pilot.read(query_path)
    assert queries['context_source']==queries['query']['context_source']==source
    assert len(queries['rows'])==len(queries['query']['observations'])==699
    identities=pilot.read(identities_path); assert [i['arm'] for i in identities]==list(ORDER)
    for identity in identities:
        arm=identity['arm']; cfg=old['arms'][arm]['config']; pilot.checkpoint.require_config(cfg)
        folder=SOURCE/arm; progress=folder/'progress.json'; p=pilot.read(progress)
        assert pilot.sha(progress)==identity['progress_sha256']
        assert p['completed']==COUNT and p['registration_sha256']==pilot.sha(source_reg)
        assert p['checkpoint']==identity['checkpoint'] and identity['root_config']==cfg['board_root']
        path=folder/'objects'/p['checkpoint']['file']
        value=json.loads(storage.read_object(folder/'objects',p['checkpoint']))
        assert value['format']==1 and value['policy_type']==pilot.checkpoint.POLICY_TYPE
        assert value['config']==cfg and value['config_sha256']==storage.digest(storage.encoded(cfg).decode())
        assert value['context_sha256']==storage.digest(source)
        assert value['catalog_sha256']==storage.digest(args['catalog_source'])
        assert value['matrix_sha256']==args['matrix_sha256'] and value['completed_iterations']==COUNT
        assert value['played_bank']==identity['played_models'] and value['next_model']==identity['unplayed_excluded']
        assert [r['generation'] for r in value['played_bank']]==list(range(COUNT))
        assert value['next_model']['generation']==COUNT and value['next_model'] not in value['played_bank']
        paths.extend([progress,path])
    # Bind all imported local Python sources and require unchanged historical inference.
    historical_sources=[]
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix=='.py':
            p=Path(path); paths.append(p)
            if str(p) in old['inputs']:
                assert pilot.sha(p)==old['inputs'][str(p)],str(p)
                historical_sources.append(str(p))
    for name in ('board_training_policy_v1.py','board_training_checkpoint_v1.py',
                 'board_training_gpu_bank_v1.py','board_training_bank_layout_v1.py'):
        assert str(ROOT/'tools/research'/name) in historical_sources
    inputs={str(p):pilot.sha(p) for p in paths}; pilot.verify(inputs)
    return dict(format=1,inputs=inputs,bank_identities=identities,order=list(ORDER),
        original_inference_sources_verified=historical_sources,models_per_bank=COUNT,
        played_generations=[0,109],excluded_generation=110,weights='1..110 for both players',
        complete_query_count=699,cpu_reference_workers=4,cuda_model_chunk=4,
        policy_absolute_tolerance=POLICY_TOL,own_reach_absolute_tolerance=REACH_TOL,
        maximum_seconds=SECONDS,maximum_new_bytes=LIMIT,reserved_bytes=RESERVE,
        global_allocated_cap=pilot.GLOBAL_LIMIT,store=str(STORE),
        gpu_sharing='Light desktop below 65%; combined 4GB CUDA cap and 2GB external headroom; active solves have priority.',
        new_training_deals=0,new_evaluation_deals=0,learning_changed=False,production_modified=False,
        scope='Complete preflop policy export only. No new sampler, payoff estimator, numerical guarantee or poker accuracy claim.'),old,args,queries


def cpu_reference(documents,weights,ma,query,guard):
    start=time.monotonic(); guard()
    p,r=pilot.reference_average(query,documents,completed_iterations=COUNT,
        weights_by_player=weights,guard=guard,device='cpu',
        **{k:v for k,v in ma.items() if k!='context_source'})
    return dict(policy=p,own_reach=r,seconds=time.monotonic()-start)


def main(run=False):
    start=time.monotonic(); spec,old,args,queries=specification()
    if not run:
        print(json.dumps(dict(source_preflight_passed=True,banks=4,models_per_bank=COUNT,
            queries=699,research_lock_present=pilot.LOCK.exists() or pilot.OTHER.exists(),gpu_started=False)),flush=True)
        return
    assert not any(p.exists() for p in (REG,RESULT,STORE)),'Preserve previous attempts'
    ready,probe=pilot.available(); assert ready,'Other research or production has priority'
    acquired=False; cancelled=threading.Event(); executor=None
    try:
        with pilot.LOCK.open('x') as handle:handle.write(str(os.getpid()))
        acquired=True
        inventory=pilot.global_measure(); allocated=sum(r['allocated_file_bytes'] for r in inventory)
        assert allocated+LIMIT+RESERVE<=pilot.GLOBAL_LIMIT
        assert time.monotonic()-start<SECONDS
        pilot.atomic_json(REG,spec); pilot.create(STORE)
        pilot.atomic_json(STORE/'admission.json',dict(allocated_bytes=allocated,inventory=inventory,
            reserved_bytes=LIMIT+RESERVE,gpu=probe,unix=time.time()))
        pilot.STORE=STORE; pilot.STATUS=STATUS; pilot.LIMIT=LIMIT
        import torch
        assert torch.cuda.is_available()
        for arm in ORDER:
            cfg=old['arms'][arm]['config']
            assert cfg['torch_version']==torch.__version__ and cfg['numpy_version']==np.__version__
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(pilot.CUDA_BUDGET_BYTES/torch.cuda.get_device_properties(0).total_memory)
        resources=pilot.Guard()
        def cpu_guard():
            if cancelled.is_set():raise RuntimeError('Control cancelled')
            if time.monotonic()-start>=SECONDS:raise TimeoutError('Export deadline exceeded')
        def guard():cpu_guard(); resources()
        executor=ThreadPoolExecutor(max_workers=4,thread_name_prefix='preflop-reference')
        weights=np.tile(np.arange(1.,COUNT+1.),(2,1)); jobs=[]; loaded=[]; gpu_rows=[]
        for identity in spec['bank_identities']:
            guard(); arm=identity['arm']; ma=dict(args,root_config=identity['root_config'])
            pilot.status('loading_frozen_preflop_bank',arm=arm)
            before=time.monotonic(); objects=SOURCE/arm/'objects'; documents=[]
            for ref in identity['played_models']:
                guard(); documents.append(pilot.checkpoint.model_document(objects,ref,**ma))
            loaded.append(documents)
            jobs.append(executor.submit(cpu_reference,documents,weights,ma,queries['query'],cpu_guard))
            load_seconds=time.monotonic()-before
            pilot.status('exporting_complete_preflop_bank',arm=arm)
            before=time.monotonic()
            bank=pilot.BoardRootCudaBank64(documents,weights,completed_iterations=COUNT,
                models_per_chunk=4,guard=guard,**ma)
            p,r=bank.average(queries['query'],guard=guard); torch.cuda.synchronize()
            gpu_rows.append(dict(arm=arm,policy=p,own_reach=r,load_seconds=load_seconds,
                cuda_export_seconds=time.monotonic()-before))
            del bank; gc.collect(); torch.cuda.empty_cache()
            print(json.dumps(dict(state='gpu_exported',arm=arm,queries=len(p))),flush=True)
        results=[]
        for job,gpu in zip(jobs,gpu_rows):
            pilot.status('checking_full_cpu_reference',arm=gpu['arm'])
            while not job.done():guard(); time.sleep(.25)
            cpu=job.result(); guard()
            p,r=gpu['policy'],gpu['own_reach']; cp,cr=cpu['policy'],cpu['own_reach']
            assert p.shape==cp.shape==(699,4) and r.shape==cr.shape==(699,)
            legal=np.arange(4)[None,:]<np.asarray([o['n'] for o in queries['query']['observations']])[:,None]
            for pp,rr in ((p,r),(cp,cr)):
                assert np.isfinite(pp).all() and np.isfinite(rr).all() and np.all(rr>=0)
                assert np.all(pp>=0) and np.all(pp[~legal]==0) and np.max(abs(pp.sum(1)-1))<1e-12
            pe=float(np.max(abs(p-cp))); re=float(np.max(abs(r-cr)))
            assert pe<POLICY_TOL and re<REACH_TOL,(gpu['arm'],pe,re)
            path=STORE/(gpu['arm']+'-preflop.json')
            pilot.atomic_json(path,dict(format=1,arm=gpu['arm'],registration_sha256=pilot.sha(REG),
                query_catalog_sha256=pilot.sha(OUT/(QUERY+'-catalog.json')),rows=queries['rows'],
                cpu_policy=cp.tolist(),cpu_own_reach=cr.tolist(),cuda_policy=p.tolist(),cuda_own_reach=r.tolist()))
            record=dict(arm=gpu['arm'],file=str(path),sha256=pilot.sha(path),
                policy_max_absolute_error=pe,own_reach_max_absolute_error=re,
                zero_own_reach_rows=int(np.count_nonzero(r==0)),cpu_reference_seconds=cpu['seconds'],
                load_seconds=gpu['load_seconds'],cuda_export_seconds=gpu['cuda_export_seconds'])
            results.append(record); print(json.dumps(dict(passed=True,**record)),flush=True)
        executor.shutdown(wait=True); executor=None
        pilot.verify(spec['inputs']); guard(); measurement=pilot.study_measure(STORE)
        assert measurement['logical_bytes']<LIMIT
        output=dict(passed=True,complete=True,registration_sha256=pilot.sha(REG),banks=results,
            query_rows_per_bank=699,models_per_bank=COUNT,cpu_workers=4,storage=measurement,
            global_admission_allocated_bytes=allocated,seconds=time.monotonic()-start,
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
            peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),gpu_used=True,
            resource_wait_seconds=resources.wait_seconds,resource_probes=resources.probes,
            new_training_deals=0,new_evaluation_deals=0,production_modified=False,
            learning_bank_modified=False,payoff_estimator_qualified=False,accuracy_claim=False,
            limitation='Observed CPU/CUDA parity is a control, not a rigorous floating-point error bound. Native payoff decomposition and proposal sampling remain separate.')
        pilot.atomic_json(RESULT,output); pilot.status('complete',result=str(RESULT))
        print(json.dumps(dict(passed=True,complete=True,result=str(RESULT),seconds=output['seconds'])),flush=True)
    except BaseException as error:
        cancelled.set()
        pilot.atomic_json(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(
            registration_sha256=pilot.sha(REG) if REG.exists() else None,error=repr(error),
            traceback=traceback.format_exc(),preserve_partial_attempts=True))
        raise
    finally:
        cancelled.set()
        if executor is not None:executor.shutdown(wait=True,cancel_futures=True)
        if acquired:
            assert pilot.LOCK.read_text()==str(os.getpid()); pilot.LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
