"""Verify unperturbed full checks and conditional gates for exploration trials."""
from check_joint import *
from check_pair_control import near
from check_root_repair import checked_local


def case(name,seed,enabled,seats,every):
    r=read(name+'-result.json');p=read(name+'-exit.json')
    require(p['returncode']==0 and p['reason'] is None,'Incomplete run')
    require(p['environment_overrides']==({'CONVERGENCE_OPPONENT_EXPLORATION':'1'} if enabled else {}),'Wrong controls')
    require(r['seed']==seed and r['schedule']=='gamma15' and r['samples']==64,'Wrong experiment')
    require(r['target']==.005 and r['check_policy']=='fixed' and r['roundtrip_exact'],'Changed accuracy or save failure')
    require(r['research_restart'] is None and not r['normalized_regret'] and r['pair_control_extra_bytes'] is None
            and r['control_variate']['refresh_interval'] is None,'Combined experiment')
    if enabled:
        require(len(r['opponent_exploration'])==2 and r['opponent_exploration'][1]==250,'Wrong decay')
        near(r['opponent_exploration'][0],.01,1e-8)
    else:require(r['opponent_exploration'] is None,'Exploratory control')
    require([c['iteration'] for c in r['checks']]==list(range(every,r['iteration']+1,every)),'Missing accuracy checks')
    streak=0
    for c in r['checks']:
        require(c['full_reference_samples']==1024 and len(c['gaps'])==len(c['evs'])==seats,'Wrong evaluation scope')
        require(all(math.isfinite(x) and x>=0 for x in c['gaps']),'Invalid gaps')
        require(all(math.isfinite(x) for x in c['evs']),'Invalid EV')
        near(sum(c['gaps']),c['gap'])
        eligible=not enabled or c['iteration']>250
        streak=streak+1 if eligible and sum(c['gaps'])<=.005 else 0
        require(c['consecutive_passes']==streak,'Convergence counted during exploration')
    require(r['converged_twice'] is (streak>=2),'Wrong convergence flag')
    require(math.isfinite(r['total_seconds']) and r['total_seconds']>0,'Invalid timing')
    return r,p


def verify():
    for name in ('tests','build'):
        p=read(f'exploration-{name}-v1-exit.json')
        require(p['returncode']==0 and p['reason'] is None,'Unfinished prerequisite')
    rows=[];hashes=set()
    for seed in (42,314159):
        pair=[]
        for enabled in (0,1):
            r,p=case(f'exploration-six-{seed}-{enabled}-v1',seed,enabled,6,25)
            require(r['nodes']==23038,'Wrong small fixture');hashes.add(p['exe_sha256']);pair.append(r)
        rows.append(dict(seed=seed,passed=all(r['converged_twice'] for r in pair) and pair[1]['total_seconds']<=1.25*pair[0]['total_seconds'],
                         iterations=[r['iteration'] for r in pair],seconds=[r['total_seconds'] for r in pair],
                         gaps=[r['checks'][-1]['gap'] for r in pair]))
    require(len(hashes)==1,'Different executable controls')
    require(rows==read('exploration-screen-v1.json'),'Wrong registered screen')
    result=dict(evidence_verified=True,screen_pass=all(r['passed'] for r in rows),screen=rows,large=None)
    paths=json.loads((HERE/'exploration-diagnostic-paths.json').read_text())
    historical=json.loads((HERE.parent/'05-preflop-convergence-20260911/raw/six-s64-a-local-v3.json').read_text())
    require(paths==[r['candidate']['path'] for r in historical['rows']],'Post-hoc path selection')
    diagnostic=[]
    for seed in (42,314159):
        for enabled in (0,1):
            name=f'exploration-six-{seed}-{enabled}-v1-local'
            if not (RAW/(name+'.json')).exists():continue
            audit=read(name+'.json');ap=read(name+'-exit.json')
            require(ap['returncode']==0 and ap['reason'] is None,'Incomplete small conditional audit')
            passed=checked_local(audit['rows'],paths)
            diagnostic.append(dict(seed=seed,exploration=bool(enabled),conditional_passes=passed,total=len(paths),
                worst_relevant_bad_action_probabilities=[r['candidate'].get('worst_relevant_probability_on_strongly_inferior_actions') for r in audit['rows']]))
    require(len(diagnostic) in (0,4),'Partial post-screen diagnostics')
    result['conditional_diagnostic']=diagnostic
    if (RAW/'exploration-eight-42-v1-result.json').exists():
        r,p=case('exploration-eight-42-v1',42,True,8,50)
        require(p['exe_sha256'] in hashes and r['nodes']==1567754,'Different large implementation/fixture')
        audit=read('exploration-eight-42-v1-broad.json');ap=read('exploration-eight-42-v1-broad-exit.json')
        require(ap['returncode']==0 and ap['reason'] is None,'Incomplete conditional audit')
        paths=json.loads((HERE/'broad-paths.json').read_text());require(len(paths)==27,'Changed path coverage')
        passed=checked_local(audit['rows'],paths)
        result['large']=dict(iterations=r['iteration'],seconds=r['total_seconds'],global_gap=r['checks'][-1]['gap'],
                             global_pass=r['converged_twice'],conditional_passes=passed,conditional_total=27,
                             initial_qualification_pass=r['converged_twice'] and passed==27)
    return result


if __name__=='__main__':print(json.dumps(verify(),indent=2))
