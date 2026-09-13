"""Guarded fixed-epsilon diagnostic, registered before observing outcomes."""
import gzip,json
from run07 import HERE,LAB,RAW,run,digest
CASES=('0','0.01','0.05')
def name(e):return 'behavioral-fixed-e'+e.replace('.','p')+'-v1'
def main():
    for n in ('behavioral-numerical-v1','behavioral-default-suite-v1','behavioral-native-compat-v1','behavioral-build-v1'):
        r=json.loads((RAW/(n+'-exit.json')).read_text())
        if r['returncode']!=0 or r['reason'] is not None:raise RuntimeError('Failed prerequisite '+n)
    exe=LAB/'target/release/examples/convergence_behavioral.exe';audit=LAB/'target/release/examples/convergence_audit_paths.exe'
    cfg=HERE.parent/'05-preflop-convergence-20260911/six-solver.json';paths=HERE/'exploration-diagnostic-paths.json'
    protocol=HERE/'BEHAVIORAL_FIXED_PLAN.md';eq=LAB/'cache/preflop_eq169.bin';fit=LAB/'cache/realization_fit.json'
    for eps in CASES:
        n=name(eps);out=LAB/'target/convergence'/n
        run(n,[exe,cfg,paths,eps,out],180,[exe,cfg,paths,protocol,eq,fit],{'REALIZATION_FIT':str(fit)})
        result=out/'result.json';packed=RAW/(n+'-result.json.gz');packed.write_bytes(gzip.compress(result.read_bytes(),mtime=0))
        (RAW/(n+'-result-envelope.json')).write_text(json.dumps(dict(original_sha256=digest(result),gzip_sha256=digest(packed),original_bytes=result.stat().st_size),indent=2)+'\n',encoding='utf-8',newline='\n')
        saved=out/'final.gtop'
        run(n+'-audit',[audit,saved,paths,RAW/(n+'-audit.json')],60,[audit,saved,paths,eq,fit],{'REALIZATION_FIT':str(fit)})
    from check_behavioral_fixed import verify
    result=verify();(RAW/'behavioral-fixed-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
