"""Replay E051 resource pass and freeze actual disjoint-buffer raw controls."""
import json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
RES=ROOT/'runs/E051-resource';P=old.read(RES/'protocol.json');Q=old.read(RES/'report.json');EX=RES/'execution'
for p,h in P['input_sha256'].items():old.pin(p,h)
assert Q['status']=='pass_resource_feasibility_only' and all(Q['gates'].values())
for label in ['rustc','probe']:
 receipt=old.read(EX/(label+'.exit.json'));assert receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
old.save(EX/'terminal.json',{'at':old.now(),'exec_chunk_id':'4decb7','returncode':0,'complete_sha256':old.sha(EX/'complete.json'),'compiler_and_probe_terminal':True,'kernel_solver_executions':0})
markers=[json.loads(x.split('E051_RESOURCE ',1)[1]) for x in (EX/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'E051_RESOURCE ' in x]
assert markers==Q['raw_markers'] and len(markers)==4
b,c=markers[1:3]
assert (b['registers'],c['registers'])==(66,62) and b['local_bytes_per_thread']==c['local_bytes_per_thread']==64
assert b['static_shared_bytes']==c['static_shared_bytes']==0
assert b['occupancy_by_threads']==[[64,14],[128,7],[256,3]] and c['occupancy_by_threads']==[[64,16],[128,8],[256,4]]
assert b['max_threads']==896 and c['max_threads']==1024
def entries(path):
 text=path.read_text(encoding='utf-8');out={}
 for m in re.finditer(r'\.visible\s+\.entry\s+(\w+)\(',text):
  begin=m.start();brace=text.index('{',m.end());j=brace+1;depth=1
  while depth:
   if text[j]=='{':depth+=1
   elif text[j]=='}':depth-=1
   j+=1
  out[m.group(1)]=text[begin:j]
 return out
a,z=entries(EX/'baseline.ptx'),entries(EX/'candidate.ptx');assert set(a)==set(z)==set(P['expected_entries'])
assert {n for n in a if a[n]!=z[n]}=={'up_action'} and a['up_action'].split('{',1)[0]==z['up_action'].split('{',1)[0]
O=ROOT/'comparisons/E051-resource-root-check';O.mkdir()
old.save(O/'report.json',{'id':'E051-resource-root-check','at':old.now(),'status':'pass_resource_feasibility_only','root_cross_check_only':True,'resource_report_sha256':old.sha(RES/'report.json'),'terminal_sha256':old.sha(EX/'terminal.json'),'registers_before_after':[66,62],'local_bytes_per_thread':64,'shared_bytes':0,'occupancy_before':b['occupancy_by_threads'],'occupancy_after':c['occupancy_by_threads'],'max_threads_before_after':[896,1024],'exact_abi_other8_entries':True,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True,'limits':'Root raw PTX/resource/receipt replay; no numerical or performance proof and no external independent audit.'})
H=ROOT/'runs/E051-kernel-control';H.mkdir();prior=ROOT/'runs/E047-kernel-control'
for v in ['baseline','candidate']:(H/(v+'.ptx')).write_bytes((EX/(v+'.ptx')).read_bytes())
(H/'discounts.rs').write_bytes((prior/'discounts.rs').read_bytes())
s=(prior/'probe.rs').read_text(encoding='utf-8').replace('E047','E051').replace('CudaContext,CudaSlice,CudaStream,LaunchConfig','CudaContext,CudaSlice,CudaStream,DevicePtr,LaunchConfig')
s=s.replace(' assert_eq!(cases.len(),819);',' assert_eq!(cases.len(),819);\n let case_count=cases.len();')
s=s.replace('"cases":717,"kernel_launches":1434','"cases":case_count,"kernel_launches":2*case_count')
assert '"cases":717' not in s and '2*case_count' in s
helper='''fn disjoint_regions(s:&Arc<CudaStream>,buffers:[&CudaSlice<f32>;3])->Vec<[u64;2]> {
 let mut regions=Vec::new();
 for buffer in buffers {let (ptr,_guard)=buffer.device_ptr(s);regions.push([ptr,buffer.len() as u64*4]);}
 for i in 0..regions.len() {for j in i+1..regions.len() {
  let ie=regions[i][0].checked_add(regions[i][1]).unwrap();let je=regions[j][0].checked_add(regions[j][1]).unwrap();
  assert!(ie<=regions[j][0]||je<=regions[i][0],"actual mutable device buffers overlap");
 }}
 regions
}
'''
s=s.replace('fn main(){',helper+'fn main(){',1)
s=s.replace('  let mut expected:Option<Vec<Vec<u32>>>=None;','  let mut expected:Option<Vec<Vec<u32>>>=None;\n  let mut device_ranges=Vec::new();')
needle='   unsafe{stream.launch_builder(f).arg(&dn)'
assert s.count(needle)==1
s=s.replace(needle,'   device_ranges.push(serde_json::json!({"arm":label,"regions":disjoint_regions(&stream,[&dr,&ds,&dv])}));\n'+needle,1)
s=s.replace('"all_raw_exact":true,"guards_exact":true}));','"all_raw_exact":true,"guards_exact":true,"disjoint_device_ranges":device_ranges}));')
assert 'disjoint_device_ranges' in s;(H/'probe.rs').write_text(s,encoding='utf-8')
for name in ['execute.py','audit.py']:
 s=(prior/name).read_text(encoding='utf-8').replace('E047','E051')
 if name=='audit.py':
  insertion='''markers=[json.loads(x.split('E051_UNIT ',1)[1]) for x in (HERE/'execution/probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'E051_UNIT ' in x]
req(len(markers)==len(cases)+1,'actual marker inventory')
for case,marker in zip(cases,markers[:-1]):
 req(marker['id']==case['id'],'device-range case identity')
 ranges=marker['disjoint_device_ranges'];req([x['arm'] for x in ranges]==['baseline','candidate'],'both actual arm witnesses')
 nh,na=case['hands'],case['actions'];nn=na+8;stride=nh+5
 expected=[(13+na*nh+17)*4,(13+na*nh+17)*4,((nn+3)*stride+17)*4]
 for witness in ranges:
  regions=witness['regions'];req(len(regions)==3 and [x[1] for x in regions]==expected,'actual mutable byte extents')
  req(all(isinstance(p,int) and p>0 and 0<=n and p+n<2**64 for p,n in regions),'valid device extents')
  req(all(regions[i][0]+regions[i][1]<=regions[j][0] or regions[j][0]+regions[j][1]<=regions[i][0] for i in range(3) for j in range(i+1,3)),'all actual mutable extents disjoint')
'''
  s=s.replace("old.custody()\nreport=",insertion+"old.custody()\nreport=",1)
 (H/name).write_text(s,encoding='utf-8')
corpus=old.read(prior/'corpus.json');corpus.update(id='E051-up-action-corpus',at=old.now(),changed_path_cases=sum(c['role']==0 and c['count']>0 and c['hands']>0 for c in corpus['cases']))
old.save(H/'corpus.json',corpus)
caller_paths=['crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/arena.rs','crates/solver/src/gpu/continuation.rs','crates/solver/src/gpu/continuation_paging.rs','crates/solver/src/gpu/continuation_storage.rs']
old.save(H/'source-review.json',{'id':'E051-raw-control-source-review','at':old.now(),'root_review_only':True,'resource_root_sha256':old.sha(O/'report.json'),'cases':819,'launches':1638,'changed_path_cases':corpus['changed_path_cases'],'scope':'Original/candidate full mutable output and actual immutable device images.3roles, bothactors/algorithms, arities1-17,tails0-1326,alternateblocks,signedzero/subnormal/quietNaN/infinity/finiteoverflow,count0.','native_reporting':'Summary counts derived from actual case vector, repairing inherited stale E047 summary before any native outcome. All actual arm mutable address/byte extents assert non-overlap and are retained/replayed.','caller_disjointness':'GpuSolver uses distinct owned CudaSlice allocations for four learning arenas and CFV, with private fields. Continuation methods pass those owners; paging swaps seven distinct owned allocations positionally and creates separately allocated dummies, retaining owners/lifetimes. Scoped GPU source search found no raw device-pointer owner construction/transmute. Host PinnedBuf unsafe raw slices are CPU-only. Supported callers have separate learning/CFV allocations; raw aliased argument experiments are outside supported kernel-call contract.','caller_source_sha256':{n:old.sha(old.REPO/n) for n in caller_paths},'limits':'Finite direct matrix and root source review only. Full solver, continuation/lifetime/F32/heldout/cumulative/performance qualification still pending. No external independent audit.'})
p=old.read(prior/'protocol.json');p.update(id='E051-kernel-control',at=old.now(),resource_report=str(RES/'report.json'),raw_output=str(H/'evidence'),expected_cases=819,expected_launches=1638)
p['rustc_command']=[x.replace('E047-kernel-control','E051-kernel-control') for x in p['rustc_command']]
deps={n:h for n,h in p['input_sha256'].items() if Path(n).suffix in ['.rlib','.lib']}
refs=[H/n for n in ['probe.rs','discounts.rs','baseline.ptx','candidate.ptx','corpus.json','source-review.json','execute.py','audit.py']]+[RES/'report.json',O/'report.json',ROOT/'runs/E051-source/manifest.json',ar.REPO/'crates/solver/src/cfr.rs',ar.REPO/'tools/postflop_autoresearch.py']+[old.REPO/n for n in caller_paths]
p['input_sha256']=deps|{str(x):old.sha(x) for x in refs};old.save(H/'protocol.json',p)
published={}
for directory in [RES,O,H]:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.pdb'] or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'kernel_launches':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(stage='Resource passed;819-case raw GPU control next',reason='Registers66to62;128thread occupancy7to8,local64unchanged. ABI/other8entries exact. Actual caller owner review and per-arm disjoint-address witnesses required.');e['evidence'].extend([{'label':'E051 resource root replay','url':'evidence/E051-resource-root-check/report.json'},{'label':'E051 fixed raw GPU control','url':'evidence/E051-kernel-control/protocol.json'}]);st.update(state='running',stage='E051 direct numerical control',activity='One fixed819case/1638launch full raw control before any solver build/timing.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
print(json.dumps({'resource_root_sha256':old.sha(O/'report.json'),'control_protocol_sha256':old.sha(H/'protocol.json'),'changed_path_cases':corpus['changed_path_cases'],'published':len(published)}),flush=True)
