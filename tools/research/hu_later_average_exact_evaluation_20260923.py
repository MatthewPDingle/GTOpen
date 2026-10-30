"""Four fixed output-average pairings, exhaustively evaluated at all-in endpoints."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
import json
import math
from pathlib import Path
import sys
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle
from later_average_support_v1 import OUT,read,weights,load_complete_cache
from sampled_visible_hybrid_checkpoint_v1 import read_object,model_document,verify_bank
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from sampled_visible_hybrid_gpu_bank_v1 import VisibleHybridCudaBank64
from finite_btn_response_v1 import integrate
from finite_bb_root_components_v1 import components,exact_difference

LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def load_bank(reg, audit, source, count):
    objects=Path(reg['store'])/'checkpoint-objects'
    checkpoint=json.loads(read_object(objects,audit['checkpoint']))
    verify_bank(objects,count,checkpoint['played_bank'],checkpoint['next_model'],context_source=source)
    assert checkpoint['completed_iterations']==count
    return [model_document(objects,r,context_source=source) for r in checkpoint['played_bank']]


def main():
    control='--control' in sys.argv;count=4 if control else 78
    train='later-average-fresh-control-v1' if control else 'later-average-fresh-pilot-v1'
    prefix='later-average-exact-control-v1' if control else 'later-average-exact-v1'
    store=Path('S:/GTOpen-research')/prefix
    started=time.monotonic();last=0.;cuda_ready=False
    def guard():
        nonlocal last
        now=time.monotonic();assert now-started<1200
        if now-last>=2:
            assert idle() and psutil.virtual_memory().available>=20_000_000_000
            assert psutil.disk_usage('S:/').free>=40_000_000_000
            if cuda_ready:assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            last=now
    guard();assert not store.exists() and not LOCK.exists() and not OTHER.exists()
    trp,tap=[OUT/f'{train}-{s}.json' for s in ('registration','independent-review')]
    tr,ta=read(trp),read(tap)
    assert ta['passed'] and ta['terminal_complete'] and ta['completed_iterations']==count
    assert ta['source_registration_sha256']==sha(trp) and ta['control_only']==control
    for p,h in {**tr['inputs'],**ta['evidence_hashes']}.items():assert sha(p)==h,p
    context=OUT/'bb-context-candidate.json';source=context.read_text()
    cache=load_complete_cache()
    crp=OUT/'complete-private-allin-cache-v2-registration.json';cr=read(crp)
    population=read(cr['population'])
    catalog_path=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    catalog=read(catalog_path)['native_observations'];obs=[r['observation'] for r in catalog]
    assert len(obs)==265 and all(o['own_history']==[] and o['phase']==0 for o in obs)
    assert {r['hand_class'] for r in catalog if r['player']==0}==set(range(169))
    assert len({r['hand_class'] for r in catalog if r['player']==1})==96
    catrp=OUT/'preflop-catalog-control-v1-registration.json';catpp=OUT/'preflop-catalog-control-v1-result.json'
    catreg,catresult=read(catrp),read(catpp)
    assert catresult['passed'] and catresult['registration_sha256']==sha(catrp)
    assert Path(catresult['catalog_artifact'])==catalog_path and catresult['catalog_sha256']==sha(catalog_path)
    for p,h in {**catreg['inputs'],**catresult.get('artifacts',{})}.items():assert sha(p)==h,p
    inputs={**tr['inputs'],**ta['evidence_hashes'],**catreg['inputs']}
    for p in (Path(__file__),ROOT/'tools/research/hu_later_average_exact_review_20260923.py',
              ROOT/'tools/research/finite_btn_response_v1.py',ROOT/'tools/research/finite_bb_root_components_v1.py',
              ROOT/'tools/research/sampled_visible_hybrid_gpu_bank_v1.py',
              ROOT/'tools/research/sampled_visible_hybrid_cpu64_v1.py',
              trp,tap,crp,context,catalog_path,catrp,catpp,Path(cr['population'])):
        inputs[str(p)]=sha(p)
    rp=OUT/f'{prefix}-registration.json'
    reg=dict(inputs=inputs,training_registration=str(trp),training_review=str(tap),
        population=cr['population'],catalog=str(catalog_path),store=str(store),
        count=count,control_only=control,maximum_seconds=1200,
        pairings=['equal/equal','equal/linear','linear/equal','linear/linear'],
        screen='Both linear/linear gains <= 0.75 * equal/equal gains; if baseline <1e-10 require new <=1e-10.',
        scope='Exact restricted endpoint gains against each pairing opponent. Not full exploitability, seed robustness or deployment qualification.')
    save(rp,reg);store.mkdir();acquired=False;error=None
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        import torch
        cuda_ready=True
        torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        assert torch.cuda.mem_get_info()[0]>=3_000_000_000
        models=load_bank(tr,ta,source,count);policies={};artifacts={};numerics={}
        for kind in ('equal','linear'):
            guard();w=weights(kind,count)
            cpu=VisibleHybridCpuBank64(models,context_source=source,weights_by_player=w)
            query=dict(context_source=source,observations=obs)
            p,reach=cpu.average(query,guard=guard)
            gpu=VisibleHybridCudaBank64(models,w,context_source=source,models_per_chunk=8,guard=guard)
            gp,gr=gpu.average(query,guard=guard);del gpu
            pe=float(np.max(abs(gp-p)));re=float(np.max(abs(gr-reach)))
            assert pe<1e-10 and re<1e-10 and np.array_equal(reach,np.full(265,w[0].sum()))
            root=np.zeros((169,4));call=[None]*169
            for r,row in zip(catalog,p):
                if r['player']==0:root[r['hand_class']]=row
                else:call[r['hand_class']]=float(row[1])
            policy=dict(context_sha256=sha(context),checkpoint=ta['checkpoint'],schedule=kind,
                weights=w.tolist(),played_generations=list(range(count)),excluded_generation=count,
                root_probabilities=root.tolist(),btn_call_probabilities=call)
            pp=store/f'{kind}-policy.json';save(pp,policy);artifacts[str(pp)]=sha(pp)
            policies[kind]=policy;numerics[kind]=dict(maximum_policy_error=pe,maximum_reach_error=re)
        results={}
        for bb_kind in ('equal','linear'):
            for btn_kind in ('equal','linear'):
                guard();root=np.asarray(policies[bb_kind]['root_probabilities'])
                call=np.asarray([float('nan') if p is None else p for p in policies[btn_kind]['btn_call_probabilities']])
                btn=integrate(source,population,root,call,cache.rows)
                table=components(source,population,root,call,cache.rows)
                response=root.copy();classes=[]
                for row in table['classes']:
                    c=row['hand_class'];f,j=row['fold_value_per_entry'],row['jam_value_per_entry']
                    m=row['entry_probability'];assert m>0
                    if j>f:response[c,3]=root[c,0]+root[c,3];response[c,0]=0.
                    elif j<f:response[c,0]=root[c,0]+root[c,3];response[c,3]=0.
                    gain=(response[c,0]-root[c,0])*f+(response[c,3]-root[c,3])*j
                    classes.append(dict(hand_class=c,entry_probability=m,fold_value_per_entry=f,jam_value_per_entry=j,
                        baseline=root[c].tolist(),response=response[c].tolist(),gain_per_entry=float(gain)))
                bb_gain=exact_difference(table,root,response)
                assert abs(bb_gain-math.fsum(r['gain_per_entry'] for r in classes))<1e-10
                results[f'{bb_kind}/{btn_kind}']=dict(bb_gain=bb_gain,btn_gain=btn['gains_per_entry']['best'],
                    bb_classes=classes,btn=btn)
        baseline,new=results['equal/equal'],results['linear/linear']
        gates={k:bool(new[k]<=(1e-10 if baseline[k]<1e-10 else .75*baseline[k])) for k in ('bb_gain','btn_gain')}
        for p,h in {**inputs,**artifacts}.items():assert sha(p)==h,p
        guard();result=dict(passed=True,registration_sha256=sha(rp),control_only=control,
            artifacts=artifacts,numerics=numerics,pairings=results,gates=gates,
            screening_passed=None if control else all(gates.values()),seconds=time.monotonic()-started,
            production_modified=False,accuracy_qualified=False,scope=reg['scope'])
        save(OUT/f'{prefix}-result.json',result)
        print(json.dumps(dict(pairings={k:{m:v[m] for m in ('bb_gain','btn_gain')} for k,v in results.items()},screening_passed=result['screening_passed'])))
    except BaseException as exc:error=repr(exc);raise
    finally:
        try:save(OUT/f'{prefix}-status.json',dict(state='stopped' if error else 'complete',error=error,seconds=time.monotonic()-started))
        finally:
            if acquired:
                assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
