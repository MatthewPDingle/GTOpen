"""Exercise exact-cache routing, explicit v3 transport and unchanged reservoirs."""
import copy
import itertools
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_reservoir_v1 import PhysicalReservoir,ingest as legacy_ingest
from sampled_allin_protocol_v3 import AllinCache,canonical,policy_document,ingest

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-protocol-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic();assert idle()
    source=Path('S:/GTOpen-research/sampled-physical-allin-board-control-v1')
    native=json.loads((source/'native.json').read_text())
    fixture=Path('S:/GTOpen-research/sampled-physical-allin-bridge-control-v1/noise-00')
    base=json.loads((fixture/'batch-v2.json').read_text())
    context=OUT/'bb-context-candidate.json';exe=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
    parent=OUT/'sampled-physical-allin-bridge-control-v1-independent-review.json'
    assert json.loads(parent.read_text())['passed']
    paths=[Path(__file__),parent,source/'native.json',fixture/'batch-v2.json',context,exe,
        ROOT/'tools/research/sampled_allin_protocol_v3.py',ROOT/'tools/research/sampled_physical_reservoir_v1.py']
    reg=dict(inputs={str(p):sha(p) for p in paths},reservoir_capacity=17,reservoir_seeds=[921,922],
        scope='Old exact private-pair fixtures only. Suit/within-hand symmetry without player swapping; explicit format-3 native transport, exact per-visit reservoir replay and malformed-input rejection. No fitting or solver-quality evaluation.',
        production_modified=False)
    rp=OUT/f'{PREFIX}-registration.json';save(rp,reg)
    assert not STORE.exists();STORE.mkdir();rows={};artifacts={};checks=0;failures=0
    def put(name,doc):
        p=STORE/name;save(p,doc);artifacts[str(p)]=sha(p);return p
    for r in native:
        key=canonical(r['private_cards'])
        row=dict(private_cards=list(key),wins=r['wins'],ties=r['ties'],losses=r['losses'],boards=r['exact_boards'])
        if key in rows:assert row==rows[key]
        rows[key]=row
    cp=put('cache.json',dict(format=1,player_roles_fixed=True,rows=list(rows.values())))
    cache=AllinCache(cp,sha(cp))
    for row in native:
        hole=row['private_cards']
        for perm in itertools.permutations(range(4)):
            mapped=[4*(c//4)+perm[c%4] for c in hole]
            for flips in range(4):
                h=mapped[:]
                if flips&1:h[:2]=h[:2][::-1]
                if flips&2:h[2:]=h[2:][::-1]
                d=h+[c for c in range(52) if c not in h][:5]
                label=cache.labels([d])[0]
                assert label['private_cards']==h
                assert all(label[k]==row[k] for k in ('wins','ties','losses'));checks+=1
    # The explicit player-swap fixture uses reversed outcomes, not reused roles.
    assert native[16]['private_cards']==native[0]['private_cards'][2:]+native[0]['private_cards'][:2]
    assert native[16]['wins']==native[0]['losses'] and native[16]['losses']==native[0]['wins']
    batch=cache.batch(base);cache.check_batch(batch);bp=put('batch.json',batch)
    qp=STORE/'queries.json';up=STORE/'updates.json'
    def invoke(mode,policy,destination):
        assert idle() and time.monotonic()-started<120
        done=subprocess.run([str(exe),mode,str(context),str(bp),str(policy),str(destination)],cwd=ROOT,
            capture_output=True,text=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
        assert done.returncode==0,done.stderr[-2000:];artifacts[str(destination)]=sha(destination)
    invoke('queries','-',qp);q=json.loads(qp.read_text());p=np.zeros((len(q['observations']),4))
    for i,o in enumerate(q['observations']):p[i,:o['n']]=1/o['n']
    pp=put('policies.json',policy_document(q,p));invoke('verify',pp,up);u=json.loads(up.read_text())
    def fresh():return [PhysicalReservoir(17,i,921+i,q['context_source']) for i in (0,1)]
    actual=fresh();expected=fresh();counts=ingest(q,u,actual,1,cache)
    oracle=[0,0]
    for i,player,tag,values in u['records']:
        if tag>0:expected[player].add(q['observations'][i],values,1);oracle[player]+=1
    assert oracle==counts
    for a,b in zip(actual,expected):
        assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
        for key in ('keys','active','arity','values','iterations'):assert np.array_equal(getattr(a,key),getattr(b,key))
    def reject(fn):
        nonlocal failures
        try:fn()
        except (ValueError,KeyError,TypeError):failures+=1
        else:raise AssertionError('Malformed input accepted')
    reject(lambda:AllinCache(cp,'0'*64))
    reject(lambda:cache.batch(batch))
    absent=next(list(h) for h in itertools.combinations(range(12),4) if canonical(list(h)) not in cache.rows)
    reject(lambda:cache.labels([absent+[c for c in range(52) if c not in absent][:5]]))
    for transform in [lambda b:b.update(format=2),lambda b:b.update(allin_cache_sha256='wrong'),
        lambda b:b['allin_counts'][0].update(wins=b['allin_counts'][0]['wins']+1),
        lambda b:b['deals'][0].__setitem__(4,b['deals'][0][0])]:
        b=copy.deepcopy(batch);transform(b);reject(lambda:cache.check_batch(b))
    reject(lambda:policy_document(dict(q,format=2),p))
    invalid=p.copy();invalid[0,0]=-1;reject(lambda:policy_document(q,invalid))
    reject(lambda:legacy_ingest(q,u,fresh(),1))
    for change in [dict(format=2),dict(maximum_cashflow_error=1.),dict(verified_cashflow_traversals=0),
                   dict(batch_id='wrong'),dict(policies_frozen_across_updater_passes=False)]:
        target=fresh();bad=dict(u,**change)
        reject(lambda:ingest(q,bad,target,1,cache));assert all(r.seen==0 for r in target)
    bad=copy.deepcopy(u);bad['records'][-1][2]=99;target=fresh()
    reject(lambda:ingest(q,bad,target,1,cache));assert all(r.seen==0 for r in target)
    for path,h in reg['inputs'].items():assert sha(path)==h,path
    result=dict(passed=True,registration_sha256=sha(rp),artifacts=artifacts,
        role_preserving_label_checks=checks,rejected_inputs=failures,positive_records=counts,
        reservoir_arrays_and_rng_exact=True,verified_native_traversals=u['verified_cashflow_traversals'],
        seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,scope=reg['scope'])
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))


if __name__=='__main__':main()
