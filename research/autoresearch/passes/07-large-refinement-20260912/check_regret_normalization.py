"""Validate the completed GPU learning-rate screen, including rejected runs."""
from check_joint import *

def verify():
    rows=[]
    for seed in (42,314159):
        pair=[]
        for enabled in (0,1):
            name=f'normalized-regret-six-{seed}-{enabled}-v1'
            result=read(name+'-result.json');process=read(name+'-exit.json')
            require(process['returncode']==0 and process['reason'] is None,'Incomplete process')
            require(result['normalized_regret'] is bool(enabled) and result['schedule']=='gamma15'
                and result['samples']==64 and result['seed']==seed,'Wrong optimizer configuration')
            require(result['target']==0.005 and result['roundtrip_exact'],'Changed target or roundtrip failure')
            require(result['research_restart'] is None and result['control_variate']['refresh_interval'] is None,
                'Unexpected combined experiment')
            streak=0
            for check in result['checks']:
                require(check['full_reference_samples']==1024,'Sampled accuracy check')
                gaps=check['gaps'];require(len(gaps)==6 and all(math.isfinite(g) and g>=0 for g in gaps),'Invalid gaps')
                require(abs(sum(gaps)-check['gap'])<1e-10,'Incorrect full global gap')
                streak=streak+1 if sum(gaps)<=0.005 else 0
                require(streak==check['consecutive_passes'],'Incorrect consecutive pass count')
            require(result['converged_twice'] is (streak>=2),'Incorrect convergence flag')
            pair.append(result)
        passed=pair[0]['converged_twice'] and pair[1]['converged_twice'] and pair[1]['total_seconds']<=2*pair[0]['total_seconds']
        rows.append(dict(seed=seed,passed=passed,baseline_iterations=pair[0]['iteration'],candidate_iterations=pair[1]['iteration'],
            baseline_seconds=pair[0]['total_seconds'],candidate_seconds=pair[1]['total_seconds'],
            baseline_gap=pair[0]['checks'][-1]['gap'],candidate_gap=pair[1]['checks'][-1]['gap']))
    recorded=read('normalized-regret-screen-v1.json')
    require([(r['seed'],r['passed']) for r in recorded]==[(r['seed'],r['passed']) for r in rows],'Wrong screen decision')
    return rows

if __name__=='__main__':
    rows=verify();print(json.dumps(rows,indent=2))
    sys.exit(0 if all(row['passed'] for row in rows) else 1)
