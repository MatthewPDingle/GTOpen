"""Check the combined model's primary evaluator on existing training deals only."""
import json
import os
from pathlib import Path
import time
import psutil
import torch
from loopback_research_validation import idle
from sampled_physical_hybrid_allin_evaluation_v1 import ROOT, sha, save, batch_values
from sampled_physical_hybrid_checkpoint_v1 import read_object, model_document, verify_bank
from sampled_physical_hybrid_cpu64_v1 import HybridCpuBank64
from sampled_physical_hybrid_gpu_bank_v2 import HybridCudaBank64

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-hybrid-allin-adapter-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-last >= 2:
            assert now-started < 600 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            assert psutil.disk_usage(str(STORE.parent)).free>=40_000_000_000
            last=now
    guard();assert not LOCK.exists() and not OTHER.exists() and not STORE.exists()
    rp=OUT/'sampled-physical-hybrid-allin-control-v1-independent-review.json'
    review=json.loads(rp.read_text());assert review['passed'] and review['terminal_complete']
    source=Path('S:/GTOpen-research/sampled-physical-hybrid-allin-control-v1')
    objects=source/'checkpoint-objects';context=OUT/'bb-context-candidate.json'
    checkpoint=json.loads(read_object(objects,review['checkpoint']))
    assert checkpoint['completed_iterations']==4
    verify_bank(objects,4,checkpoint['played_bank'],checkpoint['next_model'],context_source=context.read_text())
    inputs=[rp,context,Path(__file__),objects/review['checkpoint']['file'],
        *[objects/r['file'] for r in checkpoint['played_bank']],
        *[ROOT/'tools/research'/n for n in ('sampled_physical_hybrid_allin_evaluation_v1.py',
           'sampled_physical_hybrid_cpu64_v1.py','sampled_physical_hybrid_gpu_bank_v2.py')]]
    for chunk in range(4):
        part=source/'iteration-0001'/f'batch-{chunk:02d}'
        metric=json.loads((part.parent/'metrics.json').read_text())['subbatches'][chunk]
        assert sha(part/'batch.json')==metric['artifacts']['batch.json']
        inputs += [part/'batch.json',part.parent/'metrics.json']
    reg=dict(inputs={str(p):sha(p) for p in inputs},checkpoint=review['checkpoint'],
        complete_deals=256,policy_tolerance=1e-10,payoff_tolerance_bb=1e-8,
        scope='Integration and numerical equivalence on existing training deals; no new evaluation draws or strategic conclusions.',production_modified=False)
    regpath=OUT/f'{PREFIX}-registration.json';save(regpath,reg)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    error=None
    try:
        STORE.mkdir()
        documents=[model_document(objects,r,context_source=context.read_text()) for r in checkpoint['played_bank']]
        cpu=HybridCpuBank64(documents,context_source=context.read_text())
        gpu=HybridCudaBank64(documents,[[1.]*4]*2,context_source=context.read_text(),models_per_chunk=4,guard=guard)
        comparisons=[];artifacts={}
        for chunk in range(4):
            old=json.loads((source/'iteration-0001'/f'batch-{chunk:02d}'/'batch.json').read_text())
            # Explicit new unlabelled transport for the sampled primary evaluator.
            # Only copy the private cards and runouts; exact all-in labels are not inputs.
            batch=dict(format=2,batch_id=f'{PREFIX}-{chunk}',query_limit=100000,seed=0,deals=old['deals'])
            cf=STORE/f'cpu-{chunk}';gf=STORE/f'gpu-{chunk}'
            batch_values(context,batch,objects,checkpoint,cf,guard,cpu)
            result=batch_values(context,batch,objects,checkpoint,gf,guard,gpu,
                dict(folder=str(cf),policy_tolerance=reg['policy_tolerance'],payoff_tolerance_bb=reg['payoff_tolerance_bb']))
            comparisons.append(result['cpu_comparison'])
            for folder in (cf,gf):
                for name in ('batch.json','queries.json','profiles.json','native.json','summary.json'):
                    artifacts[str(folder/name)]=sha(folder/name)
        for p,h in reg['inputs'].items():assert sha(p)==h,p
        guard()
        result=dict(passed=True,registration_sha256=sha(regpath),complete_deals=256,
            played_generations=list(range(4)),comparisons=comparisons,artifacts=artifacts,
            maximum_policy_error=max(c['maximum_policy_error'] for c in comparisons),
            maximum_payoff_error_bb=max(c['maximum_payoff_error_bb'] for c in comparisons),
            seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False)
        save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','comparisons')}))
    except Exception as exc:error=str(exc);raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,production_modified=False))
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
