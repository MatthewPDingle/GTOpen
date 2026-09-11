"""Defer conditional-refinement validation until large GPU timings end."""
from after_phase_a import guarded
from run_experiment import HERE, LAB, idle
from run_diagnostics import digest
import json
import shutil
import time

if __name__ == '__main__':
    names=[f'followup-{fixture}-gamma15-s64-{seed}' for fixture in ('eight','modeled') for seed in (42,314159)]
    started=time.monotonic()
    while True:
        done=0
        for name in names:
            p=HERE/'raw'/f'{name}-exit.json'
            if not p.exists(): continue
            try: r=json.loads(p.read_text())
            except json.JSONDecodeError: continue
            if r['returncode'] or r['reason']: raise RuntimeError(f'Failed timing {name}')
            done+=1
        if done==len(names): break
        idle()
        if time.monotonic()-started>10000: raise RuntimeError('Wait cap')
        time.sleep(1)
    local=LAB/'target/release/examples/convergence_local.exe'
    for name in names:
        ref='eight-native-a' if '-eight-' in name else 'modeled-native-a'
        c=LAB/'target/convergence'/name/'final.gtop'; r=LAB/'target/convergence'/ref/'final.gtop'
        (HERE/'raw'/f'{name}-local-protocol.json').write_text(json.dumps(dict(candidate_sha256=digest(c),reference_sha256=digest(r),exe_sha256=digest(local)),indent=2)+'\n')
        guarded(f'{name}-local',[str(local),str(c),str(r),str(HERE/'raw'/f'{name}-local-v3.json')],600)
    guarded('refine-tests',['cargo','test','--release','-p','solver','--features','preflop-research','--lib','convergence_','--','--nocapture'],600)
    guarded('refine-build',['cargo','build','--release','-p','solver','--features','preflop-research','--example','convergence_refine'],600)
    exe=LAB/'target/release/examples/convergence_refine.exe'
    source=LAB/'target/convergence/six-native-b/final.gtop'
    output=LAB/'target/convergence/followup-six-native-local100'
    (HERE/'raw/refine-protocol.json').write_text(json.dumps(dict(input_sha256=digest(source),exe_sha256=digest(exe),local_iterations=100),indent=2)+'\n')
    guarded('refine-native100',[str(exe),str(source),'100',str(output)],600)
    shutil.copyfile(output/'result.json',HERE/'raw/refine-native100-result.json')
    guarded('refine-native100-local',[str(local),str(output/'final.gtop'),str(LAB/'target/convergence/six-reference-tight-a/final.gtop'),str(HERE/'raw/refine-native100-local-v3.json')],600)
