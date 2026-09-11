"""Run after all prior hardware work ends. Compare default and coarse/fine checks."""
from after_phase_a import guarded
from run_experiment import HERE, LAB, run
from run_phase_a import SIX,EIGHT
from run_diagnostics import digest
import json

if __name__=='__main__':
    guarded('check-schedule-build',['cargo','build','--release','-p','solver','--features','preflop-research','--example','convergence_bench'],600)
    exe=LAB/'target/release/examples/convergence_bench.exe'
    name='followup-six-gamma15-s64-default-control'
    run(name,SIX,'gamma15',64,42,1500,25,600,executable=exe)
    before=LAB/'target/convergence/followup-six-gamma15-s64-42/final.gtop'
    after=LAB/'target/convergence'/name/'final.gtop'
    record=dict(previous_sha256=digest(before),rebuilt_sha256=digest(after))
    record['exact_snapshot_match']=record['previous_sha256']==record['rebuilt_sha256']
    (HERE/'raw/check-schedule-default-control.json').write_text(json.dumps(record,indent=2)+'\n')
    if not record['exact_snapshot_match']: raise RuntimeError('Default scheduling changed snapshot; inspect before large trial')
    name='followup-eight-gamma15-s64-coarsefine-42'
    run(name,EIGHT,'gamma15',64,42,2000,50,3600,executable=exe,check_policy='coarse_then_fine')
    local=LAB/'target/release/examples/convergence_local.exe'
    c=LAB/'target/convergence'/name/'final.gtop'; r=LAB/'target/convergence/eight-native-a/final.gtop'
    (HERE/'raw'/f'{name}-local-protocol.json').write_text(json.dumps(dict(candidate_sha256=digest(c),reference_sha256=digest(r),exe_sha256=digest(local)),indent=2)+'\n')
    guarded(f'{name}-local',[str(local),str(c),str(r),str(HERE/'raw'/f'{name}-local-v3.json')],600)
    guarded('final-default-suite',['cargo','test','--release','-p','solver'],1200)
