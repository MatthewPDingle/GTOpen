"""Register board panels, audit suit orbits, and verify connected solves."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import collections
import hashlib
import itertools
import json
import sys
import numpy as np
import wizard_continuation_study as s

OUT=s.OUT.parent/'integrated-coverage-20260919'
EXE=s.ROOT/'target/release/examples/integrated_continuation_orbits.exe'
SEED='integrated-coverage-20260919-v1|'
PERMS=list(itertools.permutations(range(4)))
PAIRS=[(a,b) for a in range(52) for b in range(a+1,52)]
LOOKUP={v:i for i,v in enumerate(PAIRS)}
MASKS=np.array([(1<<a)|(1<<b) for a,b in PAIRS],dtype=np.uint64)
CLASSES=np.array([max(a//4,b//4)*13+min(a//4,b//4) if a%4==b%4 or a//4==b//4 else min(a//4,b//4)*13+max(a//4,b//4) for a,b in PAIRS])
COUNTS=np.bincount(CLASSES,minlength=169)
MAPS=np.array([[LOOKUP[tuple(sorted((a//4*4+p[a%4],b//4*4+p[b%4])))] for a,b in PAIRS] for p in PERMS])

def cards(board):return ['23456789TJQKA'.index(board[i])*4+'cdhs'.index(board[i+1]) for i in range(0,len(board),2)]
def relabel(board,p):return ''.join('23456789TJQKA'[c//4]+'cdhs'[p[c%4]] for c in cards(board))

def prepare():
    assert not (OUT/'freeze.json').exists()
    strata=collections.defaultdict(list)
    for board,iso in s.read(s.OUT/'fixtures.json')['canonical_flops']:
        cs=cards(board);key=('paired' if len({c//4 for c in cs})<3 else 'unpaired')+'/'+str(len({c%4 for c in cs}))
        strata[key].append((board,iso))
    assert len(strata)==5
    for v in strata.values():v.sort(key=lambda x:hashlib.sha256((SEED+x[0]).encode()).digest())
    base=dict(suit_orbits=True,bet_menu='50')
    manifests={}
    for name,indices in [('panel-a',[0]),('panel-b',[1]),('panel-ab',[0,1]),('reserved',[2,3])]:
        boards=[dict(board=values[i][0],weight=values[i][1]*len(values)/len(indices),stratum=k,iso_count=values[i][1],stratum_size=len(values))
                for k,values in sorted(strata.items()) for i in indices]
        manifests[name]=dict(**base,boards=boards,seed=SEED,reserved=name=='reserved')
    board='KhQd9d2c7s'
    manifests['orbit-river']=dict(**base,boards=[dict(board=board,weight=1.)])
    manifests['expanded-river']=dict(suit_orbits=False,bet_menu='50',boards=[dict(board=relabel(board,p),weight=1.) for p in PERMS])
    manifests['old-two-orbits']=dict(**base,boards=[dict(board=b,weight=1.) for b in ['KhQd9d','8c7c4h']])
    for name,m in manifests.items():s.write(OUT/(name+'.json'),m)
    inputs=[EXE,OUT/'PROTOCOL.md',s.ROOT/'crates/solver/examples/integrated_continuation_orbits.rs',s.OUT/'fixtures.json',s.OUT/'fold-history.json',s.ROOT/'tools/research/integrated_coverage.py']
    inputs+=[OUT/(n+'.json') for n in manifests]
    s.write(OUT/'freeze.json',dict(inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in inputs},panels=list(manifests)))
    print({k:[b['board'] for b in v['boards']] for k,v in manifests.items() if not k.startswith('expanded')})

def audit():
    f=s.read(OUT/'freeze.json')
    for path,digest in f['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    data=s.read(s.OUT.parent/'conditional-hu-20260919/subtree.json')
    w=np.array(data['incoming_class_mass'])[:,CLASSES]/COUNTS[CLASSES];w/=w.max(1)[:,None];w[w<1e-5]=0
    compatible=(MASKS[:,None]&MASKS[None,:])==0
    product=w[0,:,None]*w[1,None,:]
    full=compatible*product;full/=full.sum()
    prior={};rng=np.random.default_rng(902619191)
    errors=[]
    # Arbitrary continuation CFVs, including board-blocked holes: verifies
    # the actual vector projection, separately from any CFR implementation.
    for b in ['KhQd9d','8c7c4h','AsAd7c','Qc9c3c','KhQd9d2c7s']:
        legal=(MASKS&np.uint64(sum(1<<c for c in cards(b))))==0
        v=rng.normal(size=1326)*legal
        projected=np.bincount(CLASSES,weights=v,minlength=169)[CLASSES]/COUNTS[CLASSES]
        explicit=np.zeros(1326)
        for mapping in MAPS:explicit[mapping]+=v/24
        err=float(abs(projected-explicit).max());assert err<1e-14;errors.append(err)
    for name in ['old-two-orbits','panel-a','panel-b','panel-ab']:
        m=s.read(OUT/(name+'.json'));total=sum(b['weight'] for b in m['boards'])
        chance=np.zeros((1326,1326));distinct=set()
        for b in m['boards']:
            for p in PERMS:
                physical=relabel(b['board'],p);distinct.add(tuple(sorted(cards(physical))))
                legal=(MASKS&np.uint64(sum(1<<c for c in cards(physical))))==0
                chance+=legal[:,None]*legal[None,:]*b['weight']/total/24
        chance*=compatible*product;z=chance.sum();chance/=z
        marginal=chance.sum(1)
        cls=np.bincount(CLASSES,weights=marginal,minlength=169)
        row=dict(normalizer=float(z),physical_flops=len(distinct),joint_prior_tv=float(abs(chance-full).sum()/2),
            oop_class_prior_tv=float(abs(cls-np.bincount(CLASSES,weights=full.sum(1),minlength=169)).sum()/2))
        result=OUT/(name+'-result.json')
        if result.exists():
            r=s.read(result);assert r['manifest']==m
            assert abs(r['root_normalizer']/z-1)<1e-7
            for record in r['records']:
                e=record['evaluation'];sigma=np.array(e['preflop_policy'][0]);freq=sigma@marginal
                assert abs(freq-e['root_frequencies']).max()<1e-7
                assert abs(e['terminal_probability']-1)<1e-5 and e['conservation_error']<1e-4
                assert min(e['gaps'])>-1e-6
                for c in range(169):assert np.ptp(sigma[:,CLASSES==c],axis=1).max()<1e-12
            row['final']=r['records'][-1]
            row['final']={k:v for k,v in row['final'].items() if k!='evaluation'}|{k:r['records'][-1]['evaluation'][k] for k in ['gap_total','gaps','root_frequencies','expected_rake','conservation_error']}
        prior[name]=row
    comparison={}
    if (OUT/'orbit-river-result.json').exists() and (OUT/'expanded-river-result.json').exists():
        a=s.read(OUT/'orbit-river-result.json');b=s.read(OUT/'expanded-river-result.json')
        for x,y in zip(a['records'],b['records']):
            error=max(abs(np.array(x['evaluation'][k])-np.array(y['evaluation'][k])).max() for k in ['ev','gaps'])
            assert error<(0.002 if x['iteration']==1 else .02),(x['iteration'],error)
            comparison[x['iteration']]=float(error)
    s.write(OUT/'coverage-audit.json',dict(projection_max_error=max(errors),river_expansion_error=comparison,panels=prior))
    print(json.dumps(s.read(OUT/'coverage-audit.json'),indent=2))

if __name__=='__main__':{'prepare':prepare,'audit':audit}[sys.argv[1]]()
