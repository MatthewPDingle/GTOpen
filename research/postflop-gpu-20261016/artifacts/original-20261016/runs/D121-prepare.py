"""D121: prove immutable CTA-uniform node reads before one LDU candidate."""
from pathlib import Path
import difflib,hashlib,json,re,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D121-uniform-node-reads';S=R/'runs/E075-source';assert not H.exists()and not S.exists();H.mkdir();S.mkdir()
src=old.REPO/'crates/solver/src/gpu/kernels.cu';raw=src.read_bytes();old.pin(src,old.BASE['crates/solver/src/gpu/kernels.cu']);t=raw.decode().replace('\r\n','\n')
def fragment(text,name):
 m=re.search(r'\bvoid\s+'+re.escape(name)+r'\s*\(',text);assert m;start=text.rfind('\n',0,m.start())+1;left=text.index('{',m.end());end=left+1;depth=1
 while depth:
  if text[end]=='{':depth+=1
  elif text[end]=='}':depth-=1
  end+=1
 return text[start:end]
history=subprocess.run(['git','log','--all','--format=%H','-G','ldu\\.global|load_uniform|uniform_load','--','crates/solver/src/gpu'],cwd=old.REPO,text=True,capture_output=True,check=True);assert not history.stdout.strip()
matches=[];scanned=0
for p in(R/'runs').rglob('*.cu'):
 if S in p.parents:continue
 source=p.read_text(encoding='utf-8',errors='strict');scanned+=1
 if 'ldu.global'in source:matches.append(str(p))
assert not matches
old.save(H/'history.json',{'at':old.now(),'local_all_ref_query':history.args,'local_all_ref_matches':history.stdout.splitlines(),'retained_CUDA_files_scanned':scanned,'prior_LDU_sources':matches,'scope':'Bounded retained CUDA and local all-ref history, not exhaustive remote novelty.','not_closed_variants':'Not E003noalias/E018child mapping/E033L2cache policy/E046record interleaving/E070narrow attributes/E074device-call boundary. No buffers, layout, metadata values, alias qualifiers, cache reservations or calls change.'})
helpers='''// Immutable node metadata: addresses depend only on the CTA's node.
// No hand/action-indexed or mutable solver-state access uses these loads.
__device__ __forceinline__ u32 uniform_node_u32(const u32* ptr) {
    u32 value;
    asm("{ .reg .u64 addr; cvta.to.global.u64 addr, %1; ldu.global.u32 %0, [addr]; }"
        : "=r"(value) : "l"(ptr));
    return value;
}
__device__ __forceinline__ int uniform_node_i32(const int* ptr) {
    int value;
    asm("{ .reg .u64 addr; cvta.to.global.u64 addr, %1; ldu.global.s32 %0, [addr]; }"
        : "=r"(value) : "l"(ptr));
    return value;
}
__device__ __forceinline__ u64 uniform_node_u64(const u64* ptr) {
    u64 value;
    asm("{ .reg .u64 addr; cvta.to.global.u64 addr, %1; ldu.global.u64 %0, [addr]; }"
        : "=l"(value) : "l"(ptr));
    return value;
}
__device__ __forceinline__ long long uniform_node_i64(const long long* ptr) {
    long long value;
    asm("{ .reg .u64 addr; cvta.to.global.u64 addr, %1; ldu.global.s64 %0, [addr]; }"
        : "=l"(value) : "l"(ptr));
    return value;
}

'''
candidate=t;changes=[]
for name in ['up_action_impl','up_action']:
 before=fragment(candidate,name);after=before
 if name=='up_action_impl':
  edits=[('nodes[start + b]','uniform_node_u32(nodes + start + b)'),('node_na[n]','uniform_node_i32(node_na + n)'),('node_children_start[n]','uniform_node_u32(node_children_start + n)'),('node_player[n]','uniform_node_i32(node_player + n)'),('lock_off[n]','uniform_node_i64(lock_off + n)'),('node_data_off[n]','uniform_node_u64(node_data_off + n)'),('rsrc_p[n]','uniform_node_u32(rsrc_p + n)'),('cfv_slot[n]','uniform_node_u32(cfv_slot + n)')]
 else:edits=[('node_na[nodes[start + blockIdx.x]]','uniform_node_i32(node_na + uniform_node_u32(nodes + start + blockIdx.x))')]
 for a,b in edits:
  assert a in after;after=after.replace(a,b)
 assert candidate.count(before)==1;candidate=candidate.replace(before,after,1);changes.append((name,before,after))
