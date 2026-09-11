"""Serial local qualification, variance screen, then registered large schedule trials."""
from after_phase_a import guarded
from run_experiment import HERE, LAB, run
from run_phase_a import jobs, EXE, EXPECTED, EIGHT, MODELED
from run_diagnostics import digest
import json

if __name__ == '__main__':
    local = LAB / 'target/release/examples/convergence_local.exe'
    if digest(local) != 'b0448f3940c4c97af0ba758e678818ccb98258c342ef0139099c6e4c33bc2fbc':
        raise RuntimeError('Local evaluator changed')
    for name, *_ in jobs:
        record = json.loads((HERE/'raw'/f'{name}-exit.json').read_text())
        if record['returncode'] or record['reason']: raise RuntimeError(name)
        ref = ('eight-native-a' if '-eight-' in name else
               'modeled-native-a' if '-modeled-' in name else 'six-reference-tight-a')
        candidate = LAB/'target/convergence'/name/'final.gtop'
        reference = LAB/'target/convergence'/ref/'final.gtop'
        output = HERE/'raw'/f'{name}-local-v3.json'
        provenance = dict(candidate_sha256=digest(candidate), reference_sha256=digest(reference),
                          exe_sha256=digest(local), reference=ref)
        (HERE/'raw'/f'{name}-local-protocol.json').write_text(json.dumps(provenance,indent=2)+'\n')
        guarded(f'{name}-local', [str(local),str(candidate),str(reference),str(output)], 600)
        if digest(candidate)!=provenance['candidate_sha256'] or digest(reference)!=provenance['reference_sha256']:
            raise RuntimeError('Snapshot changed')
    guarded('variance-tests', ['cargo','test','--release','-p','solver','--features',
        'preflop-research','--example','convergence_variance'],600)
    guarded('variance-build', ['cargo','build','--release','-p','solver','--features',
        'preflop-research','--example','convergence_variance'],600)
    variance=LAB/'target/release/examples/convergence_variance.exe'
    (HERE/'raw/variance-exe-sha256.txt').write_text(digest(variance)+'\n')
    guarded('variance-screen', [str(variance),str(HERE/'raw/variance-screen.json')],600)
    for fixture, path, limit, cap in [('eight',EIGHT,2000,3600),('modeled',MODELED,1500,1800)]:
        for seed in (42,314159):
            if digest(EXE)!=EXPECTED: raise RuntimeError('Frozen benchmark changed')
            run(f'followup-{fixture}-gamma15-s64-{seed}',path,'gamma15',64,seed,limit,50,cap,executable=EXE)
