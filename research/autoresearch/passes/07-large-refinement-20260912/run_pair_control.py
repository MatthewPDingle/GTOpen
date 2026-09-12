"""Bounded-memory GPU CV numerical screen, then registered learning trials."""
from run07 import *
if __name__=='__main__':
    run('pair-control-tests-v1',['cargo','test','--release','-p','solver','--features','preflop-research',
        '--lib','pair_control_','--','--nocapture','--test-threads=1'],900)
    variance=[]
    for line in (RAW/'pair-control-tests-v1.log').read_text().splitlines():
        if 'PAIR_VARIANCE ' in line:variance.append(json.loads(line.split('PAIR_VARIANCE ',1)[1]))
    if [(v['players'],v['family']) for v in variance]!=[(n,f) for n in (3,4,6,8) for f in range(3)]:
        raise RuntimeError('Incomplete numerical variance coverage')
    pooled=sum(v['pooled_variance'][1] for v in variance)/sum(v['pooled_variance'][0] for v in variance)
    numerical_pass=pooled<=0.9 and all(v['ratio']<=1.25 for v in variance)
    (RAW/'pair-control-variance-v1.json').write_text(json.dumps(dict(pooled_ratio=pooled,passed=numerical_pass,fixtures=variance),indent=2)+'\n',encoding='utf-8',newline='\n')
    if not numerical_pass:
        print('Variance screen rejected; no learning trial',flush=True);sys.exit(0)
    run('pair-control-build-v1',['cargo','build','--release','-p','solver','--features','preflop-research',
        '--example','convergence_bench','--example','convergence_audit_paths'],600)
    exe=LAB/'target/release/examples/convergence_bench.exe'
    fixture=HERE.parent/'05-preflop-convergence-20260911/six-solver.json'
    screen=[]
    for seed in (42,314159):
        pair=[]
        for enabled in (False,True):
            name=f'pair-control-six-{seed}-{int(enabled)}-v1';out=LAB/'target/convergence'/name
            env={'CONVERGENCE_PAIR_CONTROL':'1'} if enabled else {}
            run(name,[exe,fixture,'gamma15','64',str(seed),'1000','25',out],600,[fixture],env)
            pair.append(json.loads((out/'result.json').read_text()))
            (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
        passed=all(d['converged_twice'] for d in pair) and pair[1]['total_seconds']<=1.25*pair[0]['total_seconds']
        screen.append(dict(seed=seed,passed=passed,baseline_seconds=pair[0]['total_seconds'],candidate_seconds=pair[1]['total_seconds']))
    (RAW/'pair-control-screen-v1.json').write_text(json.dumps(screen,indent=2)+'\n',encoding='utf-8',newline='\n')
    if not all(r['passed'] for r in screen):
        print('Learning screen rejected; no large trial',flush=True);sys.exit(0)
    fixture=LAB/'research/autoresearch/passes/03-preflop-20260910/user-session.json'
    name='pair-control-eight-42-v1';out=LAB/'target/convergence'/name
    run(name,[exe,fixture,'gamma15','64','42','1500','50',out],1200,[fixture],{'CONVERGENCE_PAIR_CONTROL':'1'})
    (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
    run(name+'-broad',[LAB/'target/release/examples/convergence_audit_paths.exe',out/'final.gtop',HERE/'broad-paths.json',RAW/(name+'-broad.json')],
        600,[out/'final.gtop',HERE/'broad-paths.json'])
