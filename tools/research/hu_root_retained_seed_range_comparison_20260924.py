"""Descriptive comparison of both fixed training seeds, after endpoint audits."""
import json
import math
from pathlib import Path
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha,save

ACTIONS = ['fold','call','raise','jam']


def load(prefix):
    rp,pp,ap=[OUT/f'{prefix}-{s}.json' for s in ('registration','result','independent-review')]
    reg,result,audit=map(read,(rp,pp,ap))
    assert result['passed'] and audit['passed']
    assert result['registration_sha256']==audit['registration_sha256']==sha(rp)
    assert audit['result_sha256']==sha(pp)
    assert reg['count']==78 and not reg['control_only'] and not reg['quality_screen_applied']
    policy_path=Path(reg['store'])/'linear-policy.json'
    policy=read(policy_path)
    assert result['artifacts'][str(policy_path)]==sha(policy_path)
    assert policy['played_generations']==list(range(78)) and policy['excluded_generation']==78
    assert policy['weights']==[list(range(1,79)),list(range(1,79))]
    rows=result['pairings']['linear/linear']['bb_classes']
    assert [r['hand_class'] for r in rows]==list(range(169))
    assert all(r['baseline']==policy['root_probabilities'][i] for i,r in enumerate(rows))
    return policy,rows,{str(p):sha(p) for p in (rp,pp,ap,policy_path)}


def label(index):
    ranks='23456789TJQKA';row,col=divmod(index,13)
    if row==col:return ranks[row]*2
    return ranks[max(row,col)]+ranks[min(row,col)]+('s' if row>col else 'o')


def main():
    path=OUT/'root-retained-seed-range-comparison-v1-result.json'
    assert not path.exists()
    first,a,inputs=load('root-retained-exact-v1')
    second,b,more=load('root-retained-replication-exact-v1');inputs.update(more)
    assert first['context_sha256']==second['context_sha256']
    assert first['checkpoint']!=second['checkpoint']
    classes=[]
    for i,(x,y) in enumerate(zip(a,b)):
        mass=x['entry_probability'];assert abs(mass-y['entry_probability'])<1e-12
        old,new=x['baseline'],y['baseline']
        assert len(old)==len(new)==4 and min(old+new)>=0
        assert abs(sum(old)-1)<1e-12 and abs(sum(new)-1)<1e-12
        delta=[v-u for u,v in zip(old,new)]
        classes.append(dict(hand_class=i,hand=label(i),entry_mass=mass,
            first=old,replication=new,change=delta,total_variation=.5*sum(map(abs,delta))))
    assert abs(math.fsum(r['entry_mass'] for r in classes)-1)<1e-12
    def average(key,index):
        return math.fsum(r['entry_mass']*r[key][index] for r in classes)
    mixes={key:dict(zip(ACTIONS,[average(key,i) for i in range(4)]))
           for key in ('first','replication','change')}
    tv=math.fsum(r['entry_mass']*r['total_variation'] for r in classes)
    assert .5*sum(map(abs,mixes['change'].values()))<=tv+1e-12
    inputs[str(Path(__file__))]=sha(Path(__file__))
    plan=OUT/'ROOT-RETAINED-SEED-COMPARISON-PLAN.md';inputs[str(plan)]=sha(plan)
    for p,h in inputs.items():assert sha(p)==h,p
    save(path,dict(passed=True,inputs=inputs,primary='linear/linear, generations 0..77',
        root_action_mixes=mixes,entry_weighted_total_variation=tv,
        maximum_class_total_variation=max(r['total_variation'] for r in classes),
        classes=classes,production_modified=False,accuracy_qualified=False,
        scope='Descriptive BB initial-decision variation across two training seeds. Incoming mass includes opponent-range card removal. No confidence interval, causal algorithm comparison, full exploitability estimate, or validation of other scenarios.'))
    print(json.dumps(dict(root_action_mixes=mixes,entry_weighted_total_variation=tv)))


if __name__=='__main__':main()
