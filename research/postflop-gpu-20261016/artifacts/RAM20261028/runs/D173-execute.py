import sys,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D173-constructor-diagnostic-r2';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid'] in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'optimization_candidate':False})
 h.child(P['rustc_command'],O,'rustc',1200);verify();binary=H/'probe.exe';h.save(binary.with_suffix('.manifest.json'),{**h.ar.source_identity(),'source_sha256':P['accepted_source_sha256']|{'crates/solver/src/gpu/mod.rs':P['instrumented_production_sha256']},'underlying_accepted_source_sha256':P['accepted_source_sha256'],'binary_sha256':h.sha(binary),'control_only':True,'diagnostic_instrumentation':'D17321hosttimelinepoints, noCUDAAPI/wait/arithmetic change; local plan and benchmark shims reverseexact','instrumentation_sha256':{str(p):h.sha(p) for p in [H/'probe.rs',H/'gpu/mod.rs',H/'gpu/arena.rs',H/'gpu/kernels.cu',H/'source-review.json']},'build_protocol_sha256':sys.argv[1],'rustc_command':P['rustc_command'],'candidate_accepted':False})
with h.ar.exclusive_lock(ROOT/'epoch-sequence.lock'):
 previous=None
 for row in P['sequence']:
  verify();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];binary=H/'probe.exe' if row['instrumented'] else ROOT/'binaries/E080-postflop_autoresearch.exe';mp=binary.with_suffix('.manifest.json');m=h.read(mp);h.pin(binary,m['binary_sha256']);assert m['source_sha256']==P['accepted_source_sha256']|({'crates/solver/src/gpu/mod.rs':P['instrumented_production_sha256']} if row['instrumented'] else {})
  command=[sys.executable,str(ROOT/'epoch/runner.py'),'--id',row['id'],'--title','D173 constructor observer '+row['id'],'--kind','diagnostic','--binary',str(binary),'--build-manifest',str(mp),'--test','postflop_complete_cycle'];h.child(command,O,row['id'],1200);verify();r=h.read(ROOT/'runs'/row['id']/'report.json');assert r['returncode']==0 and r['status']=='measured' and r['test_pass_count']==1 and r['binary_build_manifest']['data']==m and r['provenance']['source_sha256']==P['accepted_source_sha256'];assert h.exact(row['id'])==h.read(ROOT/'epoch/exact-anchor.json')
  if previous is None:previous=r['environment']
  assert previous==r['environment'];raw=(ROOT/'runs'/row['id']/'stdout.log').read_text(encoding='utf-8');traces=[json.loads(line.partition('D173_CONSTRUCTOR ')[2]) for line in raw.splitlines() if line.startswith('D173_CONSTRUCTOR ')];assert len(traces)==(3 if row['instrumented'] else 0)
  print('Completed',row['id'],'exact; timelines',len(traces),flush=True)
 h.save(O/'native-complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'all_native_children_terminal':True,'scientific_records_exact':18,'checkpoints_exact':138,'timelines':9,'performance_qualification_samples':0,'all_samples_retained':True})
h.child([sys.executable,str(ROOT/'runs/D173-assess.py'),sys.argv[1]],O,'assessment',600);verify();h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'protocol_sha256':sys.argv[1],'report_sha256':h.sha(ROOT/'comparisons/D173-constructor-diagnostic/report.json'),'candidate_accepted':False})
print('D173 all fixed diagnostic work terminal.',flush=True)
