"""Registered physical-value projection diagnostic on original saved fits."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import argparse
import concurrent.futures
import json
import multiprocessing
from pathlib import Path
import time
import traceback
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,Guard as GpuGuard,inputs,read,sha,verify,prepared_dataset
from board_later_fit_holdout_train_v1 import configure
from board_later_error_audit_math_v1 import row_totals,totals
from board_river_strength_features_v1 import geometry
from board_river_bounds_math_v1 import project,policy,predict_numpy64,error_checks,math_control,ROW_ATOL_BB2,ROW_RTOL,VIOLATION_TOLERANCE_BB,POLICY_TOLERANCE
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_features_bulk_v1 import features
from bounded_parallel_evaluation_archive_v2 import production_available
from board_prefix_publication_v1 import atomic_json

PREFIX='board-river-bounds-v1'
POT_LABELS=('under 10 bb','10-50 bb','50-100 bb','100-200 bb','200+ bb')


class CpuGuard:
    def __init__(self):self.started=time.monotonic();self.last=0.
    def __call__(self):
        assert time.monotonic()-self.started<1800
        if time.monotonic()-self.last<2:return
        assert psutil.virtual_memory().available>24_000_000_000 and production_available() and not OTHER.exists()
        assert psutil.disk_usage('S:/').free>5_000_000_000 and psutil.disk_usage('T:/').free>1_000_000_000
        self.last=time.monotonic()


def fixed_inputs():
    source,prepared,hashes=inputs()
    old_path=OUT/'board-later-fit-holdout-v1-result.json';old=read(old_path)
    old_reg=OUT/'board-later-fit-holdout-v1-registration.json'
    assert old['passed'] and old['complete'] and old['selection']['selected_steps']==512 and old['registration_sha256']==sha(old_reg)
    audit_path=OUT/'board-river-value-reference-v1-result.json';audit=read(audit_path)
    audit_reg=OUT/'board-river-value-reference-v1-registration.json'
    assert audit['passed'] and audit['complete'] and audit['registration_sha256']==sha(audit_reg)
    verify(read(audit_reg)['inputs']);hashes.update(read(audit_reg)['inputs'])
    files=[Path(__file__),ROOT/'tools/research/board_river_bounds_math_v1.py',
        ROOT/'tools/research/board_river_strength_features_v1.py',ROOT/'tools/research/board_later_error_audit_math_v1.py',
        ROOT/'tools/research/sampled_visible_hybrid_cpu64_v1.py',ROOT/'tools/research/sampled_visible_hybrid_gpu_bank_bulk_v1.py',
        OUT/'BOARD-RIVER-BOUNDS-PLAN.md',old_path,old_reg,audit_path,audit_reg]
    for row in old['datasets']:
        point=row['checkpoints'][0];assert point['step']==512 and sha(point['weights'])==point['weights_sha256'];files.append(Path(point['weights']))
    hashes.update({str(p):sha(p) for p in files})
    return source,prepared,old,read(OUT/'board-later-public-state-catalog-v1.json'),hashes


def model_parameters(point):
    import torch
    assert sha(point['weights'])==point['weights_sha256']
    state=torch.load(point['weights'],weights_only=True,map_location='cpu')
    assert set(state)=={f'{i}.{p}' for i in (0,2,4) for p in ('weight','bias')}
    assert all(v.dtype==torch.float32 and torch.isfinite(v).all() for v in state.values())
    return state,{k:v.numpy().astype(np.float64) for k,v in state.items()}


def gpu_control(data,point,seed,catalog,guard):
    import torch
    phase=data['active'][:,15].astype(int)-135;eligible,_=geometry(data['active'],data['arity'],catalog)
    selection=[]
    for mask,count in [(phase==0,65),(phase==1,64),(phase==2,64),((phase==3)&~eligible,32),(eligible,32)]:
        indices=np.flatnonzero(mask);assert len(indices)>=count
        selection.extend(indices[np.linspace(0,len(indices)-1,count,dtype=int)].tolist())
    chosen=np.array(sorted(selection));assert len(chosen)==len(np.unique(chosen))==257
    active=data['active'][chosen];arity=data['arity'][chosen]
    mask,public=geometry(active,arity,catalog);scale=data['scale']
    state,parameters=model_parameters(point)
    x=features([dict(active_features=a.tolist()) for a in active])
    cpu=predict_numpy64(x,parameters,guard);cpu_projected=project(cpu,arity,mask,public,scale)
    model=fresh_visible_network(seed).double().cuda();model.load_state_dict(state)
    with torch.no_grad():gpu=model(torch.as_tensor(x.astype(np.float64),device='cuda'))
    reference=gpu.cpu().numpy();score_error=float(np.max(np.abs(cpu-reference)));assert score_error<1e-10
    def tensor_projection(scores,selected,amounts,unit):
        p,c,r,_=amounts[selected].T
        d=(scores[selected,1]-scores[selected,0])*unit
        bounded=torch.maximum(torch.minimum(d,p-r),-c)
        adjustment=(bounded-d)/(2*unit);out=scores.clone()
        out[selected,0]-=adjustment;out[selected,1]+=adjustment
        return out
    def tensor_policy(scores,actions):
        legal=torch.arange(4,device='cuda')[None,:]<actions[:,None]
        out=torch.clamp(scores,min=0)*legal;mass=out.sum(dim=1);positive=mass>0
        out[positive]/=mass[positive,None]
        ids=torch.nonzero(~positive).flatten()
        best=scores.masked_fill(~legal,-torch.inf).argmax(dim=1)
        out[ids,best[ids]]=1.;return out
    projected=tensor_projection(gpu,torch.as_tensor(mask,device='cuda'),torch.as_tensor(public,device='cuda'),scale)
    projection_error=float(np.max(np.abs(projected.cpu().numpy()-cpu_projected)));assert projection_error<1e-10
    p=tensor_policy(projected,torch.as_tensor(arity,device='cuda')).cpu().numpy()
    policy_error=float(np.max(np.abs(p-policy(cpu_projected,arity))));assert policy_error<1e-9
    # Deliberate lower/upper violations and fallback/tie cases, independent of learned scores.
    synthetic=np.array([[-4.,8.,3.,7.],[8.,-4.,3.,7.],[-3.,-2.,-5.,99.],[-2.,-2.,-5.,99.],[0.,0.,0.,99.]])
    actions=np.array([4,3,3,3,3]);selected=np.ones(5,dtype=bool);amounts=np.array([[6.,2.,.4,100.]]*5)
    corrected=tensor_projection(torch.as_tensor(synthetic,device='cuda'),torch.as_tensor(selected,device='cuda'),torch.as_tensor(amounts,device='cuda'),1.)
    expected=project(synthetic,actions,selected,amounts,1.)
    assert np.max(np.abs(corrected.cpu().numpy()-expected))<1e-12
    assert np.max(np.abs(tensor_policy(corrected,torch.as_tensor(actions,device='cuda')).cpu().numpy()-policy(expected,actions)))<1e-12
    # Legal menus are verified by public-state replay, not guessed from arity alone.
    bad=arity.copy();at=int(np.flatnonzero(mask)[0]);bad[at]=2 if bad[at]!=2 else 3
    try:geometry(active,bad,catalog)
    except AssertionError:pass
    else:raise AssertionError('Wrong public-state menu accepted')
    return dict(passed=True,training_rows=257,eligible_rows=int(mask.sum()),maximum_cpu_gpu_score_difference=score_error,
        maximum_cpu_gpu_projection_difference=projection_error,maximum_cpu_gpu_policy_difference=policy_error,
        synthetic_ties_and_fallback=True,wrong_legal_menu_rejected=True,heldout_loss_scored=False)


def summarize(before,after,active,arity,values,weights,scale,eligible,public):
    phase=active[:,15].astype(int)-135;pot=public[:,0]
    b=row_totals(before,values,arity,weights,scale);a=row_totals(after,values,arity,weights,scale)
    p0=policy(before,arity);p1=policy(after,arity)
    l1=np.abs(p1-p0).sum(axis=1);assert np.all(l1[~eligible]==0)
    changed=l1>POLICY_TOLERANCE
    raw_delta=(before[:,1]-before[:,0])*scale;after_delta=(after[:,1]-after[:,0])*scale
    actual_delta=values[:,1]-values[:,0]
    lower=np.full(len(active),np.nan);upper=lower.copy()
    lower[eligible]=-public[eligible,1];upper[eligible]=public[eligible,0]-public[eligible,2]
    below=eligible&(raw_delta<lower-VIOLATION_TOLERANCE_BB);above=eligible&(raw_delta>upper+VIOLATION_TOLERANCE_BB)
    violation=np.zeros(len(active));violation[eligible]=np.maximum(lower[eligible]-raw_delta[eligible],np.maximum(raw_delta[eligible]-upper[eligible],0))
    assert np.all(after_delta[eligible]>=lower[eligible]-1e-10) and np.all(after_delta[eligible]<=upper[eligible]+1e-10)
    assert np.all(actual_delta[eligible]>=lower[eligible]-1e-7) and np.all(actual_delta[eligible]<=upper[eligible]+1e-7)
    action_sum_error=float(np.max(np.abs((before[:,:2].sum(axis=1)-after[:,:2].sum(axis=1))*scale)))
    assert action_sum_error<1e-10
    checks=error_checks(before,after,arity,eligible,values,scale)
    def summary(mask):
        selected=mask&eligible;mass=float(weights[mask].sum());river_mass=float(weights[selected].sum())
        violated=mask&(below|above);violation_mass=float(weights[violated].sum())
        output=dict(rows=int(mask.sum()),source_weight=mass,eligible_rows=int(selected.sum()),eligible_source_weight=river_mass,
            below_rows=int((mask&below).sum()),above_rows=int((mask&above).sum()),violating_source_weight=violation_mass,
            violating_eligible_weight_fraction=violation_mass/river_mass if river_mass else None,
            maximum_violation_bb=float(violation[selected].max()) if selected.any() else None,
            weighted_mean_violation_bb=float(np.dot(weights[selected],violation[selected])/river_mass) if river_mass else None,
            weighted_mean_violation_among_violators_bb=float(np.dot(weights[violated],violation[violated])/violation_mass) if violation_mass else None,
            policy_changed_rows=int((mask&changed).sum()),policy_changed_source_weight=float(weights[mask&changed].sum()),
            policy_changed_weight_fraction=float(weights[mask&changed].sum()/mass) if mass else None,
            weighted_mean_policy_l1=float(np.dot(weights[mask],l1[mask])/mass) if mass else None,
            weighted_mean_policy_tv=float(np.dot(weights[mask],l1[mask])/(2*mass)) if mass else None,
            baseline=totals(b,mask),projected=totals(a,mask))
        contrast={}
        for name,delta in [('baseline',raw_delta),('projected',after_delta)]:
            numerator=float(np.dot(weights[selected],(delta[selected]-actual_delta[selected])**2))
            energy=float(np.dot(weights[selected],actual_delta[selected]**2))
            contrast[name]=dict(rows=int(selected.sum()),source_weight=river_mass,squared_error_bb2=numerator,target_energy_bb2=energy,
                mse_bb2=numerator/river_mass if river_mass else None,error_relative_to_zero=numerator/energy if energy else None)
        output['contrast']=contrast;return output
    masks=[('all',np.ones(len(active),dtype=bool)),('postflop',phase>0)]+[(name,phase==i) for i,name in enumerate(('preflop','flop','turn','river'))]
    masks += [('eligible',eligible),('under_50bb',eligible&(pot<50))]
    metrics={name:summary(mask) for name,mask in masks}
    bins=np.searchsorted([10,50,100,200],pot,side='right')
    return dict(metrics=metrics,pots=[dict(label=name,**summary(eligible&(bins==i))) for i,name in enumerate(POT_LABELS)],
        per_row_checks=checks,maximum_fold_call_sum_error_bb=action_sum_error)


def one(item,proof,point,catalog):
    os.environ['CUDA_VISIBLE_DEVICES']='-1'
    from board_river_value_reference_v1 import source_data,endpoint_audit
    import torch
    torch.set_num_threads(1);assert not torch.cuda.is_initialized()
    began=time.monotonic();guard=CpuGuard();r,split,scale=source_data(item,proof,guard)
    state,parameters=model_parameters(point);del state
    partitions={};reproduction={}
    for index,name in ((0,'train'),(1,'validation')):
        select=split==index;active=r.active[:r.size][select];arity=r.arity[:r.size][select]
        values=r.values[:r.size][select];weights=r.deal_weights[:r.size][select]
        eligible,public=geometry(active,arity,catalog)
        endpoints=endpoint_audit(values[eligible,1]-values[eligible,0],weights[eligible],public[eligible,:3])
        assert endpoints['mismatches']==0
        x=features([dict(active_features=a.tolist()) for a in active]);guard()
        before=predict_numpy64(x,parameters,guard);after=project(before,arity,eligible,public,scale)
        output=summarize(before,after,active,arity,values,weights,scale,eligible,public)
        output['endpoint_audit']=endpoints;partitions[name]=output
        if name=='validation':
            for phase in ('all','postflop','preflop','flop','turn','river'):
                row=output['metrics'][phase]['baseline'];previous=point['validation'][phase]
                error=abs(row['normalized_loss']-previous['normalized_loss']);assert error<1e-6
                assert row['rows']==previous['rows']
                reproduction[phase]=error
    verify(item['inputs']);assert sha(point['weights'])==point['weights_sha256'] and not torch.cuda.is_initialized()
    return dict(dataset=item['name'],scale=scale,partitions=partitions,
        float64_vs_original_float32_loss_differences=reproduction,source_rows=r.size,
        final_test_rows_not_inferred=int((split==2).sum()),seconds=time.monotonic()-began,
        process_rss_bytes=psutil.Process().memory_info().rss,cuda_initialized=False)


def main(mode):
    source,prepared,old,catalog,hashes=fixed_inputs()
    if mode=='ready':print(json.dumps(dict(ready=True,datasets=4,no_training=True,full_run_device='cpu')));return
    cp=OUT/(PREFIX+'-control.json');rp=OUT/(PREFIX+'-registration.json');destination=OUT/(PREFIX+'-result.json')
    assert not LOCK.exists() and not OTHER.exists();acquired=False;pool=None
    guard=GpuGuard() if mode=='control' else CpuGuard()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();cpu=psutil.cpu_percent(interval=1);assert cpu<50
        if mode=='control':
            assert not cp.exists();math=math_control();configure()
            data=prepared_dataset(source['datasets'][0]);del data['raw'];assert data['proof']==prepared['datasets'][0]['split']
            qualified=gpu_control(data['train'],old['datasets'][0]['checkpoints'][0],data['item']['fit_seed'],catalog,guard)
            verify(hashes);result=dict(passed=True,math=math,numeric=qualified,inputs=hashes,seconds=time.monotonic()-guard.started)
            atomic_json(cp,result);print(json.dumps({k:v for k,v in result.items() if k!='inputs'}),flush=True);return
        control=read(cp);assert control['passed'] and control['inputs']==hashes
        hashes[str(cp)]=sha(cp);assert not rp.exists() and not destination.exists()
        from global_research_inventory_v2 import measure
        inventory=measure();guard()
        assert sum(v['allocated_file_bytes'] for v in inventory)+100_000_000<800_000_000_000
        registration=dict(inputs=hashes,datasets=source['datasets'],workers=4,numerical_threads_per_worker=1,
            device='cpu',precision='float32 stored weights and original float32 features exactly widened to float64 before inference',
            partitions=['train','validation'],full_run_no_cuda=True,no_training=True,new_deals=0,final_test_evaluated=False,
            projection='Only verified river Fold/Call: orthogonal projection to -C <= call-fold <= P-R in bb; other action scores unchanged.',
            policy='Existing positive-score normalization with first legal argmax fallback; single-fit diagnostic, not played-bank or EV evaluation.',
            endpoint_tolerance_bb=1e-7,violating_bound_tolerance_bb=VIOLATION_TOLERANCE_BB,policy_change_l1_tolerance=POLICY_TOLERANCE,
            per_row_error_nonincrease_atol_bb2=ROW_ATOL_BB2,per_row_error_nonincrease_rtol=ROW_RTOL,
            float64_baseline_vs_saved_float32_normalized_loss_tolerance=1e-6,pot_boundaries_bb=[10,50,100,200],
            metrics='Original weighted legal-action loss; weighted one-contrast loss; violation magnitudes; policy change counts and L1/TV.',
            summary='Per-dataset, each pot bucket, train vs validation, equal-dataset means. No policy improvement claim from L2 dominance.',
            maximum_seconds=1800,maximum_retained_bytes=100_000_000,storage_admission=inventory,cpu_admission_percent=cpu,
            production_modified=False,accuracy_qualified=False,created_unix=time.time(),pid=os.getpid(),process_created=psutil.Process().create_time())
        atomic_json(rp,registration)
        pool=concurrent.futures.ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn'))
        futures=[]
        for item,prior,fitted in zip(source['datasets'],prepared['datasets'],old['datasets']):
            assert item['name']==fitted['dataset']
            futures.append(pool.submit(one,item,prior['split'],fitted['checkpoints'][0],catalog))
        records=[]
        for future in futures:
            while True:
                guard()
                try:row=future.result(timeout=2);break
                except concurrent.futures.TimeoutError:pass
            records.append(row);v=row['partitions']['validation']['metrics']
            print(json.dumps(dict(dataset=row['dataset'],violating_eligible_weight_fraction=v['eligible']['violating_eligible_weight_fraction'],
                policy_changed_weight_fraction=v['eligible']['policy_changed_weight_fraction'],
                original_contrast_mse_bb2=v['eligible']['contrast']['baseline']['mse_bb2'],
                projected_contrast_mse_bb2=v['eligible']['contrast']['projected']['mse_bb2'],seconds=row['seconds'])),flush=True)
        pool.shutdown(wait=True);pool=None;verify(hashes)
        means={metric:{arm:float(np.mean([r['partitions']['validation']['metrics']['postflop'][arm]['normalized_loss']
            if metric=='postflop' else r['partitions']['validation']['metrics'][metric]['contrast'][arm]['mse_bb2'] for r in records])) for arm in ('baseline','projected')}
            for metric in ('postflop','eligible','under_50bb')}
        result=dict(passed=True,complete=True,registration_sha256=sha(rp),datasets=records,validation_equal_dataset_means=means,
            seconds=time.monotonic()-guard.started,final_test_evaluated=False,no_training=True,new_deals=0,
            full_run_cuda_initialized=False,production_modified=False,accuracy_qualified=False)
        assert len(json.dumps(result).encode())+rp.stat().st_size+cp.stat().st_size<100_000_000
        atomic_json(destination,result)
        print(json.dumps(dict(complete=True,means=means,seconds=result['seconds'])),flush=True)
    except Exception as error:
        failure=OUT/(PREFIX+'-'+mode+'-failure.json')
        if not failure.exists():atomic_json(failure,dict(type=type(error).__name__,message=str(error),
            traceback=traceback.format_exc(),seconds=time.monotonic()-guard.started,registration_exists=rp.exists()))
        raise
    finally:
        if pool is not None:
            for p in list(pool._processes.values()):
                if p.is_alive():p.terminate()
            pool.shutdown(wait=True,cancel_futures=True)
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('ready','control','run'),default='ready')
    main(parser.parse_args().mode)
