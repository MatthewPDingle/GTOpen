"""CPU controls before the fixed conditional-river reference diagnostic."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import itertools
import json
from pathlib import Path
import subprocess
import time
import traceback
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,read,sha,verify
from board_prefix_publication_v1 import atomic_json
from global_research_inventory_v2 import measure as global_measure
from board_study_storage_v1 import measure
from bounded_parallel_evaluation_archive_v2 import production_available
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_bank_v1 import histories
from board_river_opponent_reach_math_v1 import posterior,fold_call_readout,PAIR_ID

PREFIX='board-river-opponent-reach-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
EXE=ROOT/'target/release/examples/hu_river_conditional_queries_v1.exe'
CONTEXT=OUT/'bb-context-candidate.json'
LIMIT=500_000_000


class Guard:
    def __init__(self):self.start=time.monotonic();self.last=0
    def __call__(self):
        assert time.monotonic()-self.start<3600
        if time.monotonic()-self.last<2:return
        assert production_available() and not OTHER.exists() and psutil.virtual_memory().available>24_000_000_000
        assert psutil.disk_usage('S:/').free>5_000_000_000
        self.last=time.monotonic()


def export(request,folder,name,guard,context=CONTEXT):
    guard();rp=folder/(name+'-request.json');op=folder/(name+'-export.json')
    atomic_json(rp,request);start=time.monotonic()
    p=subprocess.run([str(EXE),str(context),str(rp),str(op)],capture_output=True,text=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    if p.returncode:raise RuntimeError(p.stderr[-3000:])
    doc=read(op);assert doc['context_source']==context.read_text() and doc['request_source']==rp.read_text()
    return doc,dict(name=name,request_sha256=sha(rp),export_sha256=sha(op),queries=len(doc['queries']['observations']),seconds=time.monotonic()-start)


def uniform(doc):
    n=np.array([o['n'] for o in doc['queries']['observations']]);p=(np.arange(4)[None,:]<n[:,None])/n[:,None]
    return p


def identity(o,obs):
    return {**{k:o[k] for k in ('hi','lo','actor','phase','n','active_features')},
        'history_keys':[(obs[i]['hi'],obs[i]['lo'],a,n) for i,a,n in o['own_history']]}


def crosscheck(doc,folder,name,guard):
    hero=doc['target']['actor'];cards=doc['target']['cards'];deals=[];query_ids={doc['target']['query_index']}
    for j in (0,495,989):
        pair=doc['pairs'][j];private=[None]*4;private[hero*2:hero*2+2]=cards[:2];private[(1-hero)*2:(1-hero)*2+2]=pair['cards']
        deals.append(private+cards[2:]);query_ids.update(step[0] for step in pair['path'])
    raw=folder/(name+'-full-batch.json');result=folder/(name+'-full-queries.json')
    atomic_json(raw,dict(format=2,batch_id=name,seed=0,query_limit=100000,deals=deals))
    guard();p=subprocess.run([str(ROOT/'target/release/examples/hu_sampled_bank_bridge.exe'),'queries',str(CONTEXT),str(raw),'-',str(result)],
        capture_output=True,text=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    if p.returncode:raise RuntimeError(p.stderr[-2000:])
    ref=read(result)['observations'];table={(o['hi'],o['lo']):identity(o,ref) for o in ref};obs=doc['queries']['observations']
    for i in query_ids:assert identity(obs[i],obs)==table[(obs[i]['hi'],obs[i]['lo'])]
    return dict(physical_deals=3,visible_rows_checked=len(query_ids),reference_sha256=sha(result))


def mixed_average_control(doc,entry):
    obs=doc['queries']['observations'];prior=histories(obs);models=np.zeros((2,len(obs),4));weights=np.array([[1.,4.],[3.,2.]])
    for i,o in enumerate(obs):
        n=o['n'];a=np.arange(1,n+1,dtype=float)+(int(o['lo'])%3);b=np.arange(n,0,-1,dtype=float)+(int(o['lo'])%7)
        models[0,i,:n]=a/a.sum();models[1,i,:n]=b/b.sum()
    average=np.zeros((len(obs),4))
    for i,o in enumerate(obs):
        own=weights[o['actor']].copy()
        for j,a in prior[i]:own*=models[:,j,a]
        average[i]=(models[:,i]*own[:,None]).sum(0)/own.sum()
    _,computed=posterior(doc,average,entry);hero=doc['target']['actor'];expected=[]
    for pair in doc['pairs']:
        reach=np.ones(2)
        for i,a,_ in pair['path']:
            if obs[i]['actor']!=hero:reach*=models[:,i,a]
        expected.append(float(reach@weights[1-hero]/weights[1-hero].sum()))
    error=float(np.max(abs(np.array(expected)-computed['opponent_likelihood'])));assert error<1e-12
    return error


def basic(doc,entry):
    obs=doc['queries']['observations'];histories(obs);p=uniform(doc)
    stats,arrays=posterior(doc,p,entry);hero=doc['target']['actor'];ids=arrays['pair_ids']
    allowed=set(range(52))-set(doc['target']['cards'])
    assert {tuple(x['cards']) for x in doc['pairs']}==set(itertools.combinations(sorted(allowed),2))
    prior=entry[1-hero,ids];expected=prior/prior.sum()
    assert np.max(abs(arrays['posterior']-expected))<1e-12
    assert abs(stats['equity']-expected@(arrays['outcomes']*.5))<1e-12
    fixed=np.zeros_like(p)
    for i,o in enumerate(obs):fixed[i,:o['n']]=np.arange(1,o['n']+1)/sum(range(1,o['n']+1))
    _,mixed=posterior(doc,fixed,entry);assert np.max(abs(mixed['posterior']-expected))<1e-12
    zero=entry.copy();zero[1-hero]=0;unsupported,_=posterior(doc,p,zero)
    assert not unsupported['supported'] and unsupported['equity'] is None and unsupported['call_minus_fold_bb'] is None
    no_reach=p.copy()
    for pair in doc['pairs']:
        i,a,n=next(step for step in reversed(pair['path']) if obs[step[0]]['actor']!=hero)
        no_reach[i]=0;no_reach[i,1 if a==0 else 0]=1
    unsupported,_=posterior(doc,no_reach,entry);assert not unsupported['supported']
    no_hero=p.copy();i,a,n=next(step for step in doc['pairs'][0]['path'] if obs[step[0]]['actor']==hero)
    no_hero[i]=0;no_hero[i,1 if a==0 else 0]=1
    off_path,_=posterior(doc,no_hero,entry);assert not off_path['hero_on_path'] and off_path['supported']
    point_checks=0
    for outcome in (0,1,2):
        found=np.flatnonzero(arrays['outcomes']==outcome)
        if not len(found):continue
        weights=entry.copy();weights[1-hero]=0;weights[1-hero,ids[found[0]]]=1
        point,_=posterior(doc,p,weights)
        assert point['effective_opponent_combos']==1 and point['equity']==outcome*.5
        assert abs(point['call_minus_fold_bb']-doc['geometry']['endpoints_loss_tie_win'][outcome])<1e-9;point_checks+=1
    for policy,delta,expected_gain in (([.4,.6,0,0],2,.8),([.4,.6,0,0],-2,1.2),([.2,.3,.5,0],2,.4),([0,0,1,0],2,0)):
        assert abs(fold_call_readout(policy,delta)['restricted_switch_gain_bb']-expected_gain)<1e-12
    return dict(uniform_prior_max_error=float(np.max(abs(arrays['posterior']-expected))),
        opponent_pairs=990,point_mass_outcomes_checked=point_checks,zero_opponent_mass_rejected=True,
        zero_opponent_reach_rejected=True,off_path_hero_flagged=True,mixed_bank_max_error=mixed_average_control(doc,entry))


def pack(cards,actor):return str(sum(int(c)<<(6*i) for i,c in enumerate(cards))|(actor<<42))


def main():
    guard=Guard();assert not LOCK.exists() and not OTHER.exists() and not STORE.exists();acquired=False
    result_path=OUT/(PREFIX+'-control.json');reg_path=OUT/(PREFIX+'-control-registration.json')
    assert not result_path.exists() and not reg_path.exists()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();inventory=global_measure();assert sum(x['allocated_file_bytes'] for x in inventory)+LIMIT<800_000_000_000
        selection_path=OUT/(PREFIX+'-selected-cases.json');selection=read(selection_path);verify(selection['inputs'])
        sources=[Path(__file__),TOOLS/'board_river_opponent_reach_math_v1.py',ROOT/'crates/solver/examples/hu_river_conditional_queries_v1.rs',EXE,
            ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',selection_path,CONTEXT]
        sources += [ROOT/'crates/solver/examples/research_sampled'/n for n in ('state.rs','poker_reference_v1.rs','observation_v1.rs','policy_bank_v1.rs')]
        inputs={str(p):sha(p) for p in sources};atomic_json(reg_path,dict(inputs=inputs,storage_admission=inventory,
            budget_bytes=LIMIT,maximum_seconds=3600,gpu_used=False,new_deals=0))
        STORE.mkdir();folder=STORE/'control';folder.mkdir();entry=PhysicalDeals(CONTEXT.read_text(),mode='full_deck',seed=0).weights
        records=[];documents=[]
        for i in range(0,80,8):
            case=selection['cases'][i];doc,record=export(dict(format=1,hi=case['hi'],lo=case['lo']),folder,f'case-{i:03d}',guard)
            record.update(basic(doc,entry));assert doc['geometry']['pot']==case['pot'] and doc['geometry']['amount_to_call']==case['amount_to_call']
            if i in (32,72):record['full_query_crosscheck']=crosscheck(doc,folder,f'case-{i:03d}',guard)
            records.append(record);documents.append(doc)
        source=selection['cases'][32];actor=source['actor']
        synthetic=[]
        for label,cards in (('aces',[48,49,0,13,26,35,40]),('royal',[1,6,32,36,40,44,48])):
            doc,record=export(dict(format=1,hi=source['hi'],lo=pack(cards,actor)),folder,label,guard);record.update(basic(doc,entry))
            if label=='royal':assert doc['counts_loss_tie_win']==[0,990,0]
            else:assert all(x>0 for x in doc['counts_loss_tie_win'])
            synthetic.append(record)
        original=documents[0]
        for j,permutation in enumerate(((1,0,3,2),(3,2,1,0),(1,2,3,0))):
            cards=[c//4*4+permutation[c%4] for c in original['target']['cards']]
            doc,record=export(dict(format=1,hi=original['target']['hi'],lo=pack(cards,original['target']['actor'])),folder,f'suits-{j}',guard)
            assert doc['target']==original['target'] and doc['pairs']==original['pairs']
            assert doc['queries']['observations']==original['queries']['observations'];synthetic.append(record)
        for j,(rate,cap) in enumerate(((0.,0.),(.1,0.),(.1,.1))):
            context=read(CONTEXT);context.update(rake_fraction=rate,rake_cap=cap);cp=folder/f'rake-{j}-context.json';atomic_json(cp,context)
            doc,record=export(dict(format=1,hi=source['hi'],lo=source['lo']),folder,f'rake-{j}',guard,cp)
            record.update(basic(doc,entry));synthetic.append(record)
        storage=measure(STORE,guard);assert storage['logical_bytes']<LIMIT;verify(inputs)
        result=dict(passed=True,complete=True,registration_sha256=sha(reg_path),records=records,synthetic=synthetic,storage=storage,
            seconds=time.monotonic()-guard.start,gpu_used=False,learned_inference=False,new_deals=0,production_modified=False)
        atomic_json(result_path,result);print(json.dumps(dict(passed=True,public_cases=len(records),synthetic_cases=len(synthetic),storage=storage,seconds=result['seconds'])))
    except Exception:
        if STORE.exists():atomic_json(STORE/'control-failure.json',dict(traceback=traceback.format_exc()))
        raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


TOOLS=ROOT/'tools/research'
if __name__=='__main__':main()
