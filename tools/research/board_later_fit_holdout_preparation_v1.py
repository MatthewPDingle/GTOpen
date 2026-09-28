"""Authenticate four generation-77 datasets and qualify their fixed splits."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import argparse
import concurrent.futures
import json
import multiprocessing
from pathlib import Path
import time
import numpy as np
import psutil
from board_later_fit_holdout_data_v1 import prepare,SALT
from board_root_action_replay_store_v1 import sha
from board_prefix_publication_v1 import atomic_json
from weighted_reservoir_bulk_load_v1 import load
from sampled_visible_features_bulk_v1 import features
from weighted_evaluation_readback_v1 import worker_guard

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-later-fit-holdout-preparation-v1'


def read(p):return json.loads(Path(p).read_bytes())


def one(dataset):
    started=time.monotonic();worker_guard()
    for p,h in dataset['inputs'].items():assert sha(p)==h,p
    r=load(dataset['reservoir'],Path(dataset['context']).read_text(),guard=worker_guard)
    assert r.player==dataset['player'] and r.size==dataset['retained_examples']
    assert abs(r.deal_weights[:r.size].sum()-dataset['retained_weight'])<1e-8
    assert int(r.iterations[:r.size].max())==77
    parts,proof,split=prepare(r.active[:r.size],r.arity[:r.size],r.values[:r.size],r.deal_weights[:r.size])
    # Verify real feature geometry and visible-information rules on every group.
    for data in parts.values():
        worker_guard();x=features([dict(active_features=a.tolist()) for a in data['active']])
        assert x.shape==(len(data['active']),302) and np.isfinite(x).all()
        del x
    phases=r.active[:r.size,15].astype(int)-135
    assert set(phases)<=set(range(4))
    coverage=[]
    for index,name in enumerate(('train','validation','test')):
        selected=split==index
        coverage.append(dict(split=name,phases=[dict(phase=p,rows=int(np.count_nonzero(selected&(phases==p))),
            source_weight=float(r.deal_weights[:r.size][selected&(phases==p)].sum())) for p in range(4)],
            arities=[dict(arity=a,rows=int(np.count_nonzero(selected&(r.arity[:r.size]==a)))) for a in (2,3,4)]))
        assert all(row['rows']>0 for row in coverage[-1]['phases'] if row['phase']>0)
    for p,h in dataset['inputs'].items():assert sha(p)==h,p
    return dict(dataset=dataset['name'],split=proof,coverage=coverage,
        visible_feature_geometry_checked=True,source_unchanged=True,seconds=time.monotonic()-started)


def main(run=False):
    source=OUT/'board-root-matched-continuation-v1-result.json'
    original_registration=OUT/'board-root-matched-continuation-v1-registration.json'
    control=OUT/'board-later-fit-holdout-data-v1-control.json'
    helper=ROOT/'tools/research/board_later_fit_holdout_data_v1.py'
    result,original,proof=read(source),read(original_registration),read(control)
    assert result['passed'] and result['training_complete'] and result['registration_sha256']==sha(original_registration)
    assert proof['passed'] and proof['source_sha256']==sha(helper)
    context=OUT/'bb-context-candidate.json';datasets=[]
    files=[source,original_registration,control,helper,context,Path(__file__),
        ROOT/'tools/research/weighted_reservoir_bulk_load_v1.py',ROOT/'tools/research/sampled_visible_features_bulk_v1.py']
    for arm in result['arms']:
        progress_path=Path(arm['progress_path']);assert sha(progress_path)==arm['progress_sha256']
        progress=read(progress_path);ref=progress['generations'][76];metric_path=Path(ref['path'])
        assert sha(metric_path)==ref['sha256'];metrics=read(metric_path);assert metrics['iteration']==77
        objects=progress_path.parent/'objects';checkpoint_path=objects/metrics['checkpoint']['file']
        assert sha(checkpoint_path)==metrics['checkpoint']['sha256'];checkpoint=read(checkpoint_path)
        assert checkpoint['completed_iterations']==77 and checkpoint['next_model']==metrics['next_model']
        assert checkpoint['context_sha256']==sha(context)
        expected=next(a['config'] for a in original['arms'] if a['name']==arm['arm'])
        assert checkpoint['config']==expected
        files.extend((progress_path,metric_path,checkpoint_path))
        for player,reservoir_ref in enumerate(checkpoint['reservoirs']):
            path=objects/reservoir_ref['file'];assert sha(path)==reservoir_ref['sha256'];files.append(path)
            stats=metrics['reservoirs'][player];assert stats['player']==player
            inputs={str(p):sha(p) for p in (progress_path,metric_path,checkpoint_path,path,context)}
            datasets.append(dict(name=arm['arm']+'-'+('BB','BTN')[player],arm=arm['arm'],player=player,
                reservoir=str(path),context=str(context),generation=77,retained_examples=stats['retained'],
                retained_weight=stats['retained_weight'],fit_seed=metrics['fits'][player]['seed'],inputs=inputs))
    if not run:
        print(json.dumps(dict(ready=True,datasets=[d['name'] for d in datasets],cpu_workers=2,training_started=False)));return
    worker_guard();assert psutil.virtual_memory().available>40_000_000_000 and psutil.cpu_percent(interval=1)<75
    rp=OUT/(PREFIX+'-registration.json');destination=OUT/(PREFIX+'-result.json')
    assert not rp.exists() and not destination.exists()
    reg=dict(format=1,inputs={str(p):sha(p) for p in files},datasets=datasets,salt=SALT,
        workers=2,maximum_seconds=600,new_training=False,gpu_used=False,new_deals=0,
        scope='Read-only source and split preparation; may coexist with the existing CPU readback under available resources.')
    atomic_json(rp,reg);started=time.monotonic();pool=None
    try:
        pool=concurrent.futures.ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn'))
        futures=[pool.submit(one,d) for d in datasets];results=[]
        for future in futures:
            while True:
                worker_guard();assert time.monotonic()-started<600
                try:record=future.result(timeout=2);break
                except concurrent.futures.TimeoutError:pass
            results.append(record);print(json.dumps(dict(prepared=record['dataset'],seconds=record['seconds'])),flush=True)
        pool.shutdown(wait=True);pool=None
        for p,h in reg['inputs'].items():assert sha(p)==h,p
        output=dict(passed=True,registration_sha256=sha(rp),datasets=results,seconds=time.monotonic()-started,
            source_hashes_unchanged=True,training_started=False,new_deals=0,gpu_used=False)
        atomic_json(destination,output);print(json.dumps(output),flush=True)
    finally:
        if pool is not None:
            for p in list(pool._processes.values()):
                if p.is_alive():p.terminate()
            pool.shutdown(wait=True,cancel_futures=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
