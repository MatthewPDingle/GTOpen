"""Full-length weighted fit equivalence on actual pilot reservoirs."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
import gc
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha,save
from weighted_learning_cuda_control_20260927 import safe_read_only_resources,LOCK,OTHER
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_training_fit_v1 import fit as direct
from weighted_training_graph_fit_v2 import fit as captured
from exact_initial_training_ingest_v2 import digest

PREFIX='weighted-graph-fit-control-v2'


def main(publish=False):
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    assert torch.cuda.is_available() and safe_read_only_resources() and not LOCK.exists() and not OTHER.exists()
    status=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
    assert status.returncode==0
    utilization,free=[float(s.strip()) for s in status.stdout.strip().splitlines()[0].split(',')]
    assert utilization<20 and free>4000
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        assert time.monotonic()-started<300
        if time.monotonic()-last>3:
            assert safe_read_only_resources() and torch.cuda.mem_get_info()[0]>3_000_000_000
            last=time.monotonic()
    rp=OUT/'weighted-training-pilot-v1-result.json';reference=read(rp)
    assert reference['passed'] and reference['exact_restart_replay']
    objects=Path(reference['store'])/'objects';cp=OUT/'bb-context-candidate.json';source=cp.read_text()
    checkpoint_path=objects/reference['final_checkpoint']['file']
    assert sha(checkpoint_path)==reference['final_checkpoint']['sha256'];state=read(checkpoint_path)
    reservoirs=[objects/r['file'] for r in state['reservoirs']]
    for p,r in zip(reservoirs,state['reservoirs']):assert sha(p)==r['sha256']
    inputs={str(p):sha(p) for p in [rp,cp,checkpoint_path,*reservoirs,*Path(__file__).parent.glob('*.py'),OUT/'WEIGHTED-GRAPH-FIT-V2-CONTROL-PLAN.md']}
    reg=OUT/f'{PREFIX}-registration.json'
    if publish:save(reg,dict(inputs=inputs,steps=512,chunk_size=2048,seed_base=9276001,
        maximum_seconds=300,exact_network_required=True,production_modified=False,accuracy_claim=False))
    acquired=False;rows=[]
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard()
        for player,path in enumerate(reservoirs):
            reservoir=WeightedPhysicalReservoir.load(path,source)
            options=dict(seed=9276001+player,steps=512,device='cuda',chunk_size=2048,guard=guard)
            torch.cuda.reset_peak_memory_stats();began=time.monotonic();a,ma=direct(reservoir,**options)
            direct_seconds=time.monotonic()-began;direct_peak=torch.cuda.max_memory_allocated()
            gc.collect();torch.cuda.empty_cache();guard()
            torch.cuda.reset_peak_memory_stats();began=time.monotonic();b,mb=captured(reservoir,**options)
            graph_seconds=time.monotonic()-began;graph_peak=torch.cuda.max_memory_allocated()
            error=max(float(np.max(abs(np.array(a[k])-b[k]))) for k in a)
            assert a==b and digest(a)==digest(b)
            ignored={'setup_seconds','optimizer_seconds','graph_capture_seconds','runtime'}
            assert {k:v for k,v in ma.items() if k not in ignored}=={k:v for k,v in mb.items() if k not in ignored}
            row=dict(player=player,retained=reservoir.size,grouped_observations=ma['grouped_observations'],
                parameter_error=error,exact_network_sha256=digest(a),direct_seconds=direct_seconds,
                graph_seconds=graph_seconds,speedup=direct_seconds/graph_seconds,direct_peak_bytes=direct_peak,
                graph_peak_bytes=graph_peak,direct=ma,captured=mb)
            rows.append(row);print(json.dumps(row),flush=True)
            gc.collect();torch.cuda.empty_cache()
        memory=[]
        for repeat in range(8):
            network,metric=captured(reservoir,seed=9277001,steps=8,device='cuda',chunk_size=2048,guard=guard)
            gc.collect();torch.cuda.synchronize();torch.cuda.empty_cache()
            memory.append(dict(fit=repeat+1,allocated=torch.cuda.memory_allocated(),reserved=torch.cuda.memory_reserved()))
        assert len({r['allocated'] for r in memory})==1,memory
        assert len({r['reserved'] for r in memory})==1,memory
        for p,h in inputs.items():assert sha(p)==h,p
        result=dict(passed=True,cases=rows,repeat_fit_memory=memory,exact_exported_networks=True,seconds=time.monotonic()-started,
            accuracy_qualified=False,production_modified=False,
            scope='Qualified sequential fit runtime and repeat-fit allocation plateau; full-trainer integration remains to be checked.')
        if publish:
            result['registration_sha256']=sha(reg);save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true')
    main(parser.parse_args().publish)
