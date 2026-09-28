"""Bounded CPU-only replay batches; every later policy remains unchanged."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import concurrent.futures
import json
import multiprocessing
from pathlib import Path
import time
import psutil
from board_root_action_decomposition_v1 import (restore_batch, validate_original, force_root,
    validate_forced, invoke, compare, encoded, publish, digest, require, hand_class)
from board_root_action_replay_store_v1 import owner, retire, sha, ATTEMPT, BATCH
from board_prefix_publication_v1 import atomic_json

STATE=None


def initialize(registration):
    global STATE
    path=Path(registration);reg=json.loads(path.read_bytes());identity=sha(path)
    owner(reg['store'],identity)
    for p in (reg['context_path'],reg['executable'],reg['root_stability_path']):
        require(sha(p) == reg['inputs'][p],'Changed runtime input')
    STATE=reg,identity,Path(reg['context_path']).read_bytes().decode(),json.loads(Path(reg['root_stability_path']).read_bytes())


def process_one(job):
    attempt_name,name=job
    began=time.monotonic();reg,identity,source,roots=STATE
    def guard():
        require(time.monotonic()-began < 180,'Replay batch deadline')
        require(psutil.virtual_memory().available > 20_000_000_000,'Preserve available RAM')
    guard();store=owner(reg['store'],identity)
    require(ATTEMPT.fullmatch(attempt_name) and BATCH.fullmatch(name) and name in reg['batches'],'Invalid replay job')
    parent=store/attempt_name
    require(json.loads((parent/'owner.json').read_bytes())['registration_sha256'] == identity,'Wrong attempt')
    folder=parent/name;require(not folder.exists(),'Preserve earlier partial batch');folder.mkdir()
    atomic_json(folder/'owner.json',dict(root=str(folder),registration_sha256=identity,name=name))
    raw=restore_batch(Path(reg['source_store']),name,reg['source_routes'][name],guard)
    original,indices,deal_rows,deals=validate_original(raw,source)
    for p,profile in enumerate(original['profiles']):
        donor=(p//4)*2+int(p % 4 >= 2)
        for did,deal in enumerate(deals):
            expected=roots['root_probabilities'][donor][hand_class(deal[:2])]
            actual=profile['policies'][deal_rows[did]]['probabilities']
            require(max(abs(a-b) for a,b in zip(expected,actual)) < 1e-12,'Changed complete root policy')
    forced=force_root(original,indices);validate_forced(original,forced,indices)
    scratch={'conditional-batch.json':raw['conditional-batch.json'],'forced-profiles.json':encoded(forced)}
    require(sum(map(len,scratch.values())) < 90_000_000,'Replay scratch bound')
    hashes={}
    for n,b in scratch.items():publish(folder/n,b);hashes[n]=digest(b)
    native_seconds=invoke(Path(reg['executable']),Path(reg['context_path']),folder/'conditional-batch.json',
        folder/'forced-profiles.json',folder/'native.json',guard)
    require((folder/'native.json').stat().st_size < 500_000,'Replay native output bound')
    saved=json.loads(raw['native.json'])
    # Original mixed values were already independently audited. Only forced
    # profiles are rerun here; never claim another original native replay.
    values=compare(saved,saved,json.loads((folder/'native.json').read_bytes()),original,deal_rows,deals,
        json.loads(source)['dead_money'])
    del values['maximum_replay_error']
    atomic_json(folder/'action-values.json',values)
    receipt=dict(format=1,name=name,registration_sha256=identity,source_route=reg['source_routes'][name],
        source_artifact_sha256={n:digest(b) for n,b in raw.items()},deals=32,
        artifacts={n:sha(folder/n) for n in ('native.json','action-values.json')},scratch_sha256=hashes,
        maximum_mixture_error=values['maximum_mixture_error'],root_only_deviation=True,later_behavior_fixed=True,
        original_native_rerun=False,fresh_deals=0,gpu_used=False,native_seconds=native_seconds,
        seconds=time.monotonic()-began)
    atomic_json(folder/'receipt.json',receipt)
    retire(store,folder,receipt)
    require(sum(p.stat().st_size for p in folder.iterdir()) < 1_000_000,'Completed batch retention bound')
    guard()
    return name,dict(attempt=attempt_name,receipt_sha256=sha(folder/'receipt.json'))


def stop_pool(pool):
    for proc in list(pool._processes.values()):
        if not proc.is_alive():continue
        try:
            process=psutil.Process(proc.pid)
            for child in process.children(recursive=True):
                try:child.kill()
                except psutil.NoSuchProcess:pass
            proc.terminate()
        except psutil.NoSuchProcess:pass


def create_pool(registration,workers):
    require(type(workers) is int and 1 <= workers <= 12,'Bounded qualified CPU worker count required')
    return concurrent.futures.ProcessPoolExecutor(max_workers=workers,
        mp_context=multiprocessing.get_context('spawn'),initializer=initialize,initargs=(str(registration),))


def wave(pool,attempt_name,names,guard):
    require(1 <= len(names) <= 32 and len(names) == len(set(names)),'Bounded unique wave required')
    began=time.monotonic();pending={pool.submit(process_one,(attempt_name,n)):n for n in names};found={}
    try:
        while pending:
            guard();require(time.monotonic()-began < 600,'Replay wave deadline')
            done,_=concurrent.futures.wait(pending,timeout=1,return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                name=pending.pop(future);actual,route=future.result()
                require(name == actual and name not in found,'Wrong returned replay batch')
                found[name]=route
    except BaseException:
        stop_pool(pool)
        raise
    return {name:found[name] for name in names}
