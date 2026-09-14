"""One guarded compilation or numerical suite; no benchmark claim."""
import hashlib,json,re,shutil,sys
from pathlib import Path
from run_c23 import HERE,RAW,read,run07
stage=sys.argv[1];assert stage in ['build','test']
assert read(RAW/'c24-screen-verified.json')['admitted']
exe=run07.LAB/'target/c24-integration-frozen.exe'
inputs=[Path(__file__),HERE/'C24_PROTOCOL.md',HERE/'prepare_c24_integration.py',HERE/'c24_ordinary.rs.txt',HERE/'c24_ordinary_tests.rs.txt',HERE/'artifacts/c24-integration-source-map.json']
if stage=='build':
    cmd=['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib','--no-run'];cap=300;env={}
else:
    assert read(RAW/'c24-integration-build-v1-exit.json')['returncode']==0
    cmd=[exe,'preflop::gpu::static_cdf::ordinary::tests::','--nocapture','--test-threads=1'];cap=300
    inputs+=[exe];env={'PREFLOP_GPU_ORDINARY_STATIC_OUTPUT':str(RAW/'c24-integrated-v1')}
name='c24-integration-'+stage+'-v1'
run07.run(name,cmd,cap,inputs,env);r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None
if stage=='build':
    log=(RAW/(name+'.log')).read_text(encoding='utf-8');match=re.search(r'Executable unittests .*?\(([^)]+\.exe)\)',log);assert match
    assert not exe.exists();shutil.copyfile(run07.LAB/match[1],exe)
    (RAW/'c24-integration-frozen.json').write_text(json.dumps({'sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'path':str(exe)},indent=2)+'\n')
