"""One new fold index staging source, fixed scratch footprint, no solver activation."""
from pathlib import Path
import difflib,hashlib,json,shutil,subprocess,sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as c
c.custody();assert not(R/'gpu-run.lock').exists();c.ar.refuse_active(c.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
S=R/'runs/E072-source';H=R/'runs/E072-resource';D=R/'runs/D116-fold-index-staging';assert not S.exists()and not H.exists()and not D.exists();S.mkdir();H.mkdir();D.mkdir()
assert not any(x['id']in ['D116','E072']for x in c.read(c.ar.STATUS)['experiments'])
base=(c.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();text=base.decode().replace('\r\n','\n');start=text.index('extern "C" __global__ void up_fold(');end=text.index('// Up sweep, showdown',start);original=text[start:end]
declaration='    __shared__ float total_parts[256];\n'
storage='''    // Index staging finishes before the unchanged total reduction starts.
    __shared__ union {
        float total_parts[256];
        u32 card_indices[256];
    } fold_scratch;
'''
assert original.count(declaration)==1
candidate=original.replace(declaration,'__FOLD_STORAGE__\n').replace('total_parts[','fold_scratch.total_parts[').replace('__FOLD_STORAGE__\n',storage)
marker='    __syncthreads();\n    const float* ro = local_reach;'
staging='''    const u32 cache_base = card_off[0];
    const u32 cache_count = min((u32)256, card_off[52] - cache_base);
    for (u32 k = threadIdx.x; k < cache_count; k += blockDim.x)
        fold_scratch.card_indices[k] = card_idx[cache_base + k];
'''
assert candidate.count(marker)==1;candidate=candidate.replace(marker,staging+marker)
oldloop='''        for (u32 k = card_off[card]; k < card_off[card + 1]; k++)
            sum += (float)ro[card_idx[k]];
'''
newloop='''        for (u32 k = card_off[card]; k < card_off[card + 1]; k++) {
            u32 index = k - cache_base < cache_count
                ? fold_scratch.card_indices[k - cache_base] : card_idx[k];
            sum += (float)ro[index];
        }
'''
assert candidate.count(oldloop)==1;candidate=candidate.replace(oldloop,newloop)
write='    fold_scratch.total_parts[threadIdx.x] = partial;'
reuse='''    // Every card-index consumer must finish before this storage is repurposed.
    __syncthreads();
'''
assert candidate.count(write)==1;candidate=candidate.replace(write,reuse+write)
reverse=candidate.replace(reuse,'',1).replace(newloop,oldloop,1).replace(staging,'',1).replace(storage,declaration,1).replace('fold_scratch.total_parts[','total_parts[');assert reverse==original
whole=text[:start]+candidate+text[end:];assert whole.count('__syncthreads()')==text.count('__syncthreads()')+1
newline='\r\n'if b'\r\n'in base else'\n';encoded=whole.replace('\n',newline).encode();(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(encoded)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),encoded.decode().splitlines(True),fromfile='accepted-E051/kernels.cu',tofile='E072/kernels.cu')),encoding='utf-8',newline='')
# Exhaust the supported hand-count domain and every index in three shifted spans.
checks=0;cached=0;fallback=0
for nh in range(1327):
 length=2*nh
 for shift in [0,1,17]:
  data=[0xdeadbeef]*shift+[(i*97+31)%max(1,nh)for i in range(length)];count=min(256,length);cache=data[shift:shift+count]
  assert len(cache)==count and count<=256
  for k in range(shift,shift+length):
   relative=(k-shift)&0xffffffff;observed=cache[relative]if relative<count else data[k];assert observed==data[k]
   checks+=1;cached+=relative<count;fallback+=relative>=count
