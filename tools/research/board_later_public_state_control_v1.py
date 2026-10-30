"""Check new public inputs on all four saved reservoirs; no training/heldout loss."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import concurrent.futures
import hashlib
import json
import multiprocessing
from pathlib import Path
import time
import numpy as np
import psutil
from board_later_public_state_features_v1 import NAMES,WIDTH,features,lookup,fresh_public_network
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_features_bulk_v1 import features as original_features
from weighted_reservoir_bulk_load_v1 import load
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def guard():
    assert psutil.virtual_memory().available>24_000_000_000 and production_available()


def one(item):
    guard()
    for p,h in item['inputs'].items():assert sha(p)==h,p
    r=load(item['reservoir'],Path(item['context']).read_text(),guard=guard)
    doc=read(OUT/'board-later-public-state-catalog-v1.json');table=lookup(doc)
    x=features(r.active[:r.size],r.arity[:r.size],table)
    phase=r.active[:r.size,15]-135
    assert np.all(x[phase==0]==0) and np.all(x[phase>0,0]>0)
    # Different private cards with equal public history must get identical new inputs.
    unique,first,inverse=np.unique(r.active[:r.size,14:],axis=0,return_index=True,return_inverse=True)
    assert np.array_equal(x[first][inverse],x)
    # Cover every public template present, rather than choosing favorable cards.
    baseline=original_features([dict(active_features=a.tolist()) for a in r.active[first]])
    import torch
    torch.set_num_threads(1)
    old=fresh_visible_network(item['fit_seed']).double();new=fresh_public_network(item['fit_seed']).double()
    with torch.no_grad():
        reference=old(torch.as_tensor(baseline,dtype=torch.float64))
        predicted=new(torch.as_tensor(np.column_stack((baseline,x[first])),dtype=torch.float64))
    error=float((reference-predicted).abs().max());assert error<1e-12
    bad=r.arity[:r.size].copy();at=int(np.flatnonzero(phase>0)[0]);bad[at]=2 if bad[at]!=2 else 3
    rejected=False
    try:features(r.active[:r.size],bad,table)
    except AssertionError:rejected=True
    assert rejected
    return dict(dataset=item['name'],rows=r.size,public_templates=len(unique),new_width=302+WIDTH,
        maximum_initial_function_difference=error,wrong_legal_menu_rejected=True,
        card_independent_new_inputs=True,preflop_additions_zero=True)


def main():
    began=time.monotonic();destination=OUT/'board-later-public-state-control-v1.json'
    assert not destination.exists();guard();assert psutil.cpu_percent(interval=1)<75
    rp=OUT/'board-later-fit-holdout-preparation-v1-registration.json';reg=read(rp)
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    files=[rp,Path(__file__),OUT/'board-later-public-state-catalog-v1.json',OUT/'bb-context-candidate.json',
        ROOT/'tools/research/board_later_public_state_features_v1.py',
        ROOT/'target/release/examples/hu_sampled_public_state_features_v1.exe',
        ROOT/'crates/solver/examples/hu_sampled_public_state_features_v1.rs',ROOT/'crates/solver/src/tree.rs',ROOT/'Cargo.lock']
    files += [ROOT/'crates/solver/examples/research_sampled'/n for n in ('state.rs','poker_reference_v1.rs','observation_v1.rs')]
    inputs={**reg['inputs'],**{str(p):sha(p) for p in files}}
    with concurrent.futures.ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as pool:
        futures=[pool.submit(one,d) for d in reg['datasets']];results=[]
        for future in futures:
            while True:
                guard();assert time.monotonic()-began<600
                try:result=future.result(timeout=2);break
                except concurrent.futures.TimeoutError:pass
            results.append(result);print(json.dumps(result),flush=True)
    for p,h in inputs.items():assert sha(p)==h,p
    atomic_json(destination,dict(passed=True,inputs=inputs,datasets=results,feature_names=NAMES,
        seconds=time.monotonic()-began,training_started=False,heldout_loss_scored=False,
        scope='Public betting-state inputs validated against native game state; no range improvement claimed.'))
    print(json.dumps(dict(passed=True,rows=sum(r['rows'] for r in results),result=str(destination))),flush=True)


if __name__=='__main__':main()
