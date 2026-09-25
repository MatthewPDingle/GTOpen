"""Audit the last durable prefix of a stopped later-action replication.

This cannot run against a live trial, choose a checkpoint by its ranges, change
its planned update count, or perform a training retry. Incomplete evidence from
the following update is preserved but is never represented as completed work.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
import math
from pathlib import Path
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from frozen_iteration_history_v1 import FrozenHistory,verify_snapshot
from later_action_history_audit_v1 import audit_history
from stopped_later_action_trial_v1 import assert_original_stopped

ORIGINAL='later-action-matched-replication-v1'
PREFIX='later-action-replication-storage-prefix-v1'


def main():
    assert sys.argv[1:]==['--run']
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        assert now-started<7200
        if now-last>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000
            assert psutil.disk_usage('T:/').free>1_000_000_000
            last=now
    guard();status,pipeline=assert_original_stopped()
    import torch
    torch.set_num_threads(1);assert not torch.cuda.is_available()
    oldrp=OUT/f'{ORIGINAL}-registration.json';original=read(oldrp)
    store=Path(original['store']);latest_path=store/'latest.json';latest=read(latest_path)
    cfg=read(OUT/f'{ORIGINAL}-environment.json')
    assert cfg==latest['config'] and all(cfg[k]==v for k,v in original['config'].items())
    completed=latest['completed_iterations']
    assert type(completed) is int and 0<completed<=cfg['max_iterations']==78
    final=latest['checkpoint']
    assert read(store/f'checkpoint-{completed:04d}.json')==final
    assert read(store/f'iteration-{completed:04d}/metrics.json')['checkpoint']==final
    # Charge the entire stopped controller runtime, including unfinished work.
    # This is not a reset of the original trial's six-hour allowance.
    prior=math.ceil(status['execution_seconds'])
    assert prior>0
    remaining=max(0,original['maximum_seconds']-prior)
    segments=[dict(first=1,last=completed,store=str(store),objects=str(store/'objects'))]
    history=FrozenHistory(segments,completed)
    snapshot=history.snapshot(maximum_bytes=original['maximum_logical_bytes'],guard=guard)
    steps=[]
    for iteration in range(1,completed+1):
        metrics=store/f'iteration-{iteration:04d}/metrics.json';doc=read(metrics)
        pointer=store/f'checkpoint-{iteration:04d}.json'
        assert read(pointer)==doc['checkpoint']
        snapshot['files'][str(pointer)]=sha(pointer)
        steps.append(dict(iteration=iteration,checkpoint=doc['checkpoint'],metrics_sha256=sha(metrics)))
    inputs=dict(original['inputs'])
    paths=[oldrp,latest_path,OUT/f'{ORIGINAL}-environment.json',OUT/f'{ORIGINAL}-status.json',
           OUT/f'{ORIGINAL}-resources.json',OUT/'later-action-pipeline-v1-status.json',
           OUT/'later-action-pipeline-v1-registration.json',Path(__file__).resolve(),
           ROOT/'tools/research/frozen_iteration_history_v1.py',
           ROOT/'tools/research/later_action_history_audit_v1.py',
           ROOT/'tools/research/stopped_later_action_trial_v1.py',
           ROOT/'tools/research/immutable_checkpoint_copy_v1.py']
    inputs.update({str(p):sha(p) for p in paths})
    for p,h in inputs.items():guard();assert sha(p)==h,p
    registration=OUT/f'{PREFIX}-registration.json'
    save(registration,dict(inputs=inputs,config=cfg,store=str(store),segments=segments,
        reader_pid=os.getpid(),reader_create_time=psutil.Process().create_time(),
        original_registration_sha256=sha(oldrp),original_status=status,pipeline_status=pipeline,
        original_budget_seconds=original['maximum_seconds'],prior_runtime_charge_seconds=prior,
        remaining_runtime_seconds=remaining,maximum_seconds=7200,
        checkpoint_selection='Latest fsynced progress pointer after terminal stop; no score-based choice.',
        completed_iterations=completed,planned_iterations=cfg['max_iterations'],
        gpu_used=False,production_modified=False,automatic_retry=False))
    resultpath=OUT/f'{PREFIX}-result.json'
    save(resultpath,dict(passed=True,terminal=completed==cfg['max_iterations'],
        registration_sha256=sha(registration),original_registration_sha256=sha(oldrp),
        store=str(store),config=cfg,completed_iterations=completed,steps=steps,
        final_checkpoint=final,artifacts=snapshot['files'],
        scope='Authenticated durable evidence prefix only; scalar audit below remains mandatory. No strength conclusion.'))
    reviewrp=OUT/f'{PREFIX}-readback-registration.json'
    reviewinputs={**inputs,**snapshot['files'],str(registration):sha(registration),str(resultpath):sha(resultpath)}
    save(reviewrp,dict(inputs=reviewinputs,maximum_seconds=7200,gpu_used=False,
        scope='Independent scalar replay of every completed update in a stopped trial prefix.',production_modified=False))
    try:
        summary=audit_history(cfg,history,expected_checkpoint=final,guard=guard)
        verify_snapshot(snapshot,guard)
        for p,h in inputs.items():guard();assert sha(p)==h,p
        assert_original_stopped()
        result=dict(passed=True,source_registration_sha256=sha(registration),source_result_sha256=sha(resultpath),
            readback_registration_sha256=sha(reviewrp),seconds=time.monotonic()-started,
            terminal_complete=completed==cfg['max_iterations'],production_modified=False,**summary)
        save(OUT/f'{PREFIX}-independent-review.json',result);print(json.dumps(result),flush=True)
    except BaseException as exc:
        save(OUT/f'{PREFIX}-independent-review.json',dict(passed=False,error=repr(exc),
            readback_registration_sha256=sha(reviewrp),seconds=time.monotonic()-started,
            gpu_used=False,production_modified=False));raise


if __name__=='__main__':main()
