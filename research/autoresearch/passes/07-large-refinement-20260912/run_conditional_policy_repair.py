"""Execute the single bounded saved-policy diagnostic after its prerequisites."""
import gzip,json
from run07 import HERE,LAB,RAW,run,digest
NAME='large-sampled-conditional-policy-v1'
def main():
    for name in ('conditional-policy-numerical-v1','conditional-policy-native-compat-v1',
                 'conditional-policy-default-suite-v1','conditional-policy-build-v2'):
        r=json.loads((RAW/(name+'-exit.json')).read_text())
        if r['returncode']!=0 or r['reason'] is not None:raise RuntimeError('Failed prerequisite '+name)
    exe=LAB/'target/release/examples/convergence_policy_repair.exe'
    audit=LAB/'target/release/examples/convergence_audit_paths.exe'
    source=LAB/'target/convergence/followup-eight-gamma15-s64-42/final.gtop'
    paths=HERE/'broad-paths.json'; protocol=HERE/'CONDITIONAL_POLICY_REPAIR_PLAN.md'
    eq=LAB/'cache/preflop_eq169.bin';fit=LAB/'cache/realization_fit.json'
    out=LAB/'target/convergence'/NAME
    run(NAME,[exe,source,paths,out],600,[exe,source,paths,protocol,eq,fit],{'REALIZATION_FIT':str(fit)})
    for kind in ('plan','all-paths'):(RAW/(NAME+'-'+kind+'.json')).write_bytes((out/(kind+'.json')).read_bytes())
    result=out/'result.json';packed=RAW/(NAME+'-result.json.gz')
    packed.write_bytes(gzip.compress(result.read_bytes(),mtime=0))
    (RAW/(NAME+'-result-envelope.json')).write_text(json.dumps(dict(original_sha256=digest(result),
        gzip_sha256=digest(packed),original_bytes=result.stat().st_size),indent=2)+'\n',encoding='utf-8',newline='\n')
    saved=out/'final.gtop';all_paths=out/'all-paths.json'
    run(NAME+'-audit',[audit,saved,all_paths,RAW/(NAME+'-audit.json')],120,[audit,saved,all_paths,eq,fit],{'REALIZATION_FIT':str(fit)})
    from check_conditional_policy_repair import verify
    verified=verify()
    (RAW/(NAME+'-verified.json')).write_text(json.dumps(verified,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(verified),flush=True)
if __name__=='__main__':main()
