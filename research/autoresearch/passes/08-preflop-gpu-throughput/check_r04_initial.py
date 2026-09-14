"""Freeze and verify initial R04 selection/cohort/native qualification."""
import hashlib
import json
import re
import shutil
from pathlib import Path
from run_c23 import HERE, RAW, read, run07

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    source=None;tests={}
    for stage,expected in [('selection',3),('cohorts',10),('native',20)]:
        name='r04-'+stage+'-v1';r=read(RAW/(name+'-exit.json'))
        assert r['returncode']==0 and r['reason'] is None and r['seconds']<=300
        if source is None:source=r['solver_source_files']
        else:assert source==r['solver_source_files']
        for p,h in r['inputs'].items():assert sha(p)==h,p
        log=(RAW/(name+'.log')).read_text(encoding='utf-8')
        counts=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;',log)
        assert counts and all(int(f)==0 for _,f in counts)
        assert sum(int(p) for p,_ in counts)==expected
        tests[stage]={'passed':expected,'guard_seconds':r['seconds']}
    for p,h in source.items():assert sha(run07.LAB/p)==h,p
    artifacts={}
    for name in ['candidate.cu','candidate.ptx','resources.json','continued-false.gtop','continued-true.gtop','interrupted.gtop','continuation.json']:
        path=RAW/'r04-integrated-v1'/name
        assert path.read_bytes()==(RAW/'c23-integrated-v1'/name).read_bytes(),name
        artifacts[name]=sha(path)
    log=(RAW/'r04-selection-v1.log').read_text(encoding='utf-8')
    original=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    frozen=run07.LAB/'target/r04-benchmark-frozen.exe'
    if frozen.exists():assert sha(frozen)==sha(original)
    else:shutil.copyfile(original,frozen)
    archive=HERE/'artifacts/r04-v1';archive.mkdir(exist_ok=True)
    changed=['crates/solver/src/preflop/gpu.rs','crates/solver/src/preflop/gpu/adaptive_throughput.rs',
        'crates/solver/src/preflop/gpu/static_cdf.rs','crates/solver/src/preflop/gpu/exact_reuse.rs',
        'crates/solver/src/preflop/gpu/cohort_reuse.rs','crates/solver/tests/preflop_throughput.rs']
    for name in changed:
        src=run07.LAB/name;dest=archive/Path(name).name
        if dest.exists():assert dest.read_bytes()==src.read_bytes()
        else:shutil.copyfile(src,dest)
    result={'verified':True,'admitted':True,'retained':False,'deployed':False,
        'status':'Normal-build selection qualified; integration timing next',
        'tests':tests,'gpu_kernels_and_saved_replay_identical_to_c23':True,
        'artifacts':artifacts,'executable_sha256':sha(frozen),'solver_source_files':source,
        'scope':'Initial integration gate only. Full overhead pairs, saved-fixture and isolated-server checks, default/server regressions remain.'}
    dest=RAW/'r04-initial-verified.json'
    if dest.exists():assert read(dest)==result
    else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (RAW/'r04-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='solver_source_files'},indent=2))

if __name__=='__main__':main()
