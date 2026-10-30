"""Check the fixed weighting rule against independent history-aware arithmetic."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
import json
import math
import time
from pathlib import Path
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from reboot_research_idle_v1 import idle
from later_average_support_v1 import OUT, read, weights
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from sampled_visible_hybrid_gpu_bank_v1 import VisibleHybridCudaBank64
from hu_visible_hybrid_bank_control_20260923 import reference

PREFIX='later-average-weight-control-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    start=time.monotonic()
    assert idle() and not LOCK.exists() and not OTHER.exists()
    oldrp=OUT/'sampled-visible-hybrid-bank-control-v1-registration.json'
    oldpp=OUT/'sampled-visible-hybrid-bank-control-v1-result.json'
    oldreg,old=read(oldrp),read(oldpp)
    assert old['passed'] and old['registration_sha256']==sha(oldrp)
    inputs={**oldreg['inputs'],**old['artifacts']}
    fixture=Path(read(OUT/'sampled-physical-preflop-table-control-v1-registration.json')['fixture'])
    modelpath=OUT/'sampled-visible-hybrid-bank-control-v1-models.json'
    for p in (Path(__file__), ROOT/'tools/research/later_average_support_v1.py',
              ROOT/'tools/research/hu_visible_hybrid_bank_control_20260923.py',
              ROOT/'tools/research/sampled_visible_hybrid_gpu_bank_v1.py', oldrp,oldpp,fixture,modelpath):
        inputs[str(p)]=sha(p)
    for p,h in inputs.items():assert sha(p)==h,p
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,maximum_seconds=180,schedules=['equal','linear'],
                 scope='Synthetic bank and old visible observations; no accuracy result.'))
    queries,models=read(fixture),read(modelpath)
    assert len(models)==3
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        import torch
        torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        last=0.
        def guard():
            nonlocal last
            now=time.monotonic();assert now-start<180
            if now-last>2:
                assert idle() and psutil.virtual_memory().available>=20_000_000_000
                assert torch.cuda.mem_get_info()[0]>=3_000_000_000
                last=now
        guard();records=[]
        for kind in ('equal','linear'):
            w=weights(kind,3)
            cpu=VisibleHybridCpuBank64(models,context_source=queries['context_source'],weights_by_player=w)
            actual,reach=cpu.average(queries,guard=guard)
            expected,denominator,_,policies=reference(queries,models,w)
            error=float(np.max(abs(actual-expected)));assert error<1e-11
            assert np.max(abs(reach-denominator))<1e-11
            naive=np.average(np.asarray(policies),axis=0,weights=w[0])
            history_ids=[i for i,o in enumerate(queries['observations']) if o['own_history']]
            assert history_ids
            discrepancy=float(np.max(abs(actual[history_ids]-naive[history_ids])))
            assert discrepancy>1e-4
            i=max(history_ids,key=lambda j:np.max(abs(actual[j]-naive[j])))
            o=queries['observations'][i]
            terms=[float(w[o['actor'],m])*math.prod(float(pol[prior,a]) for prior,a,_ in o['own_history'])
                   for m,pol in enumerate(policies)]
            scalar=[math.fsum(t*float(pol[i,a]) for t,pol in zip(terms,policies))/math.fsum(terms) for a in range(4)]
            assert np.max(abs(actual[i]-scalar))<1e-11
            for chunk in (1,2,3):
                gpu=VisibleHybridCudaBank64(models,w,context_source=queries['context_source'],models_per_chunk=chunk,guard=guard)
                gp,gr=gpu.average(queries,guard=guard)
                assert np.max(abs(gp-expected))<1e-10 and np.max(abs(gr-denominator))<1e-10
                del gpu
            records.append(dict(schedule=kind,weights=w.tolist(),maximum_cpu_scalar_error=error,
                own_history_rows=len(history_ids),naive_weighted_average_error=discrepancy,
                witness=dict(row=i,history=o['own_history'],realization_weights=terms,expected=scalar),cuda_chunks=[1,2,3]))
        assert weights('linear',78)[0].tolist()==list(range(1,79))
        for p,h in inputs.items():assert sha(p)==h,p
        guard()
        result=dict(passed=True,registration_sha256=sha(rp),records=records,seconds=time.monotonic()-start,
                    production_modified=False,accuracy_qualified=False)
        save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result))
    finally:
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
