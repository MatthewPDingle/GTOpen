"""Run the registered sequential selected-root conditional solve screen."""
from after_phase_a import guarded
from run_experiment import HERE,LAB
from run_diagnostics import digest
import json,shutil,sys

if __name__=='__main__':
    iterations=int(sys.argv[1]) if len(sys.argv)>1 else 100
    if iterations not in (100,1000): raise ValueError('unregistered iteration count')
    exe=LAB/'target/release/examples/convergence_refine.exe'
    local=LAB/'target/release/examples/convergence_local.exe'
    for label,source_name in [('native','six-native-b'),('sampled','followup-six-gamma15-s64-42')]:
        source=LAB/'target/convergence'/source_name/'final.gtop'
        name=f'refine-{label}-nested{iterations}'; output=LAB/'target/convergence'/name
        record=dict(input_sha256=digest(source),exe_sha256=digest(exe),iterations_per_root=iterations,roots=6)
        (HERE/'raw'/f'{name}-protocol.json').write_text(json.dumps(record,indent=2)+'\n')
        guarded(name,[str(exe),str(source),str(iterations),str(output),'nested'],600)
        if digest(source)!=record['input_sha256']: raise RuntimeError('Source changed')
        shutil.copyfile(output/'result.json',HERE/'raw'/f'{name}-result.json')
        guarded(f'{name}-local',[str(local),str(output/'final.gtop'),str(LAB/'target/convergence/six-reference-tight-a/final.gtop'),str(HERE/'raw'/f'{name}-local-v3.json')],600)
