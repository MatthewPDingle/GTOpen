"""Independent card-removal accounting for geometry-fitted weights; no strategy outcomes."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import integrated_coverage as c
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    freeze=read(OUT/'chance-weight-v1-freeze.json')
    for p,h in freeze['inputs'].items():assert sha(ROOT/p)==h,p
    result=read(OUT/'chance-weight-v1-result.json');assert result['geometry_gate_passed'] and not result['strategy_results_read']
    source=read(OUT/'expansion-train-112.json');candidate=read(OUT/'expansion-train-112-chance-weight-v1.json')
    assert [r['board'] for r in source['boards']]==[r['board'] for r in candidate['boards']]
    weights=np.array([r['weight'] for r in candidate['boards']]);assert np.array_equal(weights,result['weights'])
    def valid(w):return bool(np.all(np.isfinite(w)) and np.min(w)>=.25/112-1e-12 and np.max(w)<=4/112+1e-12 and abs(w.sum()-1)<1e-10)
    assert valid(weights)
    negative=weights.copy();negative[0]=-1.;assert not valid(negative)
    badsum=weights*1.01;assert not valid(badsum)
    nan=weights.copy();nan[0]=float('nan');assert not valid(nan)
    pop=read(c.s.OUT/'fixtures.json')['canonical_flops'];physical=set()
    for b,m in pop:
        orbit={tuple(sorted(c.cards(c.relabel(b,p)))) for p in c.PERMS}
        assert len(orbit)==m and not (orbit&physical);physical.update(orbit)
    assert physical==set(itertools.combinations(range(52),3))
    data=read(OUT.parent/'conditional-hu-20260919/subtree.json')
    w=np.array(data['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES];w/=w.max(1)[:,None];w[w<1e-5]=0
    cards=np.array(c.PAIRS);c1=cards[:,0];c2=cards[:,1]
    def mass(boardmask):
        # Total-minus-blocked-card formula, independently of the fitting script's pair matrix.
        legal=(c.MASKS&np.uint64(boardmask))==0;reach=w*legal[None,:];out=[]
        for p in range(2):
            opp=reach[1-p];bycard=np.bincount(c1,weights=opp,minlength=52)+np.bincount(c2,weights=opp,minlength=52)
            available=opp.sum()-bycard[c1]-bycard[c2]+opp
            assert available.min()>-1e-10
            out.append(np.bincount(c.CLASSES,weights=reach[p]*available,minlength=169))
        return np.array(out)
    normalizer=mass(0)[0].sum();cache={};chance={}
    for b,m in pop:
        cs=c.cards(b);ranks={v//4 for v in cs};suits={v%4 for v in cs}
        base=mass(sum(1<<v for v in cs))/normalizer
        sets=base[:,::14]*np.array([r in ranks for r in range(13)])[None,:]
        cache[b]=(base,sets)
        chance[b]=np.array([max(ranks)==r for r in range(13)]+[len(suits)==k for k in range(1,4)]+
            [len(ranks)==k for k in range(1,4)]+[r in ranks for r in range(13)],dtype=float)
    def aggregate(items):
        den=sum(m for b,m in items)
        return tuple(sum(cache[b][k]*m/den for b,m in items) for k in range(2))+(sum(chance[b]*m/den for b,m in items),)
    full=aggregate(pop);mask=full[0]>0;pairmask=full[0][:,::14]>0
    def metrics(ws):
        got=aggregate([(b['board'],float(weight)) for b,weight in zip(source['boards'],ws)])
        private=float(np.max(np.abs(got[0][mask]/full[0][mask]-1)))
        pair=float(np.max(np.abs(got[1][pairmask]/got[0][:,::14][pairmask]-full[1][pairmask]/full[0][:,::14][pairmask]))*100)
        chance_error=float(np.max(np.abs(got[2]-full[2]))*100)
        return dict(private_class_max_relative_error=private,pair_opportunity_max_error_percentage_points=pair,
            chance_max_error_percentage_points=chance_error,effective_sample_size=float(1/(ws@ws)))
    baseline=metrics(np.ones(112)/112);verified=metrics(weights)
    for name,actual in [('before',baseline),('after',verified)]:
        for k,v in actual.items():assert abs(v-result[name][k])<1e-9,(name,k,v,result[name][k])
    assert verified['private_class_max_relative_error']<=.05 and verified['pair_opportunity_max_error_percentage_points']<=2
    assert verified['chance_max_error_percentage_points']<=3 and verified['effective_sample_size']>=.6*112
    swapped=metrics(weights[::-1])
    assert max(abs(swapped[k]-verified[k]) for k in verified)>1e-3,'Board/weight scrambling must be detectable'
    review=dict(passed=True,full_physical_flops_verified=len(physical),independent_formula='Opponent total minus each blocked card plus same-combo correction',
        before=baseline,after=verified,negative_controls=['negative weight','wrong total weight','NaN weight','board/weight scrambling'],
        unsupported_features=result['unsupported_features'],strategy_results_read=False,poker_accuracy_improvement_proven=False,
        limitation='Matches selected chance moments only. Missing trips/very-low-high-card boards cannot be created by weighting. Fresh reserved95 is unchanged and is not a full-population metric.',
        inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),OUT/'chance-weight-v1-freeze.json',OUT/'chance-weight-v1-result.json',OUT/'expansion-train-112-chance-weight-v1.json']})
    with (OUT/'chance-weight-v1-review.json').open('x') as f:json.dump(review,f,indent=2)
    print(json.dumps(review,indent=2))
if __name__=='__main__':main()
