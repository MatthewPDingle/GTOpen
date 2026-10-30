"""Freeze one common-arity local-index source form and its no-launch screen."""
import ast,difflib,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
assert old.read(ROOT/'runs/D104-counter-availability/report.json')['status']=='availability_query_unavailable'
D=ROOT/'runs/D105-local-index-proof';S=ROOT/'runs/E064-source';H=ROOT/'runs/E064-resource';assert not any(p.exists() for p in [D,S,H])
for p in [D,S,H]:p.mkdir()
base=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();text=base.decode('utf-8').replace('\r\n','\n')
start=text.index('template<int NA>\n__device__ __forceinline__ void up_action_impl(');end=text.index('extern "C" __global__ void up_action(',start)
body=text[start:end];needle='doff + (u64)a * nh_p + i';assert body.count(needle)==4
body=body.replace(needle,'action_data_index<NA>(doff, a, nh_p, i)')
helper='''// Only compile-time common arities use a bounded local32bit element offset.
// Every global slot/product and the arbitrary-menu specialization stays64bit.
template<int NA>
__device__ __forceinline__ u64 action_data_index(u64 base, int action, int hands, int hand)
{
    if (NA != 0) return base + (u32)(action * hands + hand);
    return base + (u64)action * hands + hand;
}

'''
candidate=text[:start]+helper+body+text[end:];eol='\r\n' if b'\r\n' in base else '\n';(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(candidate.replace('\n',eol).encode())
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(text.splitlines(keepends=True),candidate.splitlines(keepends=True),fromfile='a/crates/solver/src/gpu/kernels.cu',tofile='b/crates/solver/src/gpu/kernels.cu')),encoding='utf-8',newline='\n')
history=[old.REPO/'research/postflop-gpu-20261016/experiments.md']+sorted((ROOT/'runs').glob('E[0-9][0-9][0-9]-source/source-review.json'))
terms=['32-bit local','32bit local','action_data_index','narrow address','address arithmetic','32-bit action','32bit action'];hits=[]
for p in history:
 for n,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
  if any(t in line.lower() for t in terms):hits.append({'path':str(p),'line':n,'text':line})
