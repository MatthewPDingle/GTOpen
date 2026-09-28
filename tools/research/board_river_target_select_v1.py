"""Freeze fresh physical-deal partitions and river keys before teacher inference."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time
import traceback
import numpy as np
import psutil
from board_river_target_common_v1 import *
from board_prefix_publication_v1 import atomic_json
from sampled_physical_deals_v1 import PhysicalDeals
from board_river_strength_features_v1 import geometry
from bounded_parallel_evaluation_archive_v2 import production_available
from global_research_inventory_v2 import measure as global_measure
from board_study_storage_v1 import measure


class Guard:
    def __init__(self):self.started=time.monotonic();self.last=0
    def __call__(self):
        assert time.monotonic()-self.started<600
        if time.monotonic()-self.last<2:return
        assert production_available() and not OTHER.exists()
        assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage('S:/').free>5_000_000_000
        self.last=time.monotonic()


def controls():
    value=sampled_labels('control','A',[.2,.3,.5],[0,1,2],[-4,1,6])
    assert abs(value['exact']-2.5)<1e-12 and abs(value['single_sample_variance']-15.25)<1e-12
    assert value==sampled_labels('control','A',[.2,.3,.5],[0,1,2],[-4,1,6])
    for selected in range(3):
        p=np.eye(3)[selected];v=sampled_labels('point','B',p,[0,1,2],[-4,1,6]);wanted=(-4,1,6)[selected]
        assert v['exact']==wanted and v['single_sample_variance']==0
        assert all(s['one']==wanted and s['sixteen']==wanted and set(s['opponent_indices'])=={selected} for s in v['samples'])
    rejected=False
    try:sampled_labels('zero','A',[0,0,0],[0,1,2],[-4,1,6])
    except AssertionError:rejected=True
    assert rejected
    return dict(passed=True,finite_distribution_expectation=2.5,variance=15.25,variance_of_mean16=15.25/16,
        deterministic_support=True,zero_mass_rejected=True,stable_seed=True,
        proof='Each independent sampled payoff has sum(p*y) expectation; averaging 16 preserves it and divides variance by 16.')


def select_one(item):
    index,deal=item;split='train' if index<TRAIN_DEALS else 'evaluation';folder=STORE/'selection'
    batch=folder/f'deal-{index:03d}-batch.json';dest=folder/f'deal-{index:03d}-queries.json'
    atomic_json(batch,dict(format=2,batch_id=f'{PREFIX}-{index:03d}',seed=0,query_limit=10000,deals=[deal]))
    child=subprocess.run([str(QUERY_EXE),'queries',str(CONTEXT),str(batch),'-',str(dest)],
        capture_output=True,text=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    if child.returncode:raise RuntimeError(child.stderr[-3000:])
    doc=read(dest);assert doc['context_source']==CONTEXT.read_text();obs=doc['observations']
    active=np.array([o['active_features'] for o in obs],dtype=np.int64);n=np.array([o['n'] for o in obs],dtype=np.int64)
    eligible,public=geometry(active,n,read(OUT/'board-later-public-state-catalog-v1.json'))
    cases=[];strata=[]
    for actor in (0,1):
        for band,low,high in BANDS:
            candidates=[]
            for i,o in enumerate(obs):
                if o['actor']==actor and eligible[i] and low<=public[i,0]<high:
                    score=hashlib.sha256(f'{SELECT_SEED}|{index}|{o["hi"]}|{o["lo"]}'.encode()).hexdigest()
                    candidates.append((score,i))
            candidates.sort();selected=candidates[:2]
            strata.append(dict(actor=actor,pot_band=band,available=len(candidates),selected=len(selected)))
            for rank,(score,i) in enumerate(selected):
                o=obs[i];cases.append(dict(case_id=f'd{index:03d}-p{actor}-{band}-{rank}',split=split,deal_index=index,
                    selection_sha256=score,source_query_index=i,hi=o['hi'],lo=o['lo'],actor=actor,phase=o['phase'],n=o['n'],
                    active_features=o['active_features'],pot_band=band,pot=float(public[i,0]),amount_to_call=float(public[i,1]),
                    rake=float(public[i,2]),branch_total=float(public[i,3])))
    assert len({(c['hi'],c['lo']) for c in cases})==len(cases) and all(c['branch_total']==400.5 for c in cases)
    return dict(deal_index=index,split=split,cases=cases,strata=strata,batch_sha256=sha(batch),query_sha256=sha(dest),
        queries=len(obs),eligible=int(eligible.sum()))


def main():
    guard=Guard();assert not LOCK.exists() and not OTHER.exists() and not STORE.exists();acquired=False
    reg=OUT/(PREFIX+'-selection-registration.json');destination=OUT/(PREFIX+'-selection.json')
    assert not reg.exists() and not destination.exists()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();inventory=global_measure();assert sum(r['allocated_file_bytes'] for r in inventory)+LIMIT<800_000_000_000
        files=[Path(__file__),ROOT/'tools/research/board_river_target_common_v1.py',PLAN,CONTEXT,QUERY_EXE,EXE,
            ROOT/'tools/research/sampled_physical_deals_v1.py',ROOT/'tools/research/board_river_strength_features_v1.py',
            OUT/'board-later-public-state-catalog-v1.json',OUT/'board-river-opponent-reach-v1-control.json',
            OUT/'board-river-opponent-reach-v1-independent-review.json']
        hashes={str(p):sha(p) for p in files};control=controls()
        atomic_json(reg,dict(inputs=hashes,deals=DEALS,training_deals=TRAIN_DEALS,deal_seed=DEAL_SEED,selection_seed=SELECT_SEED,
            maximum_selected=DEALS*20,maximum_new_bytes=LIMIT,maximum_seconds=600,native_workers=4,
            sampling_control=control,storage_admission=inventory,learned_inference=False,created_unix=time.time()))
        STORE.mkdir();(STORE/'selection').mkdir();source=CONTEXT.read_text()
        sampler=PhysicalDeals(source,mode='full_deck',seed=DEAL_SEED);initial=sampler.checkpoint();deals=sampler.sample(DEALS)['deals']
        train_boards={canonical_board(d[4:]) for d in deals[:TRAIN_DEALS]}
        test_boards={canonical_board(d[4:]) for d in deals[TRAIN_DEALS:]}
        assert not train_boards&test_boards,'Cross-partition board group collision; preserve fixed source'
        atomic_json(STORE/'deals.json',dict(deals=deals,initial=initial,final=sampler.checkpoint(),split_at=TRAIN_DEALS))
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows=[]
            for row in pool.map(select_one,enumerate(deals)):
                guard();rows.append(row)
        cases=[case for row in rows for case in row['cases']]
        train_keys={(c['hi'],c['lo']) for c in cases if c['split']=='train'}
        test_keys={(c['hi'],c['lo']) for c in cases if c['split']=='evaluation'}
        assert not train_keys&test_keys and len({c['case_id'] for c in cases})==len(cases)
        verify(hashes);storage=measure(STORE,guard);assert storage['logical_bytes']<250_000_000
        result=dict(passed=True,complete=True,registration_sha256=sha(reg),inputs=hashes,deals_sha256=sha(STORE/'deals.json'),
            cases=cases,per_deal=rows,selected_cases=len(cases),training_cases=sum(c['split']=='train' for c in cases),
            evaluation_cases=sum(c['split']=='evaluation' for c in cases),physical_deals=DEALS,
            unique_train_board_groups=len(train_boards),unique_evaluation_board_groups=len(test_boards),
            disjoint_canonical_board_groups=True,disjoint_visible_keys=True,sampling_control=control,
            learned_inference=False,payoffs_scored=False,gpu_used=False,production_modified=False,storage=storage,
            seconds=time.monotonic()-guard.started)
        atomic_json(destination,result)
        print(json.dumps({k:result[k] for k in ('passed','selected_cases','training_cases','evaluation_cases','storage','seconds')}),flush=True)
    except Exception as e:
        atomic_json(OUT/(PREFIX+'-selection-failure.json'),dict(error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
