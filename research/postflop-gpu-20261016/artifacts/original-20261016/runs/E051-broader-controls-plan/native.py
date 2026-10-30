import json,re,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'small-gain-confirmation-plan'));import common as old
sys.path.insert(0,str(old.REPO/'tools'));import postflop_validate_controls as vc
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
ROOT=old.ROOT;E=ROOT/'runs/E051-broader-controls-execution';O=ROOT/'comparisons/E051-broader-controls'
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify();assert not (ROOT/'gpu-run.lock').exists();assert not E.exists() and not O.exists();E.mkdir();O.mkdir()
for row in P['rows']:assert not (ROOT/'runs'/row['id']).exists()
records=[];seen={};f32={};fault=None
try:
 for row in P['rows']:
  verify();old.ar.refuse_active(old.ar.live_status());binary=P['binaries'][row['binary']]
  with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
   old.child([binary['path'],'--list'],E,row['id']+'-inventory',old.env(),120)
  listed=re.findall(r'^(.+): test$',(E/(row['id']+'-inventory.stdout.log')).read_text(encoding='utf-8'),re.M);assert len(listed)>0 and len(listed)==len(set(listed))
  selected=listed if row['test']=='*' else [x for x in listed if row['test'] in x]
  assert len(selected)==row['passes']
  if row['test']!='*':assert selected==[row['test']]
  env=old.env();env['POSTFLOP_AUTORESEARCH_STORAGE']=row['storage']
  if row['suite']=='stored':
   root=Path(row['stored_root']);assert not root.exists();root.mkdir(parents=True)
   env['GTO_SSD_STUDY_DIR']=str(root)
  command=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',row['id'],'--title','E051 broader '+row['id'],'--kind','validation','--binary',binary['path'],'--build-manifest',binary['manifest'],'--test',row['test']]
  if row['ordinary']:command.append('--not-ignored')
  old.child(command,E,row['id'],env,1200)
  verify();report=old.read(ROOT/'runs'/row['id']/'report.json');log=ROOT/'runs'/row['id']/'stdout.log';old.pin(log,report['stdout_sha256']);text=log.read_text(encoding='utf-8')
  assert report['status']=='measured' and report['returncode']==0 and report['binary_sha256']==binary['sha256'] and report['binary_build_manifest']['sha256']==binary['manifest_sha256']
  assert report['binary_build_manifest']['data']==old.read(binary['manifest']) and report['provenance']['source_sha256']==old.BASE
  result=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text);assert result==[(str(row['passes']),'0','0','0',str(len(listed)-len(selected)))]
  seen[row['id']]={'report':report,'text':text}
  if row['suite'] in ['state','menu','resume']:
   parsed=vc.read_run(row['id'],row['suite']);reference=P['historical_accepted_controls'][row['suite']]
   assert vc.canonical(parsed['records'])==vc.canonical(vc.read_run(reference,row['suite'])['records'])
  elif row['suite']=='f32':
   exact=old.exact_raw(row['id']);assert exact==old.exact_raw(P['f32_accepted_anchor']);f32[row['arm']]=exact
  elif row['suite']=='paging':assert '160 alternating board/player sweeps' in text
  elif row['suite']=='stored':
   passes=[json.loads(x.split('GPU_STORED_PASS ',1)[1]) for x in text.splitlines() if 'GPU_STORED_PASS ' in x]
   summaries=[json.loads(x.split('GPU_STORED_SUMMARY ',1)[1]) for x in text.splitlines() if 'GPU_STORED_SUMMARY ' in x]
   assert len(passes)==720 and all(x['passed'] is True for x in passes) and len({(x['entry'],x['iteration'],x['player']) for x in passes})==720
   assert len(summaries)==1 and summaries[0]['passes']==720 and all(summaries[0][k] is True for k in ['full_device_arrays_bitwise_equal','restored_arrays_bitwise_equal','values_bitwise_equal'])
  records.append({'id':row['id'],'arm':row['arm'],'suite':row['suite'],'passed':row['passes'],'report_sha256':old.sha(ROOT/'runs'/row['id']/'report.json'),'stdout_sha256':old.sha(log)})
  print('Completed broader',row['id'],flush=True)
 arms=[[vc.read_run(P['suite_ids'][arm][suite],suite) for suite in vc.SUITES] for arm in ['baseline','candidate']]
 controls=vc.compare(*arms);assert controls['status']=='pass' and controls['total_snapshots_each']==160
 assert f32['baseline']==f32['candidate']
 saved={}
 for arm,root in P['io_roots'].items():
  d=Path(root)/'target/research-fixtures';assert {p.name for p in d.iterdir()}==set(P['saved_names'])
  saved[arm]={p.name:{'path':str(p),'sha256':old.sha(p),'bytes':p.stat().st_size} for p in d.iterdir()}
 for name in P['saved_names']:
  a=Path(saved['baseline'][name]['path']);b=Path(saved['candidate'][name]['path']);assert a.stat().st_size==b.stat().st_size
  with a.open('rb') as x,b.open('rb') as y:
   while True:
    left,right=x.read(1048576),y.read(1048576);assert left==right
    if not left:break
 old.save(O/'report.json',{'id':'E051-broader-controls','at':old.now(),'status':'pass_broader_exact_controls_only','protocol_sha256':sys.argv[1],'checks':records,'saved_state_menu_resume':controls,'snapshots_each':160,'f32_fixtures_each':3,'f32_full_non_timing_and_checkpoints_exact':True,'gpu_suite_tests_each':6,'continuation_sweeps_each':160,'stored_full_state_passes_each':720,'latest_complete_save_files':saved,'latest_complete_save_files_byte_exact':True,'no_checkout_outputs':True,'accepted162_main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False,'limits':'Fixed broad control coverage only; GPU/CPU suite tolerance tests are separate from exact original/candidate payload comparisons. No forced SSD-spill or actual owned-capacity/whole-memory claim. Holdout/fresh-original cumulative/material-cost qualification remains pending.'})
 old.save(E/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'row_count':len(records),'all_children_terminal':True,'report_sha256':old.sha(O/'report.json'),'accepted162_main_live_ptx_unchanged':True,'candidate_accepted':False})
except BaseException as exc:
 fault=repr(exc);old.save(E/'failure.json',{'at':old.now(),'error':fault,'completed_rows':records,'candidate_accepted':False});raise
print(json.dumps({'status':'broader_terminal_pending_root_replay','complete_sha256':old.sha(E/'complete.json'),'report_sha256':old.sha(O/'report.json')}),flush=True)
