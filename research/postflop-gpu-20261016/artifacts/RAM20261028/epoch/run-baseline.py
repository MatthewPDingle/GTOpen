import sys,json,re,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import common as h
assert len(sys.argv)==2;h.pin(h.EPOCH/'baseline-protocol.json',sys.argv[1]);P=h.read(h.EPOCH/'baseline-protocol.json')
def verify():
 h.custody();h.pin(h.EPOCH/'baseline-protocol.json',sys.argv[1])
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();O=h.ROOT/'runs/RAM20261028-execution';O.mkdir(exist_ok=False)
assert shutil.disk_usage(h.ROOT).free>=P['required_free_bytes']
anchor=h.read(h.EPOCH/'exact-anchor.json')
with h.ar.exclusive_lock(h.ROOT/'epoch-sequence.lock'):
 for record in P['sequence']:
  verify();h.ar.refuse_active(h.ar.live_status())
  binary=h.ROOT/'binaries'/(record['binary']+'.exe');manifest=binary.with_suffix('.manifest.json')
  cmd=[sys.executable,str(h.EPOCH/'runner.py'),'--id',record['id'],'--title',record['title'],'--kind',record['kind'],'--binary',str(binary),'--build-manifest',str(manifest),'--test','*'if record['unit']else'postflop_complete_cycle']
  if record['unit']:cmd.append('--not-ignored')
  h.child(cmd,O,record['id']);verify()
  r=h.read(h.ROOT/'runs'/record['id']/'report.json')
  assert r['returncode']==0 and r['status']=='measured'
  assert r['provenance']['source_sha256']==h.custody()
  if record['unit']:
   raw=(h.ROOT/'runs'/record['id']/'stdout.log').read_text(encoding='utf-8')
   assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('86','0','4','0','0')]
  else:assert h.exact(record['id'])==anchor
  print('Completed',record['id'],'exactness pass',flush=True)
 h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'all_owned_children_terminal':True,'all_samples_retained':True,'sequence':[x['id']for x in P['sequence']],'unit_passed':86,'unit_ignored':4,'scored_processes':5,'warmup_processes':1,'full_result_records_exact':18,'convergence_checkpoints_exact':138,'historical_timing_samples_scored':0,'extension_runs':0,'performance_gain_claimed':False})
h.child([sys.executable,str(h.EPOCH/'assess-baseline.py'),sys.argv[1]],O,'assessment',120)
h.custody();print('Fresh E080 baseline completed on X with all exactness checks.',flush=True)
