"""Guarded GPU exploration screen, then unchanged large conditional qualification."""
from run07 import *

if __name__=='__main__':
    tests=json.loads((RAW/'exploration-tests-v1-exit.json').read_text())
    if tests['returncode'] or tests['reason']:raise RuntimeError('Exploration checks not passed')
    run('exploration-build-v1',['cargo','build','--release','-p','solver','--features','preflop-research',
        '--example','convergence_bench','--example','convergence_audit_paths'],600)
    exe=LAB/'target/release/examples/convergence_bench.exe'
    fixture=HERE.parent/'05-preflop-convergence-20260911/six-solver.json'
    rows=[]
    for seed in (42,314159):
        pair=[]
        for enabled in (0,1):
            name=f'exploration-six-{seed}-{enabled}-v1';out=LAB/'target/convergence'/name
            run(name,[exe,fixture,'gamma15','64',str(seed),'1000','25',out],600,[fixture],
                {'CONVERGENCE_OPPONENT_EXPLORATION':'1'} if enabled else {})
            raw=(out/'result.json').read_bytes();(RAW/(name+'-result.json')).write_bytes(raw);pair.append(json.loads(raw))
        rows.append(dict(seed=seed,passed=all(d['converged_twice'] for d in pair) and pair[1]['total_seconds']<=1.25*pair[0]['total_seconds'],
                         iterations=[d['iteration'] for d in pair],seconds=[d['total_seconds'] for d in pair],
                         gaps=[d['checks'][-1]['gap'] for d in pair]))
    (RAW/'exploration-screen-v1.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(rows,indent=2),flush=True)
    if not all(r['passed'] for r in rows):print('Rejected screen; no large trial',flush=True);sys.exit(0)
    fixture=LAB/'research/autoresearch/passes/03-preflop-20260910/user-session.json'
    name='exploration-eight-42-v1';out=LAB/'target/convergence'/name
    run(name,[exe,fixture,'gamma15','64','42','1500','50',out],1200,[fixture],{'CONVERGENCE_OPPONENT_EXPLORATION':'1'})
    (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
    run(name+'-broad',[LAB/'target/release/examples/convergence_audit_paths.exe',out/'final.gtop',HERE/'broad-paths.json',RAW/(name+'-broad.json')],
        600,[out/'final.gtop',HERE/'broad-paths.json'])
