"""Fixed full-bank qualification on the first archived 32 physical deals."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
from copy import deepcopy
import gc
import json
from pathlib import Path
import time
import traceback
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,Guard,read,sha,verify
from board_later_fit_holdout_train_v1 import configure
from board_prefix_publication_v1 import atomic_json
from board_river_bounds_bank_control_v1 import control
from board_river_bounds_bank_v1 import make_layout,prepare_queries,cpu_average,CudaBank
from board_training_gpu_bank_v1 import BoardRootCudaBank64
from board_training_policy_v1 import average as original_cpu
from sampled_visible_hybrid_gpu_bank_shared_v1 import prepare_cuda_queries
from board_completed_bank_v1 import load_bank
from owned_columnar_evaluation_archive_v1 import ColumnarEvaluationReader
from preflop_allin_matrix_v1 import AllinMatrix

PREFIX='board-river-bounds-bank-v1'
LABELS=('9266201-board-root','9266301-board-root')
MODULES=('board_river_bounds_bank_v1.py','board_river_bounds_bank_control_v1.py','board_river_bounds_bank_run_v1.py',
    'board_river_bounds_math_v1.py','board_river_strength_features_v1.py','board_completed_bank_v1.py',
    'board_training_bank_layout_v1.py','board_training_gpu_bank_v1.py','board_training_policy_v1.py','board_training_checkpoint_v1.py',
    'sampled_visible_hybrid_gpu_bank_shared_v1.py','sampled_visible_hybrid_gpu_bank_bulk_v1.py','sampled_physical_hybrid_gpu_bank_v2.py',
    'shared_visible_query_arrays_v1.py','sampled_physical_bank_v1.py','sampled_visible_features_bulk_v1.py',
    'board_later_fit_holdout_run_v1.py','board_later_fit_holdout_train_v1.py','owned_columnar_evaluation_archive_v1.py',
    'global_research_inventory_v2.py')


def source_inputs():
    paths=[ROOT/'tools/research'/n for n in MODULES]
    paths += [OUT/'BOARD-RIVER-BOUNDS-BANK-PLAN.md',OUT/'board-river-bounds-v1-analysis.json',OUT/'board-river-bounds-v1-result.json']
    return {str(p):sha(p) for p in paths}


def archived_queries(guard):
    rp=OUT/'weighted-complete-board-root-study-v1-registration.json'
    result_path=OUT/'weighted-complete-board-root-study-v1-result.json';r=read(result_path)
    assert r['passed'] and r['complete'] and r['deals']==65536 and r['registration_sha256']==sha(rp)
    name='test-000000';route=r['routes'][name];store=Path(r['store'])/route['attempt']
    reader=ColumnarEvaluationReader(store,{name:route['manifest_sha256']},guard=guard)
    q=reader.read_json(store/name/'queries.json');batch=reader.read_json(store/name/'query-batch.json')
    assert len(batch['deals'])==32 and len(q['observations'])==14547
    paths=[rp,result_path,store/(name+'.manifest.json'),store/(name+'.xz')]
    identity=dict(source_result_sha256=sha(result_path),batch=name,route=route,
        query_member_sha256=reader.sha256(store/name/'queries.json'),batch_member_sha256=reader.sha256(store/name/'query-batch.json'),
        physical_deals=32,observations=len(q['observations']),selection='First registered 32-deal archive, every query with own-action history. No selection on values.')
    return q,identity,{str(p):sha(p) for p in paths}


def compare(expected,got,label):
    p,r=expected;q,s=got
    pe=float(np.max(abs(p-q)));re=float(np.max(abs(r-s)))
    assert pe<=1e-9,(label,pe)
    assert np.all(abs(r-s)<=1e-10+1e-10*abs(r)),(label,re)
    return dict(label=label,maximum_policy_difference=pe,maximum_reach_difference=re)


def rejected_inputs(docs,weights,args,query,layout,catalog,guard):
    rejected=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,AssertionError,KeyError,IndexError):rejected.append(name)
        else:raise AssertionError('Accepted invalid input: '+name)
    reject('missing_model',lambda:make_layout(docs[:-1],weights,guard=guard,**args))
    reordered=list(docs);reordered[0],reordered[1]=reordered[1],reordered[0]
    reject('reordered_models',lambda:make_layout(reordered,weights,guard=guard,**args))
    bad=list(docs);bad[0]=dict(docs[0],advantage_scales=[0.,1.])
    reject('invalid_scale',lambda:make_layout(bad,weights,guard=guard,**args))
    altered=dict(query,context_source=query['context_source']+' ')
    reject('wrong_game',lambda:prepare_queries(altered,layout,catalog))
    original=prepare_queries(query,layout,catalog)
    eligible=int(np.flatnonzero(original['eligible'])[0])
    for name,key,value in [('wrong_menu','n',2 if query['observations'][eligible]['n']!=2 else 3),
                           ('wrong_actor','actor',1-query['observations'][eligible]['actor']),
                           ('wrong_phase','phase',0)]:
        altered=deepcopy(query);altered['observations'][eligible][key]=value
        reject(name,lambda:prepare_queries(altered,layout,catalog))
    altered=deepcopy(query);at=next(i for i,o in enumerate(altered['observations']) if o['own_history'])
    altered['observations'][at]['own_history'][0][0]=len(query['observations'])
    reject('missing_ancestor',lambda:prepare_queries(altered,layout,catalog))
    altered=deepcopy(query);altered['observations'][at]['own_history'][0][0]=at
    reject('self_ancestor',lambda:prepare_queries(altered,layout,catalog))
    return rejected


def describe(before,after,prepared):
    tv=.5*np.abs(before[0]-after[0]).sum(axis=1);changed=tv>5e-13
    masks={'all':np.ones(len(tv),dtype=bool),'eligible':prepared['eligible'],
        'unprojected_reach_descendants':~prepared['eligible']&prepared['reach_affected']}
    masks.update({name:prepared['phase']==i for i,name in enumerate(('preflop','flop','turn','river'))})
    output={}
    for name,mask in masks.items():
        output[name]=dict(queries=int(mask.sum()),changed_queries=int((changed&mask).sum()),
            mean_query_tv=float(tv[mask].mean()) if mask.any() else None,
            maximum_query_tv=float(tv[mask].max()) if mask.any() else None,
            maximum_reach_change=float(np.max(abs(before[1][mask]-after[1][mask]))) if mask.any() else None)
    before_river=prepared['phase']<3
    assert np.array_equal(before[0][before_river],after[0][before_river])
    assert np.array_equal(before[1][before_river],after[1][before_river])
    unaffected=~prepared['eligible']&~prepared['reach_affected']
    assert np.array_equal(before[0][unaffected],after[0][unaffected])
    assert np.array_equal(before[1][unaffected],after[1][unaffected])
    return output


def main(mode):
    import torch
    paths=source_inputs();cp=OUT/(PREFIX+'-control.json');rp=OUT/(PREFIX+'-registration.json');destination=OUT/(PREFIX+'-result.json')
    if mode=='ready':print(json.dumps(dict(ready=True,models_per_bank=78,banks=2,physical_deals=32,new_deals=0)));return
    guard=Guard();acquired=False;completed=[]
    assert not LOCK.exists() and not OTHER.exists()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();assert psutil.cpu_percent(interval=1)<50;configure();torch.use_deterministic_algorithms(True)
        if mode=='control':
            assert not cp.exists();result=control();verify(paths)
            atomic_json(cp,dict(passed=True,controls=result,inputs=paths,seconds=time.monotonic()-guard.started))
            print(json.dumps(result),flush=True);return
        checked=read(cp);assert checked['passed'] and checked['inputs']==paths;paths[str(cp)]=sha(cp)
        assert not rp.exists() and not destination.exists()
        from global_research_inventory_v2 import measure
        inventory=measure();guard()
        assert sum(x['allocated_file_bytes'] for x in inventory)+250_000_000<800_000_000_000
        query,query_identity,more=archived_queries(guard);paths.update(more)
        context=OUT/'bb-context-candidate.json';matrix=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        catalog_path=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
        public_path=OUT/'board-later-public-state-catalog-v1.json';catalog=read(public_path)
        source=context.read_text();assert query['context_source']==source
        args=dict(context_source=source,catalog_source=catalog_path.read_text(),matrix_sha256=sha(matrix),entry_mass=AllinMatrix(read(matrix),source).btn_mass)
        paths.update({str(p):sha(p) for p in (context,matrix,catalog_path,public_path)})
        data=[]
        for label in LABELS:
            t=time.monotonic();docs,weights,identity=load_bank(label,bank_args=args,guard=guard)
            bank_args=dict(args,root_config=identity['root_config'],completed_iterations=78)
            layout=make_layout(docs,weights,guard=guard,**bank_args);prepared=prepare_queries(query,layout,catalog)
            for ref in identity['model_references']:
                p=Path('S:/GTOpen-research/board-root-matched-prefix-v1')/label/'objects'/ref['file']
                assert sha(p)==ref['sha256'];paths[str(p)]=sha(p)
            data.append(dict(label=label,docs=docs,weights=weights,identity=identity,args=bank_args,layout=layout,prepared=prepared,load_seconds=time.monotonic()-t))
            print(json.dumps(dict(state='prepared_full_bank',arm=label,models=78,seconds=data[-1]['load_seconds'])),flush=True)
        reg=dict(inputs=paths,query=query_identity,banks=[d['identity'] for d in data],
            inference='Float32 saved parameters/features exactly widened to float64; per-model/player projection before own-reach weighted averaging.',
            chunks=[1,8,78],policy_tolerance=1e-9,reach_absolute_tolerance=1e-10,reach_relative_tolerance=1e-10,
            synthetic_tolerance=1e-12,timing_repeats=3,timing_order=['baseline','bounded'],
            timing_scope='Warmed prepared-query inference with identical table/cache preparation for baseline and bounded adapter; not live production speed.',
            maximum_seconds=1800,maximum_new_bytes=250_000_000,global_allocated_cap=800_000_000_000,storage_admission=inventory,
            coverage='Every query in first existing 32-deal archive; no target labels or payoff statistics scored.',
            new_deals=0,training_performed=False,production_modified=False,accuracy_qualified=False,created_unix=time.time())
        atomic_json(rp,reg)
        for d in data:
            guard();layout=d['layout'];prep=d['prepared'];bank_args=d['args']
            bad=rejected_inputs(d['docs'],d['weights'],bank_args,query,layout,catalog,guard) if not completed else []
            policy_args={k:v for k,v in bank_args.items() if k not in ('context_source','completed_iterations')}
            t=time.monotonic()
            original=original_cpu(query,d['docs'],completed_iterations=78,weights_by_player=d['weights'],guard=guard,device='cpu',**policy_args)
            reference_seconds=time.monotonic()-t
            baseline=cpu_average(layout,prep,enabled=False,guard=guard)
            candidate=cpu_average(layout,prep,enabled=True,guard=guard)
            checks=[compare(original,baseline,'original_cpu_vs_disabled_adapter')]
            changes=describe(baseline,candidate,prep)
            shared=prepare_cuda_queries(query,guard=guard)
            old=BoardRootCudaBank64(d['docs'],d['weights'],models_per_chunk=8,guard=guard,**bank_args)
            checks.append(compare(original,old.average_prepared(shared,guard=guard),'original_cpu_vs_original_cuda'))
            bank=CudaBank(layout,guard=guard);device=bank.prepare(prep);first=None
            for chunk in (1,8,78):
                a=bank.average_prepared(device,enabled=False,chunk=chunk,guard=guard)
                b=bank.average_prepared(device,enabled=True,chunk=chunk,guard=guard)
                checks.extend([compare(baseline,a,f'cuda_disabled_chunk_{chunk}'),compare(candidate,b,f'cuda_bounded_chunk_{chunk}')])
                describe(a,b,prep)
                if first is not None:checks.append(compare(first,b,f'cuda_chunk_invariance_{chunk}'))
                else:first=b
            timings={name:[] for name in ('baseline','bounded')}
            # Both branches are already warm. Identical prepared tensors and model chunk.
            for repeat in range(3):
                for name,enabled in (('baseline',False),('bounded',True)):
                    guard();torch.cuda.synchronize();t=time.monotonic()
                    got=bank.average_prepared(device,enabled=enabled,chunk=8,guard=guard)
                    torch.cuda.synchronize();timings[name].append(time.monotonic()-t)
                    compare(candidate if enabled else baseline,got,'timing_readback')
            one=dict(arm=d['label'],models=78,load_seconds=d['load_seconds'],original_cpu_seconds=reference_seconds,
                controls=checks,rejected=bad,changes=changes,timing_seconds=timings,
                timing_median_ratio=float(np.median(timings['bounded'])/np.median(timings['baseline'])),
                scale_min=float(layout['scales'].min()),scale_max=float(layout['scales'].max()),
                peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved())
            completed.append(one);print(json.dumps(one),flush=True)
            del old,shared,bank,device;gc.collect();torch.cuda.empty_cache()
        verify(paths)
        result=dict(passed=True,complete=True,registration_sha256=sha(rp),banks=completed,synthetic_control_sha256=sha(cp),
            seconds=time.monotonic()-guard.started,gpu_probes=guard.probes,new_deals=0,training_performed=False,
            target_loss_scored=False,payoffs_scored=False,accuracy_qualified=False,production_modified=False)
        assert len(json.dumps(result).encode())+rp.stat().st_size+cp.stat().st_size<250_000_000
        atomic_json(destination,result);print(json.dumps(dict(complete=True,seconds=result['seconds'])),flush=True)
    except Exception as error:
        failure=OUT/(PREFIX+'-'+mode+'-failure.json')
        if not failure.exists():atomic_json(failure,dict(error=repr(error),traceback=traceback.format_exc(),completed=completed,seconds=time.monotonic()-guard.started))
        raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('ready','control','run'),default='ready')
    main(parser.parse_args().mode)
