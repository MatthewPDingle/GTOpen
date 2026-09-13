"""Serial learning cases registered in PREDICTIVE_SCREEN_PLAN.md."""
import gzip
import json
from run07 import HERE, LAB, RAW, digest, run

CASES = ((64,42,"control"), (1024,42,"predict"), (1024,42,"zero"), (64,42,"predict"), (64,314159,"predict"), (64,314159,"control"))


def case_name(samples, seed, mode):
    return f'predictive-s{samples}-seed{seed}-{mode}-v1'


def main():
    for name in ('predictive-numerical-v1','predictive-native-compat-v1','predictive-rm-compat-v1','predictive-screen-build-v1','predictive-storage-exact-v1'):
        p = json.loads((RAW/(name+'-exit.json')).read_text())
        if p['returncode'] != 0 or p['reason'] is not None:
            raise RuntimeError('Failed prerequisite: '+name)
    exe = LAB/'target/release/examples/convergence_predictive.exe'
    audit = LAB/'target/release/examples/convergence_audit_paths.exe'
    cfg = HERE.parent/'05-preflop-convergence-20260911/six-solver.json'
    paths = HERE/'exploration-diagnostic-paths.json'
    plan = HERE/'PREDICTIVE_SCREEN_PLAN.md'
    equity = LAB/'cache/preflop_eq169.bin'; fit = LAB/'cache/realization_fit.json'
    for samples, seed, mode in CASES:
        name = case_name(samples,seed,mode)
        out = LAB/'target/convergence'/name
        run(name,[exe,cfg,paths,samples,seed,mode,out],450 if samples==1024 else 250,
            [exe,cfg,paths,plan,equity,fit],{'REALIZATION_FIT':str(fit)})
        result = out/'result.json'; packed = RAW/(name+'-result.json.gz')
        packed.write_bytes(gzip.compress(result.read_bytes(),mtime=0))
        (RAW/(name+'-result-envelope.json')).write_text(json.dumps(dict(
            original_bytes=result.stat().st_size,original_sha256=digest(result),
            gzip_sha256=digest(packed)),indent=2)+'\n',encoding='utf-8',newline='\n')
        saved = out/'final.gtop'
        run(name+'-audit',[audit,saved,paths,RAW/(name+'-audit.json')],60,
            [audit,saved,paths,equity])
    from check_predictive_screen import verify
    result = verify()
    (RAW/'predictive-screen-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)


if __name__ == '__main__':
    main()
