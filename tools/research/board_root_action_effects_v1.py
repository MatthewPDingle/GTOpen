"""Paired decomposition of old/new later-policy effects on every BB root action.

All action values are already retained. No inference, new deals, optimization or
engine changes. Require full replay readback before producing research outputs.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import argparse
import concurrent.futures
import json
import math
import multiprocessing
from pathlib import Path
import time
import numpy as np
import psutil
from board_prefix_publication_v1 import atomic_json
from board_root_action_replay_store_v1 import sha,verify_receipt
from weighted_evaluation_readback_v1 import worker_guard

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-root-action-effects-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
ACTIONS=('fold','call','raise','jam')
EFFECTS=('BB_later_vs_old_BTN','BB_later_vs_new_BTN','BTN_vs_old_BB_later','BTN_vs_new_BB_later','interaction','total')
# Profile order oldBB-oldBTN, oldBB-newBTN, newBB-oldBTN, newBB-newBTN.
COEFFICIENTS=np.array([[-1,0,1,0],[0,-1,0,1],[-1,1,0,0],[0,0,-1,1],[1,-1,-1,1],[-1,0,0,1]],dtype=float)
STATE=None


def read(p):return json.loads(Path(p).read_bytes())


def initialize(registration):
    global STATE
    evidence=read(registration);reg=read(evidence['replay_registration'])
    STATE=evidence,reg,read(evidence['readback_registration'])['replay_routes']


def load_chunk(names):
    worker_guard();evidence,reg,routes=STATE
    classes=[];values=[]
    for name in names:
        receipt,folder=verify_receipt(Path(reg['store']),evidence['replay_registration_sha256'],
            name,routes[name],reg['source_routes'][name])
        document=read(folder/'action-values.json');profiles=document['profiles']
        c=[r['native_class_index'] for r in profiles[0]['deals']]
        assert len(c) == 32
        for p in profiles:assert [r['native_class_index'] for r in p['deals']] == c
        q=np.array([[[r['action_values'][a][0] for a in range(4)] for r in p['deals']] for p in profiles])
        assert q.shape == (8,32,4) and np.isfinite(q).all()
        classes.extend(c);values.append(q.transpose(1,0,2))
    worker_guard()
    return names,np.asarray(classes,dtype=np.int16),np.concatenate(values)


def effect_values(q):
    result=np.einsum('ep,dspa->dsea',COEFFICIENTS,q.reshape(-1,2,4,4))
    # Different decomposition paths must reconstruct the same total effect.
    assert np.max(abs(result[:,:,0]+result[:,:,3]-result[:,:,5])) < 1e-10
    assert np.max(abs(result[:,:,1]+result[:,:,2]-result[:,:,5])) < 1e-10
    assert np.max(abs(result[:,:,1]-result[:,:,0]-result[:,:,4])) < 1e-10
    assert np.max(abs(result[:,:,3]-result[:,:,2]-result[:,:,4])) < 1e-10
    # Forced fold has no future policy. BB has no later action after its root jam.
    assert np.max(abs(result[:,:,:,0])) < 1e-10
    assert np.max(abs(result[:,:,:2,3])) < 1e-10
    return result


def control():
    q=np.zeros((2,8,4));q[:,:,0]=-1
    for p in range(8):
        own=(p%4)//2;opp=p%2
        q[:,p,1]=np.array([10,20])+3*own+5*opp+7*own*opp
        q[:,p,2]=-q[:,p,1]
        q[:,p,3]=11*opp
    x=effect_values(q)
    assert np.array_equal(x[0,0,:,1],[3,10,5,12,7,15])
    assert np.array_equal(x[1,1,:,1],[3,10,5,12,7,15])
    assert np.array_equal(x[0,0,:,3],[0,0,11,11,0,11])
    return dict(passed=True,known_factorial_effects=True,fold_and_jam_invariants=True)


def summarize(x):
    n=len(x);assert n > 1
    return dict(count=n,means=x.mean(0).tolist(),paired_standard_errors=(x.std(0,ddof=1)/math.sqrt(n)).tolist())


def main(run=False):
    proof=control()
    if not run:print(json.dumps(proof));return
    worker_guard();assert psutil.cpu_percent(interval=1)<30 and psutil.virtual_memory().available>28_000_000_000
    assert not LOCK.exists() and not OTHER.exists()
    rp=OUT/'board-root-action-replay-v1-registration.json'
    ap=OUT/'board-root-action-replay-readback-v1-result.json'
    ar=OUT/'board-root-action-replay-readback-v1-registration.json'
    reg,audit=read(rp),read(ap)
    assert audit['passed'] and audit['complete'] and audit['source_registration_sha256'] == sha(rp)
    assert audit['readback_registration_sha256'] == sha(ar) and audit['deals'] == 65536
    for p,h in read(ar)['inputs'].items():assert sha(p) == h,p
    registration=OUT/(PREFIX+'-registration.json');output=OUT/(PREFIX+'-result.json')
    assert not registration.exists() and not output.exists()
    evidence=dict(format=1,inputs={str(p):sha(p) for p in [rp,ap,ar,Path(__file__),
        ROOT/'tools/research/board_root_action_replay_store_v1.py']},replay_registration=str(rp),
        replay_registration_sha256=sha(rp),readback_registration=str(ar),workers=8,
        source_deals=65536,new_deals=0,gpu_used=False,maximum_seconds=600,
        effects=EFFECTS,coefficients=COEFFICIENTS.tolist(),control=proof,
        exploratory=True,accuracy_qualified=False,scope='Paired fixed-root-action values under crossed old/new complete later policies.')
    pool=None;acquired=False;started=time.monotonic()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert not OTHER.exists();atomic_json(registration,evidence)
        pool=concurrent.futures.ProcessPoolExecutor(max_workers=8,mp_context=multiprocessing.get_context('spawn'),
            initializer=initialize,initargs=(str(registration),))
        groups=[reg['batches'][i:i+32] for i in range(0,len(reg['batches']),32)]
        futures=[pool.submit(load_chunk,g) for g in groups];classes=[];values=[]
        for group,future in zip(groups,futures):
            while True:
                assert time.monotonic()-started < 600;worker_guard()
                try:names,c,q=future.result(timeout=2);break
                except concurrent.futures.TimeoutError:pass
            assert names == group;classes.append(c);values.append(q)
        pool.shutdown(wait=True);pool=None
        classes=np.concatenate(classes);q=np.concatenate(values);effects=effect_values(q)
        assert q.shape == (65536,8,4) and effects.shape == (65536,2,6,4)
        counts=np.bincount(classes,minlength=169)
        assert counts.tolist() == audit['class_evaluation_counts']
        results=dict(format=1,registration_sha256=sha(registration),passed=True,
            deals=65536,actions=ACTIONS,seeds=('first','replication'),effect_order=EFFECTS,
            overall=summarize(effects),classes=[dict(native_class_index=c,**summarize(effects[classes==c])) for c in range(169)],
            paired_before_aggregation=True,exact_factorial_identities=True,fold_and_jam_invariants=True,
            source_hashes_unchanged=True,seconds=time.monotonic()-started,new_deals=0,gpu_used=False,
            exploratory=True,accuracy_qualified=False,
            limitations='Descriptive paired standard errors on the reused sample; not fresh discoveries. Old/new factors are within a training seed, not cross-seed attribution.')
        for p,h in evidence['inputs'].items():assert sha(p) == h,p
        atomic_json(output,results)
        print(json.dumps({k:v for k,v in results.items() if k != 'classes'}),flush=True)
    finally:
        if pool is not None:
            for process in list(pool._processes.values()):
                if process.is_alive():process.terminate()
            pool.shutdown(wait=True,cancel_futures=True)
        if acquired:
            assert LOCK.read_text() == str(os.getpid());LOCK.unlink()


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
