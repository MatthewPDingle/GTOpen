import json,re,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'small-gain-confirmation-plan'));import common as old
sys.path.insert(0,str(old.REPO/'tools'));import postflop_validate_controls as vc
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();assert not (old.ROOT/'gpu-run.lock').exists()
E=old.ROOT/'runs/E051-broader-controls-execution';T=old.read(E/'terminal.json');require=old.save
assert T['returncode']==0 and T['complete_sha256']==old.sha(E/'complete.json')
QPATH=old.ROOT/'comparisons/E051-broader-controls/report.json';q=old.read(QPATH);assert q['status']=='pass_broader_exact_controls_only';checks=0
for row in P['rows']:
 r=old.read(old.ROOT/'runs'/row['id']/'report.json');log=old.ROOT/'runs'/row['id']/'stdout.log';old.pin(log,r['stdout_sha256']);text=log.read_text(encoding='utf-8')
 assert r['returncode']==0 and r['status']=='measured' and r['provenance']['source_sha256']==old.BASE
 e=old.read(E/(row['id']+'.exit.json'));assert e['returncode']==0 and e['error'] is e['cleanup'] is None
 listed=re.findall(r'^(.+): test$',(E/(row['id']+'-inventory.stdout.log')).read_text(encoding='utf-8'),re.M);selected=listed if row['test']=='*' else [x for x in listed if row['test'] in x]
 assert len(selected)==row['passes'];assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)==[(str(row['passes']),'0','0','0',str(len(listed)-len(selected)))]
 checks+=3
 if row['suite']=='f32':assert old.exact_raw(row['id'])==old.exact_raw(P['f32_accepted_anchor']);checks+=1
 if row['suite']=='stored':
  data=[json.loads(x.split('GPU_STORED_PASS ',1)[1]) for x in text.splitlines() if 'GPU_STORED_PASS ' in x];summary=[json.loads(x.split('GPU_STORED_SUMMARY ',1)[1]) for x in text.splitlines() if 'GPU_STORED_SUMMARY ' in x]
  assert len(data)==720 and len({(x['entry'],x['iteration'],x['player']) for x in data})==720 and all(x['passed'] for x in data)
  assert len(summary)==1 and all(summary[0][k] for k in ['full_device_arrays_bitwise_equal','restored_arrays_bitwise_equal','values_bitwise_equal']);checks+=2
controls=vc.compare(*[[vc.read_run(P['suite_ids'][arm][suite],suite) for suite in vc.SUITES] for arm in ['baseline','candidate']])
assert controls==q['saved_state_menu_resume'] and controls['total_snapshots_each']==160;checks+=1
for name in P['saved_names']:
 a=q['latest_complete_save_files']['baseline'][name];b=q['latest_complete_save_files']['candidate'][name]
 old.pin(a['path'],a['sha256']);old.pin(b['path'],b['sha256']);assert a['sha256']==b['sha256'] and a['bytes']==b['bytes']
 with Path(a['path']).open('rb') as x,Path(b['path']).open('rb') as y:
  while True:
   l,r=x.read(1048576),y.read(1048576);assert l==r
   if not l:break
 checks+=1
assert q['candidate_accepted'] is False and q['performance_measured'] is False
O=old.ROOT/'comparisons/E051-broader-root-check';O.mkdir();report={'id':'E051-broader-root-check','at':old.now(),'status':'pass_broader_only','root_cross_check_only':True,'checks':checks,'report_sha256':old.sha(QPATH),'terminal_sha256':old.sha(E/'terminal.json'),'snapshots_each':160,'all_f32_payloads_exact':True,'gpu_tests_each':6,'continuation_stored_passes_each':720,'latest3complete_save_files_byte_equal':True,'accepted162_main_live_ptx_unchanged':True,'candidate_accepted':False,'limits':'Root source/log/payload replay only; no external independent audit, forced SSD spill, capacity, holdout, cumulative or adoption claim.'};old.save(O/'report.json',report);print(json.dumps(report),flush=True)
