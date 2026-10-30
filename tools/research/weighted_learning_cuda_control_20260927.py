"""Separate GPU qualification of already checked weighted fitting components."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import copy
from pathlib import Path
import subprocess
import time
import json
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_visible_objective_v1 import grouped_rows,PreparedWeightedObjective
from sampled_visible_initialization_v1 import fresh_visible_network
from reboot_research_idle_v1 import idle

PREFIX='weighted-learning-cuda-control-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def safe_read_only_resources():
    # Keep this probe independent of CPU-only diagnostic modules, whose import
    # deliberately sets CUDA_VISIBLE_DEVICES=-1 for their own work.
    listening=any(c.status==psutil.CONN_LISTEN and c.laddr.port==56708
        for c in psutil.net_connections(kind='tcp'))
    return (not listening or idle()) and psutil.virtual_memory().available>20_000_000_000


def main():
    import torch
    assert torch.cuda.is_available() and safe_read_only_resources()
    assert not LOCK.exists() and not OTHER.exists()
    status=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
    assert status.returncode==0
    utilization,free=[float(s.strip()) for s in status.stdout.strip().splitlines()[0].split(',')]
    assert utilization<20 and free>4000
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        assert time.monotonic()-started<120 and psutil.virtual_memory().available>20_000_000_000
        if time.monotonic()-last>2:assert safe_read_only_resources();last=time.monotonic()
    source=OUT/'weighted-learning-control-v1-result.json';control=read(source)
    assert control['passed']
    assert control['registration_sha256']==sha(OUT/'weighted-learning-control-v1-registration.json')
    for p,h in control['artifacts'].items():assert sha(p)==h
    fixture=OUT/'weighted-learning-control-v1-checkpoint.npz';context=OUT/'bb-context-candidate.json'
    paths=[source,fixture,context,*Path(__file__).parent.glob('*.py')]
    bindings={str(p):sha(p) for p in paths}
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=bindings,steps=8,seed=9272002,chunk_size=5,
        parameter_tolerance=1e-4,gradient_tolerance=1e-5,maximum_seconds=120,
        utilization_before=utilization,free_memory_MiB_before=free,
        training=False,production_modified=False,fixture='Previously inspected synthetic weighted reservoir'))
    acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        g=grouped_rows(WeightedPhysicalReservoir.load(fixture,context.read_text()))
        cpu=fresh_visible_network(9272002);cuda=copy.deepcopy(cpu).cuda()
        pc=PreparedWeightedObjective(g,'cpu',dtype=torch.float32,guard=guard)
        pg=PreparedWeightedObjective(g,'cuda',dtype=torch.float32,guard=guard)
        oc=torch.optim.Adam(cpu.parameters(),lr=.003);og=torch.optim.Adam(cuda.parameters(),lr=.003)
        parameter_error=gradient_error=loss_error=0.
        for _ in range(8):
            guard();oc.zero_grad();og.zero_grad()
            lc=pc.objective(cpu,5,guard,backward=True);lg=pg.objective(cuda,5,guard,backward=True)
            loss_error=max(loss_error,abs(lc-lg))
            gradient_error=max(gradient_error,max(float((a.grad-b.grad.cpu()).abs().max()) for a,b in zip(cpu.parameters(),cuda.parameters())))
            oc.step();og.step()
            parameter_error=max(parameter_error,max(float((a-b.cpu()).detach().abs().max()) for a,b in zip(cpu.parameters(),cuda.parameters())))
        assert parameter_error<1e-4 and gradient_error<1e-5
        for p,h in bindings.items():assert sha(p)==h
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),steps=8,
            maximum_parameter_error=parameter_error,maximum_gradient_error=gradient_error,
            maximum_loss_error=loss_error,device=torch.cuda.get_device_name(),
            seconds=time.monotonic()-started,gpu_used=True,production_modified=False,
            training_qualified=False,scope='Numerical synthetic weighted fitting only; no poker policies learned.'))
        print(json.dumps(dict(passed=True,parameter_error=parameter_error,gradient_error=gradient_error,loss_error=loss_error)),flush=True)
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
