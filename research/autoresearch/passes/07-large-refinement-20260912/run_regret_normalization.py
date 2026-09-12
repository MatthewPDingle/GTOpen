"""Guarded GPU learning-rate screen and conditional large-game qualification."""
from run07 import *
if __name__=='__main__':
    run('normalized-regret-tests-v2',['cargo','test','--release','-p','solver','--features','preflop-research',
        '--lib','normalized_regret_','--','--nocapture','--test-threads=1'],600)
    run('normalized-regret-build-v1',['cargo','build','--release','-p','solver','--features','preflop-research',
        '--example','convergence_bench','--example','convergence_audit_paths'],600)
    exe=LAB/'target/release/examples/convergence_bench.exe'
    fixture=HERE.parent/'05-preflop-convergence-20260911/six-solver.json'
    screen=[]
    for seed in (42,314159):
        records=[]
        for enabled in (False,True):
            name=f'normalized-regret-six-{seed}-{int(enabled)}-v1'
            out=LAB/'target/convergence'/name
            env={'CONVERGENCE_NORMALIZED_REGRET':'1'} if enabled else {}
            run(name,[exe,fixture,'gamma15','64',str(seed),'1000','25',out],600,[fixture],env)
            data=json.loads((out/'result.json').read_text());records.append(data)
            (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
        passed=records[1]['converged_twice'] and records[0]['converged_twice'] and records[1]['total_seconds']<=2*records[0]['total_seconds']
        screen.append(dict(seed=seed,passed=passed,baseline_seconds=records[0]['total_seconds'],candidate_seconds=records[1]['total_seconds']))
    (RAW/'normalized-regret-screen-v1.json').write_text(json.dumps(screen,indent=2)+'\n',encoding='utf-8',newline='\n')
    if not all(row['passed'] for row in screen):
        print('Small-fixture screen rejected candidate; no large run',flush=True)
        sys.exit(0)
    fixture=LAB/'research/autoresearch/passes/03-preflop-20260910/user-session.json'
    name='normalized-regret-eight-42-v1';out=LAB/'target/convergence'/name
    run(name,[exe,fixture,'gamma15','64','42','1500','50',out],1200,[fixture],{'CONVERGENCE_NORMALIZED_REGRET':'1'})
    (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
    run(name+'-broad',[LAB/'target/release/examples/convergence_audit_paths.exe',out/'final.gtop',HERE/'broad-paths.json',RAW/(name+'-broad.json')],
        600,[out/'final.gtop',HERE/'broad-paths.json'])
