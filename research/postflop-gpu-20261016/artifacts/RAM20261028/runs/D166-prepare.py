import sys,shutil,re,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
scope=ROOT/'runs/D166-canonical-compiler-scope/scope-review.json';S=h.read(scope)
for name,digest in S['completed_prerequisites'].items():h.pin(ROOT/'comparisons'/name/'report.json',digest)
H=ROOT/'runs/D166-canonical-compiler-control';H.mkdir(exist_ok=False)
for source,dest in [('D166-bounded-child.py','bounded_child.py'),('D157-sampler.py','sampler.py'),('D166-audit.py','audit.py'),('D166-execute.py','execute.py')]:
    shutil.copyfile(ROOT/'runs'/source,H/dest);ast.parse((H/dest).read_text(encoding='utf-8'))
parent=ROOT/'runs/D150-CFV-liveness/gpu/mod.rs';t=parent.read_text(encoding='utf-8');shim=t[t.index('pub mod plan {'):t.index('\nmod arena;')]
fields=re.findall(r'field!\("([^"\n]+)", ([^\n]+)\);',t);assert len(fields)==66 and len(set(x[0] for x in fields))==66
prior=ROOT/'runs/D150-CFV-liveness/probe.rs';p=prior.read_text(encoding='utf-8');helpers=p[p.index('pub trait Word'):p.index('pub fn capture')]+p[p.index('fn host_field('):p.index('fn state_frame(')]
helpers+='''
pub fn d166_field<T:Word>(s:&Arc<CudaStream>,name:&str,d:&CudaSlice<T>,out:&mut BufWriter<File>)->Value{
 let bytes=d.len().checked_mul(std::mem::size_of::<T>()).unwrap();assert!(bytes<=8*1024usize.pow(3));
 let values=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();assert_eq!(values.len(),d.len());
 let bits=words(&values);assert_eq!(bits.len()*4,bytes);host_field(out,name,&bits);
 json!({"name":name,"elements":d.len(),"element_bytes":std::mem::size_of::<T>(),"words":bits.len(),"raw_bytes":bytes})
}
'''
benchpath=h.REPO/'crates/solver/tests/postflop_autoresearch.rs';original=benchpath.read_text(encoding='utf-8')
bench,n=re.subn(r'^//!','//',original,flags=re.M);assert n==7
bench=bench.replace('#![cfg(feature = "gpu")]\n','',1).replace('use solver::gpu::{GpuSolver, KERNEL_NAMES};','use observed::{GpuSolver, KERNEL_NAMES};',1).replace('include_str!("../../../bench_spot.json")','include_str!("bench_spot.json")',1)
assert bench.count('"runtime_nvrtc_jit_included": true')==2;bench=bench.replace('"runtime_nvrtc_jit_included": true','"runtime_nvrtc_jit_included": false')
needle='        completed += 1;';assert bench.count(needle)==1;bench=bench.replace(needle,'        assert!(!profile,"D166no profiling");\n        d156_after(gpu,host,name);\n'+needle,1)
helper=(ROOT/'runs/D156-lifecycle.rs').read_text(encoding='utf-8');assert helper.count('.cfv.u32')==1 and helper.count('g.d156_snapshot(')==1
helper=helper.replace('.cfv.u32','.gpu.bin',1).replace('g.d156_snapshot(','g.d166_snapshot(',1)
observer=(ROOT/'runs/D166-observer.rs').read_text(encoding='utf-8');assert observer.count('// D166_ALL_DEVICE_FIELDS')==1
observer=observer.replace('// D166_ALL_DEVICE_FIELDS','\n        '.join(f'field!("{n}", {e});' for n,e in fields),1)
production=(h.REPO/'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8');start=production.index('        static PTX:');end=production.index('            .clone()?;',start)+len('            .clone()?;');compile_block=production[start:end]
commands={};deps=ROOT/'reference/accepted-e080-deps'
for arm in ['baseline','candidate']:
    d=H/arm;d.mkdir();shutil.copyfile(ROOT/'runs/D162-private-dependency-repair/execution'/(arm+'.ptx'),H/(arm+'.ptx'))
    for name in ['arena.rs','kernels.cu']:shutil.copyfile(h.REPO/'crates/solver/src/gpu'/name,d/name)
    binding='        assert_eq!(arch,"compute_120");\n        println!("D166_BIND '+arm+'");\n        let ptx=cudarc::nvrtc::Ptx::from_src(include_str!("../'+arm+'.ptx"));'
    adapted=production.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1).replace(compile_block,binding,1)
    reverse=adapted.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1).replace(binding,compile_block,1);assert reverse==production
    (d/'mod.rs').write_bytes((adapted+'\n'+observer).encode())
    prefix='#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]\npub use solver::*;\n#[path="'+arm+'/mod.rs"]mod observed;\nuse cudarc::driver::{CudaSlice,CudaStream,DeviceRepr};\nuse std::{fs::{File,OpenOptions},io::BufWriter,path::Path};\n'
    source=H/(arm+'-probe.rs');source.write_bytes((prefix+bench+'\n'+helpers+'\n'+helper).encode())
    cmd=['rustc',str(source),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
    for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
    commands[arm]=cmd+['-o',str(H/(arm+'.exe'))]
shutil.copyfile(h.REPO/'bench_spot.json',H/'bench_spot.json')
h.save(H/'source-review.json',{'at':h.now(),'id':'D166','production_exact_reversal_after_plan_binding_adapters':True,'device_field_inventory':[x[0] for x in fields],'host_fields':['iteration','algorithm','hands'],'actual_fields_per_GPU_frame':69,'snapshot_scope':'Every actual66devicebuffer in exact type converted losslessly to littleendian u32words,plus host iteration/algorithm/hands. Raw bytes or lossless all-positive-zero run;no hashes/samples. CPU q/scale/rawpublication/query/save fullbytes. Complete physical CFV required equal,no prefix/tail exception. Metadata logical geometry/graph presence/host wrapper exact.','peak_design':'Streamone actual field atatime;atmost one original typed host Vec and one same-byte u32Vec perfield,each<=8GiB,drop atreturn before nextfield. Existing setup/native process bounded32GiB reportedWS/commit,availableRAM64GiB preflight/32GiB during.256GiBraw+64GiBdiskheadroom,onearmprocessatatime. Sample limitations disclosed.','telemetry_adapter':'Exactly two existing runtime_nvrtc_jit_included fields setfalse beforeexecution becausesealedPTX bypassesruntimecompile. Reader requiresfalse and excludes onlythis telemetryflag from original scientificanchor comparison,alongside original timingfields. All other result/config/state/stopping/checkpoint fields exactlyunchanged. Wholecanonical timing isdiagnostic andunscored.','lifecycle':'Existing fixed D156 appended continued/rootFreeze/lock/save/load/warmresume protocol after each fullcanonical result. All original ranges,tree,suit/algorithm/storage,target,cadence,cap andfieldcounts frozen. No packetcode ormetadata,newoptimizer/runtimecompiler/source oraccuracytransform.','failure':'Entire rawpair bytes andactualscientificanchor mustmatch. No paddingclassification,datatype/tolerance,fieldomission,source/corpus/compiler/flags/shape/sample rescue afteractualfailure. Adapter failures preserveoriginalevidence andrequireseparatemechanicalreview beforeany repetition.'})
files=[Path(__file__),scope,parent,prior,benchpath,ROOT/'runs/D156-lifecycle.rs',ROOT/'runs/D166-observer.rs',ROOT/'runs/D166-bounded-child.py',ROOT/'epoch/exact-anchor.json',ROOT/'comparisons/D165-compiler-engine-control/report.json']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
limits={'raw_reservation_bytes':256*1024**3,'disk_headroom_bytes':64*1024**3,'required_free_bytes':320*1024**3,'available_RAM_before_bytes':64*1024**3,'available_RAM_during_bytes':32*1024**3,'process_reported_peak_max_bytes':32*1024**3,'native_timeout_seconds':1800,'poll_interval_ms':200}
h.save(H/'protocol.json',{'id':'D166','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_CANONICAL_NATIVE_CONTROLS','sequence':['baseline','candidate'],'rustc_commands':commands,'limits':limits,'expected_full_records':6,'expected_checkpoints':46,'lifecycle_stages':['converged','continued','locked','resumed'],'expected_CPU_pairs':12,'expected_GPU_all69field_pairs':12,'expected_query_pairs':6,'expected_save_pairs':3,'expected_future_EV_pairs':9,'expected_PTX_bindings_per_arm':6,'input_sha256':{str(p):h.sha(p) for p in files},'scientific_telemetry_exception':'runtime_nvrtc_jit_included mustfalse botharms;omitthissingle non-scientific compile-clock telemetryflag during original-anchor comparison. All numerical/config/fingerprint/iteration/checkpoint fields exact. No other weakening.','scope':'Original full canonical same-quality science plus appended complete CPU/66devicefield/hoststate/query/save/futureEV controls. Everyphysicalretainedrawpair byte equal. TwoRustcompilers,two fixed nativearmprocesses,oneindependent streamingreader. No NVRTC orruntimecompiler,initial3/fresh16/cumulative speed samples,production activation ornew acceptedgain.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
