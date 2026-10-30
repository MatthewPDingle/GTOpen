"""Direct raw PTX/attribute replay of E050 and immutable rejection publication."""
import hashlib,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E050-resource';P=old.read(H/'protocol.json');Q=old.read(H/'report.json');E=H/'execution'
for p,h in P['input_sha256'].items():old.pin(p,h)
assert Q['status']=='rejected_resource_gate'
assert old.read(E/'rustc.exit.json')['returncode']==old.read(E/'probe.exit.json')['returncode']==0
assert old.read(E/'complete.json')['report_sha256']==old.sha(H/'report.json')
old.save(E/'terminal.json',{'at':old.now(),'exec_chunk_id':'947472','returncode':0,'complete_sha256':old.sha(E/'complete.json'),'compiler_probe_terminal':True,'kernel_solver_executions':0})
raw=(E/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E050_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E050_RESOURCE ' in x];assert markers==Q['raw_markers'] and len(markers)==22
def entries(path):
 t=path.read_text(encoding='utf-8');out={}
 for match in re.finditer(r'\.visible\s+\.entry\s+(\w+)\(',t):
  start=match.start();brace=t.index('{',match.end());i=brace+1;depth=1
  while depth:
   if t[i]=='{':depth+=1
   elif t[i]=='}':depth-=1
   i+=1
  out[match.group(1)]=t[start:i]
 return out
tables={(v,a):entries(E/(v+'-'+a+'.ptx')) for v in ['baseline','candidate'] for a in ['compute_120','compute_75']}
for table in tables.values():assert set(table)==set(P['expected_entries'])
assert tables['baseline','compute_75']==tables['candidate','compute_75']
b,c=tables['baseline','compute_120'],tables['candidate','compute_120'];assert {k for k in b if b[k]!=c[k]}=={'up_show'}
assert c['up_show'].count('cp.async.ca.shared.global')==2 and 'cp.async.wait_all;' in c['up_show']
assert not any('cp.async.' in x for x in tables['candidate','compute_75'].values())
checks=5;rows={(x['variant'],x['shape']):x for x in markers[1:-1]};observed=[]
for shape in P['shapes']:
 a,z=rows['baseline',shape],rows['candidate',shape]
 assert a['registers']==38 and z['registers']==40
 assert a['local_bytes_per_thread']==z['local_bytes_per_thread']==0
 assert a['static_shared_bytes']==z['static_shared_bytes']==1040
 assert a['dynamic_shared_bytes']==z['dynamic_shared_bytes']
 assert a['max_threads']==z['max_threads']==1024
 assert a['occupancy_by_threads']==z['occupancy_by_threads']
 assert a['fits_default_limits'] and z['fits_default_limits']
 assert not Q['details'][shape]['gates']['registers_not_increased']
 assert all(v for k,v in Q['details'][shape]['gates'].items() if k!='registers_not_increased')
 observed.append({'shape':shape,'dynamic_shared_bytes':a['dynamic_shared_bytes'],'occupancy_64_128_256':a['occupancy_by_threads']});checks+=9
header=lambda x:re.findall(r'\.param\s+\.(u[0-9]+)((?:\s+\.ptr\s+\.align\s+[0-9]+)?)\s+up_show_param_([0-9]+)',x.split('{',1)[0])
assert header(b['up_show'])==header(c['up_show']) and len(header(b['up_show']))==27;checks+=1
assert Q['kernel_launches']==Q['solver_executions']==0 and not Q['candidate_accepted']
O=ROOT/'comparisons/E050-resource-root-check';O.mkdir()
r={'id':'E050-resource-root-check','at':old.now(),'status':'pass_rejected','checks':checks,'root_cross_check_only':True,'report_sha256':old.sha(H/'report.json'),'protocol_sha256':old.sha(H/'protocol.json'),'native_terminal_sha256':old.sha(E/'terminal.json'),'registers_before_after':[38,40],'local_bytes_per_thread':0,'static_shared_bytes':1040,'max_threads':1024,'all10shape_occupancies_equal':True,'shapes':observed,'other8current_arch_entries_exact':True,'all9fallback_entries_exact':True,'abi_parameter_count':27,'performance_measured':False,'candidate_accepted':False,'accepted162_main_head_live_ptx_unchanged':True,'limits':'Frozen conservative logical-register gate failed. Equal theoretical occupancy is retained, and no increased physical register charge, observed slowdown, numerical failure or material tradeoff is claimed from this probe. No native kernel or complete solve ran. Root replay is not an external independent audit.'}
old.save(O/'report.json',r)
published={}
for directory in [H,ROOT/'runs/E050-source',O]:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.pdb'] or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(O/'publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E050');e.update(status='rejected',stage='Closed at frozen compiler/resource gate',reason='Registers38 to40 fails fixed no-increase gate. Local0,shared1040,dynamic bytes and all10shape64/128/256occupancies equal; maxthreads1024. No numerical, solver or speed test. No async/width variant rescue. E020 retained.');e['evidence'].extend([{'label':'E050 raw resource rejection','url':'evidence/E050-resource/report.json'},{'label':'E050 raw PTX and attributes root replay','url':'evidence/E050-resource-root-check/report.json'}]);st.update(state='running',stage='Next GPU source investigation',activity='E050 rejected at frozen resource gate, with equal occupancy recorded. No new accepted speedup.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'## D081 / E050 asynchronous showdown staging' not in raw
text=f'''

## D081 / E050 asynchronous showdown staging

One fixed off-tree design uses4byte cp.async.ca global-to-shared copies for original reach and card-position words onsm80+, overlapping the existing full CFV row clear. Every issuing thread waits all its copies before the original CTA barrier. Dynamic shared base is explicitly4byte aligned and both copied regions/destinations are disjoint; global source types/offsets are naturally aligned. Existing ordered floating expressions, prefix scan, correction sums and later barriers are unchanged. The pre-sm80 branch preserves original copies and clear placement. NVIDIA CUDA12.9 PTX8.8 non-bulk async-completion and inline-PTX memory-clobber documentation are linked in source review {old.sha(ROOT/'runs/E050-source/source-review.json')}; no speed forecast follows those docs. Scope is only up_show in candidate {old.sha(ROOT/'runs/E050-source/candidate.cu')}; no host/plan/arrays/evaluator or launch change. Scoped history found no prior cp.async staging candidate; E031 offset-cache/E008 scan variants are not composed.

Resource protocol {old.sha(H/'protocol.json')} froze no register/local/static/dynamic increase, no maxthreads/occupancy loss at10dynamic shapes and64/128/256threads, exact27parameter ABI, other8current-arch entries, all9sm75fallback entries and actual async/wait instructions. One standalone compiler/probe invocation completed terminal0 (chunk947472), with no production activation or kernel/solver launch. Actual RTX5090 compiled registers rose38 to40; local0/static shared1040/maxthreads1024, every queried dynamic-shape occupancy, ABI and unmodified entries remained equal. Both four-byte async sites/wait_all were emitted, and the complete lower-arch fallback entries matched byte-for-byte. E050 fails its fixed logical-register gate and is rejected before numeric/performance work. Equal occupancy is recorded: this probe does not establish higher physical register allocation, a slowdown or material cost. No qualifier, width, copy-subset, zero-placement or register variant rescue follows.

Raw report {old.sha(H/'report.json')} and root PTX/attribute replay {old.sha(O/'report.json')} ({checks}checks) preserve the decision. Root review is not external independent review. All source/protocol/raw PTX/marker/terminal/decision artifacts are served and HTTP byte-verified; checkout remained accepted162 with main/HEAD/live/protected PTX exact. E020 stays accepted at previously qualified10.3798454492% cumulative suite gain; last actual primary baseline B148. Goal remains active.
'''
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+text.encode('utf-8').replace(b'\n',nl))
old.custody();print(json.dumps({'status':'rejected_resource_gate','root_checks':checks,'report_sha256':old.sha(O/'report.json'),'published':len(published)}),flush=True)
