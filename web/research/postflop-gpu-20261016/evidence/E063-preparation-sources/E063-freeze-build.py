"""Replay fresh raw kernel evidence and freeze integrated E063 builds."""
import ast,bisect,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
K=ROOT/'runs/E063-kernel-control';RES=ROOT/'runs/E063-resource';S=ROOT/'runs/E063-source';P=old.read(K/'execution-plan.json');q=old.read(K/'report.json');resource=old.read(RES/'report.json');checks=0
def check(v):
 global checks
 assert v;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
for label in ['rustc','probe']:
 r=old.read(K/'execution'/(label+'.exit.json'));check(r['returncode']==0 and r['error'] is r['cleanup'] is None)
check(q['cases']==364 and q['kernel_launches']==728 and q['status']=='pass_scoped_show_raw_equivalence')
check(all(resource['gates'].values()))
for v in ['baseline','candidate']:check((K/'execution'/(v+'.ptx')).read_bytes()==(RES/'execution'/(v+'-compute_120.ptx')).read_bytes())
old.pin(K/'execution/raw-results.jsonl',q['raw_sha256']);corpus=old.read(K/'corpus.json');gs={g['id']:g for g in corpus['geometries']};cases=corpus['cases'];check(len(cases)==364)
markers=[json.loads(x.split('E063_EXACT ',1)[1]) for x in (K/'execution/probe.stdout.log').read_text().splitlines() if x.startswith('E063_EXACT ')];nativecases=[x for x in markers if x['stage']=='full_show_exact'];check(len(nativecases)==364)
names={'nodes':'nodes','win':'node_twin','lose':'node_tlose','tie':'node_ttie','river':'node_river_slot','rsrc':'rsrc_o','po':'p_off','pc':'p_cnt','pi':'p_idx','pl':'p_lower','pu':'p_upper','oo':'o_off','oc':'o_cnt','oi':'o_idx','co':'o_card_off','cp':'o_card_pos','same':'same_p','c1':'pc1','c2':'pc2','slots':'cfv_slot'}
def packed_expected(g):
 a=g['arrays'];lo=list(a['p_lower']);hi=list(a['p_upper']);pb=a['p_off'][1]
 for j in range(pb,pb+g['m_p']):
  i=a['p_idx'][j]
  for card,word in [(a['pc1'][i],lo),(a['pc2'][i],hi)]:
   positions=a['o_card_pos'][a['o_card_off'][53+card]:a['o_card_off'][54+card]]
   assert positions==sorted(positions)
   l=bisect.bisect_left(positions,a['p_lower'][j]);u=bisect.bisect_left(positions,a['p_upper'][j])
   word[j]|=(l<<11)|(u<<17)
 return lo,hi

outputs=immutable=guards=0;count=0
with (K/'execution/raw-results.jsonl').open(encoding='utf-8') as f:
 for i,line in enumerate(f):
  row=json.loads(line);case=cases[i];g=gs[case['geometry']];check(row['record']==nativecases[i] and row['record']['case_id']==case['id'])
  b,c=row['baseline_output_bits'],row['candidate_output_bits'];check(b==c and len(b)==len(g['output_initial']));outputs+=2*len(b)
  active=[bool(x) and case['count']>0 for x in g['output_active']]
  for index,owned in enumerate(active):
   if not owned:check(b[index]==c[index]==g['output_initial'][index]);guards+=2
  expected={n:g['arrays'][key] for n,key in names.items()}|{'reach':case['reach_o_bits']}
  for arm in ['baseline','candidate']:
   snap=row[arm+'_actual_device_inputs'];check(len(snap)==21 and len({v['buffer'] for v in snap})==21)
   arm_expected=dict(expected)
   if arm=='candidate':arm_expected['pl'],arm_expected['pu']=packed_expected(g)
   check({v['buffer']:v['actual_device_words'] for v in snap}==arm_expected);immutable+=sum(len(v['actual_device_words']) for v in snap)
  check([v for v in row['baseline_actual_device_inputs'] if v['buffer'] not in ['pl','pu']]==[v for v in row['candidate_actual_device_inputs'] if v['buffer'] not in ['pl','pu']]);count+=1
