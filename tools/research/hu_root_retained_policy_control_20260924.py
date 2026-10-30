"""CPU/CUDA and independent own-history averaging control for root retention."""
import os
os.environ.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import json
from pathlib import Path
import sys
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_visible_hybrid_checkpoint_v1 import read_object
from root_retained_checkpoint_v1 import model_document
from root_retained_policy_v1 import RootRetainedCpuBank64,RootRetainedCudaBank64,predict
from exact_initial_single_policy64_v1 import predict as nested_predict
from preflop_allin_matrix_v1 import AllinMatrix
from reboot_research_idle_v1 import idle

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='root-retained-policy-control-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def read(p):return json.loads(Path(p).read_bytes())


def main():
    assert sys.argv[1:]==['--run'] and idle() and not LOCK.exists() and not OTHER.exists()
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    cp=OUT/'bb-context-candidate.json';source=cp.read_text()
    mp=OUT/'preflop-allin-matrix-control-v1-matrix.json';matrix=AllinMatrix(read(mp),source)
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');catalog=cat.read_text()
    args=dict(context_source=source,catalog_source=catalog,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
    inputs={};banks={}
    for label in ('cpu','gpu'):
        prefix=f'root-retained-joint-{label}-control-v1'
        rr,pp=[OUT/f'{prefix}-{s}.json' for s in ('registration','result')]
        reg,result=read(rr),read(pp)
        assert result['passed'] and result['registration_sha256']==sha(rr)
        inputs.update(reg['inputs']);inputs.update({str(rr):sha(rr),str(pp):sha(pp)})
        objects=Path(reg['store'])/'objects';ref=result['final_checkpoint']
        checkpoint=json.loads(read_object(objects,ref));inputs[str(objects/ref['file'])]=ref['sha256']
        banks[label]=[model_document(objects,r,**args) for r in checkpoint['played_bank']]
        for r in checkpoint['played_bank']:inputs[str(objects/r['file'])]=r['sha256']
    querypath=Path('S:/GTOpen-research/wider-root-evaluation-control-v1/train-000000/queries.json')
    summarypath=querypath.parent/'summary.json'
    assert sha(querypath)==read(summarypath)['artifacts']['queries.json']
    queries={'native_history':read(querypath),'catalog':dict(context_source=source,
        observations=[r['observation'] for r in json.loads(catalog)['native_observations']])}
    for p in [Path(__file__),cp,mp,cat,querypath,summarypath,*[ROOT/'tools/research'/s for s in (
            'root_retained_policy_v1.py','root_retained_checkpoint_v1.py',
            'sampled_root_policy_table_v1.py','sampled_root_regret_accumulator_v1.py',
            'exact_initial_hybrid_policy_v1.py','exact_initial_single_policy64_v1.py',
            'sampled_visible_hybrid_cpu64_v1.py','sampled_visible_hybrid_gpu_bank_v1.py')]]:
        inputs[str(p)]=sha(p)
    for p,h in inputs.items():assert sha(p)==h,p
    save(rp,dict(inputs=inputs,maximum_seconds=600,tolerance=1e-10,
        fixtures={k:len(v) for k,v in banks.items()},weights=['equal','linear','opposite'],chunks=[1,2,4],
        scope='Numeric policy parity and independent per-observation own-history products using already stored control deals. No new fitting or poker accuracy claim.',production_modified=False))
    start=time.monotonic();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert not OTHER.exists() and idle()
        import torch
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        def guard():
            assert time.monotonic()-start<600 and idle()
            assert psutil.virtual_memory().available>20_000_000_000
            assert torch.cuda.mem_get_info()[0]>3_000_000_000
        guard();comparisons=[];singles=[];override_effect=0.
        for label,models in banks.items():
            n=len(models)
            for qlabel,q in queries.items():
                obs=q['observations'];allp=[]
                for m in models:
                    kw=dict(catalog_source=catalog,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
                    _,pc,cc=predict(q,m,device='cpu',**kw)
                    _,pg,cg=predict(q,m,device='cuda',**kw)
                    _,pn,_=nested_predict(q,m['exact_model'],device='cpu',**kw)
                    nonroot=[i for i,o in enumerate(obs) if int(o['hi'])!=1]
                    assert np.array_equal(pc[nonroot],pn[nonroot])
                    override_effect=max(override_effect,float(np.max(abs(pc-pn))))
                    error=float(np.max(abs(pc-pg)));assert error<1e-10 and cc==cg
                    singles.append(dict(bank=label,query=qlabel,generation=m['generation'],maximum_error=error))
                    allp.append(pc)
                for wlabel,w in [('equal',np.ones((2,n))),('linear',np.tile(np.arange(1,n+1),(2,1))),
                                 ('opposite',np.array([np.arange(1,n+1),np.arange(n,0,-1)]))]:
                    # Direct reference: no bank implementation or history helper.
                    numerator=np.zeros((len(obs),4));denominator=np.zeros(len(obs))
                    for g,p in enumerate(allp):
                        for i,o in enumerate(obs):
                            reach=float(w[o['actor'],g])
                            for prior,action,arity in o['own_history']:
                                assert obs[prior]['actor']==o['actor'] and obs[prior]['n']==arity
                                reach*=float(p[prior,action])
                            numerator[i]+=reach*p[i];denominator[i]+=reach
                    expected=np.zeros_like(numerator)
                    for i,o in enumerate(obs):
                        if denominator[i]>0:expected[i]=numerator[i]/denominator[i]
                        else:expected[i,:o['n']]=1./o['n']
                    cp_,cr=RootRetainedCpuBank64(models,completed_iterations=n,weights_by_player=w,**args).average(q,guard=guard)
                    assert np.max(abs(cp_-expected))<1e-10 and np.max(abs(cr-denominator))<1e-10
                    for chunk in (1,2,4):
                        gpu=RootRetainedCudaBank64(models,w,completed_iterations=n,models_per_chunk=chunk,guard=guard,**args)
                        actual,reach=gpu.average(q,guard=guard)
                        pe=float(np.max(abs(actual-expected)));re=float(np.max(abs(reach-denominator)))
                        assert pe<1e-10 and re<1e-10
                        comparisons.append(dict(bank=label,query=qlabel,weights=wlabel,chunk=chunk,
                            maximum_probability_error=pe,maximum_reach_error=re))
                        del gpu
        assert override_effect>1e-6, 'Fixture must actually exercise changed root policies'
        for p,h in inputs.items():assert sha(p)==h,p
        out=dict(passed=True,registration_sha256=sha(rp),comparisons=comparisons,single_models=singles,
            maximum_override_effect=override_effect,seconds=time.monotonic()-start,
            gpu_used=True,production_modified=False,accuracy_qualified=False)
        save(OUT/f'{PREFIX}-result.json',out)
        print(json.dumps(dict(passed=True,comparisons=len(comparisons),single_models=len(singles),
            maximum_probability_error=max(r['maximum_probability_error'] for r in comparisons),
            maximum_reach_error=max(r['maximum_reach_error'] for r in comparisons),override_effect=override_effect)))
    except BaseException as exc:
        save(OUT/f'{PREFIX}-result.json',dict(passed=False,error=repr(exc),registration_sha256=sha(rp)))
        raise
    finally:
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
