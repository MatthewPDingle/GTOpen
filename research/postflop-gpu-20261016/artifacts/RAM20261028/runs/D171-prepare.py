import ast,json,re,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status());S=ROOT/'runs/E094-source-r3';M=h.read(S/'manifest.json');H=ROOT/'runs/D171-offset-raw-control';H.mkdir(exist_ok=False)
prior=ROOT/'runs/D166-canonical-compiler-control';old=(prior/'baseline/mod.rs').read_text(encoding='utf-8');shim=old[old.index('pub mod plan {'):old.index('\nmod arena;')]
fields=re.findall(r'field!\("([^"\n]+)", ([^\n]+)\);',old);assert len(fields)==66
parent=ROOT/'runs/D150-CFV-liveness/probe.rs';p=parent.read_text(encoding='utf-8');helpers=p[p.index('pub trait Word'):p.index('pub fn capture')]+p[p.index('fn host_field('):p.index('fn state_frame(')]
priorprobe=(prior/'baseline-probe.rs').read_text(encoding='utf-8');start=priorprobe.index('pub fn d166_field');a=priorprobe.index('{',start);end=a+1;depth=1
while depth:
 if priorprobe[end]=='{':depth+=1
 elif priorprobe[end]=='}':depth-=1
 end+=1
helpers+=priorprobe[start:end]+'\n'
assert helpers.count('pub fn d166_field')==1 and helpers.rstrip().endswith('}')
bench=(h.REPO/'crates/solver/tests/postflop_autoresearch.rs').read_text(encoding='utf-8');bench,n=re.subn(r'^//!','//',bench,flags=re.M);assert n==7
bench=bench.replace('#![cfg(feature = "gpu")]\n','',1).replace('use solver::gpu::{GpuSolver, KERNEL_NAMES};','use observed::{GpuSolver, KERNEL_NAMES};',1).replace('include_str!("../../../bench_spot.json")','include_str!("bench_spot.json")',1);assert bench.count('"runtime_nvrtc_jit_included": true')==2;bench=bench.replace('"runtime_nvrtc_jit_included": true','"runtime_nvrtc_jit_included": false');needle='        completed += 1;';assert bench.count(needle)==1;bench=bench.replace(needle,'        assert!(!profile);\n        d156_after(gpu,host,name);\n'+needle,1)
life=(ROOT/'runs/D156-lifecycle.rs').read_text(encoding='utf-8').replace('.cfv.u32','.gpu.bin',1).replace('g.d156_snapshot(','g.d166_snapshot(',1)
observer=(ROOT/'runs/D166-observer.rs').read_text(encoding='utf-8');commands={};deps=ROOT/'reference/accepted-e080-deps';source_reversals={}
for arm in ['baseline','candidate']:
 d=H/arm;d.mkdir();production=(h.REPO/'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8') if arm=='baseline' else Path(M['owned']['crates/solver/src/gpu/mod.rs']['candidate']).read_text(encoding='utf-8')
 for name in ['arena.rs','kernels.cu']:shutil.copyfile(h.REPO/'crates/solver/src/gpu'/name,d/name)
 if arm=='candidate':
  for name in ['data_offsets.rs','kernels_offset32.cu']:shutil.copyfile(M['owned']['crates/solver/src/gpu/'+name]['candidate'],d/name)
 start=production.index('        static PTX:');end=production.index('            .clone()?;',start)+len('            .clone()?;');compileblock=production[start:end]
 resource=ROOT/'runs/D170-offset-width/execution';shutil.copyfile(resource/('baseline-compute_120.ptx' if arm=='baseline' else 'candidate-compute_120.ptx'),H/(arm+'.ptx'))
 binding='        assert_eq!(arch,"compute_120");\n        println!("D171_BIND '+arm+'");\n'
 binding+='        let ptx=cudarc::nvrtc::Ptx::from_src(include_str!("../baseline.ptx"));' if arm=='baseline' else '        let ptx=if narrow_offsets {cudarc::nvrtc::Ptx::from_src(include_str!("../candidate.ptx"))} else {cudarc::nvrtc::Ptx::from_src(include_str!("../baseline.ptx"))};'
 adapted=production.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1).replace(compileblock,binding,1)
 reverse=adapted.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1).replace(binding,compileblock,1);assert reverse==production;source_reversals[arm]=True
 obs=observer.replace('// D166_ALL_DEVICE_FIELDS','\n        '.join(f'field!("{n}", {e});' if n!='d_node_data_off' or arm=='baseline' else 'match &self.d_node_data_off {DeviceOffsets::Narrow(v)=>field!("d_node_data_off",v),DeviceOffsets::Wide(v)=>field!("d_node_data_off",v)};' for n,e in fields),1)
 original='        serde_json::json!(';assert obs.count(original)==1;obs=obs.replace(original,'        let mut record=serde_json::json!(',1)
 tail='"device_fields":fields,"host_fields":3})';assert obs.count(tail)==1
 if arm=='baseline':extra='record["offset_format_bits"]=serde_json::json!(64);record["offset_enum_extra_bytes"]=serde_json::json!(0);'
 else:extra='record["offset_format_bits"]=serde_json::json!(match &self.d_node_data_off {DeviceOffsets::Narrow(_)=>32,DeviceOffsets::Wide(_)=>64});record["offset_enum_extra_bytes"]=serde_json::json!(std::mem::size_of::<DeviceOffsets>()-std::mem::size_of::<CudaSlice<u64>>());'
 obs=obs.replace(tail,tail+';\n        '+extra+'\n        record',1)
 if arm=='candidate':obs+='''
#[test]
fn d171_offset_physical_formats() {
 let ctx=CudaContext::new(0).unwrap();let stream=ctx.new_stream().unwrap();
 let v=[0u64,1,u32::MAX as u64-1,u64::MAX];let n=DeviceOffsets::upload(&stream,&v,true).unwrap();
 assert_eq!(n.bytes(),16);match n {DeviceOffsets::Narrow(d)=>assert_eq!(stream.clone_dtoh(&d).unwrap(),[0,1,u32::MAX-1,u32::MAX]),_=>panic!()};
 let v=[u32::MAX as u64,1u64<<32,u64::MAX-1,u64::MAX];assert!(!data_offsets::narrow_fits(&v));let w=DeviceOffsets::upload(&stream,&v,false).unwrap();
 assert_eq!(w.bytes(),32);match w {DeviceOffsets::Wide(d)=>assert_eq!(stream.clone_dtoh(&d).unwrap(),v),_=>panic!()};
 stream.synchronize().unwrap();ctx.check_err().unwrap();
}
'''
 (d/'mod.rs').write_text(adapted+'\n'+obs,encoding='utf-8',newline='\n')
 prefix='#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]\npub use solver::*;\n#[path="'+arm+'/mod.rs"]mod observed;\nuse cudarc::driver::{CudaSlice,CudaStream,DeviceRepr};\nuse std::{fs::{File,OpenOptions},io::BufWriter,path::Path};\n'
 source=H/(arm+'-probe.rs');source.write_text(prefix+bench+'\n'+helpers+'\n'+life,encoding='utf-8',newline='\n');cmd=['rustc',str(source),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
 for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
 commands[arm]=cmd+['-o',str(H/(arm+'.exe'))]
shutil.copyfile(h.REPO/'bench_spot.json',H/'bench_spot.json')
for source,dest in [('D166-bounded-child.py','bounded_child.py'),('D157-sampler.py','sampler.py'),('D171-execute.py','execute.py'),('D171-audit.py','audit.py')]:shutil.copyfile(ROOT/'runs'/source,H/dest);ast.parse((H/dest).read_text(encoding='utf-8'))
h.save(H/'source-review.json',{'id':'D171','at':h.now(),'source_reversals':source_reversals,'device_field_inventory':[x[0] for x in fields],'scope':'Original full canonical 3 fixtures, stopping/cadence/quality, entire CPU state/physical65 unchanged device buffers/CFV and actual private offset payload, four lifecycle stages, query/save/futureEV. Only private offsets decode32->64 with reserved sentinels; both actual raw formats/extents retained. No array omitted, no physicalCFV padding allowance.','prospective_representation_exception':'Only d_node_data_off differs in physical dtype/extent (baseline8*Nbytes,candidate4*N); every encoded32 value decodes exactly to original64. All other raw physical bytes exact. Wrapper-size delta permitted exactly size_of(DeviceOffsets)-size_of(CudaSlice<u64>), field inventory/count/othergeometry exact. Offset format must32 for allcanonical candidateframes/64baseline; actualformat/bufferphysicalextent recorded. Original CPU plans and save bytes exact.','telemetry':'Only runtime_nvrtc_jit_included false because sealed diagnostic PTX; excluded with original timing fields from original science anchor. Giant observers/compile bypass clocks unscored.','first_controls':'Before full canonical native process, candidate executable runs2 offset boundary/physical upload tests with actual CUDA32/64 allocation/readback and u32MAX/2^32/u64MAX fallback input. No application kernel in those tests.','failure':'No actual mismatch, source/corpus/precision/field omission/width threshold/shape/source flag resampling rescue. All failed originals retained. Narrow enum actual accounting and continuation forcewide source must receive later feature build/broad performance/resource qualification before any adoption.'})
files=[Path(__file__),S/'manifest.json',S/'source-review.json',ROOT/'runs/D170-offset-width/report.json',ROOT/'epoch/exact-anchor.json',ROOT/'epoch/common.py']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
limits={'raw_reservation_bytes':256*1024**3,'disk_headroom_bytes':64*1024**3,'required_free_bytes':320*1024**3,'available_RAM_before_bytes':64*1024**3,'available_RAM_during_bytes':32*1024**3,'process_reported_peak_max_bytes':32*1024**3,'native_timeout_seconds':1800,'poll_interval_ms':200}
h.save(H/'protocol.json',{'id':'D171','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_NATIVE','sequence':['baseline','candidate'],'rustc_commands':commands,'limits':limits,'expected_full_records':6,'expected_checkpoints':46,'lifecycle_stages':['converged','continued','locked','resumed'],'expected_CPU_pairs':12,'expected_GPU_all69field_pairs':12,'expected_query_pairs':6,'expected_save_pairs':3,'expected_future_EV_pairs':9,'input_sha256':{str(p):h.sha(p) for p in files},'scientific_telemetry_exception':'Same original full science except honest compile telemetryfalse; all timing diagnostic. One offset payload representation exception exactly specified in source-review, no other numeric tolerance/field/padding exception.','native_performance_runs':0,'candidate_accepted':False})
print(h.sha(H/'protocol.json'),flush=True)
