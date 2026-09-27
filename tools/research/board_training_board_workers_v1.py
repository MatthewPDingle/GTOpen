"""Bounded CPU board workers for one frozen typed training model."""
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
import psutil
from board_training_targets_v1 import prepare, request, draw_record
from sampled_physical_root_evaluation_v1 import save, sha
from bounded_parallel_evaluation_archive_v2 import production_available

_STATE=None


def initialize(payload,context_path,executable,folder):
    global _STATE
    # Only the spawned CPU process receives this setting; the trainer keeps CUDA.
    os.environ['CUDA_VISIBLE_DEVICES']='-1'
    from threadpoolctl import threadpool_limits
    limit=threadpool_limits(limits=1)
    if Path(context_path).read_text()!=payload['context_source']:
        raise ValueError('Native board context changed')
    _STATE=dict(prepared=prepare(**payload),context_path=context_path,executable=executable,
                folder=Path(folder),limit=limit,began=time.monotonic())


def guard():
    if time.monotonic()-_STATE['began']>1200:raise RuntimeError('Board worker generation deadline')
    if psutil.virtual_memory().available<20_000_000_000:raise RuntimeError('Board worker RAM reserve')
    if psutil.disk_usage(_STATE['folder'].anchor).free<40_000_000_000:raise RuntimeError('Board worker disk reserve')
    if not production_available():raise RuntimeError('Production became busy')


def complete(index,board):
    guard();began=time.monotonic();s=_STATE;folder=s['folder']/f'board-{index:03d}';folder.mkdir()
    req,_=request(s['prepared'],board);rp=folder/'request.json';save(rp,req)
    raw=subprocess.check_output([str(s['executable']),str(s['context_path']),str(rp)],
        timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    tree_hash=hashlib.sha256(raw).hexdigest();tree=json.loads(raw);del raw
    guard();record=draw_record(s['prepared'],tree,tree_sha256=tree_hash,draw_index=index,board=board)
    result=dict(record=record,request_sha256=sha(rp),seconds=time.monotonic()-began,
                pid=os.getpid(),rss_bytes=psutil.Process().memory_info().rss,
                cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'))
    target=folder/'result.json';save(target,result);guard()
    return dict(result=result,path=str(target),sha256=sha(target))


def pool(workers,*,payload,context_path,executable,folder):
    if type(workers) is not int or not 1<=workers<=4:raise ValueError('One to four board workers required')
    return ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn'),
        initializer=initialize,initargs=(payload,context_path,executable,folder))
