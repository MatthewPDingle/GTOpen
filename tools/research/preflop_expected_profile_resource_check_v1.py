"""Independent storage/GPU admission and real spawn cancellation controls."""
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time
from concurrent.futures import ProcessPoolExecutor, CancelledError
from unittest.mock import patch

import preflop_expected_native_cycle_profile_v1 as profile
from preflop_expected_worker_cancellation_v1 import coordinated_pool

EVENT=None


def initialize(event):
    global EVENT
    EVENT=event


def waiting():
    began=time.monotonic()
    while not EVENT.is_set():
        if time.monotonic()-began>20: raise TimeoutError('Software fixture guard deadline')
        time.sleep(.01)
    raise InterruptedError('Exact shared event observed')


def immediate(): return os.getpid()


def main(folder):
    folder=Path(folder).resolve(); folder.mkdir(exist_ok=False)
    began=time.monotonic(); refused=[]; now=time.time()
    roots=[dict(root=p,allocated_file_bytes=100) for p in
           (r'S:\GTOpen-research',r'T:\GTOpen-research',str(profile.ROOT/'research'))]
    valid=dict(format=1,observed_unix=now,allocated_total_bytes=300,roots=roots,read_only=True)
    inventory=folder/'inventory.json'; profile.write(inventory,valid)
    admitted=profile.admission(inventory); assert admitted['snapshot']==valid
    profile.admission(inventory,expected=admitted)
    cases={'expired':dict(valid,observed_unix=now-3601),'future':dict(valid,observed_unix=now+100),
           'over-cap':dict(valid,allocated_total_bytes=profile.ALLOCATED_CAP),
           'incomplete':dict(valid,roots=roots[:2]),'wrong-root':dict(valid,roots=[dict(r,root='X:/wrong') for r in roots]),
           'incorrect-total':dict(valid,allocated_total_bytes=301),'not-read-only':dict(valid,read_only=False)}
    for label,doc in cases.items():
        path=folder/(label+'.json'); profile.write(path,doc)
        try: profile.admission(path)
        except ValueError: refused.append(label)
        else: raise AssertionError('Invalid storage admitted: '+label)
    altered=dict(admitted,identity='0'*64)
    try: profile.admission(inventory,expected=altered)
    except ValueError: refused.append('changed-recorded-identity')
    else: raise AssertionError('Changed recorded admission admitted')
    for label,raw in (('valid','NVIDIA GeForce RTX 3090, 4, 3408, 20919'),
                      ('wrong-gpu','NVIDIA GeForce RTX 4090, 4, 3408, 20919'),
                      ('unknown-telemetry','NVIDIA GeForce RTX 3090, [N/A], 3408, 20919'),
                      ('multiple-gpus','NVIDIA GeForce RTX 3090, 4, 3408, 20919\nNVIDIA GeForce RTX 3090, 4, 3408, 20919')):
        with patch.object(profile.subprocess,'check_output',return_value=raw):
            if label=='valid': assert profile.gpu_snapshot()['gpu_memory_free_mib']==20919
            else:
                try: profile.gpu_snapshot()
                except ValueError: refused.append(label)
                else: raise AssertionError('Invalid GPU admitted: '+label)
    ctx=mp.get_context('spawn'); event=ctx.Event()
    with coordinated_pool(ProcessPoolExecutor(1,mp_context=ctx,initializer=initialize,initargs=(event,)),event) as pool:
        normal_pid=pool.submit(immediate).result(timeout=30)
    assert not event.is_set()
    event=ctx.Event(); futures=[]; signaled=False; cleanup=time.monotonic()
    try:
        with coordinated_pool(ProcessPoolExecutor(1,mp_context=ctx,initializer=initialize,initargs=(event,)),event) as outer:
            outer.submit(immediate).result(timeout=30)
            futures.append(outer.submit(waiting))
            with coordinated_pool(ProcessPoolExecutor(1,mp_context=ctx,initializer=initialize,initargs=(event,)),event) as inner:
                inner.submit(immediate).result(timeout=30)
                futures.extend(inner.submit(waiting) for _ in range(8))
                raise RuntimeError('Injected parent guard failure')
    except RuntimeError as exc:
        assert str(exc)=='Injected parent guard failure'; signaled=event.is_set()
    assert signaled and time.monotonic()-cleanup<30
    observed=[]
    for f in futures:
        assert f.done()
        try: f.result()
        except (InterruptedError,CancelledError) as exc: observed.append(type(exc).__name__)
        else: raise AssertionError('Canceled software task finished normally')
    result=dict(passed=True,scope='Synthetic resource gates and actual spawned software jobs; no native poker or GPU fit',
                refused=refused,normal_child_pid=normal_pid,cancellation_outcomes=observed,
                cancellation_cleanup_seconds=time.monotonic()-cleanup,seconds=time.monotonic()-began,
                source_identities={str(p):profile.pipeline.sha(p) for p in
                  (Path(__file__).resolve(),Path(profile.__file__).resolve(),Path(profile.STAGE/'preflop_expected_worker_cancellation_v1.py'))})
    profile.write(folder/'result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='source_identities'}),flush=True)


if __name__=='__main__': main(sys.argv[1])
