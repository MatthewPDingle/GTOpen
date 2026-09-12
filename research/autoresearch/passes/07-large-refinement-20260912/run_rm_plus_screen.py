"""Serial learning cases registered in RM_PLUS_SCREEN_PLAN.md."""
import gzip
import json
from run07 import HERE, LAB, RAW, digest, run

CASES = ((64,42,False), (1024,42,True), (64,42,True), (64,314159,True), (64,314159,False))


def case_name(samples, seed, plus):
    return f'rm-plus-s{samples}-seed{seed}-plus{int(plus)}-v1'


def main():
    for name in ('rm-plus-numerical-v2','rm-plus-native-compat-v1','rm-plus-build-v1'):
        p = json.loads((RAW/(name+'-exit.json')).read_text())
        if p['returncode'] != 0 or p['reason'] is not None:
            raise RuntimeError('Failed prerequisite: '+name)
    exe = LAB/'target/release/examples/convergence_rm_plus.exe'
    audit = LAB/'target/release/examples/convergence_audit_paths.exe'
    cfg = HERE.parent/'05-preflop-convergence-20260911/six-solver.json'
    paths = HERE/'exploration-diagnostic-paths.json'
    plan = HERE/'RM_PLUS_SCREEN_PLAN.md'
    equity = LAB/'cache/preflop_eq169.bin'; fit = LAB/'cache/realization_fit.json'
    for samples, seed, plus in CASES:
        name = case_name(samples,seed,plus)
        out = LAB/'target/convergence'/name
        run(name,[exe,cfg,paths,samples,seed,int(plus),out],300,
            [exe,cfg,paths,plan,equity,fit],{'REALIZATION_FIT':str(fit)})
        result = out/'result.json'; packed = RAW/(name+'-result.json.gz')
        packed.write_bytes(gzip.compress(result.read_bytes(),mtime=0))
        (RAW/(name+'-result-envelope.json')).write_text(json.dumps(dict(
            original_bytes=result.stat().st_size,original_sha256=digest(result),
            gzip_sha256=digest(packed)),indent=2)+'\n',encoding='utf-8',newline='\n')
        saved = out/'final.gtop'
        run(name+'-audit',[audit,saved,paths,RAW/(name+'-audit.json')],60,
            [audit,saved,paths,equity])
    from check_rm_plus_screen import verify
    result = verify()
    (RAW/'rm-plus-screen-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)


if __name__ == '__main__':
    main()
