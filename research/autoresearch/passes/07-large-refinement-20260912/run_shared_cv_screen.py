"""First-stage seed42 screen registered in SHARED_CV_SCREEN_PLAN.md."""
import gzip,json
from run07 import HERE,LAB,RAW,run,digest
CASES=((1024,'control'),(64,'control'),(64,'old32'),(64,'shared32'),(64,'shared64'))
def name(samples,mode):return f'shared-cv-s{samples}-seed42-{mode}-v1'
def main():
    for n in ('shared-cv-numerical-v4','shared-cv-old-compat-v1','shared-cv-native-compat-v1','shared-cv-default-suite-v1','shared-cv-screen-build-v1'):
        r=json.loads((RAW/(n+'-exit.json')).read_text())
        if r['returncode']!=0 or r['reason'] is not None:raise RuntimeError('Failed prerequisite '+n)
    inv=LAB/'target/release/examples/convergence_shared_cv_storage.exe'
    source=LAB/'target/convergence/followup-eight-gamma15-s64-42/final.gtop'
    run('shared-cv-storage-exact-v2',[inv,source,RAW/'shared-cv-storage-exact-v2.json'],120,[inv,source,HERE/'SHARED_CV_PLAN.md'])
    from check_shared_cv_storage import verify as storage
    (RAW/'shared-cv-storage-verified.json').write_text(json.dumps(storage(),indent=2)+'\n',encoding='utf-8',newline='\n')
    exe=LAB/'target/release/examples/convergence_shared_cv.exe';audit=LAB/'target/release/examples/convergence_audit_paths.exe'
    cfg=HERE.parent/'05-preflop-convergence-20260911/six-solver.json';paths=HERE/'exploration-diagnostic-paths.json'
    protocol=HERE/'SHARED_CV_SCREEN_PLAN.md';eq=LAB/'cache/preflop_eq169.bin';fit=LAB/'cache/realization_fit.json'
    for samples,mode in CASES:
        n=name(samples,mode);out=LAB/'target/convergence'/n
        run(n,[exe,cfg,paths,samples,42,mode,out],450 if samples==1024 else 250,[exe,cfg,paths,protocol,eq,fit],{'REALIZATION_FIT':str(fit)})
        result=out/'result.json';packed=RAW/(n+'-result.json.gz');packed.write_bytes(gzip.compress(result.read_bytes(),mtime=0))
        (RAW/(n+'-result-envelope.json')).write_text(json.dumps(dict(original_sha256=digest(result),gzip_sha256=digest(packed),original_bytes=result.stat().st_size),indent=2)+'\n',encoding='utf-8',newline='\n')
        saved=out/'final.gtop'
        run(n+'-audit',[audit,saved,paths,RAW/(n+'-audit.json')],60,[audit,saved,paths,eq,fit],{'REALIZATION_FIT':str(fit)})
    from check_shared_cv_screen import verify
    r=verify();(RAW/'shared-cv-screen-verified.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(r),flush=True)
if __name__=='__main__':main()
