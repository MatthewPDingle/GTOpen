"""Both ordinary unit suites, then exactly three unchanged full-cycle pairs."""
import json,re,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E098-primary-plan';P=h.read(H/'protocol.json');O=ROOT/'runs/E098-primary-execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();assert not(ROOT/'gpu-run.lock').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'epoch-sequence.lock'):
 anchor=h.read(h.EPOCH/'exact-anchor.json');previous_env=None;previous_gpu=None
 for row in P['sequence']:
  verify();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];binary=ROOT/'binaries'/(row['binary']+'.exe');mp=binary.with_suffix('.manifest.json');m=h.read(mp);h.pin(binary,m['binary_sha256'])
  assert m['source_sha256']==P['accepted_source_sha256'] and m['build_protocol_sha256']==P['build_protocol_sha256'] and m['arm']==row['arm'] and m['rustc_flags']==([] if row['arm']=='default' else ['-C','target-cpu=znver3'])
  cmd=[sys.executable,str(h.EPOCH/'runner.py'),'--id',row['id'],'--title','E098 '+row['id'],'--kind','validation' if row['unit'] else ('baseline' if row['arm']=='default' else 'candidate'),'--binary',str(binary),'--build-manifest',str(mp),'--test','*' if row['unit'] else 'postflop_complete_cycle']
  if row['unit']:cmd.append('--not-ignored')
  h.child(cmd,O,row['id'],1200);verify();r=h.read(ROOT/'runs'/row['id']/'report.json');assert r['returncode']==0 and r['status']=='measured' and r['binary_sha256']==m['binary_sha256'] and r['binary_build_manifest']['sha256']==h.sha(mp) and r['provenance']['source_sha256']==P['accepted_source_sha256'] and r['binary_build_manifest']['data']==m
  if row['unit']:
   raw=(ROOT/'runs'/row['id']/'stdout.log').read_text(encoding='utf-8');assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('86','0','4','0','0')]
  else:
   assert h.exact(row['id'])==anchor;gpu=[x.strip() for x in r['telemetry_before']['gpu']['stdout'].split(',')[:4]];assert P['GPU_uuid'] in gpu and r['environment']['RAYON_NUM_THREADS']=='16' and r['environment']['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed'
   if previous_env is None:previous_env=r['environment'];previous_gpu=gpu
   assert previous_env==r['environment'] and previous_gpu==gpu
  print('Completed',row['id'],'exact.',flush=True)
 h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'sequence':[x['id'] for x in P['sequence']],'ordinary_units_passed':86,'baseline_ordinary_units_passed':86,'ordinary_units_ignored_per_arm':4,'fixture_results_exact':18,'convergence_records_exact':138,'all_owned_children_terminal':True,'all_samples_retained':True,'extension_runs':0,'historical_samples_scored':0,'candidate_accepted':False})
print('E098 frozen primary cohort terminal; read-only assessment next.',flush=True)
