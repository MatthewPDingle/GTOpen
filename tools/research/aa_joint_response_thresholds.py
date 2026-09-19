"""Exact affine all-in response thresholds for the restricted AA experiment."""
import numpy as np
import aa_joint_response_study as t
import conditional_hu_audit as c


def main():
    t.checked();data=t.s.read(c.OUT/'subtree.json');g=c.Game(data,True)
    policy={int(i):np.array(v) for i,v in t.s.read(c.OUT/'compatible_fresh.json')['records'][-1]['policy'].items()}
    labels=t.s.read(t.OUT/'fixtures.json')['labels'];aa=labels.index('AA')
    # g.payoffs[1,*] use the same fixed compatible root conditional chance.
    difference=g.payoffs[1,11]-g.payoffs[1,10]
    jam=policy[0][3].copy();jam[aa]=1.
    intercept=difference@jam;slope=-difference[:,aa]
    aa_fold=g.payoffs[0,10][aa];aa_call=g.payoffs[0,11][aa]
    delta=aa_call-aa_fold
    def value(q):
        take=(intercept+slope*q)>0
        return float(aa_fold.sum()+delta@take+6.)
    thresholds=[]
    for h in range(169):
        if slope[h]==0:continue
        q=-intercept[h]/slope[h]
        if not 0<=q<=1:continue
        a=intercept+slope*q
        tied=abs(a)<1e-12
        take=a>0;take[tied]=False
        base=aa_fold.sum()+delta@take+6.
        thresholds.append(dict(hand=labels[h],q=float(q),lj_incoming_probability=float(g.prior[1,h]),
            aa_jam_value_interval_at_tie=[float(base+np.minimum(delta[tied],0).sum()),
                float(base+np.maximum(delta[tied],0).sum())],
            aa_value_jump_if_lj_calls=float(delta[h])))
    thresholds.sort(key=lambda r:r['q'])
    # Verify affine reconstruction and the standalone AA payoff calculation
    # at every registered range state against the separately prepared values.
    for case in t.s.read(t.OUT/'fixtures.json')['cases']:
        assert abs(value(case['q'])-case['jam_value_bb'])<1e-8
    qgrid=sorted(set(np.linspace(0,1,101).tolist()+[r['q'] for r in thresholds]))
    out=dict(thresholds=thresholds,curve=[dict(q=q,aa_jam_bb=value(q)) for q in qgrid],
        note='Conditional sampled-equity model, not exact real-poker thresholds. Very near-zero crossings are sensitive to starting-policy and equity-cache error. At a tie an opponent best response is a set, not a unique pure action. The postflop bootstrap does not quantify these uncertainties.')
    t.s.write(t.OUT/'response-thresholds.json',out)
    print('First ten thresholds:',thresholds[:10])


if __name__=='__main__':main()
