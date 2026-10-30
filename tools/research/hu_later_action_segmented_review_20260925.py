"""Independent complete audit of the same trial continued across T: and S:."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
from pathlib import Path
import json
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from frozen_iteration_history_v1 import FrozenHistory,verify_snapshot
from later_action_history_audit_v1 import audit_history

PREFIX='later-action-replication-volume-continuation-v1'


def main():
    assert sys.argv[1:]==['--run']
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-started<7200
        if now-last>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000
            assert psutil.disk_usage('T:/').free>1_000_000_000
            last=now
    guard()
    import torch
    torch.set_num_threads(1);assert not torch.cuda.is_available()
    rp,pp,sp=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result','status')]
    reg,result,status=map(read,(rp,pp,sp))
    assert status['state']=='complete' and status['error'] is None and status['exit_code']==0
    assert result['passed'] and result['terminal'] and result['registration_sha256']==sha(rp)
    cfg=result['config'];assert cfg==reg['config']
    assert result['completed_iterations']==cfg['max_iterations']==78
    assert result['history_segments']==reg['history_segments']
    history=FrozenHistory(result['history_segments'],78)
    snapshot=history.snapshot(maximum_bytes=50_000_000_000,guard=guard)
    assert all(result['artifacts'].get(p)==h for p,h in snapshot['files'].items())
    for step in result['steps']:
        folder,_=history.location(step['iteration'])
        assert sha(folder/'metrics.json')==step['metrics_sha256']
    assert [s['iteration'] for s in result['steps']]==list(range(1,79))
    inputs={**reg['inputs'],**result['artifacts'],str(rp):sha(rp),str(pp):sha(pp),str(sp):sha(sp)}
    for name in ('hu_later_action_segmented_review_20260925.py','frozen_iteration_history_v1.py',
                 'later_action_history_audit_v1.py','hu_later_action_training_review_20260925.py',
                 'immutable_checkpoint_copy_v1.py'):
        p=ROOT/'tools/research'/name;inputs[str(p)]=sha(p)
    for p,h in inputs.items():guard();assert sha(p)==h,p
    reviewrp=OUT/f'{PREFIX}-readback-registration.json'
    save(reviewrp,dict(inputs=inputs,maximum_seconds=7200,gpu_used=False,
        history_segments=result['history_segments'],production_modified=False,
        scope='Full independent scalar reconstruction from generation zero across the original and continued evidence locations.'))
    try:
        review=audit_history(cfg,history,expected_checkpoint=result['final_checkpoint'],guard=guard)
        assert review['complete_training_history'] and review['completed_updates']==78
        verify_snapshot(snapshot,guard)
        for p,h in inputs.items():guard();assert sha(p)==h,p
        result=dict(passed=True,source_registration_sha256=sha(rp),source_result_sha256=sha(pp),
            readback_registration_sha256=sha(reviewrp),seconds=time.monotonic()-started,
            production_modified=False,**review)
        save(OUT/f'{PREFIX}-independent-review.json',result);print(json.dumps(result),flush=True)
    except BaseException as exc:
        save(OUT/f'{PREFIX}-independent-review.json',dict(passed=False,error=repr(exc),
            readback_registration_sha256=sha(reviewrp),seconds=time.monotonic()-started,
            gpu_used=False,production_modified=False));raise


if __name__=='__main__':main()
