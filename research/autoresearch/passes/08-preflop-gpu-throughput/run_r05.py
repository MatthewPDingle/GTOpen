"""Serial, idle-app-guarded R05 qualification."""
import sys,shutil,re,json
from pathlib import Path
from run_c23 import HERE,RAW,read,run07
stage=sys.argv[1];version=sys.argv[2] if len(sys.argv)>2 else 'v1'
commands={
 'selection':['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib','adaptive_throughput::tests::','--','--nocapture','--test-threads=1'],
 'ordinary':['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib','static_cdf::ordinary::tests::','--','--nocapture','--test-threads=1'],
 'cohorts':['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib','cohort_reuse::tests::','--','--nocapture','--test-threads=1'],
 'native':['cargo','test','--release','-p','solver','--features','gpu','--test','gpu','--test','preflop_gpu','--test','preflop_throughput','--','--test-threads=1'],
 'default':['cargo','test','--release','-p','solver'],
 'server-tests':['cargo','test','--release','-p','server','--features','gpu','--','--test-threads=1'],
 'server-build':['cargo','build','--release','-p','server','--features','gpu'],
}
name=f'r05-{stage}-{version}'
run07.run(name,commands[stage],600 if stage=='server-build' else 300,
 [Path(__file__),HERE/'R05_PROTOCOL.md',HERE/'prepare_r05.py',HERE/'artifacts/r05-before-source-map.json'],
 {'PREFLOP_GPU_STATIC_CDF_INTEGRATED_OUTPUT':str(RAW/'r05-integrated-v1'),
  'PREFLOP_GPU_ORDINARY_STATIC_OUTPUT':str(RAW/'r05-ordinary-v1')})
if stage=='selection':
 log=(RAW/(name+'.log')).read_text(encoding='utf-8')
 src=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
 dest=run07.LAB/'target/r05-test-frozen.exe';shutil.copyfile(src,dest)
 (RAW/'r05-test-frozen.json').write_text(json.dumps({'sha256':run07.digest(dest),'source':name},indent=2)+'\n',encoding='utf-8')
if stage=='server-build':
 dest=run07.LAB/'target/r05-server-frozen.exe';shutil.copyfile(run07.LAB/'target/release/gto-server.exe',dest)
 (RAW/'r05-server-frozen.json').write_text(json.dumps({'sha256':run07.digest(dest),'source':name},indent=2)+'\n',encoding='utf-8')
