import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
K=ROOT/'runs/E052-kernel-control';P=old.read(K/'protocol.json');EP=old.read(K/'execution-plan.json');r=old.read(K/'report.json');assert r['status']=='pass_scoped_show_raw_equivalence'
for p,h in EP['input_sha256'].items():old.pin(p,h)
for name in ['rustc','probe']:
 e=old.read(K/'execution'/(name+'.exit.json'));assert e['returncode']==0 and e['error'] is None and e['cleanup'] is None
corpus=old.read(K/'corpus.json');gs={g['id']:g for g in corpus['geometries']};cases=corpus['cases'];checks=0;outputs=inputs=guards=active=0;seen=set()
mapping={'nodes':'nodes','win':'node_twin','lose':'node_tlose','tie':'node_ttie','river':'node_river_slot','rsrc':'rsrc_o','po':'p_off','pc':'p_cnt','pi':'p_idx','pl':'p_lower','pu':'p_upper','oo':'o_off','oc':'o_cnt','oi':'o_idx','co':'o_card_off','cp':'o_card_pos','same':'same_p','c1':'pc1','c2':'pc2','slots':'cfv_slot'}
for g in gs.values():
 a=g['arrays'];co=a['o_card_off'];cp=a['o_card_pos'];m=g['m_o'];base,end=co[53],co[105]
 assert base>0 and end-base==2*m and 0<=m<=1081 and g['nh_o']<=1326
 assert all(0<=pos<m and pos==int.from_bytes(pos.to_bytes(2,'little'),'little') for pos in cp[base:end]);checks+=2
with (K/'execution/raw-results.jsonl').open() as stream:
 for i,line in enumerate(stream):
  row=json.loads(line);c=cases[i];g=gs[c['geometry']];record=row['record'];assert record['case_id']==c['id'] and c['id'] not in seen;seen.add(c['id']);checks+=1
  b=row['baseline_output_bits'];n=row['candidate_output_bits'];assert b==n;outputs+=2*len(b);checks+=1
  mask=[bool(v) and c['count']>0 for v in g['output_active']];assert len(b)==len(mask)==len(g['output_initial']);checks+=1
  for j,enabled in enumerate(mask):
   if enabled:active+=1
   else:assert b[j]==n[j]==g['output_initial'][j];guards+=2
  expected={name:g['arrays'][key] for name,key in mapping.items()}|{'reach':c['reach_o_bits']}
  for arm in ['baseline','candidate']:
   actual=row[arm+'_actual_device_inputs'];assert len(actual)==21 and len({v['buffer'] for v in actual})==21 and {v['buffer']:v['actual_device_words'] for v in actual}==expected;inputs+=sum(len(v['actual_device_words']) for v in actual);checks+=1
  assert record['baseline_dynamic_shared_bytes']==4*g['nh_o']+16*g['m_o'] and record['candidate_dynamic_shared_bytes']==4*g['nh_o']+12*g['m_o'];checks+=1
assert len(seen)==328 and outputs==r['full_output_words_both_arms'] and inputs==r['full_actual_device_input_words_both_arms'] and guards==r['guard_word_checks_both_arms'] and active==P['expected_active_words'];checks+=1
old.pin(K/'execution/raw-results.jsonl',r['raw_sha256']);old.pin(K/'corpus.json',r['corpus_sha256']);assert (K/'accepted-evaluator.rs').read_bytes()==(old.REPO/'crates/solver/src/evaluator.rs').read_bytes();checks+=1
R=ROOT/'comparisons/E052-kernel-control';R.mkdir();old.save(R/'report.json',{'at':old.now(),'status':'pass_scoped_show_raw_equivalence','cases':328,'kernel_launches':656,'root_replay_checks':checks,'actual_complete_outputs_both_arms':outputs,'actual_complete_immutable_device_words_both_arms':inputs,'actual_guard_checks_both_arms':guards,'active_words_compared':active,'full_raw_file_sha256':r['raw_sha256'],'report_sha256':old.sha(K/'report.json'),'all_consumed_positions_fit_u16':True,'all_full_outputs_inputs_guards_exact':True,'root_replay_external_independent_review':False,'performance_measured':False,'candidate_accepted':False})
old.save(K/'execution/terminal.json',{'at':old.now(),'session':47442,'returncode':0,'all_children_terminal':True,'root_report_sha256':old.sha(R/'report.json')})
H=ROOT/'runs/E052-build-plan';H.mkdir();prior=ROOT/'runs/E051-build-plan';D=ROOT/'runs/E052-source'
script=(prior/'build.py').read_text().replace('E051','E052').replace('accepted E020','accepted E051').replace("sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old","sys.path.insert(0,str(HERE.parent/'accepted-E051'));import common_e051 as old")
(H/'build.py').write_text(script,encoding='utf-8',newline='\n')
p=old.read(prior/'build-protocol.json');p.update(id='E052-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(ROOT/'runs/accepted-E051/protected-main.json'))
p['phases']=[{**x,'target':x['target'].replace('e051','e052'),'outputs':{k:v.replace('E051','E052') for k,v in x['outputs'].items()}} for x in p['phases']]
p['owned']={}
for rel,b,c in [('crates/solver/src/gpu/kernels.cu','baseline.cu','candidate.cu'),('crates/solver/src/gpu/mod.rs','baseline-mod.rs','candidate-mod.rs')]:p['owned'][rel]={'base':str(D/b),'base_sha256':old.sha(D/b),'candidate':str(D/c),'candidate_sha256':old.sha(D/c)}
paths=[H/'build.py',D/'manifest.json',D/'source-review.json',R/'report.json',K/'report.json',K/'protocol.json',K/'execution-plan.json',K/'execution/complete.json',K/'execution/terminal.json',ROOT/'runs/E052-resource/report.json',ROOT/'comparisons/E052-resource-root-check/report.json',Path(p['protected_main']),ROOT/'runs/accepted-E051/common_e051.py',old.REPO/'tools/postflop_autoresearch.py']
for v in p['owned'].values():paths +=[Path(v['base']),Path(v['candidate'])]
p['input_sha256']={str(x):old.sha(x) for x in paths};old.save(H/'build-protocol.json',p)
published={}
for directory in [H,R,K,ROOT/'runs/E052-resource',ROOT/'comparisons/E052-resource-root-check']:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.pdb'] or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-build-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E052');e.update(stage='Raw controls passed; fresh integrated builds',reason='328cases/656launches,1519952output words/2762740actual immutable words/1164920guard words exact. Source/resources pass. Complete solve performance remains unmeasured.');e['evidence'] +=[{'label':'E052 full raw control root replay','url':'evidence/E052-kernel-control/report.json'},{'label':'E052 fixed integrated build protocol','url':'evidence/E052-build-plan/build-protocol.json'}];st.update(updated_at=old.now(),stage='E052 fresh integrated builds',activity='Build fresh feature and GPU-only binaries; restore acceptedE051 after each terminal phase.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'checks':checks,'raw_outputs':outputs,'raw_inputs':inputs,'published':len(published),'build_protocol_sha256':old.sha(H/'build-protocol.json')}),flush=True)
