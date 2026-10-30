"""Freeze process-local Windows prefetch and page-fault CPU component controls."""
from pathlib import Path
import ast,json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D126-owned-memory-prefetch';assert not H.exists();H.mkdir();A=R/'runs/D092-action-arity-order'
history=subprocess.run(['git','log','--all','--format=%H','-G','PrefetchVirtualMemory|prefault|WIN32_MEMORY_RANGE_ENTRY','--','crates/solver/src/gpu','crates/solver/src/store.rs'],cwd=old.REPO,text=True,capture_output=True,check=True);assert not history.stdout.strip()
arena=(old.REPO/'crates/solver/src/gpu/arena.rs').read_text(encoding='utf-8');a=arena.index('        let zero = match store {');b=arena.index('        // Keep previously captured',a)
body=arena[a:b].strip();assert body.startswith('let zero = ')and body.endswith(';');body=body[len('let zero = '):-1]
old.save(H/'api-review.json',{'at':old.now(),'primary_sources':{'prefetch':'https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-prefetchvirtualmemory','range_layout':'https://learn.microsoft.com/en-us/windows/desktop/api/memoryapi/ns-memoryapi-win32_memory_range_entry','memory_counters':'https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters','counter_function':'https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo'},'contract':'Current-process handle only, borrowed owned quantized-buffer ranges, flags0, no data mutation or required correctness dependency. API is a best-effort hint, chiefly useful for paged-out memory; fresh zero allocations may receive no benefit. Cached prefetched pages are not immediately reflected in working set, so process counters alone cannot prove physical-cache cost. Only ranges consumed by unchanged full scans are requested. No settings, privileges, working-set limit setters, page eviction, memory lock or external-process access.','ABI':'Win64 repr(C) range pointer+usize=16bytes; basic PROCESS_MEMORY_COUNTERS has2u32+8usize=72bytes. Kernel32 imports, current-process memory info only. Native ability checks layouts/return codes and full owned byte guards.','novelty_query':history.args,'local_all_ref_matches':history.stdout.splitlines(),'closed_forms_remain_closed':'E045 parallel OR, D090 widened OR, E049 provenance/scan omission, D123 metadata initialization and E077 prefix tags are not composed or reopened.'})
for i in range(3):shutil.copyfile(A/f'fixture-{i}.json',H/f'fixture-{i}.json')
probe=r'''#![cfg(all(target_os="windows",target_pointer_width="64"))]
use solver::{Solver,Spot,SpotConfig,store::{Store,Storage},gpu::plan::GpuPlan};
use std::{ffi::c_void,io::{self,Write},sync::Arc,time::Instant};
use serde_json::{json,Value};
#[repr(C)]#[derive(Clone,Copy)]struct MemoryRange {address:*mut c_void,bytes:usize}
#[repr(C)]#[derive(Default)]struct MemoryCounters {cb:u32,faults:u32,peak_ws:usize,ws:usize,quota_peak_paged:usize,quota_paged:usize,quota_peak_nonpaged:usize,quota_nonpaged:usize,commit:usize,peak_commit:usize}
#[link(name="kernel32")]extern "system" {
 fn GetCurrentProcess()->*mut c_void;
 fn GetLastError()->u32;
 fn PrefetchVirtualMemory(process:*mut c_void,entries:usize,ranges:*const MemoryRange,flags:u32)->i32;
 fn K32GetProcessMemoryInfo(process:*mut c_void,counters:*mut MemoryCounters,bytes:u32)->i32;
}
fn emit(value:Value){let mut out=io::stdout().lock();writeln!(out,"D126 {value}").unwrap();out.flush().unwrap();}
fn counters()->MemoryCounters {let mut m=MemoryCounters::default();m.cb=std::mem::size_of::<MemoryCounters>()as u32;assert_ne!(unsafe{K32GetProcessMemoryInfo(GetCurrentProcess(),&mut m,m.cb)},0);assert_eq!(m.cb,72);assert!(m.ws>0&&m.peak_ws>=m.ws);m}
fn counter_json(m:&MemoryCounters)->Value{json!({"page_faults":m.faults,"working_set_bytes":m.ws,"peak_working_set_bytes":m.peak_ws,"commit_bytes":m.commit,"peak_commit_bytes":m.peak_commit})}
#[inline(never)]fn original_zero_predicate(store:&Store)->bool {BODY}
fn zero_ranges(stores:[&Store;4])->(usize,Option<[MemoryRange;4]>) {
 let mut ranges=[MemoryRange{address:std::ptr::null_mut(),bytes:0};4];let mut total=0usize;
 for(i,store)in stores.iter().enumerate(){let(ptr,bytes)=match store {Store::I16{q,..}=>(q.as_slice().as_ptr()as *mut c_void,q.len().checked_mul(2).unwrap()),Store::U16{q,..}=>(q.as_slice().as_ptr()as *mut c_void,q.len().checked_mul(2).unwrap()),Store::F32(_)=>return(0,None)};ranges[i]=MemoryRange{address:ptr,bytes};total=total.checked_add(bytes).unwrap();}
 if total<64*1024*1024||ranges.iter().any(|r|r.bytes==0){return(total,None);}
 for store in stores {let scale=match store{Store::I16{scale,..}|Store::U16{scale,..}=>scale,Store::F32(_)=>unreachable!()};if !scale.as_slice().iter().all(|v|v.to_bits()==0){return(total,None);}}
 (total,Some(ranges))
}
fn ability(){
 assert_eq!(std::mem::size_of::<MemoryRange>(),16);assert_eq!(std::mem::align_of::<MemoryRange>(),8);assert_eq!(std::mem::size_of::<MemoryCounters>(),72);
 let input:Vec<u16>=(0..4128).map(|i|((i*73+17)&65535)as u16).collect();let mut values=input.clone();let range=MemoryRange{address:unsafe{values.as_mut_ptr().add(16)}as *mut c_void,bytes:4096*2};let before=counters();let ok=unsafe{PrefetchVirtualMemory(GetCurrentProcess(),1,&range,0)};let error=if ok==0{unsafe{GetLastError()}}else{0};let after=counters();assert_eq!(values,input);
 let mut controls=0;
 for signed in [false,true]{let mut s=if signed{Store::i16(257,4)}else{Store::u16(257,4)};assert!(original_zero_predicate(&s));controls+=1;
  match &mut s {Store::I16{q,..}=>q.as_mut_slice()[256]=-1,Store::U16{q,..}=>q.as_mut_slice()[256]=1,_=>unreachable!()};assert!(!original_zero_predicate(&s));controls+=1;
  match &mut s {Store::I16{q,..}=>q.as_mut_slice()[256]=0,Store::U16{q,..}=>q.as_mut_slice()[256]=0,_=>unreachable!()};
  for bits in [0x8000_0000,0x7f80_0000,0xff80_0000,0x7fc0_1234,1] {match &mut s {Store::I16{scale,..}|Store::U16{scale,..}=>scale.as_mut_slice()[3]=f32::from_bits(bits),_=>unreachable!()};assert!(!original_zero_predicate(&s));controls+=1;}
 }
 assert!(!original_zero_predicate(&Store::f32(257)));controls+=1;
 emit(json!({"stage":"ability","prefetch_success":ok!=0,"last_error":error,"prefetch_calls":1,"owned_range_bytes":8192,"full_before_u16":input,"full_after_u16":values,"all_guards_and_data_exact":true,"predicate_controls":controls,"range_struct_bytes":16,"memory_counter_bytes":72,"before":counter_json(&before),"after":counter_json(&after),"GPU_executions":0}));
}
fn run(arm:&str){
 let fixtures=[include_str!("fixture-0.json"),include_str!("fixture-1.json"),include_str!("fixture-2.json")];
 for(case,config)in fixtures.iter().enumerate(){
  let cfg:SpotConfig=serde_json::from_str(config).unwrap();let mut s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),Storage::Compressed);s.use_isomorphism=true;
  let plan=GpuPlan::build(&s.spot,s.use_isomorphism);std::hint::black_box(&plan);
  let stores=[&s.regrets[0],&s.regrets[1],&s.strat[0],&s.strat[1]];let q_bytes:usize=stores.iter().map(|store|match store{Store::I16{q,..}=>q.len()*2,Store::U16{q,..}=>q.len()*2,_=>0}).sum();assert!(q_bytes<4*1024*1024*1024usize);
  let before=counters();let t=Instant::now();let(mut calls,mut success,mut error,mut range_count,mut range_bytes)=(0,false,0,0,0);let mut prefetch_ms=0.0;
  if arm=="prefetch" {let(bytes,ranges)=zero_ranges(stores);if let Some(ranges)=ranges {assert_eq!(bytes,q_bytes);for r in ranges {assert!(!r.address.is_null()&&r.bytes>0);}let start=Instant::now();let ok=unsafe{PrefetchVirtualMemory(GetCurrentProcess(),4,ranges.as_ptr(),0)};prefetch_ms=start.elapsed().as_secs_f64()*1000.0;calls=1;success=ok!=0;error=if success{0}else{unsafe{GetLastError()}};range_count=4;range_bytes=bytes;}}
  let checked=stores.map(original_zero_predicate);std::hint::black_box(checked);let elapsed=t.elapsed().as_secs_f64()*1000.0;let after=counters();assert_eq!(checked,[true;4]);
  emit(json!({"stage":"CPU_zero_scan","fixture_index":case,"board":s.spot.config.board,"arm":arm,"q_bytes":q_bytes,"cpu_arena_bytes":s.arena_bytes(),"nodes":s.spot.tree.nodes.len(),"plan_levels":plan.num_levels,"component_ms":elapsed,"prefetch_ms_contained":prefetch_ms,"prefetch_calls":calls,"prefetch_success":success,"prefetch_error":error,"prefetch_range_count":range_count,"prefetch_bytes":range_bytes,"all4_original_full_checks_pass":checked,"before":counter_json(&before),"after":counter_json(&after),"process_page_fault_delta":after.faults.wrapping_sub(before.faults),"GPU_executions":0,"full_solve_performance_measured":false}));
 }
 emit(json!({"stage":"complete","arm":arm,"fixtures":3,"GPU_executions":0,"full_solve_performance_measured":false}));
}
fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);match args[1].as_str(){"ability"=>ability(),"baseline"=>run("baseline"),"prefetch"=>run("prefetch"),_=>panic!("invalid mode")}}
'''
assert probe.count('BODY')==1;probe=probe.replace('BODY',body);(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
old.save(H/'source-review.json',{'at':old.now(),'predicate_body_exact_match_to_accepted_arena_rs':True,'original_arena_sha256':old.BASE['crates/solver/src/gpu/arena.rs'],'predicate_source_body':body,'model_scope':'Accepted solver RLIB/mimalloc/Spot/Solver/GpuPlan CPU build, fresh process per arm, original reg0/reg1/strat0/strat1 exact predicates copied verbatim. No GPU/context/pinned buffer/device allocation. Model is not the production upload function; layout fresh snapshot guards are trivially true and private ArenaLayout construction is not reproduced.','proposed_mechanism':'For Windows quantized stores with total q payload >=64MiB and every scale positive-zero, hint all4 owned q ranges once, then execute all4 original validation scans. No cached provenance, skipped/reordered q scan, parallel OR, SIMD helper, initialization omission or source activation. Threshold64MiB is fixed before first native observation and cannot be tuned after failure. Tiny cases fall back before scale precheck; additional eligibility work stays inside component clock.','limits':'Source is an isolated component prototype. Counters describe whole process and cannot isolate hard faults or physical-cache allocation. Prefetch and extra eligibility/timer overhead included. No no-tradeoff or complete-cycle claim.'})
P0=old.read(R/'runs/D123-node-array-initialization/protocol.json');command=[x.replace(str(R/'runs/D123-node-array-initialization'),str(H)).replace('d123_plan_probe','d126_prefetch_probe')for x in P0['compile_commands']['rustc']]
deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in['.rlib','.rmeta','.lib','.dll']}
for p,h in deps.items():old.pin(p,h)
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],old.REPO/'crates/solver/src/gpu/arena.rs',old.REPO/'crates/solver/src/store.rs',old.REPO/'crates/solver/src/lib.rs',R/'runs/E077-initial-closure/decision.json',C/'common_e051_live.py',C/'protected-main.json']
P={'id':'D126','at':old.now(),'status':'FROZEN_PRE_COMPILER_NATIVE','rustc_command':command,'input_sha256':deps|{str(p):old.sha(p)for p in paths},'order':[{'id':'D126B1','arm':'baseline'},{'id':'D126T1','arm':'prefetch'},{'id':'D126T2','arm':'prefetch'},{'id':'D126B2','arm':'baseline'},{'id':'D126B3','arm':'baseline'},{'id':'D126T3','arm':'prefetch'}],'component_admission':{'minimum_sum_fixture_median_saving_ms':95.825124,'minimum_total_prefetch_bytes':64*1024*1024,'guard':'For applicable>=64MiB fixtures require positive median saving and at least2/3 improving paired component observations. Inapplicable tiny fallback timing is retained; only later unchanged complete-solve strict fixture rule can qualify it.','meaning':'1% of preserved9582.5124ms E051 complete-suite medians is a prospective screening budget only. No historical sample pooling, actual speed/no-tradeoff or necessary-condition claim.'},'scope':'One Rust compiler, one small owned-buffer API/layout/predicate ability process; only if capability succeeds, exactly6 fresh CPU-only processes in BC/CB/BC order, each same3 fixtures and full original4 predicates. Same binary, no warmup/repeats/extensions. One call per eligible fixture, flags0, current-process owned ranges only. Stop on API failure, no retries/other API/flags/threshold forms. No production change, CUDA/GPU kernels or new full-solve timing.','candidate_accepted':False};old.save(H/'protocol.json',P)
for p in H.iterdir():
 if not p.is_file():continue
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'all_prepared_artifacts_HTTP_byte_verified':True,'compiler_or_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='D126'for x in s['experiments']);s['experiments'].append({'id':'D126','at':old.now(),'title':'Owned Windows prefetch and zero-scan page-fault screen','kind':'diagnostic','status':'running','correctness':'Frozen local memory/API and original-predicate controls','fixture':'3 CPU fixtures per6 fresh processes after ability control','stage':'CPU-only prefetch component screen','reason':'Check whether a current-process memory hint reduces cold quantized zero-scan cost. Original full scans retained; no new GPU/solver timing or source activation.64MiB threshold and95.825124ms saving budget fixed before observations.','accepted':False,'evidence':[{'label':'Official API contract and caveats','url':'evidence/D126-owned-memory-prefetch/api-review.json'},{'label':'Frozen component/ability protocol','url':'evidence/D126-owned-memory-prefetch/protocol.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D126',stage='D126 process-local prefetch CPU screen',activity='E077 closed after exactness passed but0.1920% aggregate slowdown. Test a separate OS memory-hint mechanism around unchanged zero validation, using owned process memory only. No kernel/new complete-solve gain; E051 accepted/live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
print('D126 protocol',old.sha(H/'protocol.json'),flush=True)
