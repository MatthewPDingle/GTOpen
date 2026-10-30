"""Replay complete raw fusion data, repair only stale summary counts, freeze builds."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();K=ROOT/'runs/E053-kernel-control';EP=old.read(K/'execution-plan-r2.json');P=old.read(K/'protocol.json');summary=old.read(K/'report.json')
for p,h in EP['input_sha256'].items():old.pin(p,h)
checks=[]
def ck(label,value):checks.append({'label':label,'passed':bool(value)});assert value,label
for label in ['rustc','probe']:
 e=old.read(K/'execution'/(label+'.exit.json'));ck(label+' terminal0',e['returncode']==0 and e['error'] is None and e['cleanup'] is None)
markers=[json.loads(x.split('E053_EXACT ',1)[1]) for x in (K/'execution/probe.stdout.log').read_text().splitlines() if 'E053_EXACT ' in x];ck('367markers',len(markers)==367)
ck('native complete364pairs728launches',markers[-1]['comparison_pairs']==P['cases']==364 and markers[-1]['kernel_launches']==P['kernel_launches']==728 and markers[-1]['all_output_bits_exact'] and markers[-1]['all_inputs_unchanged'])
def fnv(data):
 n=0xcbf29ce484222325
 for b in data:n=((n^b)*0x100000001b3)&0xffffffffffffffff
 return f'{n:016x}'
for arm in ['baseline','candidate']:
 ck(arm+' exact source fingerprint',markers[1][arm+'_source_fnv1a64']==fnv((K/(arm+'.cu')).read_bytes()))
 ck(arm+' same actual PTX as resource probe',(K/'execution'/(arm+'.ptx')).read_bytes()==(ROOT/'runs/E053-resource/execution'/(arm+'-compute_120.ptx')).read_bytes())
corpus=old.read(K/'corpus.json');gs={g['id']:g for g in corpus['geometries']};cases=corpus['cases'];ck('fixed364cases',len(cases)==364 and len(gs)==36)
mapping={'nodes':'nodes','win':'node_twin','lose':'node_tlose','tie':'node_ttie','river':'node_river_slot','rsrc':'rsrc_o','po':'p_off','pc':'p_cnt','pi':'p_idx','pl':'p_lower','pu':'p_upper','oo':'o_off','oc':'o_cnt','oi':'o_idx','co':'o_card_off','cp':'o_card_pos','same':'same_p','c1':'pc1','c2':'pc2','slots':'cfv_slot'}
outputs=inputs=guards=active=0;seen=set()
with (K/'execution/raw-results.jsonl').open() as stream:
 for i,line in enumerate(stream):
  row=json.loads(line);c=cases[i];g=gs[c['geometry']];record=row['record'];ck('case'+str(i)+' identity',record==markers[i+2] and record['case_id']==c['id'] and c['id'] not in seen);seen.add(c['id'])
  b,n=row['baseline_output_bits'],row['candidate_output_bits'];ck('case'+str(i)+' all output bits',b==n and len(b)==len(g['output_initial']));outputs+=2*len(b)
  mask=[bool(x) and c['count']>0 for x in g['output_active']]
  for j,enabled in enumerate(mask):
   if enabled:active+=1
   else:assert b[j]==n[j]==g['output_initial'][j];guards+=2
  ck('case'+str(i)+' same shared reservation',record['baseline_dynamic_shared_bytes']==record['candidate_dynamic_shared_bytes']==4*g['nh_o']+16*g['m_o'])
  expected={name:g['arrays'][key] for name,key in mapping.items()}|{'reach':c['reach_o_bits']}
  for arm in ['baseline','candidate']:
   actual=row[arm+'_actual_device_inputs'];ck('case'+str(i)+' '+arm+' all actual device inputs',len(actual)==21 and len({x['buffer'] for x in actual})==21 and {x['buffer']:x['actual_device_words'] for x in actual}==expected);inputs+=sum(len(x['actual_device_words']) for x in actual)
ck('totals',len(seen)==364 and outputs==summary['full_output_words_both_arms'] and inputs==summary['full_actual_device_input_words_both_arms'] and guards==P['expected_guard_checks']==summary['guard_word_checks_both_arms'] and active==P['expected_active_words'])
ck('raw file hashes',old.sha(K/'execution/raw-results.jsonl')==summary['raw_sha256'] and old.sha(K/'corpus.json')==summary['corpus_sha256'])
ck('accepted rank oracle identical',(K/'accepted-evaluator.rs').read_bytes()==(old.REPO/'crates/solver/src/evaluator.rs').read_bytes())
corrected=summary|{'at':old.now(),'cases':len(cases),'kernel_launches':markers[-1]['kernel_launches'],'preserved_original_report_sha256':old.sha(K/'report.json'),'assessment_only_repair':'Top-level328/656summary literals were inherited; native complete marker, raw364records, all vectors and assertions already cover364/728. Correct counts from raw evidence only; no native rerun.'}
old.save(K/'report-r2.json',corrected)
RR=ROOT/'comparisons/E053-kernel-control-root-check';RR.mkdir();old.save(RR/'report.json',{'at':old.now(),'status':'pass_scoped_show_raw_equivalence','cases':364,'kernel_launches':728,'checks_passed':len(checks),'checks':checks,'actual_complete_outputs_both_arms':outputs,'actual_complete_immutable_device_words_both_arms':inputs,'actual_guard_checks_both_arms':guards,'active_words_compared':active,'all_full_outputs_inputs_guards_exact':True,'full_raw_file_sha256':summary['raw_sha256'],'corrected_native_report_sha256':old.sha(K/'report-r2.json'),'root_replay_external_independent_review':False,'performance_measured':False,'candidate_accepted':False})
old.save(K/'execution/terminal.json',{'at':old.now(),'returncode':0,'all_children_terminal':True,'root_report_sha256':old.sha(RR/'report.json'),'no_session_handle_direct_exec_completed':True})
H=ROOT/'runs/E053-build-plan';H.mkdir();prior=ROOT/'runs/E052-build-plan';D=ROOT/'runs/E053-source'
(H/'build.py').write_text((prior/'build.py').read_text().replace('E052','E053'),encoding='utf-8',newline='\n')
p=old.read(prior/'build-protocol.json');p.update(id='E053-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(ROOT/'runs/accepted-E051/protected-main.json'),owned={'crates/solver/src/gpu/kernels.cu':{'base':str(D/'baseline.cu'),'base_sha256':old.sha(D/'baseline.cu'),'candidate':str(D/'candidate.cu'),'candidate_sha256':old.sha(D/'candidate.cu')}})
p['phases']=[{**x,'target':x['target'].replace('e052','e053'),'outputs':{k:v.replace('E052','E053') for k,v in x['outputs'].items()}} for x in p['phases']]
paths=[H/'build.py',D/'manifest.json',D/'source-review.json',D/'baseline.cu',D/'candidate.cu',RR/'report.json',K/'report-r2.json',K/'execution-plan-r2.json',K/'execution/complete.json',K/'execution/terminal.json',ROOT/'runs/E053-resource/report.json',ROOT/'comparisons/E053-resource-root-check/report.json',Path(p['protected_main']),ROOT/'runs/accepted-E051/common_e051.py',old.REPO/'tools/postflop_autoresearch.py'];p['input_sha256']={str(x):old.sha(x) for x in paths};old.save(H/'build-protocol.json',p)
published={}
for directory,prefix in [(H,H.name),(RR,RR.name),(K,'E053-kernel-control-native'),(ROOT/'runs/E053-resource','E053-resource'),(ROOT/'comparisons/E053-resource-root-check','E053-resource-root-check')]:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.pdb'] or '__pycache__' in src.parts:continue
  key=prefix+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data,key
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-build-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E053');e.update(stage='Raw exactness passed; integrated builds',reason='364cases/728launches,1687304output words/3065944actual immutable words/1292824guards exact; same PTX as resource probe. Source/resources/ownership pass. Speed remains unmeasured.');e['evidence'] +=[{'label':'E053 root full raw replay','url':'evidence/E053-kernel-control-root-check/report.json'},{'label':'E053 corrected native summary, original preserved','url':'evidence/E053-kernel-control-native/report-r2.json'},{'label':'E053 frozen integrated build protocol','url':'evidence/E053-build-plan/build-protocol.json'}];st.update(updated_at=old.now(),stage='E053 fresh integrated builds',activity='364raw cases exact, including signalingNaNs. Compile fresh feature/primary artifacts and restore acceptedE051 after each phase.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'checks':len(checks),'outputs':outputs,'actual_inputs':inputs,'published':len(published),'build_protocol_sha256':old.sha(H/'build-protocol.json')}),flush=True)
