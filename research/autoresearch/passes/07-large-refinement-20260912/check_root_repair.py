"""Recompute root-mixture construction, selection, and unchanged accuracy gates."""
from check_joint import *
import struct

def f32(x):
    return struct.unpack('f',struct.pack('f',x))[0]

def checked_local(rows, paths):
    require([r['candidate']['path'] for r in rows]==paths,'Wrong audit coverage')
    count=0
    for row,path in zip(rows,paths):
        if row['candidate']['status']=='unreachable_under_reference':
            require(row['candidate'].get('passes_local_tail_gate') is not True,'Unreachable path passed')
        else:
            count+=local([row],[path])
    return count

def case(variant):
    name=f'large-eight-{variant}-root-repair-v1'
    result=read(name+'-result.json');process=read(name+'-exit.json')
    audit=read(name+'-broad.json');audit_process=read(name+'-broad-exit.json')
    for p in (process,audit_process):
        require(p['returncode']==0 and p['reason'] is None,'Incomplete process')
    require(result['nodes']==1567754 and result['global_age']==1050,'Wrong fixture/age')
    require(result['nonroot_arenas_unchanged'] and result['roundtrip_exact'],'Preservation failure')
    require(result['normal_global_resume_supported'] is False,'Unsupported continuation claim')
    paths=json.loads((HERE/'broad-paths.json').read_text())
    root=result['root_values'];na=len(root['actions']);original=[0.]*(na*169);target=original.copy()
    require(root['path']==[] and root['forced_or_frozen'] is False,'Wrong root context')
    require([h['class_index'] for h in root['hands']]==list(range(169)),'Incomplete root hands')
    for h,hand in enumerate(root['hands']):
        q=hand['action_values_counterfactual_bb'];p=hand['average_probabilities']
        require(len(q)==len(p)==na and all(math.isfinite(v) for v in q+p),'Invalid root values')
        require(all(0<=v<=1 for v in p) and abs(sum(p)-1)<1e-6,'Invalid root probabilities')
        eligible=[a for a in range(na) if max(q)-q[a]<=1e-8];mass=sum(p[a] for a in eligible)
        for a in range(na):original[a*169+h]=p[a]
        for a in eligible:target[a*169+h]=f32(p[a]/mass if mass>1e-12 else 1/len(eligible))
    grid=[0.,0.0625,0.125,0.25,0.5,1.]
    candidates=result['candidates'];require([c['alpha'] for c in candidates]==grid,'Changed grid')
    actor=root['actor'];base_ev=candidates[0]['global_evs'][actor]
    predicted_gain=sum(hand['actor_reach']*sum(target[a*169+h]*hand['action_values_counterfactual_bb'][a]
        -original[a*169+h]*hand['action_values_counterfactual_bb'][a] for a in range(na))
        for h,hand in enumerate(root['hands']))
    summaries=[]
    for c,alpha in zip(candidates,grid):
        expected=[f32((1-alpha)*a+alpha*b) for a,b in zip(original,target)]
        for h in range(169):
            mass=sum(expected[a*169+h] for a in range(na))
            for a in range(na):expected[a*169+h]=f32(expected[a*169+h]/mass)
        require(len(c['root_policy'])==len(expected) and all(abs(a-b)<=1e-7 for a,b in zip(expected,c['root_policy'])),
            'Wrong root mixture')
        gaps=c['global_gaps'];require(len(gaps)==8 and all(math.isfinite(g) and g>=0 for g in gaps),'Invalid gaps')
        require(abs(c['global_evs'][actor]-base_ev-alpha*predicted_gain)<=1e-5,
            'Root actor EV does not match the predicted one-step improvement')
        passed=checked_local(c['rows'],paths);qualified=sum(gaps)<=0.005 and passed==27
        require(c['passed']==passed and c['qualified'] is qualified,'Incorrect candidate qualification')
        summaries.append(dict(alpha=alpha,gap=sum(gaps),passed=passed,qualified=qualified))
    selected=result['selected_index'];require(selected==min(range(6),key=lambda i:summaries[i]['gap']),'Wrong selection rule')
    final_passed=checked_local(audit['rows'],paths)
    require(final_passed==summaries[selected]['passed'],'Independent saved-file pass count differs')
    for actual,expected in zip(audit['rows'],candidates[selected]['rows']):
        actual=actual['candidate'];expected=expected['candidate']
        require(actual['status']==expected['status'],'Independent saved-file reach differs')
        if actual['status']=='evaluated':
            for a,b in zip(actual['hands'],expected['hands']):
                for key,tolerance in [('action_values_bb',1e-5),('candidate_probabilities',2e-6)]:
                    require(len(a[key])==len(b[key]) and all(abs(x-y)<=tolerance for x,y in zip(a[key],b[key])),
                        'Independent saved-file policy/value differs')
    final=result['final_global_gaps'];require(len(final)==8 and all(math.isfinite(g) and g>=0 for g in final),'Invalid final gaps')
    require(all(abs(a-b)<=1e-5 for a,b in zip(final,candidates[selected]['global_gaps'])),'Final full recheck differs')
    return dict(variant=variant,seconds=process['seconds'],candidates=summaries,selected_alpha=grid[selected],
        final_gap=sum(final),final_passed=final_passed,qualified=sum(final)<=0.005 and final_passed==27)

if __name__=='__main__':
    results=[]
    for variant in ('sampled','native'):
        try:results.append(case(variant))
        except Exception as error:results.append(dict(variant=variant,qualified=False,error=str(error)))
    print(json.dumps(dict(results=results,all_qualified=all(r['qualified'] for r in results)),indent=2))
    sys.exit(0 if all(r['qualified'] for r in results) else 1)
