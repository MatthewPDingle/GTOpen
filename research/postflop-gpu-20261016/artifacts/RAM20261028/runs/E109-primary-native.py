"""Ordinary units followed by the frozen six-run E109 primary screen."""
import sys,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E109-primary-plan';assert len(sys.argv)==2;P=h.read(H/'protocol.json');O=ROOT/'runs/E109-primary-execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();assert not(ROOT/'gpu-run.lock').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'epoch-sequence.lock'):
 previous_env=None;previous_gpu=None;anchor=h.read(h.EPOCH/'exact-anchor.json')
 for record in P['sequence']:
  verify();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];stem=record['binary'];binary=ROOT/'binaries'/(stem+'.exe');mp=binary.with_suffix('.manifest.json');m=h.read(mp)
  h.pin(binary,m['binary_sha256']);expected=P['accepted_source_sha256']|(P['candidate_owned_sha256']if stem.startswith('E109')else{})
  assert m['source_sha256']==expected
  if stem.startswith('E109'):assert m['build_protocol_sha256']==P['build_protocol_sha256']
  cmd=[sys.executable,str(h.EPOCH/'runner.py'),'--id',record['id'],'--title','E109 '+record['id'],'--kind','validation'if record['unit']else('baseline'if record['id'].startswith('B')else'candidate'),'--binary',str(binary),'--build-manifest',str(mp),'--test','*'if record['unit']else'postflop_complete_cycle']
  if record['unit']:cmd.append('--not-ignored')
  h.child(cmd,O,record['id'],1200);verify();r=h.read(ROOT/'runs'/record['id']/'report.json')
  assert r['returncode']==0 and r['status']=='measured'and r['binary_sha256']==m['binary_sha256']and r['binary_build_manifest']['sha256']==h.sha(mp)
  assert r['provenance']['source_sha256']==P['accepted_source_sha256']and r['binary_build_manifest']['data']==m
  if record['unit']:
   raw=(ROOT/'runs'/record['id']/'stdout.log').read_text(encoding='utf-8');assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('86','0','4','0','0')]
  else:
   assert h.exact(record['id'])==anchor
   gpu=[x.strip()for x in r['telemetry_before']['gpu']['stdout'].split(',')[:4]]
   assert 'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee'in gpu and r['environment']['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed'and r['environment']['RAYON_NUM_THREADS']=='16'
   if previous_env is None:previous_env=r['environment'];previous_gpu=gpu
   assert previous_env==r['environment']and previous_gpu==gpu
  print('Completed',record['id'],'exact',flush=True)
 h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'sequence':[x['id']for x in P['sequence']],'ordinary_units_passed':86,'ordinary_units_ignored':4,'fixture_results_exact':18,'convergence_records_exact':138,'all_owned_children_terminal':True,'all_samples_retained':True,'extension_runs':0,'historical_samples_scored':0,'candidate_accepted':False})
print('E109 primary execution complete; assess retained observations.',flush=True)
