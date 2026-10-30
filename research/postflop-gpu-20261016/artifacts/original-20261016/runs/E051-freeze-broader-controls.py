"""Freeze sixteen fixed broader controls only after all correctness compilers are terminal."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
B=ROOT/'runs/E051-broader-build';assert old.read(B/'terminal.json')['returncode']==0 and old.read(B/'complete.json')['all_compilers_terminal']
H=ROOT/'runs/E051-broader-controls-plan';H.mkdir()
native=r'''import json,re,sys
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
'''
(H/'native.py').write_text(native,encoding='utf-8');ast.parse(native)
root=r'''import json,re,sys
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
'''
(H/'root-check.py').write_text(root,encoding='utf-8');ast.parse(root)
rows=[];binaries={};paths=[H/'native.py',H/'root-check.py',B/'complete.json',B/'terminal.json',ROOT/'runs/E051-broader-build-plan/protocol.json',ROOT/'comparisons/E051-fresh16-confirmation/report.json',ROOT/'comparisons/E051-fresh16-root-check/report.json',ROOT/'runs/E051-confirmation-plan/confirmation-publication.json',ar.REPO/'tools/postflop_autoresearch.py',ar.REPO/'tools/postflop_validate_controls.py',ROOT/'runs/E051-broader-scout/report.json']
suite_ids={'baseline':{},'candidate':{}}
tests={'state':('postflop_state_perf','postflop_states',False,1),'menu':('postflop_action_menus','postflop_action_menus',False,1),'resume':('postflop_resume_state','postflop_resume_state',False,1),'gpu':('gpu','*',True,6),'f32':('postflop_autoresearch','postflop_complete_cycle',False,1),'paging':('continuation_paging','paging_preserves_resident_trajectories_and_rejects_invalid_inputs',True,1),'rejection':('continuation_symmetry','symmetric_continuation_rejects_unsupported_inputs_without_mutation',True,1),'stored':('solver','gpu::continuation::storage::device_tests::direct_gpu_storage_preserves_720_full_state_passes',True,1)}
for suite,(target,test,ordinary,passed) in tests.items():
 for arm in ['baseline','candidate']:
  if suite in ['state','menu','resume','gpu']:stem='E051-broader-'+arm+'-'+target
  elif suite=='f32':stem='SG-E020-postflop_autoresearch' if arm=='baseline' else 'E051-postflop_autoresearch'
  elif suite in ['paging','rejection']:stem=('E020-' if arm=='baseline' else 'E051-broader-')+target
  else:stem='E020-continuation-tests' if arm=='baseline' else 'E051-feature-solver'
  binary=ROOT/'binaries'/(stem+'.exe');manifest=binary.with_suffix('.manifest.json');m=old.read(manifest);old.pin(binary,m['binary_sha256'])
  expected=old.BASE|({'crates/solver/src/gpu/kernels.cu':'a926bf0bc818a2ba808c862b59a552dfb7ade453ca18f347b4307784e47d9647'} if arm=='candidate' else {})
  assert m['source_sha256']==expected
  binaries[stem]={'path':str(binary),'sha256':old.sha(binary),'manifest':str(manifest),'manifest_sha256':old.sha(manifest)};paths.extend([binary,manifest])
  identity='V051-'+suite+'-'+arm;assert not (ROOT/'runs'/identity).exists()
  row={'id':identity,'arm':arm,'suite':suite,'binary':stem,'test':test,'ordinary':ordinary,'passes':passed,'storage':'f32' if suite=='f32' else 'compressed'}
  if suite=='stored':row['stored_root']=str(ROOT/'runs/E051-broader-stored'/arm)
  rows.append(row)
  if suite in ['state','menu','resume']:suite_ids[arm][suite]=identity
history={'state':'V020-state','menu':'V020-menu','resume':'V020-resume'}
for identity in list(history.values())+['V020-f32-candidate']:paths.extend([ROOT/'runs'/identity/'report.json',ROOT/'runs'/identity/'stdout.log'])
io=old.read(ROOT/'runs/E051-broader-build-plan/protocol.json')['arms']
p={'id':'E051-broader-controls','at':old.now(),'status':'FROZEN_PRE_NATIVE','rows':rows,'binaries':binaries,'suite_ids':suite_ids,'historical_accepted_controls':history,'f32_accepted_anchor':'V020-f32-candidate','io_roots':{a:v['io_root'] for a,v in io.items()},'saved_names':['postflop-state.gto','action-menus.gto','postflop-resume.gto'],'input_sha256':{str(x):old.sha(x) for x in paths},'scope':'Fixed broader controls and complete latest save bytes. Primary/fresh16timing remain unchanged. No capacity/holdout/cumulative/adoption claim.'}
old.save(H/'protocol.json',p)
published={}
for directory in [H,B]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-native-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'new_native_runs':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(status='preparing',stage='Broader builds terminal; fixed16controls next',reason='Exact saved-state/menu/resume160snapshots perarm,F32three fixtures,sixGPUtests,paging160sweeps,rejection,stored720passes perarm. All temporary saves isolated onS. Material capacity/holdout/cumulative gates remain.');e['evidence'].append({'label':'E051 fixed broader controls protocol','url':'evidence/E051-broader-controls-plan/protocol.json'});st.update(state='running',stage='E051 broader correctness controls',activity='Fixed16before/after correctness invocations; no source adoption or new primary sampling.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'control_invocations':len(rows),'published':len(published)}),flush=True)
