"""Root resource verification and one declarative original/new chance-kernel corpus."""
import hashlib,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
RES=ROOT/'runs/E048-resource';P=old.read(RES/'protocol.json');R=old.read(RES/'report.json');checks=0
def req(v,m):
 global checks
 assert v,m;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
req(R['status']=='pass_resource_feasibility_only' and all(R['gates'].values()),'all predeclared gates')
raw=(RES/'execution/probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E048_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E048_RESOURCE ' in x];req(markers==R['raw_markers'] and len(markers)==6,'raw marker inventory')
for label in ['rustc','probe']:
 e=old.read(RES/'execution'/(label+'.exit.json'));req(e['returncode']==0 and e['error'] is None and e['cleanup'] is None,'terminal child')
def entries(path):
 t=path.read_text(encoding='utf-8');result={};at=0
 while True:
  at=t.find('.visible .entry ',at)
  if at<0:return result
  par=t.index('(',at);name=t[at+len('.visible .entry '):par].strip();opening=t.index('{',par);end=opening+1;depth=1
  while depth:depth+=(t[end]=='{')-(t[end]=='}');end+=1
  req(name not in result,'unique entry');result[name]=t[at:end];at=end
be,ce=[entries(RES/'execution'/(v+'.ptx')) for v in ['baseline','candidate']]
req(set(be)==set(ce)==set(P['expected_entries']),'same nine entries')
for k in be:req((be[k]==ce[k])==(k not in P['changed_entries']),'exact expected changed entry set')
for k in P['changed_entries']:
 for v,table in [('baseline',be),('candidate',ce)]:
  header=table[k].split('{',1)[0];declarations=[line.strip() for line in header.splitlines() if '.param ' in line]
  req(len(declarations)==len(P['expected_abi'][k][v]),'all ABI declarations accounted')
  for i,(line,typ) in enumerate(zip(declarations,P['expected_abi'][k][v])):
   req(line.startswith('.param .'+typ+' ') and re.search(k+'_param_'+str(i)+r'(?:,|$)',line) is not None,'parameter type/index')
   req(('.ptr .align 1' in line)==(typ=='u64'),'pointer/alignment metadata')
  row=next(x for x in markers if x.get('stage')=='resource' and x['kernel']==k and x['variant']==v);req(row==R['details'][k][v],'queried resource exact')
 req(R['details'][k]['candidate']['registers']<=R['details'][k]['baseline']['registers'],'resource no-regression')
OUT=ROOT/'comparisons/E048-resource-root-check';OUT.mkdir()
old.save(OUT/'report.json',{'id':'E048-resource-root-check','at':old.now(),'status':'pass_resource_feasibility_only','checks':checks,'root_cross_check_only':True,'resource_report_sha256':old.sha(RES/'report.json'),'down_registers':[30,28],'up_registers':[30,30],'same_occupancy':[[64,24],[128,12],[256,6]],'exact_changed_abi_and_other7_entries':True,'kernel_launches':0,'solver_executions':0,'accepted162_main_live_ptx_unchanged':True,'candidate_accepted':False,'limits':'Root source/PTX/raw-marker/receipt verification, not external independent review or numerical/speed qualification.'})
HERE=ROOT/'runs/E048-kernel-control';HERE.mkdir()
for v in ['baseline','candidate']:(HERE/(v+'.ptx')).write_bytes((RES/'execution'/(v+'.ptx')).read_bytes())
(HERE/'probe.rs').write_bytes((ROOT/'runs/E048-control-probe.rs').read_bytes())
cases=[];seen=set()
def add(f,n0,n1,t,active,mode,perm,width,pattern,salt,label):
 d=[f,n0,n1,t,active,mode,perm,width,pattern,salt];key=tuple(d)
 if key in seen:return
 seen.add(key);cases.append({'id':len(cases),'descriptor':d,'group':label})
tails=[0,1,2,31,32,33,63,64,65,127,128,129,255,256,257,511,512,513,1023,1024,1325,1326]
for t in [1,32,64,128,256]:
 for mode in range(3):add(0,1326,1326,t,1,mode,0,52,0,0,'down_full_canonical')
for n in tails:
 for orientation in range(2):
  for mode in range(3):
   a,b=(n,max(0,n-3)) if orientation==0 else (max(0,n-3),n);add(0,a,b,128,1,mode,0,3,1,17,'down_tails')
