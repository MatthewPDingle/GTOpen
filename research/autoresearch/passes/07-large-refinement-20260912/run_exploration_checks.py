"""Post-screen correctness diagnostics and serial regression checks."""
from run07 import *

if __name__=='__main__':
    paths=HERE/'exploration-diagnostic-paths.json'
    historical=json.loads((HERE.parent/'05-preflop-convergence-20260911/raw/six-s64-a-local-v3.json').read_text())
    if json.loads(paths.read_text())!=[r['candidate']['path'] for r in historical['rows']]:raise RuntimeError('Changed historical path set')
    for seed in (42,314159):
        for enabled in (0,1):
            name=f'exploration-six-{seed}-{enabled}-v1';saved=LAB/'target/convergence'/name/'final.gtop'
            run(name+'-local',[LAB/'target/release/examples/convergence_audit_paths.exe',saved,paths,RAW/(name+'-local.json')],
                600,[saved,paths])
    run('exploration-gpu-regressions-v1',['cargo','test','--release','--features','preflop-research','--test','gpu','--test','preflop_gpu',
        '--','--test-threads=1'],600)
    run('exploration-default-regressions-v1',['cargo','test','--release','-p','solver'],600)
