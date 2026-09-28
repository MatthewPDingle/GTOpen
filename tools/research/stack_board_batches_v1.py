"""Owned hidden workers preparing batches of exact-target board/card factors."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import numpy as np
from owned_windows_job_v1 import OwnedJob
from board_study_storage_v1 import path_within_research
from board_prefix_publication_v1 import atomic_json
from stack_price_reference_v1 import board_group,conditional_counts
from stack_price_reference_control_v1 import native,RANKS
from stack_price_learning_data_v2 import card_factors

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def worker(request):
    assert sys.stdin.readline().strip()=='OWNED_START'
    document=json.loads(Path(request).read_bytes());store=path_within_research(Path(document['store']))
    assert Path(request).parent==store and store.is_dir()
    records=[]
    for task in document['tasks']:
        started=time.monotonic();board=task['board'];index=task['index']
        assert type(index) is int and index>=0
        raw=native(RANKS,board)
        hands=np.asarray([r['hand'] for r in raw['rows']],dtype=np.int64)
        ranks=np.asarray([r['rank'] for r in raw['rows']],dtype=np.int64)
        counts=conditional_counts(board,hands,ranks);factors=card_factors(board)
        assert np.array_equal(hands,factors['hands']) and np.all(counts.sum(1)==990)
        dest=store/f'board-{index}.npz'
        with dest.open('xb') as f:np.savez_compressed(f,features=factors['features'],counts=counts,
            hands=hands,canonical_cards=factors['canonical_cards'],lo_actor_zero=factors['lo_actor_zero'])
        records.append(dict(index=index,split=task['split'],board=board,canonical_group=board_group(board),
            file=str(dest),sha256=sha(dest),preparation_seconds=time.monotonic()-started))
    print(json.dumps(records),flush=True)

def prepare_boards(tasks,store,guard,progress):
    store=path_within_research(Path(store));assert store.is_dir() and tasks
    start=time.monotonic();results=[];cancel=threading.Event()
    batches=[tasks[i::8] for i in range(min(8,len(tasks)))]
    with OwnedJob() as job:
        def launch(batch):
            if cancel.is_set():raise RuntimeError('Preparation cancelled')
            req=store/f"batch-{batch[0]['index']}-request.json"
            atomic_json(req,dict(store=str(store),tasks=batch))
            proc=subprocess.Popen([sys.executable,'-B',__file__,str(req)],env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1'),
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                job.assign(proc);stdout,stderr=proc.communicate(b'OWNED_START\n',timeout=900)
                if proc.returncode:raise RuntimeError(stderr.decode(errors='replace')[-3000:])
                rows=json.loads(stdout);assert sorted(r['index'] for r in rows)==sorted(t['index'] for t in batch)
                return rows
            except BaseException:
                if proc.poll() is None:proc.kill();proc.wait(timeout=10)
                raise
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures={pool.submit(launch,b) for b in batches}
            try:
                while futures:
                    guard();done,futures=wait(futures,timeout=2,return_when=FIRST_COMPLETED)
                    for future in done:results.extend(future.result())
                    if done:progress('preparing_boards',completed=len(results),total=len(tasks))
            except BaseException:
                cancel.set();job.close()
                for future in futures:future.cancel()
                raise
        accounting=job.accounting();assert accounting['active_processes']==0
    return sorted(results,key=lambda r:r['index']),dict(seconds=time.monotonic()-start,job=accounting)

def load_boards(records):
    result=[]
    for ref in records:
        assert sha(ref['file'])==ref['sha256']
        with np.load(ref['file'],allow_pickle=False) as d:
            assert d['features'].shape==(1081,362) and d['counts'].shape==(1081,3)
            assert np.isfinite(d['features']).all() and np.all(d['counts'].sum(1)==990)
            result.append(dict(features=d['features'].copy(),counts=d['counts'].copy()))
    return result

if __name__=='__main__':
    assert len(sys.argv)==2;worker(sys.argv[1])
