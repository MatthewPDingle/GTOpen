"""Five redundant visible river inputs; no hidden cards or training targets."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from sampled_visible_initialization_v1 import fresh_visible_network

ROOT=Path('T:/Dev/GTOpen')
EXE=ROOT/'target/release/examples/hu_river_value_reference_v1.exe'
NAMES=('river_call_fold','net_matched_pot_fraction','call_fraction','centered_uniform_equity','uniform_call_value_fraction')
WIDTH=len(NAMES)


def digest(a):
    a=np.ascontiguousarray(a)
    return hashlib.sha256(str(a.dtype).encode()+str(a.shape).encode()+a.tobytes()).hexdigest()


def geometry(active,arity,catalog):
    active=np.asarray(active);arity=np.asarray(arity)
    assert active.shape==(len(arity),36) and active.dtype.kind in 'iu'
    assert np.all(np.diff(active.astype(int),axis=1)>0) and np.all((active>=0)&(active<269))
    assert arity.dtype.kind in 'iu' and np.all((arity>=2)&(arity<=4))
    table={(r['public_id'],r['actor'],r['phase'],tuple(r['history'])):r for r in catalog['rows']}
    assert len(table)==catalog['decision_templates']
    unique,inverse=np.unique(np.column_stack((active[:,14:],arity)),axis=0,return_inverse=True)
    result=np.full((len(unique),4),np.nan);eligible=np.zeros(len(unique),dtype=bool)
    for i,row in enumerate(unique):
        actor=int(row[0])-133;phase=int(row[1])-135;public=int(row[2])-139
        assert actor in (0,1) and phase in range(4) and public in range(16)
        history=[int(x)-(155+6*j) for j,x in enumerate(row[3:22])]
        assert all(0<=x<=5 for x in history)
        end=next((j for j,x in enumerate(history) if x==0),len(history));assert not any(history[end:])
        if phase==0:
            assert end==0;continue
        native=table[(public,actor,phase,tuple(history[:end]))]
        assert int(row[-1])==native['legal_actions']
        if phase!=3 or native['action_kinds'][:2]!=['fold','call']:continue
        p,c=native['pot'],native['amount_to_call'];assert c==native['action_costs'][1] and c>0
        gross=native['rake_fraction']*(p+c)
        rake=min(gross,native['rake_cap']) if native['rake_cap']>0 else gross
        total=native['starting_pot']+2*native['initial_effective_stack']
        assert abs(p+native['remaining_actor']+native['remaining_opponent']-total)<1e-8
        assert 0<p+c<=total+1e-8 and 0<=rake<p+c
        result[i]=[p,c,rake,total];eligible[i]=True
    return eligible[inverse],result[inverse]


def cards(active):
    assert active.shape==(len(active),36) and np.all(active[:,15]==138)
    ranks=active[:,:14:2].astype(int)-np.arange(7)[None,:]*19
    suits=active[:,1:14:2].astype(int)-(np.arange(7)[None,:]*19+14)
    assert np.all((ranks>=0)&(ranks<13)) and np.all((suits>=0)&(suits<4))
    result=(ranks*4+suits).astype(np.uint8)
    assert np.all(np.diff(np.sort(result.astype(int),axis=1),axis=1)>0)
    result[:,:2]=np.sort(result[:,:2],axis=1);result[:,2:]=np.sort(result[:,2:],axis=1)
    return result


def enumerate_cards(unique,guard,threads):
    assert 1<=threads<=16 and unique.shape==(len(unique),7)
    outputs=[];native_seconds=0.
    for start in range(0,len(unique),4096):
        guard()
        child=subprocess.run([str(EXE),'equities',str(threads)],
            input=json.dumps(unique[start:start+4096].tolist()).encode(),capture_output=True,
            check=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        value=json.loads(child.stdout);assert value['opponent_pairs_per_row']==990
        outputs.extend(value['counts_win_tie_loss']);native_seconds+=value['seconds']
    counts=np.asarray(outputs,dtype=np.int64).reshape((-1,3))
    assert counts.shape==(len(unique),3) and np.all(counts>=0) and np.all(counts.sum(axis=1)==990)
    return counts,native_seconds


def make_pack(active,arity,catalog,equity):
    eligible,public=geometry(active,arity,catalog)
    assert equity.shape==(int(eligible.sum()),) and np.isfinite(equity).all() and np.all((equity>=0)&(equity<=1))
    x=np.zeros((len(active),WIDTH),dtype=np.float32)
    p,c,r,total=public[eligible].T
    x[eligible]=np.column_stack((np.ones(len(p)),(p+c-r)/total,c/total,2*equity-1,(equity*(p+c-r)-c)/total))
    assert np.isfinite(x).all() and np.all(x[~eligible]==0)
    assert np.all((x[:,:3]>=0)&(x[:,:3]<=1)) and np.all(np.abs(x[:,3:])<=1)
    _,first,inverse=np.unique(active,axis=0,return_index=True,return_inverse=True)
    assert np.array_equal(x[first][inverse],x),'Equal visible inputs changed added features'
    return dict(extra=x,eligible=eligible,public=public,active_sha256=digest(active),arity_sha256=digest(arity))


def prepare_features(partitions,catalog,guard,*,threads=4):
    """Callers must pass training and validation only, never final-test rows."""
    assert set(partitions)<= {'train','validation'} and 'train' in partitions
    began=time.monotonic();visible=[];sizes=[]
    for item in partitions.values():
        guard();eligible,_=geometry(item['active'],item['arity'],catalog)
        decoded=cards(item['active'][eligible]);visible.append(decoded);sizes.append(len(decoded))
    combined=np.concatenate(visible);unique,inverse=np.unique(combined,axis=0,return_inverse=True)
    counts,native_seconds=enumerate_cards(unique,guard,threads)
    equity=((counts[:,0]+counts[:,1]/2)/990)[inverse]
    packs={};offset=0
    for (name,item),size in zip(partitions.items(),sizes):
        packs[name]=make_pack(item['active'],item['arity'],catalog,equity[offset:offset+size]);offset+=size
    assert offset==len(combined)
    metadata=dict(partitions=list(partitions),eligible_rows=dict(zip(partitions,sizes)),unique_visible_card_sets=len(unique),
        cards_sha256=digest(unique),counts_sha256=digest(counts),native_seconds=native_seconds,
        seconds=time.monotonic()-began,threads=threads,extra_sha256={k:digest(v['extra']) for k,v in packs.items()},
        uses_hidden_cards=False,uses_targets=False,final_test_features_created=False,persistent_cache_bytes=0)
    return packs,metadata


def extras(pack,arm):
    assert arm in ('geometry','strength')
    x=pack['extra'].copy()
    if arm=='geometry':
        mask=pack['eligible'];p,c,r,total=pack['public'][mask].T
        x[:,3]=0.;x[mask,4]=(.5*(p+c-r)-c)/total
    return x


def fresh_network(seed):
    import torch
    original=fresh_visible_network(seed)
    with torch.random.fork_rng(devices=[]):
        model=torch.nn.Sequential(torch.nn.Linear(302+WIDTH,64),torch.nn.ReLU(),
            torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,4))
        with torch.no_grad():
            model[0].weight.zero_();model[0].weight[:,:302].copy_(original[0].weight)
            model[0].bias.copy_(original[0].bias)
            for layer in (2,4):model[layer].load_state_dict(original[layer].state_dict())
    return model
