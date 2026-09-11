"""Resume the registered native100 screen after corrected tests/build pass."""
from after_phase_a import guarded
from run_experiment import HERE,LAB
from run_diagnostics import digest
import json,shutil,subprocess

if __name__=='__main__':
    for name in ('refine-tests-v2','refine-build'):
        r=json.loads((HERE/'raw'/f'{name}-exit.json').read_text())
        if r['returncode'] or r['reason']: raise RuntimeError(name)
    exe=LAB/'target/release/examples/convergence_refine.exe'
    source=LAB/'target/convergence/six-native-b/final.gtop'
    output=LAB/'target/convergence/followup-six-native-local100'
    record=dict(input_sha256=digest(source),exe_sha256=digest(exe),local_iterations=100,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=LAB,text=True).strip())
    (HERE/'raw/refine-protocol.json').write_text(json.dumps(record,indent=2)+'\n')
    guarded('refine-native100',[str(exe),str(source),'100',str(output)],600)
    if digest(source)!=record['input_sha256']: raise RuntimeError('Source changed')
    shutil.copyfile(output/'result.json',HERE/'raw/refine-native100-result.json')
    local=LAB/'target/release/examples/convergence_local.exe'
    guarded('refine-native100-local',[str(local),str(output/'final.gtop'),str(LAB/'target/convergence/six-reference-tight-a/final.gtop'),str(HERE/'raw/refine-native100-local-v3.json')],600)
