"""Independently recompute recorded joint-run gates; no solver or live writes."""
import json, math, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE/'raw'

def require(condition, message):
    if not condition: raise ValueError(message)

def read(name):
    return json.loads((RAW/name).read_text())

def local(rows, expected):
    candidates=[r['candidate'] for r in rows]
    require([c['path'] for c in candidates]==expected, 'Wrong path coverage/order')
    passed=0
    for c in candidates:
        require(c['status']=='evaluated' and c['conditioned_before_evaluation'] is True,
                'Missing conditioned evaluation')
        require(c['forced_or_frozen'] is False, 'Unexpected constrained node')
        hands=c['hands']
        require([h['class_index'] for h in hands]==list(range(169)), 'Wrong hand coverage')
        worst=0.0
        mass_sum=0.0
        for h in hands:
            q=h['action_values_bb']; p=h['candidate_probabilities']; m=h['conditional_hand_mass']
            require(len(q)==len(p)==len(c['actions']) and len(q)>0, 'Wrong action coverage')
            require(all(math.isfinite(v) for v in q+p+[m]), 'Nonfinite local values')
            require(m>=0 and all(0<=v<=1 for v in p) and abs(sum(p)-1)<=1e-5, 'Invalid probabilities')
            mass_sum+=m
            bad=sum(prob for value,prob in zip(q,p) if max(q)-value>0.1)
            require(abs(bad-h['probability_on_actions_losing_over_0_1bb'])<=1e-10, 'Bad-action mass mismatch')
            if m>=0.0025: worst=max(worst,bad)
        require(abs(mass_sum-1)<=1e-5, 'Invalid conditional hand distribution')
        require(abs(worst-c['worst_relevant_probability_on_strongly_inferior_actions'])<=1e-10,
                'Worst relevant mass mismatch')
        ok=worst<=0.1
        require(c['passes_local_tail_gate'] is ok, 'Incorrect recorded local pass flag')
        passed+=ok
    return passed

def case(variant, suffix):
    name=f'large-eight-{variant}-{suffix}'
    result=read(name+'-result.json'); process=read(name+'-exit.json')
    audit=read(name+'-broad.json'); audit_process=read(name+'-broad-exit.json')
    for p in (process,audit_process):
        require(p['returncode']==0 and p['reason'] is None, 'Incomplete/failed process')
    expected=json.loads((HERE/'broad-paths.json').read_text())
    require(result['normal_global_resume_supported'] is False, 'Missing local-age limitation')
    require(1<=len(result['cycles'])<=4, 'Wrong cycle coverage')
    if suffix=='joint-retained-v1':
        require(result['nodes']==1567754 and result['retained_ancestor_history'] is True,
                'Wrong experiment/fixture')
        require(result['original_global_age']==result['final_global_age']==1050, 'Global age changed')
        require(process['environment_overrides']=={'CONVERGENCE_RETAIN_ANCESTOR_HISTORY':'1'},
                'Wrong retained-history configuration')
    cycles=[]
    for i,c in enumerate(result['cycles']):
        require(c['cycle']==i and c['roundtrip_exact'] is True, 'Cycle or roundtrip mismatch')
        upstream=c['upstream']
        require(upstream['global_iteration_unchanged']==1050 and upstream['retained_and_fixed_arenas_unchanged'] is True,
                'Ancestor invariants unproven')
        if suffix=='joint-retained-v1':
            require(upstream['local_iteration_start']==25*i and upstream['local_iteration_end']==25*(i+1),
                    'Local history reset or wrong age')
        for u in c['updates']:
            r=u['refinement']
            require(r['fixed_policy_equivalence'] is True and r['global_iteration_unchanged']==1050
                    and r['normal_global_resume_supported'] is False, 'Compact invariants unproven')
        gaps=c['global_gaps']
        require(len(gaps)==8 and all(math.isfinite(g) and g>=0 for g in gaps), 'Invalid global gaps')
        count=local(c['rows'],expected)
        qualifies=sum(gaps)<=0.005 and count==27
        require(c['passed']==count and c['qualified'] is qualifies, 'Incorrect cycle qualification flag')
        cycles.append({'cycle':i,'global_gap':sum(gaps),'local_passes':count,'qualified':qualifies})
    final_count=local(audit['rows'],expected)
    require(final_count==cycles[-1]['local_passes'], 'Final independent audit disagrees')
    # The independent audit must contain the same final per-hand policy/Q data.
    require([r['candidate'] for r in audit['rows']]==[r['candidate'] for r in result['cycles'][-1]['rows']],
            'Final saved policy evaluation differs from final cycle')
    require(result['qualified'] is cycles[-1]['qualified'], 'Incorrect final qualification flag')
    return {'variant':variant,'seconds':process['seconds'],'cycles':cycles,'qualified':cycles[-1]['qualified']}

if __name__=='__main__':
    suffix=sys.argv[1] if len(sys.argv)==2 else 'joint-retained-v1'
    require(suffix in ('joint-v1','joint-retained-v1'), 'Unknown experiment')
    results=[]
    for variant in ('sampled','native'):
        try: results.append(case(variant,suffix))
        except Exception as error: results.append({'variant':variant,'qualified':False,'error':str(error)})
    success=all(r['qualified'] for r in results)
    print(json.dumps({'scope':'Recorded canonical eight-player fixture and 27 paths; not deployment approval',
        'all_qualified':success,'results':results},indent=2))
    sys.exit(0 if success else 1)
