"""Separate pure-plan verification of the 12-node conditional game results."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import conditional_hu_audit as study
from wizard_continuation_study import read,write


def check(game,policy):
    # UTG plans: fold, call, 4bet/fold, 4bet/call, jam.
    # LJ plans: one of fold/call/jam versus 4bet AND fold/call versus jam.
    # This enumerates full contingent plans, without the training traversal or
    # its best-response recursion. Correlation between LJ's mutually exclusive
    # decisions is irrelevant to outcomes; their product is a valid plan mix.
    x=np.array([policy[0][0],policy[0][1],policy[0][2]*policy[6][0],
        policy[0][2]*policy[6][1],policy[0][3]])
    y=np.array([policy[3][a]*policy[9][b] for a in range(3) for b in range(2)])
    assert np.max(abs(x.sum(0)-1))<1e-10 and np.max(abs(y.sum(0)-1))<1e-10
    values=[np.zeros_like(x),np.zeros_like(y)]
    rake=mass=0.
    for a in range(5):
        for b in range(6):
            reply=b//2;calljam=b%2
            if a==0:terminal=1
            elif a==1:terminal=2
            elif a==4:terminal=10+calljam
            elif reply==0:terminal=4
            elif reply==1:terminal=5
            else:terminal=7+(a==3)
            u=game.utilities[0,terminal]*game.joint
            v=game.utilities[1,terminal].T*game.joint
            values[0][a]+=u@y[b]
            values[1][b]+=v.T@x[a]
            probability=float(x[a]@game.joint@y[b]);mass+=probability
            rake+=probability*game.rakes[terminal]
    ev=[float((values[0]*x).sum()),float((values[1]*y).sum())]
    br=[float(v.max(0).sum()) for v in values]
    gaps=np.array(br)-ev
    recursive=game.evaluate(policy)
    error=max(abs(np.array(ev)-recursive['evs']).max(),abs(gaps-recursive['gaps']).max(),
        abs(rake-recursive['expected_rake']),abs(mass-1))
    assert error<1e-8,error
    return dict(evs=ev,gaps=gaps.tolist(),gap_total=float(gaps.sum()),recursive_difference=float(error))


def main():
    manifest=study.frozen();data=read(study.OUT/'subtree.json');rows=[]
    for model in ['independent','compatible']:
        g=study.Game(data,model=='compatible')
        rows.append(dict(chance=model,policy='saved',**check(g,g.saved)))
        for job in manifest['jobs']:
            result=read(study.OUT/(job+'.json'))
            for record in result['records']:
                policy={int(i):np.array(v) for i,v in record['policy'].items()}
                rows.append(dict(chance=model,policy=job,iteration=record['iteration'],**check(g,policy)))
    write(study.OUT/'pure-plan-verification.json',dict(passed=True,results=rows,
        note='Exhaustive 5 by 6 contingent-plan payoff enumeration checks both player values and best responses independently of CFR traversal.'))
    print('Verified',len(rows),'policy/model combinations; max error',max(r['recursive_difference'] for r in rows))


if __name__=='__main__':main()
