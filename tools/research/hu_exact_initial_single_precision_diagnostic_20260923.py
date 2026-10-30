"""Diagnose the preserved float32 single-model CUDA parity failure."""
import os
os.environ.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import json
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from exact_initial_hybrid_policy_v1 import predict
from exact_initial_hybrid_checkpoint_v1 import model_document
from sampled_visible_hybrid_checkpoint_v1 import read_object
from preflop_allin_matrix_v1 import AllinMatrix
from reboot_research_idle_v1 import idle

PREFIX='exact-initial-single-precision-diagnostic-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    assert idle() and not LOCK.exists() and not OTHER.exists()
    oldrp=OUT/'exact-initial-gpu-control-v1-registration.json'
    oldpp=OUT/'exact-initial-gpu-control-v1-result.json'
    old,failed=read(oldrp),read(oldpp)
    assert failed['passed'] is False and failed['registration_sha256']==sha(oldrp)
    inputs=dict(old['inputs']);inputs.update({str(oldrp):sha(oldrp),str(oldpp):sha(oldpp),str(Path(__file__)):sha(Path(__file__))})
    for p,h in inputs.items():assert sha(p)==h,p
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    save(rp,dict(inputs=inputs,maximum_seconds=180,
        scope='Numerical diagnosis of existing frozen fixtures after failed single float32 CPU/CUDA gate. No training or selection.',production_modified=False))
    start=time.monotonic()
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        import torch
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        source=(OUT/'bb-context-candidate.json').read_text()
        mp=OUT/'preflop-allin-matrix-control-v1-matrix.json';matrix=AllinMatrix(read(mp),source)
        catalog=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json').read_text()
        args=dict(context_source=source,catalog_source=catalog,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
        kwargs={k:v for k,v in args.items() if k!='context_source'}
        queries={'native_history':read('S:/GTOpen-research/wider-root-evaluation-control-v1/train-000000/queries.json'),
            'complete_initial_catalog':dict(context_source=source,observations=[x['observation'] for x in json.loads(catalog)['native_observations']])}
        results=[]
        for label,prefix in [('synthetic_exact_states','exact-initial-checkpoint-control-v1'),('joint_cpu_training','exact-initial-joint-cpu-control-v1')]:
            reg,res=[read(OUT/f'{prefix}-{suffix}.json') for suffix in ('registration','result')]
            objects=Path(reg['store']) if label=='synthetic_exact_states' else Path(reg['store'])/'objects'
            ref=res['checkpoint'] if label=='synthetic_exact_states' else res['final_checkpoint']
            checkpoint=json.loads(read_object(objects,ref))
            for ref in checkpoint['played_bank']:
                model=model_document(objects,ref,**args)
                for name,q in queries.items():
                    assert time.monotonic()-start<180 and idle()
                    assert psutil.virtual_memory().available>20_000_000_000 and torch.cuda.mem_get_info()[0]>3_000_000_000
                    sc,pc,cc=predict(q,model,device='cpu',**kwargs)
                    sg,pg,cg=predict(q,model,device='cuda',**kwargs)
                    errors=np.max(abs(pc-pg),axis=1);bad=np.flatnonzero(errors>=1e-5)
                    samples=[]
                    for i in sorted(bad,key=lambda i:-errors[i])[:8]:
                        o=q['observations'][i]
                        samples.append(dict(index=int(i),hi=o['hi'],lo=o['lo'],actor=o['actor'],n=o['n'],
                            cpu_scores=sc[i].tolist(),gpu_scores=sg[i].tolist(),cpu_policy=pc[i].tolist(),gpu_policy=pg[i].tolist()))
                    results.append(dict(bank=label,query=name,generation=model['generation'],coverage_equal=cc==cg,
                        maximum_score_error=float(np.max(abs(sc-sg))),maximum_policy_error=float(errors.max()),
                        rows_over_tolerance=len(bad),samples=samples))
        for p,h in inputs.items():assert sha(p)==h,p
        save(OUT/f'{PREFIX}-result.json',dict(complete=True,registration_sha256=sha(rp),comparisons=results,
            seconds=time.monotonic()-start,production_modified=False,gpu_used=True,accuracy_qualified=False))
        print(json.dumps(results),flush=True)
    finally:
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