for n in [0,17,1326]:add(0,n,n,128,0,0,0,52,0,3,'down_count_zero')
add(0,33,17,128,1,0,0,0,0,1,'down_empty_edges')
for n0,n1 in [(0,1326),(1326,0)]:
 for mode in range(3):add(0,n0,n1,128,1,mode,0,52,0,5,'down_one_player_zero')
for mode in range(3):add(0,17,129,128,1,mode,0,7,2,7,'down_scattered_cards')
for card in range(52):add(1,1326,0,128,1,0,0,1,3,card,'up_each_card_canonical')
for t in [1,32,64,128,256]:
 for mode in range(3):
  for perm in range(2):add(1,1326,0,t,1,mode,perm,52,0,0,'up_full_canonical')
for n in tails:
 for perm in range(2):
  for mode in range(3):add(1,n,0,128,1,mode,perm,3,1,19,'up_tails')
for width in [0,1,2,47,52]:
 for mode in range(3):
  for perm in range(2):add(1,129,0,128,1,mode,perm,width,2,5,'up_widths')
for n in [0,1,129,1326]:
 for perm in range(2):
  for mode in range(3):add(1,n,0,128,0,mode,perm,52,0,11,'up_count_zero')
counts={str(f):sum(c['descriptor'][0]==f for c in cases) for f in [0,1]}
old.save(HERE/'corpus.json',{'id':'E048-canonical-chance-corpus','at':old.now(),'status':'FROZEN_PRE_NATIVE','case_count':len(cases),'kernel_launches':2*len(cases),'families':{'0':'down_chance','1':'up_chance'},'family_case_counts':counts,'descriptor':['family','nh0_or_up_nh','nh1_or_zero','threads','active_count_flag','float_mode','permutation_mode','width','card_pattern','salt'],'float_modes':{'0':'all positive finite; membership observable individually','1':'signedzero/subnormal/quietNaN/infinities/mixed finite','2':'finite overflow stress and tiny finite'},'cases':cases,'raw_schema':'inputs:E048_IN1 then idu32,descriptor vec(lengthu64,u32 words),immutable vec-list(countu32,each vec),seed output vec-list. baseline/candidate:E048_OUT1 then id,actual immutable vec-list,full output vec-list. U64 masks split low/high u32, f32 values raw bits. Little endian.','coverage':'Both kernels, both player orientations/down hand asymmetry, every1326 canonical hand versus each52cards individually, zero counts/empty lists, tails, identity/nonidentity permutation tables, extra grids, float stress. No malformed inconsistent masks or >2^32 physical spans claim.','max_raw_bytes':1024**3,'max_case_array_words':1000000,'deduplication':'Identical prospective descriptors deduplicated deterministically before any execution; no observed-case exclusion.'})
old.save(HERE/'source-review.json',{'id':'E048-direct-control-source-review','at':old.now(),'status':'pass_to_one_frozen_original_gpu_control','root_review_only':True,'resource_root_check_sha256':old.sha(OUT/'report.json'),'case_count':len(cases),'kernel_launches':2*len(cases),'family_case_counts':counts,'reference':'Exact passed-resource original/new PTX in distinct modules. Identical typed canonical masks/card arrays uploaded to both arms, including unused representations. All actual immutable images read back and compared.','correctness':'Full mutable outputs compared bitwise; every unowned/guard word unchanged. Finite down matrix also checks independent CPU zero/copy membership. Three complete raw files retained. No hash substitutes for raw comparisons.','safety':'Every copy/kernel completes on one owned stream before buffers release; no cross-stream tracking. Descriptor-derived allocations bound active/guard rows and arbitrary valid permutations.','summary_counts':'Native comparator reads the frozen JSON corpus; completed-case and launch counters are derived from the actual loop, never copied constants.','limits':'Finite explicit corpus/canonical inputs; not universal floating payload, malformed input or speed proof. No full solver run yet.'})
prior=ROOT/'runs/E047-kernel-control';template=(prior/'execute.py').read_text(encoding='utf-8');prefix=template[:template.index('with old.ar.exclusive_lock')].replace('E047','E048')
body='''with old.ar.exclusive_lock(old.ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(old.ROOT).free>=54*1024**3
 assert not OUT.exists() and not (HERE/'probe.exe').exists() and not Path(P['raw_output']).exists();OUT.mkdir()
 assert old.read(P['resource_report'])['status']=='pass_resource_feasibility_only'
 old.save(OUT/'before.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'all_inputs_verified':True,'accepted162_unchanged':True})
 env=old.env();child(P['rustc_command'],'rustc',env,180);old.custody()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 binary=HERE/'probe.exe';data=binary.read_bytes();assert all((HERE/(v+'.ptx')).read_bytes() in data for v in ['baseline','candidate'])
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(binary),'exact_ptx_embedded':True,'rustc_terminal':True,'native_executions':0})
 env['E048_CONTROL_DIR']=P['raw_output'];child([str(binary)],'probe',env,300);old.custody()
 raw=(OUT/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E048_CONTROL ',1)[1]) for x in raw.splitlines() if 'E048_CONTROL ' in x]
 corpus=old.read(HERE/'corpus.json');cases=corpus['cases'];assert len(markers)==len(cases)+1
 for c,m in zip(cases,markers[:-1]):assert m['stage']=='case' and m['id']==c['id'] and m['descriptor']==c['descriptor'] and m['full_outputs_exact'] and m['actual_immutable_inputs_exact'] and m['guards_exact']
 end=markers[-1];assert end['stage']=='complete' and end['cases']==len(cases) and end['kernel_launches']==2*len(cases) and end['full_outputs_exact'] and end['actual_immutable_inputs_exact']
 assert (OUT/'probe.stderr.log').read_bytes()==b''
 rawdir=Path(P['raw_output']);files={str(p):old.sha(p) for p in rawdir.iterdir()};assert len(files)==3 and sum(p.stat().st_size for p in rawdir.iterdir())<=corpus['max_raw_bytes']
 old.save(OUT/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'source_review_sha256':old.sha(HERE/'source-review.json'),'binary_sha256':old.sha(binary),'raw_marker_summary':end,'raw_file_sha256':files,'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'all_children_terminal':True,'accepted162_main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False})
 print(json.dumps({'summary':end,'complete_sha256':old.sha(OUT/'complete.json')},indent=2),flush=True)
'''
(HERE/'execute.py').write_text(prefix+body,encoding='utf-8')
p=old.read(prior/'protocol.json');p.update(id='E048-kernel-control',at=old.now(),resource_report=str(RES/'report.json'),raw_output=str(HERE/'evidence'),expected_cases=len(cases),expected_launches=2*len(cases),criterion='All full GPU outputs and actual immutable input images exact, guards unchanged; complete raw inputs/outputs retained.',max_raw_evidence_bytes=1024**3)
p['rustc_command']=[x.replace('E047-kernel-control','E048-kernel-control') for x in p['rustc_command']]
deps={n:h for n,h in p['input_sha256'].items() if '/build/' in n.replace('\\','/')};refs=[HERE/n for n in ['probe.rs','baseline.ptx','candidate.ptx','corpus.json','source-review.json','execute.py']]+[RES/'report.json',OUT/'report.json',ROOT/'runs/E048-design/manifest.json',ar.REPO/'tools/postflop_autoresearch.py',ROOT/'runs/small-gain-confirmation-plan/common.py'];p['input_sha256']=deps|{str(x):old.sha(x) for x in refs};old.save(HERE/'protocol.json',p)
published={}
for directory in [RES,OUT,HERE]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);raw=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==raw
  else:dst.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(src)
old.save(HERE/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'kernel_launches':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);e=next(x for x in s['experiments'] if x['id']=='E048');e.update(stage='Resource gate passed; fixed raw GPU comparator next',reason=f'Both chance kernels pass ABI/resource checks; down registers30 to28/up30 unchanged. Fixed{len(cases)}case/{2*len(cases)}launch corpus covers all canonical card relations and stress. No solver speed measured.');e['evidence'].extend([{'label':'E048 root resource verification','url':'evidence/E048-resource-root-check/report.json'},{'label':'E048 frozen direct GPU corpus','url':'evidence/E048-kernel-control/corpus.json'}]);s.update(state='running',stage='E048 direct GPU numerical controls',activity='One original-mask/new-card raw comparator before host implementation or solve timing.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
print(json.dumps({'resource_root_sha256':old.sha(OUT/'report.json'),'control_protocol_sha256':old.sha(HERE/'protocol.json'),'cases':len(cases),'family_cases':counts}),flush=True)
