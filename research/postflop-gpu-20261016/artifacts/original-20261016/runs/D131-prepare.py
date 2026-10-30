"""Freeze original serial zero-validation overlapping caller-only NVRTC/pinned/layout setup."""
from pathlib import Path
import ast,json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D131-zero-check-setup-overlap';assert not H.exists();H.mkdir();A=R/'runs/D092-action-arity-order'
history=subprocess.run(['git','log','--all','--format=%H','-G','prechecked|zero_check_worker|zero_validation_task|validate_while_setup|checks_with_setup','--','crates/solver/src/gpu','crates/solver/src/store.rs'],cwd=old.REPO,text=True,capture_output=True,check=True);assert not history.stdout.strip()
arena=(old.REPO/'crates/solver/src/gpu/arena.rs').read_text(encoding='utf-8');mod=(old.REPO/'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8');a=arena.index('        let zero = match store {');b=arena.index('        // Keep previously captured',a);body=arena[a:b].strip();assert body.startswith('let zero = ')and body.endswith(';');body=body[len('let zero = '):-1]
(H/'accepted-arena.rs').write_bytes((old.REPO/'crates/solver/src/gpu/arena.rs').read_bytes());old.pin(H/'accepted-arena.rs',old.BASE['crates/solver/src/gpu/arena.rs'])
bridge='''
impl ArenaLayout {
    pub(super) fn probe_guards(&self, which: usize) -> bool {
        self.initial[which].is_empty() && self.inactive.iter().all(|b| b.initial[which] == usize::MAX)
    }
    pub(super) fn probe_words(&self) -> Vec<u64> {
        let mut v=vec![self.compact as u64,self.len as u64];
        for (n,c) in [(self.active.len(),self.active.capacity()),(self.copies.len(),self.copies.capacity()),(self.inactive.len(),self.inactive.capacity())] {v.extend([n as u64,c as u64]);}
        for b in &self.active {v.extend([b.node as u64,b.host,b.device as u64,b.len as u64]);}
        for b in &self.copies {v.extend([b.host,b.device as u64,b.len as u64]);}
        for b in &self.inactive {v.extend([b.node as u64,b.host,b.len as u64,b.initial[0]as u64,b.initial[1]as u64]);}
        for a in self.initial.iter().chain(std::iter::once(&self.zeros)) {v.extend([a.len()as u64,a.capacity()as u64]);v.extend(a.iter().map(|x|x.to_bits()as u64));}
        v
    }
    pub(super) fn probe_original_predicate(store: &Store) -> bool {
        let layout=Self{compact:false,len:0,active:vec![],copies:vec![],inactive:vec![],initial:[vec![],vec![]],zeros:vec![]};
        layout.can_upload_zeros(store,0)
    }
}
'''
(H/'arena-observed.rs').write_text(arena+bridge,encoding='utf-8',newline='\n');assert(H/'arena-observed.rs').read_text(encoding='utf-8').removesuffix(bridge)==arena
a=mod.index('pub(crate) struct PinnedBuf {');b=mod.index('/// Rough VRAM requirement',a);pinned=mod[a:b]
a=mod.index('fn write_arena(');b=mod.index('#[cfg(test)]',a);writer=mod[a:b]
for i in range(3):shutil.copyfile(A/f'fixture-{i}.json',H/f'fixture-{i}.json')
shutil.copyfile(old.REPO/'crates/solver/src/gpu/kernels.cu',H/'kernels.cu');old.pin(H/'kernels.cu',old.BASE['crates/solver/src/gpu/kernels.cu'])
d130=(R/'runs/D130-plan-context-overlap/probe.rs').read_text(encoding='utf-8');a=d130.index('#[repr(C)]');b=d130.index('fn coordinate<',a);counters=d130[a:b].replace('D130 ','D131 ')
probe=r'''#![allow(dead_code)]
pub use solver::{cfr,store,tree};
use solver::{Solver,Spot,SpotConfig,store::{Storage,Store},gpu::plan::GpuPlan};
use cudarc::{driver::{CudaContext,CudaStream,CudaModule},nvrtc::{compile_ptx_with_opts,CompileOptions,Ptx}};
use std::{ffi::c_void,fs::{File,OpenOptions},io::{self,BufWriter,Write},path::Path,sync::{Arc,atomic::{AtomicUsize,Ordering}},time::Instant};
use rayon::prelude::*;use serde_json::{json,Value};
mod plan{pub use solver::gpu::plan::GpuPlan;}
#[path="arena-observed.rs"]mod arena;
fn e(err:impl std::fmt::Debug)->String{format!("{err:?}")}
PINNED
WRITER
COUNTERS
struct ZeroCheck<'a>{store:&'a Store,positive:bool}
impl<'a> ZeroCheck<'a>{
 fn new(store:&'a Store)->Self{let positive={PREDICATE};Self{store,positive}}
 fn positive_for(&self,store:&Store)->Option<bool>{std::ptr::eq(self.store,store).then_some(self.positive)}
}
fn checks_with_setup<S,V:Send,F:FnOnce()->Result<S,String>,C:Fn()->V+Sync>(eligible:bool,setup:F,checks:C)->Result<(S,V),String>{
 if !eligible{let s=setup()?;return Ok((s,checks()));}
 std::thread::scope(|scope|{
  let worker=std::thread::Builder::new().name("gtopen-zero-check".into()).spawn_scoped(scope,||checks());
  let s=setup();let result=worker.ok().map(|h|h.join());let s=s?;
  let values=match result{Some(Ok(v))=>v,Some(Err(payload))=>std::panic::resume_unwind(payload),None=>checks()};Ok((s,values))
 })
}
struct Mock(Arc<AtomicUsize>);impl Drop for Mock{fn drop(&mut self){self.0.fetch_add(1,Ordering::SeqCst);}}
fn store_image(s:&Store)->Vec<u32>{match s{Store::I16{q,scale}=>q.as_slice().iter().map(|&x|x as u16 as u32).chain(scale.as_slice().iter().map(|x|x.to_bits())).collect(),Store::U16{q,scale}=>q.as_slice().iter().map(|&x|x as u32).chain(scale.as_slice().iter().map(|x|x.to_bits())).collect(),Store::F32(b)=>b.as_slice().iter().map(|x|x.to_bits()).collect()}}
fn ability(){
 let mut lifecycle=0;let caller=std::thread::current().id();
 for eligible in[false,true]{for setupmode in[0,1,2]{for checkmode in[0,1]{
  let calls=Arc::new(AtomicUsize::new(0));let drops=Arc::new(AtomicUsize::new(0));let c=calls.clone();let d=drops.clone();
  let outcome=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||checks_with_setup(eligible,||{assert_eq!(std::thread::current().id(),caller);match setupmode{0=>Ok(7usize),1=>Err("setup".into()),_=>panic!("setup mock")}},||{c.fetch_add(1,Ordering::SeqCst);assert_eq!(std::thread::current().id()==caller,!eligible);if checkmode==1{panic!("check mock");}Mock(d.clone())})));
  let expected=if eligible||setupmode==0{1}else{0};assert_eq!(calls.load(Ordering::SeqCst),expected);
  match(setupmode,checkmode,outcome){(1,_,Ok(Err(x)))=>assert_eq!(x,"setup"),(2,_,Err(_))=>{},(0,0,Ok(Ok((s,v))))=>{assert_eq!(s,7);drop(v);},(0,1,Err(_))=>{},_=>panic!("incorrect lifecycle")}
  assert_eq!(drops.load(Ordering::SeqCst),if checkmode==0{expected}else{0});lifecycle+=1;
 }}}
 let mut predicates=0;let mut full_words=0;let mut images=Vec::new();
 for signed in[false,true]{let mut s=if signed{Store::i16(257,4)}else{Store::u16(257,4)};
  for step in 0..7 {if step==1{match &mut s{Store::I16{q,..}=>q.as_mut_slice()[256]=-1,Store::U16{q,..}=>q.as_mut_slice()[256]=1,_=>unreachable!()}}else if step>=2{match &mut s{Store::I16{q,scale}=>{q.as_mut_slice()[256]=0;scale.as_mut_slice()[3]=f32::from_bits([0x8000_0000,0x7f80_0000,0xff80_0000,0x7fc0_1234,1][step-2]);},Store::U16{q,scale}=>{q.as_mut_slice()[256]=0;scale.as_mut_slice()[3]=f32::from_bits([0x8000_0000,0x7f80_0000,0xff80_0000,0x7fc0_1234,1][step-2]);},_=>unreachable!()}}
   let before=store_image(&s);let check=ZeroCheck::new(&s);let original=arena::ArenaLayout::probe_original_predicate(&s);assert_eq!(check.positive_for(&s),Some(original));assert_eq!(original,step==0);let other=Store::u16(257,4);assert_eq!(check.positive_for(&other),None);drop(check);let after=store_image(&s);assert_eq!(before,after);full_words+=before.len()*2;images.push(json!({"signed":signed,"step":step,"before":before,"after":after}));predicates+=1;
  }
 }
 let s=Store::f32(257);assert!(!arena::ArenaLayout::probe_original_predicate(&s));assert_eq!(ZeroCheck::new(&s).positive_for(&s),Some(false));predicates+=1;
 assert_eq!(lifecycle,12);assert_eq!(predicates,15);assert_eq!(std::mem::size_of::<FileTime>(),8);assert_eq!(std::mem::size_of::<MemoryCounters>(),72);let c=cpu_ticks();let _=counters();assert!(cpu_ticks()>=c);
 emit(json!({"stage":"ability","lifecycle_cases":lifecycle,"predicate_cases":predicates,"all_full_words_before_after_exact":true,"full_words_checked":full_words,"full_images":images,"wrong_store_tokens_rejected":14,"setup_stays_on_caller":true,"cleanup_and_setup_error_priority_pass":true,"CUDA_or_application_executions":0}));
}
fn setup(ctx:&Arc<CudaContext>,s:&Solver,plan:&GpuPlan)->Result<(Arc<CudaModule>,PinnedBuf,[arena::ArenaLayout;2]),String>{
 let(major,minor)=ctx.compute_capability().map_err(e)?;let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 static PTX:std::sync::OnceLock<Result<Ptx,String>>=std::sync::OnceLock::new();
 let ptx=PTX.get_or_init(||compile_ptx_with_opts(include_str!("kernels.cu"),CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
 let module=ctx.load_module(ptx).map_err(e)?;let data_len=plan.arena_elements;let pinned=PinnedBuf::new(ctx,data_len[0].max(data_len[1]))?;
 let layouts=[arena::ArenaLayout::new(s,plan,0),arena::ArenaLayout::new(s,plan,1)];Ok((module,pinned,layouts))
}
fn words(f:&mut impl Write,v:&[u64]){f.write_all(&(v.len()as u64).to_le_bytes()).unwrap();for c in v.chunks(8192){let b:Vec<u8>=c.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();}}
fn run(arm:&str,out:&Path){std::fs::create_dir(out).unwrap();let configs=[include_str!("fixture-0.json"),include_str!("fixture-1.json"),include_str!("fixture-2.json")];
 for(i,config)in configs.iter().enumerate(){let cfg:SpotConfig=serde_json::from_str(config).unwrap();let mut s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),Storage::Compressed);s.use_isomorphism=true;let plan=GpuPlan::build(&s.spot,s.use_isomorphism);let ctx=CudaContext::new(0).unwrap();let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}assert_eq!(ctx.compute_capability().unwrap(),(12,0));
  let stores=[&s.regrets[0],&s.regrets[1],&s.strat[0],&s.strat[1]];let q_bytes:usize=stores.iter().map(|s|match s{Store::I16{q,..}=>q.len()*2,Store::U16{q,..}=>q.len()*2,Store::F32(_)=>0}).sum();let eligible=arm=="overlap"&&q_bytes>=64*1024*1024;
  let mb=counters();let cb=cpu_ticks();let clock=Instant::now();
  let((module,pinned,layouts),proofs)=checks_with_setup(eligible,||setup(&ctx,&s,&plan),||stores.map(ZeroCheck::new)).unwrap();
  let flags=[proofs[0].positive_for(stores[0]).unwrap()&&layouts[0].probe_guards(0),proofs[1].positive_for(stores[1]).unwrap()&&layouts[1].probe_guards(0),proofs[2].positive_for(stores[2]).unwrap()&&layouts[0].probe_guards(1),proofs[3].positive_for(stores[3]).unwrap()&&layouts[1].probe_guards(1)];std::hint::black_box(flags);
  let elapsed=clock.elapsed().as_secs_f64()*1000.0;let ca=cpu_ticks();let ma=counters();assert_eq!(flags,[true;4]);assert!(ca>=cb);stream.synchronize().unwrap();
  let raw=out.join(format!("fixture-{i}.bin"));let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(&raw).unwrap());f.write_all(b"D131-LAYOUT-R1\0\0").unwrap();f.write_all(&(i as u32).to_le_bytes()).unwrap();f.write_all(&(2u32).to_le_bytes()).unwrap();let mut layout_words=0;
  for p in 0..2{let reference=arena::ArenaLayout::new(&s,&plan,p);let actual=layouts[p].probe_words();let expected=reference.probe_words();assert_eq!(actual,expected);layout_words+=actual.len();words(&mut f,&actual);words(&mut f,&expected);}f.flush().unwrap();f.get_ref().sync_all().unwrap();
  emit(json!({"stage":"zero_setup_component","fixture_index":i,"arm":arm,"board":s.spot.config.board,"nodes":s.spot.tree.nodes.len(),"q_bytes":q_bytes,"overlap_eligible":eligible,"pinned_bytes":pinned.len*4,"component_ms":elapsed,"process_CPU_ms":(ca-cb)as f64/10000.0,"cpu_before_ticks100ns":cb,"cpu_after_ticks100ns":ca,"before":mem(&mb),"after":mem(&ma),"all_original_full_predicates_and_guards":flags,"full_private_layout_words_per_arm":layout_words,"raw_layout":raw,"setup_CUDA_calls_stay_on_caller":true,"application_kernel_launches":0,"GPU_solver_executions":0,"performance_is_full_solve":false}));
  drop(proofs);drop(layouts);drop(pinned);drop(module);drop(stream);drop(ctx);drop(plan);drop(s);
 }
 emit(json!({"stage":"complete","arm":arm,"fixtures":3,"application_kernel_launches":0,"GPU_solver_executions":0,"performance_is_full_solve":false}));}
fn main(){let args:Vec<_>=std::env::args().collect();match args.get(1).map(String::as_str){Some("ability")=>{assert_eq!(args.len(),2);ability();},Some("baseline")|Some("overlap")=>{assert_eq!(args.len(),3);run(&args[1],Path::new(&args[2]));},_=>panic!("invalid mode")}}
'''
for key,value in[('PINNED',pinned),('WRITER',writer),('COUNTERS',counters),('PREDICATE',body)]:assert probe.count(key)==1;probe=probe.replace(key,value)
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
old.save(H/'source-review.json',{'at':old.now(),'original_arena_sha256':old.BASE['crates/solver/src/gpu/arena.rs'],'original_mod_sha256':old.BASE['crates/solver/src/gpu/mod.rs'],'original_CUDA_sha256':old.BASE['crates/solver/src/gpu/kernels.cu'],'full_arena_source_byte_verified':True,'arena_bridge_only':'Append read-only field serialization, snapshot guards, and original full-predicate accessibility; original implementation unchanged.','PinnedBuf_and_write_arena_copied_verbatim':True,'predicate_expression_copied_verbatim':body,'mechanism':'All four original serial scale/q scans execute once, in original reg0/reg1/strat0/strat1 order, on one scoped CPU-only worker while caller performs original NVRTC/module/pinned/layout setup. Typed epoch-local ZeroCheck borrows Store and accepts only identical store address; all original snapshot/inactive guards execute on caller after join. No persistent metadata/provenance cache or skipped validation, integer grouping/ISA/precision/order unchanged. No CUDA call/context/stream leaves caller.','eligibility':'Fixed total quantized bytes>=64MiB; smaller/F32 paths serial. No iteration/freshness inference or extra positive-zero scale precheck. Fixed before first native; no threshold/scope/placement/thread rescue after actual failure.','safety':'ArenaBuf exposes Sync for Sync types but as_slice contract requires no mutating traversal. Solver constructor immutable borrow and actual setup source only touch tree/plan/owned allocations; no CPUstore writes or traversal while proof borrowed. Worker joined before all consumers/errors. Setup error retains priority over worker panic; normal error/panic cleanup tested. OSspawnfailure serial fallback reviewed, not resource-injected.','novelty_query':history.args,'all_ref_matches':history.stdout.splitlines(),'prior_false_positive_review':'Archived E045 ZERO_PROOF helpers are parallel per-q integer-OR chunk reductions and remain closed. D131 performs original full serial scans once, changes dependency scheduling only. E049 persistent ArenaBuf provenance, D126 hints, D127 sparse firsttouch, E071 planner stages, and E079 context worker are neither reused nor tuned. CUDA context creation/binding remain original caller-only before the test window.','limits':'Source-matched component includes actual NVRTC/module/pinned allocation/ArenaLayout source and exact predicates, but omits device arenas/uploads/solving and private integrated GpuSolver caller. Default-context, warm/F32/copy/panic/memory/compatibility/fullsolve risks still need qualification. Source reasoning is root audit, not external independence.'})
P0=old.read(R/'runs/D130-plan-context-overlap/protocol.json');command=[x.replace(str(R/'runs/D130-plan-context-overlap'),str(H)).replace('d130_plan_context_probe','d131_zero_setup_probe')for x in P0['rustc_command']];deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in['.rlib','.rmeta','.lib','.dll']}
for p,h in deps.items():old.pin(p,h)
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],old.REPO/'crates/solver/src/gpu/mod.rs',old.REPO/'crates/solver/src/gpu/arena.rs',old.REPO/'crates/solver/src/store.rs',R/'runs/E079-initial-closure/decision.json',C/'common_e051_live.py',C/'protected-main.json']
P={'id':'D131','at':old.now(),'status':'FROZEN_PRE_COMPILER_COMPONENT','input_sha256':deps|{str(p):old.sha(p)for p in paths},'rustc_command':command,'order':[{'id':'D131B1','arm':'baseline'},{'id':'D131T1','arm':'overlap'},{'id':'D131T2','arm':'overlap'},{'id':'D131B2','arm':'baseline'},{'id':'D131B3','arm':'baseline'},{'id':'D131T3','arm':'overlap'}],'screen':{'minimum_sum_fixture_median_saving_ms':95.825124,'minimum_total_q_bytes':64*1024*1024,'maximum_CPU_median_ratio':1.10,'CPU_median_allowance_ms':5.0,'wall_guard':'Eligiblelargefixtures:positive median saving and>=2/3improvingpairs. Tinyserialpath retained; actualfullcycle strictfixtureguard unchanged.','meaning':'Fixed prospectivecomponentbudget1%ofpreserved9582.5124ms acceptedscoreonly,nosamplepooling/headroom/fullsolve/no-tradeoffclaim.'},'scope':'Onecompiler;oneCPU-only12lifecycle/15predicate/fullbeforeafter/wrongStoretokenabilityprocess;thenexactly6freshprocessesBC/CB/BC,each3canonicalcompressedfixtures. OriginalCPUplan/budgetcontext/streambeforeclock oncaller. Clock covers originalNVRTC/module/PinnedBuf/ArenaLayout setup+fullfourpositivezero scans/guards vsindependentCPUscanoverlap. SamefixedSourceCUDA/PTXOnceLockbehavior, actualcallerCUDAAPIsonly. Noapplicationkernel/devicearenaupload/solver. Fullprivatelayoutsource/data/caps compareoutsideclockaftereachfixture. No repeats/extensions/variantsafteractualfailedcomponent.','candidate_accepted':False};old.save(H/'protocol.json',P)
for p in H.iterdir():
 if p.is_file():
  key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'all_prepared_artifacts_HTTP_byte_verified':True,'compiler_native_or_CUDA_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='D131'for x in s['experiments']);s['experiments'].append({'id':'D131','at':old.now(),'title':'Overlap full zero validation with GPU compiler and staging setup','kind':'diagnostic','status':'running','correctness':'Frozen original predicates, lifecycle/token and full layout controls','fixture':'Six fresh component processes, three compressed fixtures each','stage':'Zero-validation/setup component screen','reason':'One CPU-only worker runs all original serial scans while the caller does original NVRTC, module, pinned-memory, and arena-layout setup. CUDA stays on the caller. Every scan and layout guard retained; no persistent cached metadata. No full-solve speed claim.','accepted':False,'evidence':[{'label':'Frozen component protocol','url':'evidence/D131-zero-check-setup-overlap/protocol.json'},{'label':'Exact source/borrow/ownership review','url':'evidence/D131-zero-check-setup-overlap/source-review.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D131',stage='D131 zero-validation and setup overlap screen',activity='E079 closed after the river fixture regression. Test a distinct dependency overlap with original full scans and caller-only CUDA setup. Compare exact layout data and all-thread CPU cost. Accepted/live E051 gain remains 12.44%.');old.ar.atomic_json(old.ar.STATUS,s)
print('D131 preparation protocol',old.sha(H/'protocol.json'),flush=True)
