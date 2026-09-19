"""LP bounds on AA value against near-best LJ all-in responses."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from scipy.optimize import linprog
import aa_joint_response_study as t
import conditional_hu_audit as c


def main():
    t.checked();data=t.s.read(c.OUT/'subtree.json');g=c.Game(data,True)
    p={int(i):np.array(v) for i,v in t.s.read(c.OUT/'compatible_fresh.json')['records'][-1]['policy'].items()}
    fixtures=t.s.read(t.OUT/'fixtures.json');aa=fixtures['labels'].index('AA');rows=[]
    raw=g.payoffs[1,11]-g.payoffs[1,10]
    base=float(g.payoffs[0,10][aa].sum()+6.)
    delta=g.payoffs[0,11][aa]-g.payoffs[0,10][aa]
    for case in fixtures['cases']:
        reach=p[0][3].copy();reach[aa]=1-case['q']
        gain=raw@reach;probability=float(g.prior[0]@reach)
        weighted=g.prior[1]*gain/probability
        # Loss = sum(max(weighted gain,0)) - weighted gain @ call policy.
        best=(gain>0).astype(float)
        costs=abs(weighted);change=delta*(1-2*best)
        best_value=float(base+delta@best)
        assert abs(base+delta@best-case['jam_value_bb'])<1e-8
        for epsilon in [0.,.0001,.001,.01]:
            endpoints=[]
            for sign in [1.,-1.]:
                bounds=[(0,0) if epsilon==0 and cost>0 else (0,1) for cost in costs]
                fit=linprog(sign*change,A_ub=costs[None,:],b_ub=[epsilon],
                    bounds=bounds,method='highs',
                    options=dict(primal_feasibility_tolerance=1e-9,dual_feasibility_tolerance=1e-9))
                assert fit.success,fit.message
                loss=float(costs@fit.x);assert -1e-8<=loss<=epsilon+1e-8
                endpoints.append(dict(aa_jam_value_bb=float(best_value+change@fit.x),lj_loss_bb=loss,
                    lj_calls=(best+(1-2*best)*fit.x).tolist()))
            rows.append(dict(q=case['q'],lj_loss_budget_bb=epsilon,minimum=endpoints[0],maximum=endpoints[1]))
            print(case['q'],epsilon,[round(e['aa_jam_value_bb'],5) for e in endpoints])
    paths=[t.OUT/'RESPONSE-ROBUSTNESS.md',t.s.ROOT/'tools/research/aa_response_robustness.py']
    t.s.write(t.OUT/'response-robustness.json',dict(results=rows,
        source_hashes={x.relative_to(t.s.ROOT).as_posix():t.s.sha(x) for x in paths},
        note='LP envelopes over near-best all-in responses; budget is conditional on reaching the jam, not per dealt hand. Numerical sensitivity, not statistical confidence.'))


if __name__=='__main__':main()
