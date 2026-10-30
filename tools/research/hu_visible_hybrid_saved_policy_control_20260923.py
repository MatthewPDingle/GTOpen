"""Reproduce every saved control policy and check complete-bank CPU/CUDA inference.

Uses only the completed four-update integration control's existing observations.
No new deals, fitting, opponent selection or strength evaluation.
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
from sampled_visible_hybrid_checkpoint_v1 import read_object,model_document,verify_bank
from sampled_visible_hybrid_policy_v1 import probabilities
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from sampled_visible_hybrid_gpu_bank_v1 import VisibleHybridCudaBank64

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-visible-hybrid-saved-policy-control-v1'
SOURCE='sampled-visible-hybrid-allin-control-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    assert '--run' in sys.argv and idle() and not LOCK.exists() and not OTHER.exists()
    started=time.monotonic();error=None
    rp=OUT/f'{SOURCE}-independent-review.json';review=json.loads(rp.read_text())
    regpath=OUT/f'{SOURCE}-registration.json';reg=json.loads(regpath.read_text())
    assert review['passed'] and review['terminal_complete'] and review['control_only']
    assert review['completed_iterations']==4 and review['source_registration_sha256']==sha(regpath)
    for p,h in {**reg['inputs'],**review['evidence_hashes']}.items():assert sha(p)==h
    store=Path(reg['store']);objects=store/'checkpoint-objects'
    context_path=OUT/'bb-context-candidate.json';context=context_path.read_text()
    checkpoint=json.loads(read_object(objects,review['checkpoint']))
    verify_bank(objects,4,checkpoint['played_bank'],checkpoint['next_model'],context_source=context)
    documents=[model_document(objects,r,context_source=context) for r in checkpoint['played_bank']]
    inputs=[rp,regpath,context_path,Path(__file__),objects/review['checkpoint']['file'],
        *[objects/r['file'] for r in checkpoint['played_bank']],
        *[ROOT/'tools/research'/name for name in ('sampled_visible_hybrid_checkpoint_v1.py',
            'sampled_visible_hybrid_policy_v1.py','sampled_visible_initialization_v1.py',
            'sampled_visible_poker_features_v1.py','sampled_visible_hybrid_cpu64_v1.py',
            'sampled_visible_hybrid_gpu_bank_v1.py','sampled_physical_hybrid_gpu_bank_v2.py',
            'sampled_physical_preflop_table_v1.py','sampled_physical_bank_v1.py')]]
    metrics=[]
    for iteration in range(1,5):
        path=store/f'iteration-{iteration:04d}'/'metrics.json'
        metric=json.loads(path.read_text());inputs.append(path);metrics.append(metric)
        assert sha(path)==review['steps'][iteration-1]['metrics_sha256']
        for record in metric['subbatches']:
            part=path.parent/f"batch-{record['chunk']:02d}"
            for name,h in record['artifacts'].items():assert sha(part/name)==h
            inputs.extend((part/'queries.json',part/'policies.json'))
    registration=dict(inputs={str(p):sha(p) for p in inputs},maximum_seconds=300,
        saved_policy_tolerance=0.,bank_policy_tolerance=1e-10,bank_reach_tolerance=1e-10,
        scope='Replay saved CUDA float32 control policies; compare complete played bank CPU/CUDA float64 on all first-update query batches. Existing control observations only.',production_modified=False)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
        import torch
        from threadpoolctl import threadpool_limits
        torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        def guard():
            assert time.monotonic()-started<300 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            assert psutil.disk_usage('S:/').free>=40_000_000_000
        guard();newreg=OUT/f'{PREFIX}-registration.json';save(newreg,registration)
        comparisons=[];saved_error=0.;count=0;covered=[0,0]
        with threadpool_limits(limits=2):
            cpu=VisibleHybridCpuBank64(documents,context_source=context)
            gpu=VisibleHybridCudaBank64(documents,[[1.]*4]*2,context_source=context,models_per_chunk=3,guard=guard)
            for iteration,metric in enumerate(metrics,1):
                model=documents[iteration-1]
                for record in metric['subbatches']:
                    guard();part=store/f'iteration-{iteration:04d}'/f"batch-{record['chunk']:02d}"
                    queries=json.loads((part/'queries.json').read_text())
                    stored=json.loads((part/'policies.json').read_text())
                    actual,c=probabilities(queries,model,'cuda')
                    expected=np.array([p['probabilities'] for p in stored['policies']])
                    error_here=float(np.max(abs(actual-expected)));saved_error=max(saved_error,error_here)
                    assert np.array_equal(actual,expected) and c==record['preflop_table_queries']
                    count+=len(actual);covered=[a+b for a,b in zip(covered,c)]
                    if iteration==1:
                        a,ar=cpu.average(queries,guard=guard);b,br=gpu.average(queries,guard=guard)
                        pe=float(np.max(abs(a-b)));re=float(np.max(abs(ar-br)))
                        assert pe<registration['bank_policy_tolerance'] and re<registration['bank_reach_tolerance']
                        comparisons.append(dict(chunk=record['chunk'],observations=len(a),maximum_policy_error=pe,maximum_reach_error=re))
        assert min(covered)>0
        guard()
        for p,h in registration['inputs'].items():assert sha(p)==h
        output=dict(passed=True,registration_sha256=sha(newreg),saved_policy_rows=count,
            maximum_saved_policy_error=saved_error,covered_preflop_rows=covered,
            played_generations=list(range(4)),unused_generation=4,bank_comparisons=comparisons,
            seconds=time.monotonic()-started,accuracy_qualified=False,production_modified=False)
        save(OUT/f'{PREFIX}-result.json',output);print(json.dumps(output),flush=True)
    except Exception as exc:error=repr(exc);raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,production_modified=False))
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