proof={'id':'D116','at':c.now(),'status':'pass_source_and_integer_address_model','hand_counts':list(range(1327)),'span_bases':[0,1,17],'index_checks':checks,'cached_indices_checked':cached,'fallback_indices_checked':fallback,'zero_length_and_256_boundary_covered':True,'unchanged_static_payload_bytes':256*4,'source_reverse_equals_accepted':True,'GPU_numerical_executions':0,'limits':'CPU address-selection model only; no GPU compiler, barrier, numeric, allocation or speed proof.'};c.save(D/'integer-proof.json',proof)
review={'id':'E072','at':c.now(),'status':'frozen_root_source_design_not_external_review','candidate_sha256':c.sha(S/'candidate.cu'),'owned_source':'crates/solver/src/gpu/kernels.cu','entry':'up_fold','mechanism':'Cooperatively read the first at most256 card_idx words into the existing256word reduction scratch before its first use. Original card loops consume cached prefix or original global fallback, in original k order. One new CTA barrier ends all integer readers before the original float reduction writes this union storage.','unchanged':'Original reach loads,53card offsets,all card/partial/tree-reduction/valid/payout float expressions and per-thread ordering,ABI,host/plan/launch widths/counts/graphs,global arrays/payload,public budgets,save schema and all other8entries.','scratch_lifetime_proof':['All threads return together only at original uniform block-count guard.','Each staging index has one block-stride writer; existing first CTA barrier publishes reach and cached indices.','Card loops are the only readers of cached indices. Every thread reaches the added barrier after its card/partial loops.','Only after that barrier does every thread write its original float total_parts slot. Original reduction barriers/order and final consumers stay exact.','Union arms both25632bitwords with matching alignment; no additional static or dynamic scratch allocation authored.','No union word is read as the other type; indices are dead before float stores, and every subsequently consumed float slot is initialized as before.'],'global_access_model':'Total card_idx words read per CTA are unchanged for valid ordered spans: cached prefix once cooperatively, remaining words once through fallback. Coalescing and instruction locality are hypotheses, not measured transaction counts or speed. Two extra boundary loads and one additional barrier can outweigh them.','producer_and_consumers':'mod.rs288-299 builds53monotonic fold offsets and original-order indices, uploads to private immutable d_fold_card_off/idx; only existing fold launch arguments read them. Engine tables start0; shifted CPU model is additional coverage.','bounded_novelty':'Current ledger, retained *.cu/source-review files and all-ref kernels.cu searches find no matching fold card-index staging form. This is not an exhaustive remote novelty claim.','not_closed_rescue':'Not E031/E066showdown53offset cache, E030fold-card reordering, E019fold reduction shuffle, E035zero shortcut, E070global metadata encoding or E071parallel CPU planner. None composed or reopened.','declined_leads':['NVRTCalready selects actual compute capability; no arch-switch optimizer needed.','D085traced up_action_eval family is only27.764328ms on its rainbow trace; no new evaluation cache prototype justified from that limited diagnostic.','Showdown offset reuse is within the closed E031/E066cache family and is not pursued.'],'authoritative_reference':{'url':'https://nvidia.github.io/cccl/unstable/cub/index.html','section':'Block-wide sorting example,shared union of TempStorage and barriers for shared-memory reuse','use':'Reference demonstrates the shared-union/barrier idiom only, not this implementation correctness/performance. No CUB dependency or reduction algorithm introduced.'},'resource_rule':'Both compute120and75 compile; unchanged8PTXentries and foldABI; emitted integer shared staging and extra barrier; original FP opcode counts; no increased local/dynamic/static bytes, maxthread loss or zero occupancy/default-limit failure. Register/occupancy warnings follow D108, never acceptance.','next':'Only if compiler/resource gates pass, freeze direct full-output/input/guard numerical controls, then integrated1%complete-solve screen and downstream full qualification. No source/cache-width/threshold variants after failure.','source_activated':False,'native_solver_or_timing_runs':0};c.save(S/'source-review.json',review)
for name in ['baseline.cu','candidate.cu']:shutil.copyfile(S/name,H/name)
ref=R/'runs/E070-resource';P=c.read(ref/'protocol.json')
probe=(ref/'probe.rs').read_text(encoding='utf-8').replace('E070_RESOURCE','E072_RESOURCE').replace('for kernel in ["down_action","up_fold","up_action","up_action_eval"]','for kernel in ["up_fold"]').replace('"resource_rows":8','"resource_rows":2')
assert 'for kernel in ["up_fold"]'in probe
with(H/'probe.rs').open('x',encoding='utf-8',newline='\n')as out:out.write(probe)
cmd=[str(H/'probe.rs')if x==str(ref/'probe.rs')else(str(H/'probe.exe')if x==str(ref/'probe.exe')else x)for x in P['rustc_command']]
inputs=[Path(__file__),*S.iterdir(),D/'integer-proof.json',H/'baseline.cu',H/'candidate.cu',H/'probe.rs',R/'runs/E072-resource-execute.py',R/'runs/accepted-E051-live-20261018/common_e051_live.py',R/'runs/accepted-E051-live-20261018/protected-main.json',c.REPO/'tools/postflop_resource_feasibility.py',c.REPO/'tools/postflop_resource_admission.py']
pins={str(p):c.sha(p)for p in inputs if p.is_file()}
for path,h in P['input_sha256'].items():
 if '\\build\\release\\deps\\'in path:c.pin(path,h);pins[path]=h
P={'id':'E072-resource','at':c.now(),'status':'FROZEN_PRE_COMPILE_RESOURCE','rustc_command':cmd,'gpu_uuid':P['gpu_uuid'],'allocation_proof':P['allocation_proof'],'expected_entries':P['expected_entries'],'changed_entries':['up_fold'],'input_sha256':pins,'fixed_gates':review['resource_rule'],'application_kernel_launches':0,'performance_measurements':0,'source_activated':False,'no_variants_or_retry_after_prerequisite_failure':True}
c.save(H/'protocol.json',P);c.save(S/'manifest.json',{'id':'E072','at':c.now(),'accepted_source':'E051','candidate_owned_sha256':{'crates/solver/src/gpu/kernels.cu':c.sha(S/'candidate.cu')},'resource_protocol_sha256':c.sha(H/'protocol.json'),'source_activated':False,'GPU_or_solver_executions':0})
print({'resource_protocol_sha256':c.sha(H/'protocol.json'),'candidate_sha256':c.sha(S/'candidate.cu'),'CPU_index_checks':checks,'source_activated':False},flush=True)
