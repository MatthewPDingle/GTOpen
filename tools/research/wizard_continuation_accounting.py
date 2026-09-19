"""Isolate physical-card compatibility inside the unchanged fast formula."""
import numpy as np
import wizard_continuation_study as s


def audit():
    fixtures=s.read(s.OUT/'fixtures.json');case,=fixtures['cases']
    pairs=[(a,b) for a in range(52) for b in range(a+1,52)]
    masks=np.array([(1<<a)|(1<<b) for a,b in pairs],dtype=np.uint64)
    classes=np.array([max(a//4,b//4)*13+min(a//4,b//4) if a%4==b%4 or a//4==b//4 else min(a//4,b//4)*13+max(a//4,b//4) for a,b in pairs])
    counts=np.zeros((169,169));a,b=np.where((masks[:,None]&masks[None,:])==0)
    np.add.at(counts,(classes[a],classes[b]),1)
    assert counts.sum()==1326*1225 and np.array_equal(counts,counts.T)
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    base=np.array(s.read(s.ROOT/'cache/realization_fit.json')['class_base'])
    x=eq*base[:,None]*.92;y=(1-eq)*base[None,:]*1.08
    relative=x/np.maximum(x+y,1e-12);blend=min(case['stack']/case['pot']/8,1)
    net=case['pot']-min(case['pot']*.04,6)
    pair_value=net*(eq+blend*(relative-eq))
    w=np.array(case['weights'])
    masses=counts*w[0][:,None]*w[1][None,:]
    oop=counts*w[1][None,:];ip=counts*w[0][:,None]
    values=(oop*pair_value).sum(axis=1)/oop.sum(axis=1)
    opposite=(ip*(net-pair_value)).sum(axis=0)/ip.sum(axis=0)
    mean=(masses.sum(axis=1)@values+masses.sum(axis=0)@opposite)/masses.sum()
    assert abs(mean-net)<1e-8
    result=[]
    for i,h in enumerate(case['balanced']['hands'][0]):
        if h['hand'] in fixtures['probes']:
            result.append(dict(hand=h['hand'],independent_fast_bb=h['value_bb'],compatible_fast_bb=float(values[i]),change_bb=float(values[i]-h['value_bb'])))
    s.write(s.OUT/'card-compatibility-audit.json',dict(results=result,range_net_value_bb=float(mean),
        source_hashes={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in [s.OUT/'fixtures.json',s.ROOT/'cache/preflop_eq169.bin',s.ROOT/'cache/realization_fit.json']},
        note='Changes only compatible two-player card weighting inside the same fast formula. Folded-player card removal remains absent. Cached class equities remain sampled.'))
    for r in result:print(r['hand'],f"{r['change_bb']:+.4f}bb")


if __name__=='__main__':audit()