check(count==364 and outputs==q['full_output_words_both_arms']==1687304 and immutable==q['full_actual_device_input_words_both_arms']==3065944 and guards==q['guard_word_checks_both_arms']==1292824)
R=ROOT/'comparisons/E063-kernel-control-root-check';R.mkdir()
old.save(R/'report.json',{'id':R.name,'at':old.now(),'status':'pass_scoped_show_raw_equivalence','checks':checks,'cases':364,'kernel_launches':728,'full_output_words_both_arms':outputs,'full_actual_device_input_words_both_arms':immutable,'guard_word_checks_both_arms':guards,'all_full_outputs_inputs_guards_exact':True,'resource_and_raw_ptx_byte_identical':True,'raw_sha256':q['raw_sha256'],'corpus_sha256':q['corpus_sha256'],'resource_report_sha256':old.sha(RES/'report.json'),'current_source_candidate':'E063','packed_boundary_representation_independently_validated':True,'source_activated':False,'performance_measured':False,'candidate_accepted':False,'limits':'Full raw direct-kernel bytes, actual post-device immutable inputs, and guard ranges. Retained corpus reused with fresh outputs. Not complete solver state/graph/behavior/material/holdout or speed qualification. Root replay is not external independent review. Candidate boundary words intentionally differ; root bisect reconstruction verifies all actual words, raw executor separately used linear classification. Other19buffers exact across arms. Retained corpus protocol is provenance only.'})
old.save(K/'execution/terminal.json',{'at':old.now(),'native_child_receipt_sha256':old.sha(K/'execution/probe.exit.json'),'returncode':0,'all_children_terminal':True,'complete_sha256':old.sha(K/'execution/complete.json'),'root_report_sha256':old.sha(R/'report.json'),'no_native_reexecution':True})
H=ROOT/'runs/E063-build-plan';assert not H.exists();H.mkdir();prior=ROOT/'runs/E062-build-plan'
code=(prior/'build.py').read_text(encoding='utf-8').replace('E062','E063').replace('one-file','two-file');ast.parse(code);(H/'build.py').write_text(code,encoding='utf-8',newline='\n')
B=old.read(prior/'build-protocol.json');B.update(id='E063-final-build',at=old.now(),status='FROZEN_PRE_INTEGRATED_BUILD',accepted_source_sha256=old.BASE,source_form='one_fixed_new_per_card_cutoff_precomputation',protected_main=str(ROOT/'runs/accepted-E051/protected-main.json'),owned={n:{'base':str(S/b),'base_sha256':old.sha(S/b),'candidate':str(S/c),'candidate_sha256':old.sha(S/c)} for n,b,c in [('crates/solver/src/gpu/kernels.cu','baseline.cu','candidate.cu'),('crates/solver/src/gpu/mod.rs','baseline-mod.rs','candidate-mod.rs')]})
B['phases']=[{**x,'target':x['target'].replace('e060','e062'),'outputs':{k:v.replace('E062','E063').replace('one-file','two-file') for k,v in x['outputs'].items()}} for x in B['phases']]
for phase in B['phases']:check(not Path(phase['target']).exists())
paths=[H/'build.py',*S.iterdir(),RES/'protocol.json',RES/'report.json',K/'execution-plan.json',K/'report.json',K/'execution/complete.json',K/'execution/terminal.json',R/'report.json',Path(B['protected_main']),ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/D102-card-cutoffs-r3/report.json',ROOT/'runs/D102-card-cutoffs-r3/helper.rs',RES/'compiled-mechanism.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'tools/postflop_autoresearch.py',Path(__file__)]
B['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()};old.save(H/'build-protocol.json',B)
published={}
for folder in [H,R,K,RES]:
 for p in folder.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.exe','.pdb','.bin']:continue
  key='evidence/'+folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():check(dst.read_bytes()==p.read_bytes())
  else:dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:check(response.read()==p.read_bytes())
  published[key]=old.sha(p)
old.save(H/'pre-build-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'native_solver_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E063');e.update(stage='Fresh exact kernel control passed; integrated build',reason='364pairs/728launches pass,1,687,304full output words/3,065,944actual per-arm inputs (candidate boundaries independently validated)/1,292,824guards exact. Same resource-qualified PTX. Build fresh feature/primary binaries; no solver speed measurement yet.');e['evidence'].extend([{'label':'Fresh full raw root replay','url':'evidence/'+R.name+'/report.json'},{'label':'Fresh integrated build protocol','url':'evidence/'+H.name+'/build-protocol.json'}]);st.update(updated_at=old.now(),stage='E063 fresh integrated builds',activity='Packed per-card cutoff form passes complete direct GPU numerical evidence. Fresh solver builds next; accepted E051restored between phases.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'build_protocol_sha256':old.sha(H/'build-protocol.json'),'root_checks':old.read(R/'report.json')['checks'],'full_raw_outputs_exact':True,'published':len(published)}),flush=True)
