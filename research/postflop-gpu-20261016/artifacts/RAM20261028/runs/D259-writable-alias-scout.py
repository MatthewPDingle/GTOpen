"""Read-only code/history audit for a complete writable-formal alias contract."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
assert not h.read(ROOT/'comparisons/E112-fresh16-confirmation/report.json')['performance']['fresh_confirmation_pass']
O=ROOT/'runs/D259-writable-alias-scout';O.mkdir(exist_ok=False);repo=h.REPO;cuda=repo/'crates/solver/src/gpu/kernels.cu';source=cuda.read_bytes();assert b'\r\n'in source and source.replace(b'\r\n',b'').count(b'\n')==0
def contract(data):
 text=data.decode('utf-8-sig');out=[]
 for m in re.finditer(r'(?:__global__|__device__)[^{};]*?\bvoid\s+(\w+)\s*\((.*?)\)\s*\{',text,re.S):
  name,args=m.group(1,2)
  params=re.findall(r'(?<!const )\bfloat\*\s*(?:(__restrict__)\s*)?(\w+)',args)
  if params:out.append({'function':name,'writable_float_formals':[{'name':n,'restricted':bool(q)}for q,n in params]})
 return out
current=contract(source);assert sum(len(x['writable_float_formals'])for x in current)==19 and not any(p['restricted']for x in current for p in x['writable_float_formals'])
history=[];matches=[];seen=set()
def inspect(identity,data):
 digest=hashlib.sha256(data).hexdigest();rows=contract(data);same_shape=[x for x in rows if x['function']in['up_action','up_action_impl','down_action','down_action_impl']];restricted=[{'function':x['function'],'name':p['name']}for x in same_shape for p in x['writable_float_formals']if p['restricted']]
 history.append({'identity':identity,'sha256':digest,'bytes':len(data),'restricted_original_action_writable_formals':restricted})
 if restricted:matches.append(history[-1])
 seen.add(digest)
revisions=subprocess.check_output(['git','rev-list','--all','--','crates/solver/src/gpu/kernels.cu'],cwd=repo,text=True).splitlines()
for revision in revisions:
 done=subprocess.run(['git','show',revision+':crates/solver/src/gpu/kernels.cu'],cwd=repo,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if done.returncode:history.append({'identity':'git:'+revision,'absent_path':True,'stderr':done.stderr.decode('utf-8',errors='replace')});continue
 inspect('git:'+revision,done.stdout)
roots=[ROOT/'runs',Path(r'S:\GTOpen-research\postflop-gpu-20261016')/'runs',repo/'research/autoresearch'];files=[]
for root in roots:
 names=subprocess.check_output(['rg','--files',str(root),'-g','*.cu','-g','!target/**','-g','!build*/**'],text=True).splitlines()
 for name in names:
  p=Path(name);assert p.drive.upper()in['X:','S:']and p.is_file();assert p.stat().st_size<=4*1024**2;files.append(p)
for p in files:inspect(str(p),p.read_bytes())
cuda_refs=[]
for p in (repo/'crates/solver').rglob('*.rs'):
 text=p.read_text(encoding='utf-8-sig')
 if 'f_copy_root'in text or'f_up_action'in text or'f_down_action'in text or'f_copy_span'in text:
  cuda_refs.append({'path':str(p),'sha256':h.sha(p),'references':[{'line':i+1,'text':line.strip()}for i,line in enumerate(text.splitlines())if any(n in line for n in ['f_copy_root','f_up_action','f_down_action','f_copy_span'])]})
P={'id':'D259','at':h.now(),'status':'novel_writable_formal_contract_source_design_only'if not matches else'declined_duplicate_contract','current_CUDA_sha256':h.sha(cuda),'current_formals':current,'local_ref_revisions':len(revisions),'retained_CUDA_files':len(files),'unique_CUDA_hashes':len(seen),'matching_previous_original_action_writable_restrictions':matches,'history':history,'caller_files':cuda_refs,'proposed_fixed_form':'Add __restrict__ to all19 currently unqualified mutable float pointer formals in all9 original entries and2 inline action helpers. No other source/ABI/float/control/loop/store/graph/width/flag changes. The one coherent promise covers separately owned mutable device allocations; within one CFV/reach allocation all accesses still derive from its same formal pointer.','caller_ownership_review':'Production GpuSolver owns separate CudaSlice allocations for regrets[2],strat[2],reach[2],cfv,weights[2],eval_roots and metadata. Training/evaluation/research/continuation launch builders bind those fields; physical lifetime reuse inside CFV uses the same formal. Continuation workspace swaps whole owned allocations. Actual address extents/full raw state still mandatory before numerical/speed claims. No host rewrite/allocation/new pointer/fallback or narrower entry subset proposed.','risks':['Adding a false alias promise is undefined behavior; verify all real call paths and disjoint actual extents before kernel tests.','Compiler may emit identical instructions or increase registers/local storage; compiled mechanism and original resource gates must pass before application kernels.','No speed from source syntax or D142 sync-distorted family rankings; only fixed complete-cycle >=1%/strict fixture/fresh16 and broader/material/holdout/cumulative/app gates can qualify.'],'NVIDIA_primary_reference':'https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-programming-guide/index.html#restrict','closed_families_not_composed':['E112 constant discounts','E075 uniform ldu metadata','E099 adjacent-hand vector memory','E054 early CFV store','E006/E007 register caps/launch bounds'],'application_kernels':0,'compilers':0,'source_activated':False,'candidate_created':False,'performance_samples':0,'accepted_source_main_live_PTX_unchanged':True,'X_bulk_S_read_only_no_T_access':True}
h.save(O/'report.json',P);h.save(O/'unexecuted-broader-drafts.json',{'at':h.now(),'reason':'E112 fixed fresh16 rejected; preparer assertion forbids later broader build. These drafts were prepared while waiting but never executed. Do not run them.','files':{str(ROOT/'runs'/n):h.sha(ROOT/'runs'/n)for n in['E112-prepare-broader-build.py','E112-broader-build.py']},'protocol_created':False,'compilers':0,'native_tests':0});h.custody();print(json.dumps({k:P[k]for k in['status','local_ref_revisions','retained_CUDA_files','unique_CUDA_hashes','matching_previous_original_action_writable_restrictions']}),flush=True)
