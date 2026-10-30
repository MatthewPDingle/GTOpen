"""Fit a separate positive-weight card-geometry candidate without strategic outcomes."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import scipy
from scipy.optimize import minimize
import integrated_coverage as c

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (OUT/'chance-weight-v1-freeze.json').exists()
    count=json.loads((OUT/'expansion-capacity-v1-selection.json').read_text())['selected_boards'];assert count==112
    fixture=c.s.OUT/'fixtures.json';sub=OUT.parent/'conditional-hu-20260919/subtree.json'
    source=OUT/f'expansion-train-{count}.json'
    files=[Path(__file__),fixture,sub,source,OUT/'CHANCE-WEIGHT-PROTOCOL.md',OUT/'expansion-registration-freeze.json',
        OUT/'expansion-capacity-v1-selection.json',ROOT/'tools/research/integrated_coverage.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in files}
    with (OUT/'chance-weight-v1-freeze.json').open('x') as f:json.dump(dict(inputs=frozen,python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
        strategy_results_read=False,minimum_relative_weight=0.25,maximum_relative_weight=4,ridge=0.00001,ftol=1e-12,maxiter=2000),f,indent=2)
    pop=json.loads(fixture.read_text())['canonical_flops'];data=json.loads(sub.read_text());manifest=json.loads(source.read_text())
    w=np.array(data['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES];w/=w.max(1)[:,None];w[w<1e-5]=0
    ix=[np.flatnonzero(w[p]) for p in range(2)];masks=[c.MASKS[i] for i in ix];classes=[c.CLASSES[i] for i in ix]
    support=[sorted(set(int(x) for x in cl)) for cl in classes];pairs=[[cl for cl in sp if cl%14==0] for sp in support]
    joint=w[0,ix[0]][:,None]*w[1,ix[1]][None,:]*((masks[0][:,None]&masks[1][None,:])==0);normalizer=joint.sum()
    labels=[];groups=[];pair_links=[];private_index={}
    for p in range(2):
        for cl in support[p]:
            private_index[p,cl]=len(labels);labels.append(f'private-p{p}-class{cl}');groups.append(f'private-p{p}')
    for p in range(2):
        for cl in pairs[p]:
            pair_links.append((len(labels),private_index[p,cl],p,cl));labels.append(f'set-p{p}-class{cl}');groups.append('pair-sets')
    for r in range(13):labels.append(f'high-rank-{r}');groups.append('high-card')
    for k in range(1,4):labels.append(f'suit-count-{k}');groups.append('suits')
    for k in range(1,4):labels.append(f'distinct-ranks-{k}');groups.append('pairing')
    for r in range(13):labels.append(f'contains-rank-{r}');groups.append('rank-presence')
    rows=[]
    for board,_ in pop:
        cards=c.cards(board);ranks={v//4 for v in cards};suits={v%4 for v in cards};mask=np.uint64(sum(1<<v for v in cards))
        legal=[(m&mask)==0 for m in masks];board_joint=joint*legal[0][:,None]*legal[1][None,:]
        mass=[np.bincount(classes[p],weights=board_joint.sum(axis=1-p),minlength=169)/normalizer for p in range(2)]
        row=[mass[p][cl] for p in range(2) for cl in support[p]]
        row += [mass[p][cl]*(cl//14 in ranks) for p in range(2) for cl in pairs[p]]
        row += [float(max(ranks)==r) for r in range(13)]+[float(len(suits)==k) for k in range(1,4)]
        row += [float(len(ranks)==k) for k in range(1,4)]+[float(r in ranks) for r in range(13)]
        assert len(row)==len(labels);rows.append(row)
    matrix=np.asarray(rows);physical=np.asarray([m for b,m in pop],dtype=float);physical/=physical.sum();target=physical@matrix
    lookup={b:i for i,(b,m) in enumerate(pop)};sample=matrix[[lookup[b['board']] for b in manifest['boards']]]
    scale=np.ones(len(labels))
    for (p,cl),j in private_index.items():scale[j]=target[j]
    for j,d,p,cl in pair_links:scale[j]=target[d]
    assert np.all(scale>0)
    group_scale=np.array([1/(groups.count(g)*len(set(groups))) for g in groups])
    a=(sample/scale).T/count;b=target/scale
    def fun(x):
        residual=a@x-b
        return float(np.sum(group_scale*residual**2)+0.00001*np.mean((x-1)**2))
    def jac(x):return 2*a.T@(group_scale*(a@x-b))+0.00002*(x-1)/count
    # An independent centered finite difference guards the analytic gradient before fitting.
    probe=np.linspace(.7,1.3,count);direction=np.sin(np.arange(count));eps=1e-5
    fd=(fun(probe+eps*direction)-fun(probe-eps*direction))/(2*eps)
    assert abs(fd-float(jac(probe)@direction))<1e-8
    fit=minimize(fun,np.ones(count),jac=jac,method='SLSQP',bounds=[(.25,4.)]*count,
        constraints=[dict(type='eq',fun=lambda x:x.sum()-count,jac=lambda x:np.ones(count))],
        options=dict(ftol=1e-12,maxiter=2000))
    weights=fit.x/count
    def metrics(weights):
        moments=weights@sample
        private=max(abs(moments[j]/target[j]-1) for j in private_index.values())
        set_error=max(abs(moments[j]/moments[d]-target[j]/target[d]) for j,d,p,cl in pair_links)
        chance=max(abs(moments[j]-target[j]) for j,g in enumerate(groups) if g not in ['private-p0','private-p1','pair-sets'])
        return dict(private_class_max_relative_error=float(private),pair_opportunity_max_error_percentage_points=float(set_error*100),
            chance_max_error_percentage_points=float(chance*100),effective_sample_size=float(1/np.sum(weights**2)))
    before=metrics(np.ones(count)/count);after=metrics(weights)
    passed=bool(fit.success and np.all(np.isfinite(weights)) and abs(weights.sum()-1)<1e-10 and weights.min()>=.25/count-1e-12
        and weights.max()<=4/count+1e-12 and after['effective_sample_size']>=.6*count and after['private_class_max_relative_error']<=.05
        and after['pair_opportunity_max_error_percentage_points']<=2 and after['chance_max_error_percentage_points']<=3)
    unsupported=[dict(feature=labels[j],target=float(target[j])) for j in range(len(labels)) if target[j]>0 and np.all(sample[:,j]==0)]
    result=dict(geometry_gate_passed=passed,optimizer_success=bool(fit.success),optimizer_message=str(fit.message),iterations=int(fit.nit),
        objective_before=fun(np.ones(count)),objective_after=fun(fit.x),before=before,after=after,
        unsupported_features=unsupported,minimum_weight_ratio=float(weights.min()*count),maximum_weight_ratio=float(weights.max()*count),
        strategy_results_read=False,accuracy_improvement_claim=False,weights=weights.tolist(),labels=labels,groups=groups,
        full_targets=target.tolist(),weighted_moments=(weights@sample).tolist())
    for p,h in frozen.items():assert sha(ROOT/p)==h,p
    with (OUT/'chance-weight-v1-result.json').open('x') as f:json.dump(result,f,indent=2)
    candidate=manifest|dict(purpose='Separate geometry-fitted weight candidate; original panel unchanged; not strategically validated.',geometry_gate_passed=passed,
        boards=[row|dict(weight=float(weight)) for row,weight in zip(manifest['boards'],weights)])
    with (OUT/'expansion-train-112-chance-weight-v1.json').open('x') as f:json.dump(candidate,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k not in ['weights','labels','groups','full_targets','weighted_moments']},indent=2))
if __name__=='__main__':main()
