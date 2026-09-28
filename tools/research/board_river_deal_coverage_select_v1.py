"""Pre-label membership freeze for equal-row-budget physical-deal coverage."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time
import traceback
import numpy as np
import psutil
from board_river_deal_coverage_common_v1 import *
from board_prefix_publication_v1 import atomic_json
from sampled_physical_deals_v1 import PhysicalDeals
from board_river_strength_features_v1 import geometry
from bounded_parallel_evaluation_archive_v2 import production_available
from global_research_inventory_v2 import measure as global_measure
from board_study_storage_v1 import measure


SCHEDULES=(('under10','10to50','50to100'),('10to50','100to200','200plus'),('50to100','100to200','200plus'))


def assignment():
    order=sorted(range(TRAIN_DEALS),key=lambda i:hashlib.sha256(f'{ASSIGN_SEED}|{i}'.encode()).hexdigest())
    return {i:SCHEDULES[k%3] for k,i in enumerate(order)}


class Guard:
    def __init__(self):self.started=time.monotonic();self.last=0
    def __call__(self):
        assert time.monotonic()-self.started<600
        if time.monotonic()-self.last<2:return
        assert production_available() and not OTHER.exists()
        assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage('S:/').free>5_000_000_000
        self.last=time.monotonic()


def controls():
    assigned=assignment();assert set(assigned)==set(range(192))
    actual=Counter(b for bands in assigned.values() for b in bands)
    expected=dict(under10=64,**{'10to50':128,'50to100':128,'100to200':128,'200plus':128})
    assert actual==expected and sum(actual.values())==576
    assert assigned==assignment()
    value=sampled_labels('control','A',[.2,.3,.5],[0,1,2],[-4,1,6])
    assert abs(value['exact']-2.5)<1e-12 and abs(value['single_sample_variance']-15.25)<1e-12
    assert value==sampled_labels('control','A',[.2,.3,.5],[0,1,2],[-4,1,6])
    for selected in range(3):
        row=sampled_labels('point','B',np.eye(3)[selected],[0,1,2],[-4,1,6]);wanted=(-4,1,6)[selected]
        assert row['exact']==wanted and row['single_sample_variance']==0
        assert all(s['one']==wanted and s['sixteen']==wanted for s in row['samples'])
    rejected=False
    try:sampled_labels('zero','A',[0,0,0],[0,1,2],[-4,1,6])
    except AssertionError:rejected=True
    assert rejected
    board=[0,5,14,23,32];relabel=[c//4*4+(c%4+1)%4 for c in board]
    assert canonical_board(board)==canonical_board(relabel)
    return dict(passed=True,per_actor_quotas=expected,schedules=assigned,
        deterministic_support=True,zero_mass_rejected=True,stable_seed=True,
        finite_distribution_expectation=2.5,variance=15.25,canonical_relabeling_invariant=True)


def select_one(item):
    index,deal,bands=item;split='train' if index<TRAIN_DEALS else 'evaluation';folder=STORE/'selection'
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
            if split=='train' and band not in bands:continue
            candidates=[]
            for i,o in enumerate(obs):
                if o['actor']==actor and eligible[i] and low<=public[i,0]<high:
                    score=hashlib.sha256(f'{SELECT_SEED}|{index}|{o["hi"]}|{o["lo"]}'.encode()).hexdigest()
                    candidates.append((score,i))
            candidates.sort();required=1 if split=='train' or band=='under10' else 2
            assert len(candidates)>=required,(index,actor,band,len(candidates),required)
            selected=candidates[:required]
            strata.append(dict(actor=actor,pot_band=band,available=len(candidates),selected=len(selected)))
            for rank,(score,i) in enumerate(selected):
                o=obs[i];cases.append(dict(case_id=f'coverage-d{index:03d}-p{actor}-{band}-{rank}',split=split,deal_index=index,
                    selection_sha256=score,source_query_index=i,hi=o['hi'],lo=o['lo'],actor=actor,phase=o['phase'],n=o['n'],
                    active_features=o['active_features'],pot_band=band,pot=float(public[i,0]),amount_to_call=float(public[i,1]),
                    rake=float(public[i,2]),branch_total=float(public[i,3])))
    assert len(cases)==(6 if split=='train' else 18)
    assert len({(c['hi'],c['lo']) for c in cases})==len(cases) and all(c['branch_total']==400.5 for c in cases)
    return dict(deal_index=index,split=split,cases=cases,strata=strata,batch_sha256=sha(batch),query_sha256=sha(dest),
        queries=len(obs),eligible=int(eligible.sum()))


def main():
    guard=Guard();assert not LOCK.exists() and not OTHER.exists() and not STORE.exists();acquired=False
    reg=OUT/(PREFIX+'-selection-registration.json');destination=OUT/(PREFIX+'-selection.json')
    assert not reg.exists() and not destination.exists()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();inventory=global_measure()
        assert sum(r['allocated_file_bytes'] for r in inventory)+LIMIT<800_000_000_000
        old_selection_path=OUT/(OLD_PREFIX+'-selection.json');old_readback_path=OUT/(OLD_PREFIX+'-readback.json')
        old=read(old_selection_path);proof=read(old_readback_path);old_deals=read(OLD_STORE/'deals.json')['deals']
        assert old['passed'] and old['complete'] and proof['passed'] and proof['complete']
        assert sha(Path(proof['dataset']))==proof['dataset_sha256'];verify(old['inputs'])
        assert sha(OLD_STORE/'deals.json')==old['deals_sha256'] and len(old_deals)==96
        files=[Path(__file__),ROOT/'tools/research/board_river_deal_coverage_common_v1.py',PLAN,CONTEXT,QUERY_EXE,EXE,
            ROOT/'tools/research/sampled_physical_deals_v1.py',ROOT/'tools/research/board_river_strength_features_v1.py',
            ROOT/'tools/research/bounded_parallel_evaluation_archive_v2.py',ROOT/'tools/research/global_research_inventory_v2.py',
            ROOT/'tools/research/board_study_storage_v1.py',OUT/'board-later-public-state-catalog-v1.json',
            old_selection_path,old_readback_path,OLD_STORE/'deals.json',Path(proof['dataset']),
            OUT/'board-river-opponent-reach-v1-control.json',OUT/'board-river-opponent-reach-v1-independent-review.json']
        hashes={str(p):sha(p) for p in files};control=controls();assigned=assignment()
        atomic_json(reg,dict(inputs=hashes,new_deals=160,reused_training_deals=64,new_training_deals=128,
            fresh_evaluation_deals=32,deal_seed=DEAL_SEED,selection_seed=SELECT_SEED,assignment_seed=ASSIGN_SEED,
            exact_new_case_count=1344,maximum_new_bytes=LIMIT,maximum_seconds=600,native_workers=4,
            control=control,storage_admission=inventory,learned_inference=False,created_unix=time.time()))
        STORE.mkdir();(STORE/'selection').mkdir()
        sampler=PhysicalDeals(CONTEXT.read_text(),mode='full_deck',seed=DEAL_SEED);initial=sampler.checkpoint()
        existing={canonical_board(d[4:]) for d in old_deals};seen=set(existing);deals=old_deals[:64].copy();proposals=[]
        while len(deals)<DEALS:
            assert len(proposals)<1000;guard();deal=sampler.sample(1)['deals'][0];board=canonical_board(deal[4:])
            row=dict(proposal_index=len(proposals),deal=deal,canonical_board=board)
            if board in seen:row.update(accepted=False,reason='canonical_board_already_present')
            else:
                row.update(accepted=True,accepted_deal_index=len(deals));deals.append(deal);seen.add(board)
            proposals.append(row)
        atomic_json(STORE/'deals.json',dict(deals=deals,reused_training_deals=64,split_at=192,
            initial=initial,final=sampler.checkpoint(),proposals=proposals,excluded_original_board_groups=len(existing)))
        dense=[c for c in old['cases'] if c['split']=='train'];assert len(dense)==1152
        reused=[]
        for index in range(64):
            for actor in (0,1):
                for band in assigned[index]:
                    choices=[c for c in dense if c['deal_index']==index and c['actor']==actor and c['pot_band']==band]
                    assert choices;reused.append(min(choices,key=lambda c:c['selection_sha256']))
        assert len(reused)==384
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows=[]
            for row in pool.map(select_one,((i,deals[i],assigned.get(i,())) for i in range(64,DEALS))):
                guard();rows.append(row)
        cases=[c for row in rows for c in row['cases']];broad=reused+[c for c in cases if c['split']=='train']
        final=[c for c in cases if c['split']=='evaluation'];assert len(broad)==1152 and len(final)==576 and len(cases)==1344
        quota=lambda rows:Counter((c['actor'],c['pot_band']) for c in rows)
        assert quota(dense)==quota(broad)
        train_keys={(c['hi'],c['lo']) for c in dense+broad};final_keys={(c['hi'],c['lo']) for c in final}
        spent_keys={(c['hi'],c['lo']) for c in old['cases'] if c['split']=='evaluation'}
        assert not train_keys&final_keys and not train_keys&spent_keys and not final_keys&spent_keys
        train_boards={canonical_board(d[4:]) for d in deals[:192]};final_boards={canonical_board(d[4:]) for d in deals[192:]}
        assert len(train_boards)==192 and len(final_boards)==32 and not train_boards&final_boards
        assert not final_boards&existing
        members=dict(dense=[c['case_id'] for c in dense],broad=[c['case_id'] for c in broad],evaluation=[c['case_id'] for c in final])
        assert len(set(members['dense'])&set(members['broad']))==384
        assert len(set(members['dense']+members['broad']+members['evaluation']))==2496
        verify(hashes);storage=measure(STORE,guard);assert storage['logical_bytes']<250_000_000
        result=dict(passed=True,complete=True,registration_sha256=sha(reg),inputs=hashes,deals_sha256=sha(STORE/'deals.json'),
            cases=cases,per_deal=rows,selected_cases=len(cases),training_cases=768,evaluation_cases=576,physical_deals=224,
            reused_dataset=proof['dataset'],reused_dataset_sha256=proof['dataset_sha256'],memberships=members,
            reused_broad_cases=reused,per_actor_pot_quotas={f'{a}/{b}':n for (a,b),n in quota(dense).items()},
            unique_train_board_groups=192,unique_evaluation_board_groups=32,proposed_new_deals=len(proposals),
            disjoint_canonical_board_groups=True,disjoint_visible_keys=True,sampling_control=control,
            learned_inference=False,payoffs_scored=False,gpu_used=False,production_modified=False,
            storage=storage,seconds=time.monotonic()-guard.started)
        atomic_json(destination,result)
        print(json.dumps({k:result[k] for k in ('passed','selected_cases','training_cases','evaluation_cases','storage','seconds')}),flush=True)
    except Exception as e:
        atomic_json(OUT/(PREFIX+'-selection-failure.json'),dict(error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
