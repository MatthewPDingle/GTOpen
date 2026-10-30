"""Exclusive CUDA gate for exact initial policy inference and bank averaging.

Prepared while the wider evaluation runs; refuses execution until both shared
research locks are free. No live app changes, new training or range-quality claim.
"""
import os
os.environ.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import json
from pathlib import Path
import sys
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_visible_hybrid_checkpoint_v1 import read_object
from exact_initial_hybrid_checkpoint_v1 import model_document
from exact_initial_hybrid_policy_v1 import ExactInitialCpuBank64,ExactInitialCudaBank64
from exact_initial_single_policy64_v1 import predict
from sampled_visible_hybrid_gpu_bank_v1 import VisibleHybridCudaBank64
from preflop_allin_matrix_v1 import AllinMatrix
from reboot_research_idle_v1 import idle

PREFIX='exact-initial-gpu-control-v2'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    assert sys.argv[1:]==['--run'], 'Explicit --run required for exclusive CUDA use'
    assert idle() and not LOCK.exists() and not OTHER.exists(), 'Current work retains exclusive GPU use'
    rp=OUT/f'{PREFIX}-registration.json'
    assert not rp.exists(), 'Preserve previous attempts'
    cp=OUT/'bb-context-candidate.json';source=cp.read_text()
    mp=OUT/'preflop-allin-matrix-control-v1-matrix.json';matrix=AllinMatrix(read(mp),source)
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');catalog=cat.read_text()
    args=dict(context_source=source,catalog_source=catalog,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
    inputs={};banks={}
    for label,prefix in [('synthetic_exact_states','exact-initial-checkpoint-control-v1'),
                         ('joint_cpu_training','exact-initial-joint-cpu-control-v1')]:
        rr,pp=[OUT/f'{prefix}-{suffix}.json' for suffix in ('registration','result')]
        reg,result=read(rr),read(pp)
        assert result['passed'] and result['registration_sha256']==sha(rr)
        inputs.update(reg['inputs']);inputs.update({str(rr):sha(rr),str(pp):sha(pp)})
        if label=='synthetic_exact_states':
            objects=Path(reg['store']);ref=result['checkpoint']
        else:
            objects=Path(reg['store'])/'objects';ref=result['final_checkpoint']
            auditpath=OUT/f'{prefix}-independent-review.json';audit=read(auditpath)
            assert audit['passed'] and audit['source_result_sha256']==sha(pp)
            inputs[str(auditpath)]=sha(auditpath)
        checkpoint=json.loads(read_object(objects,ref));inputs[str(objects/ref['file'])]=ref['sha256']
        banks[label]=[model_document(objects,r,**args) for r in checkpoint['played_bank']]
        for r in checkpoint['played_bank']:inputs[str(objects/r['file'])]=r['sha256']
    querypath=Path('S:/GTOpen-research/wider-root-evaluation-control-v1/train-000000/queries.json')
    summarypath=querypath.parent/'summary.json'
    assert sha(querypath)==read(summarypath)['artifacts']['queries.json']
    queries={'native_history':read(querypath),'complete_initial_catalog':dict(context_source=source,
        observations=[r['observation'] for r in json.loads(catalog)['native_observations']])}
    for p in [Path(__file__),cp,mp,cat,querypath,summarypath,*[ROOT/'tools/research'/n for n in (
        'exact_initial_hybrid_policy_v1.py','exact_initial_single_policy64_v1.py','exact_initial_hybrid_checkpoint_v1.py',
        'exact_btn_policy_table_v1.py','sampled_visible_hybrid_cpu64_v1.py',
        'sampled_visible_hybrid_gpu_bank_v1.py','sampled_physical_hybrid_gpu_bank_v2.py',
        'sampled_visible_hybrid_policy_v1.py')]]:
        inputs[str(p)]=sha(p)
    for p,h in inputs.items():assert sha(p)==h,p
    save(rp,dict(inputs=inputs,maximum_seconds=600,bank_probability_tolerance=1e-10,
        bank_reach_tolerance=1e-10,single_model_probability_tolerance=1e-10,
        fixtures={k:len(v) for k,v in banks.items()},query_sets={k:len(v['observations']) for k,v in queries.items()},
        weights=['equal','linear','opposite_per_player'],model_chunks=[1,2,4],
        scope='Float64 single-model and bank CPU/CUDA numerical policy and own-history average parity, complete initial catalog and real later queries. No training, no poker-strength claim.',production_modified=False))
    started=time.monotonic();acquired=False;error=None
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        assert not OTHER.exists() and idle()
        import torch
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        assert torch.cuda.is_available()
        def guard():
            assert time.monotonic()-started<600 and idle()
            assert psutil.virtual_memory().available>20_000_000_000
            assert psutil.disk_usage('T:/').free>40_000_000_000
            assert torch.cuda.mem_get_info()[0]>3_000_000_000
        guard();comparisons=[];single=[]
        hi=json.loads(source)['nodes'][0]['children'][3]+1
        for label,models in banks.items():
            n=len(models)
            for qlabel,q in queries.items():
                response=np.array([o['actor']==1 and int(o['hi'])==hi for o in q['observations']])
                for model in models:
                    kw=dict(catalog_source=catalog,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
                    _,pc,cc=predict(q,model,device='cpu',**kw)
                    _,pg,cg=predict(q,model,device='cuda',**kw)
                    pe=float(np.max(abs(pc-pg)))
                    assert pe<1e-10 and cc==cg
                    if model['generation']>0: assert np.array_equal(pc[response],pg[response])
                    single.append(dict(bank=label,query=qlabel,generation=model['generation'],maximum_probability_error=pe))
                for wlabel,weights in [('equal',np.ones((2,n))),('linear',np.tile(np.arange(1,n+1),(2,1))),
                                      ('opposite_per_player',np.array([np.arange(1,n+1),np.arange(n,0,-1)]))]:
                    expected,expected_reach=ExactInitialCpuBank64(models,completed_iterations=n,weights_by_player=weights,**args).average(q,guard=guard)
                    for chunk in (1,2,4):
                        gpu=ExactInitialCudaBank64(models,weights,completed_iterations=n,models_per_chunk=chunk,guard=guard,**args)
                        actual,reach=gpu.average(q,guard=guard)
                        pe=float(np.max(abs(actual-expected)));re=float(np.max(abs(reach-expected_reach)))
                        assert pe<1e-10 and re<1e-10
                        base=VisibleHybridCudaBank64([m['base_model'] for m in models],weights,
                            context_source=source,models_per_chunk=chunk,guard=guard)
                        old,old_reach=base.average(q,guard=guard)
                        assert np.array_equal(actual[~response],old[~response])
                        assert np.array_equal(reach,old_reach)
                        comparisons.append(dict(bank=label,query=qlabel,weights=wlabel,chunk=chunk,
                            maximum_probability_error=pe,maximum_reach_error=re,nonresponse_unchanged=True))
                        del gpu,base
            print(json.dumps(dict(completed_fixture=label)),flush=True)
        guard()
        for p,h in inputs.items():assert sha(p)==h,p
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
            comparisons=comparisons,single_model=single,seconds=time.monotonic()-started,
            gpu_used=True,device=torch.cuda.get_device_name(),accuracy_qualified=False,production_modified=False))
        print(json.dumps(dict(passed=True,bank_comparisons=len(comparisons),single_model_comparisons=len(single))),flush=True)
    except BaseException as exc:
        error=repr(exc)
        save(OUT/f'{PREFIX}-result.json',dict(passed=False,registration_sha256=sha(rp),error=error,
            seconds=time.monotonic()-started,production_modified=False))
        raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,production_modified=False))
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
