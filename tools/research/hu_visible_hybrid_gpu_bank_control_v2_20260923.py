"""Explicit, exclusive GPU control on frozen synthetic visible-feature models.

Version 2 sets the required deterministic cuBLAS workspace before Torch import.
Run only after the current research job releases the GPU. No training or new
evaluation draws. This does not admit the representation's training pipeline.
"""
import json
import os
from pathlib import Path
import sys
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from sampled_visible_hybrid_gpu_bank_v1 import VisibleHybridCudaBank64

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-visible-hybrid-gpu-bank-control-v2'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    assert '--run' in sys.argv,'Explicit --run required; this control uses CUDA'
    assert idle() and not LOCK.exists() and not OTHER.exists()
    started=time.monotonic();acquired=False;error=None
    result_path=OUT/'sampled-visible-hybrid-bank-control-v1-result.json'
    reg_path=OUT/'sampled-visible-hybrid-bank-control-v1-registration.json'
    result=json.loads(result_path.read_text());reg=json.loads(reg_path.read_text())
    assert result['passed'] and result['registration_sha256']==sha(reg_path)
    for p,h in {**reg['inputs'],**result['artifacts']}.items():assert sha(p)==h
    fixture_reg=OUT/'sampled-physical-preflop-table-control-v1-registration.json'
    fixture=Path(json.loads(fixture_reg.read_text())['fixture'])
    models_path=OUT/'sampled-visible-hybrid-bank-control-v1-models.json'
    queries=json.loads(fixture.read_text());models=json.loads(models_path.read_text())
    inputs=[result_path,reg_path,fixture_reg,fixture,models_path,Path(__file__),
        *[ROOT/'tools/research'/name for name in ('sampled_visible_hybrid_cpu64_v1.py',
            'sampled_visible_hybrid_gpu_bank_v1.py','sampled_physical_hybrid_gpu_bank_v2.py',
            'sampled_visible_hybrid_checkpoint_v1.py','sampled_visible_initialization_v1.py',
            'sampled_visible_poker_features_v1.py','sampled_physical_preflop_table_v1.py',
            'sampled_physical_bank_v1.py')]]
    registration=dict(inputs={str(p):sha(p) for p in inputs},maximum_seconds=180,
        policy_tolerance=1e-10,reach_tolerance=1e-10,
        scope='Float64 CPU/CUDA bank equivalence on old observations with fixed synthetic nonzero feature weights. No new deals or poker strength evaluation.',production_modified=False)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    acquired=True
    try:
        os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
        import torch
        from threadpoolctl import threadpool_limits
        torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        def guard():
            assert time.monotonic()-started<180 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            assert psutil.disk_usage('S:/').free>=40_000_000_000
        guard()
        path=OUT/f'{PREFIX}-registration.json';save(path,registration)
        comparisons=[]
        with threadpool_limits(limits=2):
            for weights in (np.ones((2,3)),np.array([[1.,2.,4.],[5.,3.,1.]])):
                cpu=VisibleHybridCpuBank64(models,context_source=queries['context_source'],weights_by_player=weights)
                expected,expected_reach=cpu.average(queries,guard=guard)
                for chunk in (1,2,3):
                    gpu=VisibleHybridCudaBank64(models,weights,context_source=queries['context_source'],models_per_chunk=chunk,guard=guard)
                    actual,reach=gpu.average(queries,guard=guard)
                    pe=float(np.max(abs(actual-expected)));re=float(np.max(abs(reach-expected_reach)))
                    assert pe<registration['policy_tolerance'] and re<registration['reach_tolerance']
                    comparisons.append(dict(weights=weights.tolist(),chunk=chunk,maximum_policy_error=pe,maximum_reach_error=re))
                    del gpu
        guard()
        for p,h in registration['inputs'].items():assert sha(p)==h
        output=dict(passed=True,registration_sha256=sha(path),observations=len(queries['observations']),
            comparisons=comparisons,seconds=time.monotonic()-started,torch_version=torch.__version__,
            device=torch.cuda.get_device_name(),accuracy_qualified=False,production_modified=False)
        save(OUT/f'{PREFIX}-result.json',output);print(json.dumps(output),flush=True)
    except Exception as exc:error=repr(exc);raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,production_modified=False))
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