old.save(D/'history-audit.json',{'at':old.now(),'terms':terms,'scope_sha256':{str(p):old.sha(p) for p in history},'hits':hits,'finding':'Bounded indexed source-review and ledger search. D104next proposal mentions this idea; no prior executed local-action index32bit mechanism found. Distinct from E020showdown shared integer index cache,E05216bit shared positions,E060reciprocal reuse,E063card cutoff metadata and closed scheduling/readback families. Not an exhaustive semantic novelty proof.'})
old.save(S/'source-review.json',{'id':'E064','at':old.now(),'scope':'Only the four local action-data expressions inside training up_action_impl. One inline helper chooses32bit action*hands+hand only for compile-time NA2/3/4; NA0generic expression stays original64bit. No other entry/caller/metadata/ABI/launch/workload/precision/stopping/FPoperation change.','integer_proof':'Spot::new unique NLHEcombos bound hands<=1326. Each guarded hand loop has0<=hand<hands; common instantiated NAin{2,3,4} gives0<=action<NA, so action*hands+hand<=4*1326-1=5303, no signed32overflow. Adding this identical nonnegative local offset to a64bit base gives same unsigned64address, including synthetic wrap boundaries. Empty hand loops never call helper. All genericNA0arities and global reach/CFV/node slots remain64bit.','closed_families_unchanged':['E060math/reciprocal','E063packed cutoff','E057/E062prefix map','E009/E010GPUquantization','E012/E013CPUencoder'],'expected_benefit':'Potential lower integer address-generation work in hot common-arity paths. Compiler may already perform equivalent lowering or hoist original addresses; no source-level speed inference.','fixed_admission':'First exhaustive integer proof and unchanged current D094allocation/local/shared/occupancy/ABI/other8entry filters at actualGPU, plus compute75other8entries exact. If passed, require separately pinned current-driver machine-code evidence of intended address-work reduction before any application kernel. PTX opcode/line counts are diagnostic, not hardware cost or speed. No casts/placement/arity-subset/helper/flag variants to rescue a failure.','history_audit_sha256':old.sha(D/'history-audit.json'),'source_activated':False,'candidate_accepted':False})
owned={'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu')};old.save(S/'manifest.json',{'id':'E064','at':old.now(),'candidate_owned_sha256':owned,'source_sha256':old.BASE|owned,'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir() if p.is_file()},'source_activated':False,'one_fixed_form':True})
prior=ROOT/'runs/E060-resource';oldp=old.read(prior/'protocol.json')
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
proof=r'''fn prove_local_indices(){
 let bases=[0u64,1,(u32::MAX as u64)-5303,u32::MAX as u64,(1u64<<48)+123,u64::MAX-5303,u64::MAX];
 let(mut locals,mut cases,mut maxlocal)=(0u64,0u64,0i32);
 for actions in [2i32,3,4] {for hands in 1..=1326i32 {for action in 0..actions {for hand in 0..hands {
  let local=std::hint::black_box(action*hands+hand);assert!(local>=0&&local<=5303);maxlocal=maxlocal.max(local);locals+=1;
  for base in bases {let b=std::hint::black_box(base);let original=b.wrapping_add((action as u64)*(hands as u64)).wrapping_add(hand as u64);let narrowed=b.wrapping_add((local as u32) as u64);assert_eq!(original,narrowed);cases+=1;}
 }}}}
 assert_eq!(locals,7918209);assert_eq!(cases,55427463);assert_eq!(maxlocal,5303);
 emit(serde_json::json!({"stage":"integer_proof","local_combinations":locals,"base_address_cases":cases,"max_local_element_index":maxlocal,"base_patterns":7,"no_memory_dereferences":true,"floating_results_compared":false,"kernel_launches":0}));
}
'''
probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E060','E064');assert probe.count('fn main(){')==1;probe=probe.replace('fn main(){',proof+'\nfn main(){\n prove_local_indices();')
needle=' ctx.check_err().unwrap();emit(serde_json::json!({"stage":"complete"';assert probe.count(needle)==1
fallback=r''' for (variant,source) in [("baseline",include_str!("baseline.cu")),("candidate",include_str!("candidate.cu"))] {
  let ptx=compile_ptx_with_opts(source,CompileOptions{arch:Some("compute_75"),..Default::default()}).unwrap();
  let mut f=OpenOptions::new().create_new(true).write(true).open(format!("{variant}-compute75.ptx")).unwrap();f.write_all(ptx.to_src().as_bytes()).unwrap();f.flush().unwrap();f.sync_all().unwrap();
 }
'''
probe=probe.replace(needle,fallback+needle);(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(prior/'execute.py').read_text(encoding='utf-8').replace('E060','E064')
needle="assert len(markers)==4 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'";assert runner.count(needle)==1;runner=runner.replace(needle,"assert len(markers)==5 and markers[0]['stage']=='integer_proof' and markers[1]['stage']=='device' and markers[-1]['stage']=='complete'\n assert markers[0]['local_combinations']==7918209 and markers[0]['base_address_cases']==55427463 and markers[0]['max_local_element_index']==5303")
assert runner.count('markers[1:-1]')==1;runner=runner.replace('markers[1:-1]','markers[2:-1]')
needle="unchanged=[k for k in be if be[k]==ce[k]];gates=";assert runner.count(needle)==1;runner=runner.replace(needle,"bf,cf=entries(OUT/'baseline-compute75.ptx'),entries(OUT/'candidate-compute75.ptx');assert set(bf)==set(cf)==set(P['expected_entries'])\n unchanged=[k for k in be if be[k]==ce[k]];gates=")
needle="'other8_entries_exact':set(unchanged)==set(be)-set(P['changed_entries'])";assert runner.count(needle)==1;runner=runner.replace(needle,needle+",'other8_compute75_entries_exact':all(bf[k]==cf[k] for k in bf if k not in P['changed_entries'])")
needle=" report={'id':'E064-resource'";assert runner.count(needle)==1
metrics=r''' def integer_sites(t):
  ops=re.findall(r'^\s*(?:@!?%p\d+\s+)?((?:add|sub|mul|mad|shl|shr|cvt)[.A-Za-z0-9_]+)\s',t,re.M)
  return {'wide_address_arithmetic_sites':sum(bool(re.search(r'\.(?:s64|u64|b64)$',x)) for x in ops if not x.startswith('cvt.')),'integer_arithmetic_and_conversion_sites':len(ops),'entry_lines':len(t.splitlines()),'opcode_histogram':{x:ops.count(x) for x in sorted(set(ops))}}
 static={'baseline':integer_sites(be['up_action']),'candidate':integer_sites(ce['up_action']),'limits':'PTX virtual static sites only. No machine-address throughput, dynamic instruction or runtime speed inference. If resources pass, separately pinned driver-machine proof required before any application kernel.'}
'''
runner=runner.replace(needle,metrics+needle)
needle="'raw_markers':markers,";assert runner.count(needle)==1;runner=runner.replace(needle,needle+"'integer_model_proof':markers[0],'static_address_code':static,")
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P={k:oldp[k] for k in ['changed_entries','gpu_uuid','expected_entries','expected_abi','allocation_proof']};P.update(id='E064-resource',at=old.now(),status='FROZEN_PRE_INTEGER_AND_RESOURCE_EXECUTION',source_manifest_sha256=old.sha(S/'manifest.json'),rustc_command=[s.replace(str(prior),str(H)) for s in oldp['rustc_command']],fixed_gates='Exhaust all7,918,209local common-arity inputs and55,427,463base cases. Current D094allocation/local/shared/maxthread/occupancy/fit filter, unchanged20parameter ABI and8other entries actual/compute75. If pass, actual current-driver machine proof of intended address-work reduction required before GPU numerics. No source variants or resampling. All1%/strict-fixture/exactness/fresh16/broad/material/holdout/cumulative rules unchanged.')
paths=[*D.iterdir(),*S.iterdir(),*H.iterdir(),Path(__file__),ROOT/'runs/D104-counter-availability/report.json',ROOT/'comparisons/D104-availability-root-check/report.json',ROOT/'runs/D094-resource-materiality/report.json',ROOT/'runs/D094-resource-materiality/test-report.json',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in oldp['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']};old.save(H/'protocol.json',P)
old.save(D/'protocol.json',{'id':'D105-local-index-proof','at':old.now(),'combined_resource_protocol_sha256':old.sha(H/'protocol.json'),'execution':'Integer model first inside the same one-shot no-launch E064resource probe; no separate duplicate execution.','scope':'Typed32/64element arithmetic proof only; GPU raw values not compared yet.','source_activated':False,'performance_measured':False})
published={}
for folder in [D,S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key='evidence/'+folder.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id'] in ['D105','E064'] for e in st['experiments']);st['experiments'].extend([{'id':'D105','at':old.now(),'kind':'diagnostic','title':'Bounded local action-index arithmetic proof','status':'running','correctness':'pending','stage':'Exhaustive integer model before CUDA resource query','reason':'CommonNA2/3/4local index<=5303; generic/global64bit semantics retained.55million synthetic base comparisons, no actual memory access or FP/speed claim.','evidence':[{'label':'Frozen model scope','url':'evidence/D105-local-index-proof/protocol.json'}]},{'id':'E064','at':old.now(),'kind':'candidate','title':'Common-arity local action-index narrowing','status':'running','correctness':'pending','accepted':False,'stage':'No-launch compiler/resource admission','reason':'One fixed integer-only helper at4local expressions inside trainingup_action. Prove bounds/ABI/unchanged entries/resources, then actual machine mechanism before any GPU numerical or speed work.','evidence':[{'label':'Fixed source review','url':'evidence/E064-source/source-review.json'},{'label':'Frozen combined prelaunch protocol','url':'evidence/E064-resource/protocol.json'}]}]);st.update(updated_at=old.now(),state='running',active_experiment='E064',stage='E064integer and compiled-resource proof',activity='Distinct common-arity local address-generation hypothesis. No profiler counters, application kernels, source activation or speed measurement.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'status':'integer_resource_screen_frozen','protocol_sha256':old.sha(H/'protocol.json'),'candidate_sha256':old.sha(S/'candidate.cu'),'native_executions':0}),flush=True)
