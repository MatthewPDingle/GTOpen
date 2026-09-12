"""Verify coverage, unit factors, tolerances and the policy-floor counterexample."""
import struct
from check_joint import *


def f32(x):return struct.unpack('f',struct.pack('f',x))[0]


def verify():
    p=read('history-units-tests-v2-exit.json')
    require(p['returncode']==0 and p['reason'] is None,'Incomplete unit tests')
    rows=[];floors=[]
    for line in (RAW/'history-units-tests-v2.log').read_text().splitlines():
        if 'HISTORY_UNITS ' in line:rows.append(json.loads(line.split('HISTORY_UNITS ',1)[1]))
        if 'HISTORY_FLOOR ' in line:floors.append(json.loads(line.split('HISTORY_FLOOR ',1)[1]))
    cases=[[f32(x) for x in masses] for masses in ([.03125,.125,.5,.25],[.037,.173,.61,.83])]
    require([(r['calibrated'],r['incoming_masses']) for r in rows]==[(c,m) for c in (False,True) for m in cases],'Wrong case coverage')
    for r in rows:
        factors=[]
        for p in range(4):
            value=1.
            for q,m in enumerate(r['incoming_masses']):
                if q!=p:value=f32(value*m)
            factors.append(value)
        require(factors==r['counterfactual_factors'],'Wrong counterfactual units')
        require(r['nodes']==526 and r['levels']==11,'Wrong fixture/depth coverage')
        require(r['action_values_checked']==4*(r['nodes']-1)*169,'Incomplete child action-value coverage')
        require(r['learning_entries_checked']==64727 and r['folded_leaf_visits']==1100,'Missing update or folded-seat coverage')
        for key,limit in [('worst_conditional_value_error_bb',.0002),('worst_conditional_regret_increment_error_bb',.0002),('worst_average_increment_error',.000002)]:
            require(math.isfinite(r[key]) and 0<=r[key]<limit,'Unit conversion exceeds registered tolerance')
        require(r['fixed_and_other_actor_histories_unchanged'] is True,'History preservation failed')
    require([r['mode'] for r in floors]==[0,1],'Missing regret/average floor cases')
    for r in floors:
        require(r['actions']==3 and r['history_scale']==.001,'Wrong counterexample')
        require(r['before_probability']==1 and abs(r['after_probability']-1/3)<1e-6,'Missing policy change')
        require(r['conversion_must_not_claim_policy_preservation'] is True,'Unsafe conversion claim')
    return dict(evidence_verified=True,cases=rows,policy_floor_counterexamples=floors,
                resume_qualified=False,scope='Numerical unit identities on explicit small GPU fixtures; no continuation algorithm or timing claim')


if __name__=='__main__':print(json.dumps(verify(),indent=2))
