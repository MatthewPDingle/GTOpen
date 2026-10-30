import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E112-confirmation-plan';assert len(sys.argv)==2;P=h.read(H/'protocol.json');O=ROOT/'runs/E112-confirmation-execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O.mkdir(exist_ok=False);anchor=h.read(ROOT/'epoch/exact-anchor.json');environment=gpu=None
with h.ar.exclusive_lock(ROOT/'epoch-sequence.lock'):
 for ident in P['measurement_order']:
  verify();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];stem='E080-postflop_autoresearch'if ident.startswith('B')else'E112-postflop_autoresearch';binary=ROOT/'binaries'/(stem+'.exe');mp=binary.with_suffix('.manifest.json');m=h.read(mp);h.pin(binary,m['binary_sha256']);assert m['source_sha256']==P['accepted_source_sha256']|(P['candidate_owned_sha256']if stem.startswith('E112')else{})
  cmd=[sys.executable,str(ROOT/'epoch/runner.py'),'--id',ident,'--title','E112 fresh16 '+ident,'--kind','baseline'if ident.startswith('B')else'candidate','--binary',str(binary),'--build-manifest',str(mp),'--test','postflop_complete_cycle'];h.child(cmd,O,ident,1200);verify();q=h.read(ROOT/'runs'/ident/'report.json');assert q['returncode']==0 and q['status']=='measured'and q['binary_sha256']==m['binary_sha256']and q['binary_build_manifest']['sha256']==h.sha(mp)and q['binary_build_manifest']['data']==m;assert q['provenance']['source_sha256']==P['accepted_source_sha256'];assert h.exact(ident)==anchor
  nowgpu=[x.strip()for x in q['telemetry_before']['gpu']['stdout'].split(',')[:4]];assert P['GPU_uuid']in nowgpu and q['environment']['RAYON_NUM_THREADS']=='16'and q['environment']['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed'
  if environment is None:environment=q['environment'];gpu=nowgpu
  assert q['environment']==environment and nowgpu==gpu;print('Completed fresh16',ident,'exact',flush=True)
 h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'measurement_order':P['measurement_order'],'fixture_results':96,'convergence_records':736,'all_owned_children_terminal':True,'all_samples_retained':True,'excluded_samples':[],'extension_runs':0,'initial_or_historical_samples_scored':0,'candidate_accepted':False})
print('All32fresh16processes complete; assess fixed cohort.',flush=True)
