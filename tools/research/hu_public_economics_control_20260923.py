"""CPU-only public-chip feature controls on existing observations and arithmetic fixtures."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_public_economics_features_v1 import encode_document,SPEC,NAMES

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='public-economics-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic()
    assert psutil.virtual_memory().available>20_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    context=OUT/'bb-context-candidate.json'
    fixture_reg=OUT/'sampled-physical-preflop-table-control-v1-registration.json'
    old=json.loads(fixture_reg.read_text())
    for p,h in old['inputs'].items():assert sha(p)==h,p
    fixture=Path(old['fixture']);queries=json.loads(fixture.read_text());assert queries['context_source']==context.read_text()
    exe=ROOT/'target/release/examples/hu_public_economics_v1.exe'
    paths=[context,fixture_reg,fixture,exe,Path(__file__),
           ROOT/'tools/research/sampled_public_economics_features_v1.py',
           ROOT/'crates/solver/examples/hu_public_economics_v1.rs',
           ROOT/'crates/solver/examples/research_sampled/state.rs',
           ROOT/'crates/solver/examples/research_sampled/poker_reference_v1.rs']
    registration=dict(inputs={str(p):sha(p) for p in paths},feature_spec=SPEC,maximum_seconds=180,
        scope='Existing 200bb queries, independent chip-ledger checks, synthetic depth arithmetic and rejection tests. No GPU, new poker deals, learned policy or cross-depth accuracy claim.',production_modified=False)
    rp=OUT/f'{PREFIX}-registration.json';save(rp,registration);STORE.mkdir(exist_ok=False)
    def native(q,name):
        dest=STORE/name
        done=subprocess.run([str(exe),str(context),str(q),str(dest)],cwd=ROOT,timeout=90,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        assert done.returncode==0,done.stderr[-2000:]
        return json.loads(dest.read_text())
    document=native(fixture,'public.json');matrix=encode_document(document,expected_context_sha256=sha(context))
    rows={r['hi']:r for r in document['public_states']};assert len(rows)==len(matrix)
    # Reconstruct every public chip ledger using only action-history links, not State::put.
    c=json.loads(context.read_text());stack=c['config']['stack'];count=0
    for hi,row in rows.items():
        key=int(hi)
        if key>>63==0:
            n=c['nodes'][key-1];assert row['invested']==n['invested'] and row['pot']==n['pot']
            for a,b in zip(row['actions'],n['actions']):
                expected=0. if a['kind'] in ('fold','check') else b['to']-n['invested'][row['actor']]
                assert abs(a['increment']-expected)<1e-9
        else:
            branch=key&15;encoded=(key&~(1<<63))>>4;tokens=[]
            while encoded>1:tokens.append(encoded&7);encoded>>=3
            assert encoded==1;tokens.reverse();contrib=list(c['nodes'][branch]['invested']);h=1
            for token in tokens:
                if token!=5:
                    parent=rows[str((1<<63)|(h<<4)|branch)]
                    contrib[parent['actor']]+=parent['actions'][token-1]['increment']
                h=(h<<3)|token
            assert np.max(abs(np.array(contrib)-row['invested']))<1e-9
            assert abs(sum(contrib)+c['dead_money']-row['pot'])<1e-9
        count+=1
    root=rows['1'];assert root['call_cost']==1 and root['pot']==3.5
    assert [a['increment'] for a in root['actions']]==[0,1,5,199]
    assert root['remaining']==[199,198]
    flop=rows[str((1<<63)|(1<<4)|2)]
    assert flop['invested']==[2,2] and flop['remaining']==[198,198] and flop['pot']==4.5 and flop['call_cost']==0
    # Private cards, hidden batch labels and inference targets cannot affect public output.
    changed=copy.deepcopy(queries)
    for obs in changed['observations']:
        obs['lo']='0';obs['active_features']=[]
    changed['batch_source']='unread hidden labels';changed['targets']=[999]
    q=STORE/'mutated-private.json';save(q,changed)
    assert native(q,'mutated-public.json')==document
    # Synthetic arithmetic only; these are not native game exports or training contexts.
    depth_rows=[];vectors=[];base=copy.deepcopy(root)
    for depth in (20,40,60,100,150,200,400):
        source=json.dumps(dict(config=dict(stack=depth),dead_money=.5,rake_fraction=.05,rake_cap=2),sort_keys=True)
        r=copy.deepcopy(base);r['starting_stacks']=[depth,depth];r['remaining']=[depth-1,depth-2]
        r['actions'][-1]['increment']=depth-1
        d=dict(format=1,context_source=source,public_states=[r]);v=encode_document(d,expected_context_sha256=hashlib.sha256(source.encode()).hexdigest())[0]
        vectors.append(v);depth_rows.append(dict(depth=depth,call_cost=r['call_cost'],jam_increment=r['actions'][-1]['increment']))
    assert all(not np.array_equal(a,b) for i,a in enumerate(vectors) for b in vectors[i+1:])
    rejected=0
    for mutate in ('hash','remaining','pot','call','oversize','allin','nan','check','duplicate','actions'):
        d=copy.deepcopy(document);r=d['public_states'][0];expected=sha(context)
        if mutate=='hash':expected='0'*64
        elif mutate=='remaining':r['remaining'][0]+=1
        elif mutate=='pot':r['pot']+=1
        elif mutate=='call':r['call_cost']+=1
        elif mutate=='oversize':r['actions'][2]['increment']=1000
        elif mutate=='allin':r['actions'][-1]['all_in']=False
        elif mutate=='nan':r['pot']=float('nan')
        elif mutate=='check':r['actions'][0]['kind']='check'
        elif mutate=='duplicate':d['public_states'].append(copy.deepcopy(r))
        else:r['actions']*=2
        try:encode_document(d,expected_context_sha256=expected)
        except ValueError:rejected+=1
        else:raise AssertionError('Accepted '+mutate)
    for p,h in registration['inputs'].items():assert sha(p)==h,p
    result=dict(passed=True,registration_sha256=sha(rp),public_states=len(rows),observations=len(queries['observations']),
        feature_width=matrix.shape[1],independent_ledger_paths=count,private_information_invariance=True,
        synthetic_depth_checks=depth_rows,negative_controls=rejected,
        artifacts={str(p):sha(p) for p in STORE.iterdir()},seconds=time.monotonic()-started,
        accuracy_qualified=False,production_modified=False,scope=registration['scope'])
    assert result['seconds']<180
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))

if __name__=='__main__':main()
