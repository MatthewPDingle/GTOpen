"""Replay E055 resource evidence and freeze the complete action raw matrix."""
import json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
RES=ROOT/'runs/E055-resource';P=old.read(RES/'protocol.json');Q=old.read(RES/'report.json');EX=RES/'execution'
for p,h in P['input_sha256'].items():old.pin(p,h)
assert Q['status']=='pass_resource_feasibility_only' and all(Q['gates'].values())
for label in ['rustc','probe']:
 r=old.read(EX/(label+'.exit.json'));assert r['returncode']==0 and r['error'] is r['cleanup'] is None
old.save(EX/'terminal.json',{'at':old.now(),'exec_chunk_id':'a76b41','returncode':0,'complete_sha256':old.sha(EX/'complete.json'),'compiler_and_probe_terminal':True,'kernel_solver_executions':0})
markers=[json.loads(x.split('E055_RESOURCE ',1)[1]) for x in (EX/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'E055_RESOURCE ' in x]
assert markers==Q['raw_markers'] and len(markers)==4
b,c=markers[1:3];assert b['variant']=='baseline' and c['variant']=='candidate'
assert b['registers']==c['registers']==62 and b['local_bytes_per_thread']==c['local_bytes_per_thread']==64
assert b['static_shared_bytes']==c['static_shared_bytes']==0 and b['max_threads']==c['max_threads']==1024
assert b['occupancy_by_threads']==c['occupancy_by_threads']==[[64,16],[128,8],[256,4]]
def entries(path):
 t=path.read_text(encoding='utf-8');out={}
 for m in re.finditer(r'\.visible\s+\.entry\s+(\w+)\(',t):
  a=t.index('{',m.end());j=a+1;depth=1
  while depth:
   if t[j]=='{':depth+=1
   elif t[j]=='}':depth-=1
   j+=1
  assert m.group(1) not in out;out[m.group(1)]=t[m.start():j]
 return out
a,z=entries(EX/'baseline.ptx'),entries(EX/'candidate.ptx')
assert set(a)==set(z)==set(P['expected_entries']) and {n for n in a if a[n]!=z[n]}=={'up_action'}
assert a['up_action'].split('{',1)[0]==z['up_action'].split('{',1)[0]
for arm in ['baseline','candidate']:old.pin(EX/(arm+'.ptx'),Q['ptx_sha256'][arm])
O=ROOT/'comparisons/E055-resource-root-check';O.mkdir()
old.save(O/'report.json',{'id':'E055-resource-root-check','at':old.now(),'status':'pass_resource_feasibility_only','root_cross_check_only':True,'resource_report_sha256':old.sha(RES/'report.json'),'terminal_sha256':old.sha(EX/'terminal.json'),'registers_before_after':[62,62],'local_bytes_before_after':[64,64],'shared_bytes_before_after':[0,0],'occupancy_before':b['occupancy_by_threads'],'occupancy_after':c['occupancy_by_threads'],'max_threads_before_after':[1024,1024],'exact_abi_other8_entries':True,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True,'limits':'Root replay of compute_120 PTX, actual loaded attributes, compiler/probe receipts only. No universal hardware, numerical or speed proof.'})
H=ROOT/'runs/E055-kernel-control';H.mkdir();prior=ROOT/'runs/E051-kernel-control'
for v in ['baseline','candidate']:(H/(v+'.ptx')).write_bytes((EX/(v+'.ptx')).read_bytes())
(H/'discounts.rs').write_bytes((prior/'discounts.rs').read_bytes())
s=(prior/'probe.rs').read_text(encoding='utf-8').replace('E051','E055')
needle='  let discounts=Discounts::for_iteration'
assert s.count(needle)==1
s=s.replace(needle,'  assert_eq!(slots[parent],parent as u32);\n  for child in &children[cs..cs+na] {assert_ne!(slots[parent],slots[*child as usize],"parent/child CFVrows overlap");}\n'+needle,1)
s=s.replace('"disjoint_device_ranges":device_ranges','"disjoint_device_ranges":device_ranges,"parent_child_rows_disjoint":true')
(H/'probe.rs').write_text(s,encoding='utf-8',newline='\n')
for name in ['execute.py','audit.py']:
 s=(prior/name).read_text(encoding='utf-8').replace('E051','E055').replace("HERE.parent/'small-gain-confirmation-plan'","HERE.parent/'accepted-E051'").replace('import common as old','import common_e051 as old')
 if name=='audit.py':
  needle=" req(list(imm[8][4:6])=="
  assert s.count(needle)==1
  extra=" req(imm[10][2]==2 and all(imm[10][2]!=imm[10][child] for child in imm[5][2:2+na]),'actual parent output row disjoint from every actual child input row')\n"
  s=s.replace(needle,extra+needle,1)
  s=s.replace("ROOT/'comparisons/E055-kernel-control'","ROOT/'comparisons/E055-kernel-control-root-check'")
  s=s.replace(" req(marker['id']==case['id'],'device-range case identity')"," req(marker['id']==case['id'] and marker['parent_child_rows_disjoint'] is True,'device-range case identity and parent child row assertion')")
  s=s.replace("'candidate_accepted':False,'limits':","'candidate_accepted':False,'all_parent_child_cfv_rows_disjoint':True,'limits':")
 assert 'import common as old' not in s
 (H/name).write_text(s,encoding='utf-8',newline='\n')
corpus=old.read(prior/'corpus.json');corpus.update(id='E055-up-action-corpus',at=old.now())
assert len(corpus['cases'])==819 and corpus['changed_path_cases']==264
old.save(H/'corpus.json',corpus)
caller_paths=['crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/arena.rs','crates/solver/src/gpu/continuation.rs','crates/solver/src/gpu/continuation_paging.rs','crates/solver/src/gpu/continuation_storage.rs','crates/solver/src/gpu/continuation_capacity.rs']
old.save(H/'source-review.json',{'id':'E055-raw-control-source-review','at':old.now(),'root_review_only':True,'resource_root_sha256':old.sha(O/'report.json'),'source_review_sha256':old.sha(ROOT/'runs/E055-source/source-review.json'),'cases':819,'launches':1638,'changed_path_cases':264,'scope':'Same819case matrix, complete actual output/input/guard words and disjoint owned device addresses. Bothactors, own/locked/opponent, arities1-17,hands0-1326,alternateblocks,algorithms/iterations,signedzero/subnormal/quietNaN/infinity/finiteoverflow/count0. No dropped cases.','discount_buffer_contract':'Exact3float device buffer initialized before eachlaunch; actual immutable device words captured and compared to original production-derived discounts. Supported ordinary/continuation stream dependencies prevent concurrent writes during launch. Own-unlocked arithmetic reads same3values; locked/opponent paths use none. Invalid/trapping custom buffers are outside supported kernel-call contract.','production_proof':'Only placement of3readonly discount loads changes. Resource and conservative PTX reachability gate passes: opponent/locked read0words, each declaredarity unlocked reads3words. Same arithmetic/reduction/store order, host/ABI/graphs/allocations/quality. Existing raw parent/child row and learning/CFV allocation disjointness checks retained unchanged, although this transform does not move a CFVstore.','caller_source_sha256':{n:old.sha(old.REPO/n) for n in caller_paths},'limits':'Finite direct raw matrix and root source/PTX review only. No external independent audit or universal malformed-input guarantee. Full solver, broader/F32/lifetime/capacity/saves/holdout/cumulative/performance qualification remains required.'})
p=old.read(prior/'protocol.json');p.update(id='E055-kernel-control',at=old.now(),resource_report=str(RES/'report.json'),raw_output=str(H/'evidence'),expected_cases=819,expected_launches=1638)
p['rustc_command']=[x.replace('E051-kernel-control','E055-kernel-control') for x in p['rustc_command']]
deps={n:h for n,h in p['input_sha256'].items() if Path(n).suffix in ['.rlib','.lib']}
refs=[H/n for n in ['probe.rs','discounts.rs','baseline.ptx','candidate.ptx','corpus.json','source-review.json','execute.py','audit.py']]+[RES/'report.json',O/'report.json',ROOT/'runs/E055-source/manifest.json',ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/accepted-E051/baseline.json',old.REPO/'crates/solver/src/cfr.rs',old.REPO/'tools/postflop_autoresearch.py']+[old.REPO/n for n in caller_paths]
p['input_sha256']=deps|{str(x):old.sha(x) for x in refs}
for f,h in p['input_sha256'].items():old.pin(f,h)
old.save(H/'protocol.json',p)
published={}
for directory,prefix in [(RES,RES.name),(O,O.name),(H,'E055-kernel-control-native')]:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.pdb'] or '__pycache__' in src.parts:continue
  key=prefix+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data,key
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as r:assert r.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'kernel_launches':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E055');e.update(stage='Resource passed; fixed819case raw matrix',reason='62registers/local64 unchanged, ABI/other8entries exact. ConditionalPTX gate skips discount reads on unused roles; immutable3float caller buffer retained. Full raw outputs, actual immutable device inputs and guards next.');e['evidence'] +=[{'label':'E055 resource root replay','url':'evidence/E055-resource-root-check/report.json'},{'label':'E055 fixed raw matrix','url':'evidence/E055-kernel-control-native/protocol.json'},{'label':'E055 parent/child CFV row contract','url':'evidence/E055-kernel-control-native/source-review.json'}];st.update(state='running',stage='E055 raw numerical controls',activity='Exactly819cases/1638launches with full actual output/input images and guard words retained. Speed remains unmeasured.',updated_at=old.now());old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'resource_root_sha256':old.sha(O/'report.json'),'protocol_sha256':old.sha(H/'protocol.json'),'published':len(published)}),flush=True)
