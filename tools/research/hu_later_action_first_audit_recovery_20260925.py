"""Freshly recorded independent audit if the supervisor interrupted the first one.

The original complete training result and interrupted audit registration remain
untouched. A new metadata identity points to the same immutable training files.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from stopped_later_action_trial_v1 import assert_original_stopped
from frozen_iteration_history_v1 import FrozenHistory,verify_snapshot
from later_action_history_audit_v1 import audit_history

ORIGINAL='later-action-matched-first-v1'
PREFIX='later-action-first-audit-recovery-v1'


def main():
    assert sys.argv[1:]==['--run']
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-started<7500
        if now-last>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000
            assert psutil.disk_usage('T:/').free>1_000_000_000
            last=now
    guard();assert_original_stopped()
    pipeline=read(OUT/'later-action-pipeline-v1-status.json')
    previous=OUT/f'{ORIGINAL}-independent-review.json'
    assert not previous.exists() or not read(previous)['passed'],'Existing passed audit must be used'
    for proc in psutil.process_iter(['cmdline']):
        command=proc.info['cmdline'] or []
        assert not (ORIGINAL in command and any(Path(s).name=='hu_later_action_training_review_20260925.py'
                    for s in command)),'Original first audit is still live'
    oldrp,oldpp,oldrr,oldstatus=[OUT/f'{ORIGINAL}-{s}.json' for s in
        ('registration','result','readback-registration','status')]
    original,result,oldreadback,status=map(read,(oldrp,oldpp,oldrr,oldstatus))
    assert status['state']=='complete' and status['exit_code']==0 and status['error'] is None
    assert result['passed'] and result['terminal'] and result['completed_iterations']==78
    assert result['registration_sha256']==sha(oldrp)
    cfg=result['config'];assert cfg['max_iterations']==78 and all(cfg[k]==v for k,v in original['config'].items())
    store=Path(original['store']);history=FrozenHistory([
        dict(first=1,last=78,store=str(store),objects=str(store/'objects'))],78)
    snapshot=history.snapshot(maximum_bytes=40_000_000_000,guard=guard)
    assert all(result['artifacts'].get(p)==h for p,h in snapshot['files'].items())
    inputs={**original['inputs'],**oldreadback['inputs']}
    paths=[oldrp,oldpp,oldrr,oldstatus,OUT/'later-action-pipeline-v1-status.json',
        Path(__file__).resolve(),ROOT/'tools/research/stopped_later_action_trial_v1.py',
        ROOT/'tools/research/frozen_iteration_history_v1.py',ROOT/'tools/research/later_action_history_audit_v1.py',
        ROOT/'tools/research/immutable_checkpoint_copy_v1.py']
    if previous.exists():paths.append(previous)
    inputs.update({str(p):sha(p) for p in paths})
    for p,h in inputs.items():guard();assert sha(p)==h,p
    rp=OUT/f'{PREFIX}-registration.json';pp=OUT/f'{PREFIX}-result.json'
    save(rp,dict(inputs=inputs,config=cfg,store=str(store),maximum_seconds=7500,
        original_registration_sha256=sha(oldrp),original_result_sha256=sha(oldpp),
        interrupted_readback_registration_sha256=sha(oldrr),pipeline_terminal_status=pipeline,
        scope='New audit attempt only, using the unchanged original complete first trial. No training rerun or new model.',
        gpu_used=False,production_modified=False))
    alias=dict(result,registration_sha256=sha(rp),original_registration_sha256=sha(oldrp),
        original_result_sha256=sha(oldpp),scope='Metadata alias for unchanged complete first trial; new independent audit required.')
    save(pp,alias)
    rr=OUT/f'{PREFIX}-readback-registration.json'
    reviewinputs={**inputs,**result['artifacts'],str(rp):sha(rp),str(pp):sha(pp)}
    save(rr,dict(inputs=reviewinputs,maximum_seconds=7500,gpu_used=False,production_modified=False,
        scope='Repeat the independent scalar audit after an externally interrupted attempt; preserve that attempt.'))
    try:
        import torch
        torch.set_num_threads(1);assert not torch.cuda.is_available()
        review=audit_history(cfg,history,expected_checkpoint=result['final_checkpoint'],guard=guard)
        assert review['complete_training_history'] and review['completed_updates']==78
        verify_snapshot(snapshot,guard)
        for p,h in inputs.items():guard();assert sha(p)==h,p
        final=dict(passed=True,source_registration_sha256=sha(rp),source_result_sha256=sha(pp),
            readback_registration_sha256=sha(rr),seconds=time.monotonic()-started,production_modified=False,**review)
        save(OUT/f'{PREFIX}-independent-review.json',final);print(json.dumps(final),flush=True)
    except BaseException as exc:
        save(OUT/f'{PREFIX}-independent-review.json',dict(passed=False,error=repr(exc),
            readback_registration_sha256=sha(rr),seconds=time.monotonic()-started,
            gpu_used=False,production_modified=False));raise


if __name__=='__main__':main()
