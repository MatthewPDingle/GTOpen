"""Guarded four-case native finish; preserves original fixed-stage inputs."""
import gzip,json
from run07 import HERE,LAB,RAW,run,digest
from run_behavioral_fixed import name as pretrain_name
CASES=(('0','keep'),('0','reset'),('0.01','reset'),('0.05','reset'))
def name(e,m):return 'behavioral-finish-e'+e.replace('.','p')+'-'+m+'-v1'
def main():
    from check_behavioral_fixed import verify as previous
    admitted=previous()['transition_design_candidates']
    if admitted!=[0.01,0.05]:raise RuntimeError('Fixed-stage admission changed')
    for n in ('behavioral-transition-numerical-v1','behavioral-finish-default-v1','behavioral-finish-native-v1','behavioral-finish-build-v1'):
        r=json.loads((RAW/(n+'-exit.json')).read_text())
        if r['returncode']!=0 or r['reason'] is not None:raise RuntimeError('Failed prerequisite '+n)
    exe=LAB/'target/release/examples/convergence_behavioral_finish.exe';audit=LAB/'target/release/examples/convergence_audit_paths.exe'
    paths=HERE/'exploration-diagnostic-paths.json';protocol=HERE/'BEHAVIORAL_TRANSITION_PLAN.md'
    eq=LAB/'cache/preflop_eq169.bin';fit=LAB/'cache/realization_fit.json'
    for eps,mode in CASES:
        initial=LAB/'target/convergence'/pretrain_name(eps);source=initial/'final.gtop';stage=initial/'result.json'
        envelope=json.loads((RAW/(pretrain_name(eps)+'-result-envelope.json')).read_text())
        if digest(stage)!=envelope['original_sha256']:raise RuntimeError('Pretraining result changed')
        n=name(eps,mode);out=LAB/'target/convergence'/n
        run(n,[exe,source,paths,mode,stage,out],180,[exe,source,paths,stage,protocol,eq,fit],{'REALIZATION_FIT':str(fit)})
        result=out/'result.json';packed=RAW/(n+'-result.json.gz');packed.write_bytes(gzip.compress(result.read_bytes(),mtime=0))
        (RAW/(n+'-result-envelope.json')).write_text(json.dumps(dict(original_sha256=digest(result),gzip_sha256=digest(packed),original_bytes=result.stat().st_size),indent=2)+'\n',encoding='utf-8',newline='\n')
        saved=out/'final.gtop'
        run(n+'-audit',[audit,saved,paths,RAW/(n+'-audit.json')],60,[audit,saved,paths,eq,fit],{'REALIZATION_FIT':str(fit)})
    from check_behavioral_finish import verify
    r=verify();(RAW/'behavioral-finish-verified.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(r),flush=True)
if __name__=='__main__':main()