needle='// Up sweep, action nodes: traverser nodes combine children with the current';assert candidate.count(needle)==1;candidate=candidate.replace(needle,helpers+needle,1)
reverse=candidate.replace(helpers,'',1)
for name,before,after in reversed(changes):assert reverse.count(after)==1;reverse=reverse.replace(after,before,1)
assert reverse==t
entries=['copy_root','down_action','down_chance','up_fold','up_show','up_chance','up_action','copy_span','up_action_eval'];assert all(fragment(t,n)==fragment(candidate,n)for n in entries if n!='up_action')
# Every transformed address uses n only, never i/a/children or mutable state.
calls=re.findall(r'uniform_node_(?:u32|i32|u64|i64)\(([^()]+)\)',fragment(candidate,'up_action_impl'))
expected=['nodes + start + b','node_na + n','node_children_start + n','node_player + n','lock_off + n','node_data_off + n','rsrc_p + n','cfv_slot + n']
assert set(calls)==set(expected)and all('i]'not in x and 'a]'not in x for x in calls)
nl='\r\n'if b'\r\n'in raw else'\n';data=candidate.replace('\n',nl).encode();(S/'baseline.cu').write_bytes(raw);(S/'candidate.cu').write_bytes(data);(S/'candidate.patch').write_text(''.join(difflib.unified_diff(raw.decode().splitlines(True),data.decode().splitlines(True),fromfile='E051/kernels.cu',tofile='E075/kernels.cu')),encoding='utf-8',newline='')
inputs=[Path(__file__),src,old.REPO/'crates/solver/src/gpu/mod.rs',old.REPO/'crates/solver/src/gpu/plan.rs',C/'common_e051_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',S/'baseline.cu',S/'candidate.cu',S/'candidate.patch',H/'history.json']
old.save(H/'protocol.json',{'id':'D121','at':old.now(),'input_sha256':{str(p):old.sha(p)for p in inputs},'scope':'Source/immutability/uniform-address proof only, no compiler/kernel/solve/timing.','address_proof':'b=blockIdx.x,start/count are kernel parameters, read-only nodes[start+b]gives the same n to every thread in the entireCTA. Every transformed address is an immutable base plus n, or originalnodesbase plusstart+b. These never depend on threadIdx/hand i/action a/branch/reach/CFV data. Thus even independently scheduled/inactive lanes and divergent outer iterations have the same address whenever a transformed site executes. Uniform b>=count rejection preserves all excess-grid guards.','immutable_input_ownership':'nodes,node_na,node_children_start,node_player,lock_off,node_data_off,rsrc_p,cfv_slot are private immutable metadata CUDAallocations during each kernel. RustGPUconstructor/uploads and update_locks/graph invalidation retain existing stream/lifetime/exclusive-mutability rules. No memory-clobber asm promises are added for mutable data. Existing physical allocation/alias contracts unchanged.','typed_loads':'u32/s32/u64/s64same width and interpretation; explicit cvta.to.global before eachldu, natural allocation alignment. Original generic/locked/opponent/common paths and arbitrary arities preserved.','prospective_prerequisite':'BotharchPTXexact20ABI/other8entries; emittedldu and unchanged code outside scope. D108nonewlocal/dynamic/reducedmaxthreads/defaultfit/positiveoccupancy. Before appkernels, capture actual driverCUBINs using existing pinnedD098owned-resource-callback binary and disassemble both with existingnvdisasm; reject unchanged native up_actioninstruction stream. No new capturebinary/tool/SDKinstall, counters, liveattach or settings. Driver/SASSdifference not a speed/traffic/numerical proof.','acceptance':'Same complete raw GPU controls and unrounded1%/strictfixture/fresh16/broad/state/F32/save/resume/continuation/actualCPU/host+GPUpeak/capacity/holdout/cumulative gates. No load/helper/source-scope/width/placement/cache or sample variants after failed frozen prerequisites/results.','candidate_accepted':False})
old.save(S/'manifest.json',{'id':'E075','at':old.now(),'accepted_source':'E051','candidate_owned_sha256':{'crates/solver/src/gpu/kernels.cu':hashlib.sha256(data).hexdigest()},'source_activated':False,'application_kernel_launches':0,'solver_executions':0})
old.save(S/'source-review.json',{'id':'E075','at':old.now(),'status':'pass_immutable_CTA_uniform_node_address_proof','source_manifest_sha256':old.sha(S/'manifest.json'),'D121_protocol_sha256':old.sha(H/'protocol.json'),'source_reverse_exact':True,'other8global_source_entries_exact':True,'transformed_address_expressions':expected,'floating_source_recurrences_barriers_ABI_unchanged':True,'no_thread_or_action_dependent_addresses_transformed':True,'immutable_load_site_count_in_helper':len(calls),'hardware_benefit_unproven':True,'resource_and_SASS_prerequisites_before_numerical_launch':True,'risk':'Original backend may already optimize these reads; ldu/address conversions/opaque asm can change scheduling/registers and hurt. Need actual emitted native difference plus full raw numerical and complete-cycle/material qualification.','reference':{'url':'https://docs.nvidia.com/cuda/archive/12.9.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-ldu','review':'PTX8.8ldu loads read-only global data whose address is common across the warp, with supported32/64bit signed/unsigned scalar types. This source proves addressesCTAuniform, not all metadata/float operands in general. No hardware speed claim from the instruction specification.'},'external_independent_review':False,'candidate_accepted':False})
pub=[]
for folder in [H,S]:
 for p in folder.iterdir():
  if p.is_file():
   key=folder.name+'/'+p.name;dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
   with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
   pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(H/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']in['D121','E075']for x in s['experiments']);s['experiments'].append({'id':'D121','at':old.now(),'title':'Immutable uniform node-read proof','kind':'diagnostic','status':'measured','correctness':'source/address proof; GPU untested','fixture':'CTAuniform read-only metadata only','stage':'Source ownership/address review complete','reason':'Alltransformed addresses depend only on CTA node n orstart+blockIdx, never hand/action/thread. Typedldu keeps every metadata bit and original float body. No compiler/kernel/solve or timing.','accepted':False,'evidence':[{'label':'Uniform address/ownership proof','url':'evidence/D121-uniform-node-reads/protocol.json'}]});s['experiments'].append({'id':'E075','at':old.now(),'title':'Uniform immutable action-node loads','kind':'candidate','status':'planned','correctness':'GPU untested','fixture':'Registered complete-solve suite; not run','stage':'Compiler/resource and actual machine-code checks next','reason':'Testexplicitldu for CTAuniform immutable node metadata only. Float data/hand/action-indexed reads untouched. Must show changed native code and feasibility before full raw controls; no speed claim.','accepted':False,'evidence':[{'label':'Frozen source and risk review','url':'evidence/E075-source/source-review.json'},{'label':'Single-file patch','url':'evidence/E075-source/candidate.patch'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E075',stage='E075 compiler/resource and native-code prerequisite',activity='E074closed because registers/occupancy didnot improve. D121proves immutable CTAuniform metadata addresses for one LDUcandidate. Actual native code/resources before any numerical/speed trial; E051accepted/deployed gain12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'status':'source_address_proof_pass','candidate_CUDA_sha256':old.sha(S/'candidate.cu'),'immutable_helper_sites':len(calls),'prior_CUDA_files_scanned':scanned,'compiler_or_GPU_executions':0}),flush=True)
