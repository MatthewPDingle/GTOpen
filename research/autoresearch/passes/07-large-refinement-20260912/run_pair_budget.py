"""Registered 32-particle corrected vs 64-particle native learning screen only."""
from run07 import *

if __name__=='__main__':
    run('pair-budget-tests-v2',['cargo','test','--release','-p','solver','--features','preflop-research',
        '--lib','pair_control_','--','--nocapture','--test-threads=1'],900)
    run('pair-budget-cyclic-v2',['cargo','test','--release','-p','solver','--features','preflop-research',
        '--lib','cyclic_sampling_covers_every_particle_equally','--','--test-threads=1'],120)
    run('pair-budget-build-v2',['cargo','build','--release','-p','solver','--features','preflop-research',
        '--example','convergence_bench'],600)
    exe=LAB/'target/release/examples/convergence_bench.exe'
    fixture=HERE.parent/'05-preflop-convergence-20260911/six-solver.json'
    rows=[]
    for seed in (42,314159):
        pair=[]
        for enabled,samples in ((False,64),(True,32)):
            name=f'pair-budget-six-{seed}-{int(enabled)}-v2'
            out=LAB/'target/convergence'/name
            run(name,[exe,fixture,'gamma15',str(samples),str(seed),'1000','25',out],600,[fixture],
                {'CONVERGENCE_PAIR_CONTROL':'1'} if enabled else {})
            raw=(out/'result.json').read_bytes()
            (RAW/(name+'-result.json')).write_bytes(raw)
            pair.append(json.loads(raw))
        rows.append(dict(seed=seed,passed=all(d['converged_twice'] for d in pair)
                         and pair[1]['total_seconds']<pair[0]['total_seconds'],
                         iterations=[d['iteration'] for d in pair],seconds=[d['total_seconds'] for d in pair],
                         gaps=[d['checks'][-1]['gap'] for d in pair]))
    (RAW/'pair-budget-screen-v2.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(rows,indent=2),flush=True)
    print('Screen only; no large trial or deployment',flush=True)
