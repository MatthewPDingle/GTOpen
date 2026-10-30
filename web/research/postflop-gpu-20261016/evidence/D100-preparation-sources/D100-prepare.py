"""Freeze one up_show L1-cache hint with resource/raw/actual-driver configuration gates."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
H=ROOT/'runs/D100-show-cache-configuration';assert not H.exists();H.mkdir();prior=ROOT/'runs/E053-kernel-control';C=ROOT/'runs/D087-cupti-driver-profile'
for n in ['accepted-evaluator.rs','corpus.json']:(H/n).write_bytes((prior/n).read_bytes())
base=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();assert base==(prior/'baseline.cu').read_bytes()
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes(base)
collector=(C/'collector.cpp').read_text(encoding='utf-8').replace('D087','D100').replace("'D','0','8','7'","'D','1','0','0'")
needle='row.regs=a->registersPerThread;row.staticShared=a->staticSharedMemory;row.dynamicShared=a->dynamicSharedMemory;';assert collector.count(needle)==1
collector=collector.replace(needle,needle+'\n            row.detail=uint32_t(a->cacheConfig.both)|(uint32_t(a->isSharedMemoryCarveoutRequested)<<8)|(uint32_t(a->sharedMemoryCarveoutRequested)<<16);row.bytes=a->sharedMemoryExecuted;')
(H/'collector.cpp').write_text(collector,encoding='utf-8',newline='\n')
probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E053_EXACT','D100_EXACT')
prelude='''
#[link(name="D100Collector")]
extern "C" {fn D100StartTrace()->u32;fn D100StopTrace()->u32;}
struct TraceGuard;
impl Drop for TraceGuard {fn drop(&mut self){let ok=unsafe{D100StopTrace()};if ok!=1{eprintln!("D100collector stop failed");}}}
'''
probe=probe.replace('type Result<T>=',prelude+'\ntype Result<T>=',1)
needle='let bf=bm.load_function("up_show")?;let cf=cm.load_function("up_show")?;';assert probe.count(needle)==1
probe=probe.replace(needle,needle+'\n cf.set_function_cache_config(cudarc::driver::sys::CUfunc_cache_enum::CU_FUNC_CACHE_PREFER_L1)?;')
needle=' let mut file=BufWriter::new(';assert probe.count(needle)==1
resource=r''' // Fixed no-launch admission before the raw controls or collector.
 use cudarc::driver::sys::{CUfunction_attribute_enum as A,CUoccupancy_flags_enum as F};
 let attrs=[A::CU_FUNC_ATTRIBUTE_NUM_REGS,A::CU_FUNC_ATTRIBUTE_LOCAL_SIZE_BYTES,A::CU_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES,A::CU_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK,A::CU_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES];
 let battr:Vec<i32>=attrs.iter().map(|&a|bf.get_attribute(a).unwrap()).collect();let cattr:Vec<i32>=attrs.iter().map(|&a|cf.get_attribute(a).unwrap()).collect();
 let mut occupancy=Vec::new();let mut resource_ok=battr==cattr;
 for (geometry,g) in gs.iter().enumerate(){let dynamic=n(g,"dynamic_shared_bytes");for width in [64u32,128,256]{for flag in [F::CU_OCCUPANCY_DEFAULT,F::CU_OCCUPANCY_DISABLE_CACHING_OVERRIDE]{let b=bf.occupancy_max_active_blocks_per_multiprocessor(width,dynamic,Some(flag))?;let c=cf.occupancy_max_active_blocks_per_multiprocessor(width,dynamic,Some(flag))?;if c<b||c==0{resource_ok=false;}occupancy.push(json!({"geometry":geometry,"threads":width,"dynamic_shared_bytes":dynamic,"flag":flag as u32,"baseline_blocks":b,"candidate_blocks":c}));}}}
 emit(json!({"stage":"resource_gate","baseline_attributes":battr,"candidate_attributes":cattr,"attribute_order":["registers","local_bytes","static_shared_bytes","max_threads","max_dynamic_shared_bytes"],"occupancy":occupancy,"passed":resource_ok,"kernel_launches":0,"code_identical":BASELINE==CANDIDATE}))?;
 if !resource_ok {emit(json!({"stage":"resource_rejected","kernel_launches":0,"solver_executions":0,"performance_measurement":false}))?;return Ok(());}
 if unsafe{D100StartTrace()}!=1{return Err("D100collector start failed".into());}let trace=TraceGuard;
'''
probe=probe.replace(needle,resource+needle)
needle='file.flush()?;file.get_ref().sync_all()?;s.synchronize()?;ctx.check_err()?;';assert probe.count(needle)==1
probe=probe.replace(needle,needle+'\n if unsafe{D100StopTrace()}!=1{return Err("D100collector finalization failed".into());}drop(trace);')
probe=probe.replace('//! E053: exact128thread sorted-copy/prefix fusion differential; no timing.','//! D100: identical production code; one up_show cache preference only; no timing.')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
oldcommand=old.read(C/'build/collector.invocation.json')['command'];command=oldcommand.replace(str(C),str(H)).replace('D087Collector','D100Collector')
assert command.count('cl /nologo')==1;command=command.replace('cl /nologo','cl /Fo:'+str(H/'build/collector.obj')+' /nologo')
P=old.read(prior/'execution-plan-r2.json');rustc=[x.replace(str(prior),str(H)) for x in P['rustc_command']];rustc.extend(['-L','native='+str(H/'build')])
cppdeps=old.read(C/'build-plan.json')['input_sha256'];deps={p:h for p,h in cppdeps.items() if Path(p).suffix in ['.h','.lib','.dll']};deps.update({p:h for p,h in P['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']})
inputs=[*H.iterdir(),Path(__file__),ROOT/'runs/accepted-E051/common_e051.py',old.REPO/'crates/solver/src/gpu/kernels.cu',old.REPO/'crates/solver/src/gpu/mod.rs',Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7\src\driver\safe\core.rs')]
pins={str(p):old.sha(p) for p in inputs if p.is_file()}|deps
old.save(H/'protocol.json',{'id':H.name,'at':old.now(),'status':'FROZEN_PRE_COMPILE_AND_GPU','collector_command':command,'rustc_command':rustc,'input_sha256':pins,'private_cupti_dll_dir':str(ROOT/'runs/D085-cupti-activity/vendor/cuda_cupti/cuda_cupti-windows-x86_64-12.9.79-archive/lib'),'fixed_hint':'CU_FUNC_CACHE_PREFER_L1only on candidate module up_show. Baseline default per-function config. Code/ABI/launch/buffers/arithmetic identical. No global/context setting, injection, counters or live attach. No alternate preference/carveout/kernel/scope variant rescue.','stages':['Actual compiled attributes equal (registers/local/static shared/maxthreads/maxdynamic), both functions fit same default block limits.','All36geometry x64/128/256threads x default/disable-caching-override flags driver occupancies nondecreasing and nonzero before any kernel. Stop if fail.','Exactly364paired direct raw comparisons/728kernels from retained corpus, exact full outputs/actual inputs/guards/nonfinite cases.','Private CUPTI collector records requested/executed cache byte, carveout flag/percent and driver sharedMemoryExecuted with every kernel. Explicit lifecycle, no counters, dropped/errors/invalid timestamps forbidden. Join all728launches to driver correlations and retained raw case/arm/geometry.','Require actual recorded driver configuration change in at least one matched geometry before any integrated source or timing candidate. Requested enum alone is insufficient; if carveout explicitly requested ignore documented stale cacheConfig fields and use driver shared-memory size.'],'trace_schema':{'bytes':176,'format':'<6I4Q10I80s','magic':'D100-TRACE-v1 followed by3null bytes','kernel_detail':'cacheConfig.both in bits0..7,isSharedMemoryCarveoutRequested in8..15,sharedMemoryCarveoutRequested in16..23','kernel_bytes_field':'uint64 copy of actual CUPTI sharedMemoryExecuted; not memory traffic or hardware cache counter'},'case_identities':'Original retained corpus names are preserved; new diagnostic marker D100_EXACT.','expected_cases':364,'expected_launches':728,'no_timing_score':True,'no_source_activation':True,'future_qualification':'Only if resource+exactness+actual mechanism gates pass may one fixed integrated cache-hint candidate run ordinary units and unchanged1%fullcycle/fixture/fresh16/broader/material/holdout/cumulative qualification. No universal cache-size or speed inference from SDK fields.','official_references':['https://docs.nvidia.com/cuda/archive/12.9.1/cuda-driver-api/group__CUDA__EXEC.html#group__CUDA__EXEC_1g40f8c11e81def95dc0072a375f965681','https://docs.nvidia.com/cupti/12.9.1/api/structCUpti__ActivityKernel9.html'],'driver_documentation_limits':'Cache request is a preference, may be overridden or do nothing on fixed-cache devices; switching preferences may insert device-side synchronization. Blackwell B200SM10.0cache capacities are not GeForce5090SM12.0measurements.'})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(e['id']=='D100' for e in s['experiments'])
 s['experiments'].append({'id':'D100','at':old.now(),'kind':'diagnostic','title':'Check actual showdown cache configuration','status':'running','correctness':'pending','stage':'Frozen resource gate before raw kernel/driver configuration audit','reason':'One L1preference with identical CUDA. Require preserved occupancy, exact raw states and actual driver configuration change before integrated timing.','evidence':[]})
 s.update(updated_at=old.now(),state='running',active_experiment='D100',stage='D100 GPU cache mechanism admission',activity='D099allocator component closed. Test one per-function showdown L1hint against default using actual resource/configuration fields; no claimed speed gain.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'tracked_source_activated':False,'code_source_sha256':old.sha(H/'baseline.cu'),'expected_maximum_kernel_launches':728}),flush=True)
