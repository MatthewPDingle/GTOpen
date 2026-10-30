"""Freeze direct scalar exactness admission from the fixed E060 source expressions."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
S=ROOT/'runs/E060-source';RES=ROOT/'runs/E060-resource';H=ROOT/'runs/E060-scalar-control';assert not H.exists();H.mkdir()
p=old.read(RES/'protocol.json');q=old.read(RES/'report.json')
for n,h in p['input_sha256'].items():old.pin(n,h)
assert all(q['gates'].values()) and q['status']=='pass_resource_prerequisite'
assert [q['details']['up_action'][v]['registers'] for v in ['baseline','candidate']]==[62,64]
for v in ['baseline','candidate']:old.pin(RES/'execution'/(v+'.ptx'),q['ptx_sha256'][v])
for label in ['rustc','probe']:assert old.read(RES/'execution'/(label+'.exit.json'))['returncode']==0
c=(S/'candidate.cu').read_text(encoding='utf-8')
a=c.index('            float uni = 1.f / (float)na;',c.index('void up_action_impl('));b=c.index('            float reach = rp[i];',a);prep=c[a:b]
a=c.index('                float numerator = r > 0.f ? r : 0.f;',b);b=c.index('                float v = cfv[',a);divide=c[a:b]
assert 'rcp.approx.ftz.f32' in prep and '__fmaf_rn' in prep and 'action_divide_with_refinement' in divide
cu=c+'''
extern "C" __global__ void scalar_baseline(const float* r,const float* d,u32* out,int n) {
 int i=blockIdx.x*blockDim.x+threadIdx.x;
 if(i<n){float numerator=r[i]>0.f?r[i]:0.f;float sum=d[i];float sig=sum>1e-12f?numerator/sum:1.f/3.f;out[i+16]=__float_as_uint(sig);}
}
extern "C" __global__ void scalar_candidate(const float* rr,const float* d,u32* out,int n) {
 int i=blockIdx.x*blockDim.x+threadIdx.x;
 if(i<n){const int NA=3,na=3;float r=rr[i],sum=d[i];
'''+prep+divide+'''
 out[i+16]=__float_as_uint(sig);}
}
'''
(H/'scalar.cu').write_text(cu,encoding='utf-8',newline='\n')
rs=r'''//! Fixed scalar IEEE/native-fallback differential control; no timing score.
use cudarc::{driver::{CudaContext,LaunchConfig,PushKernelArg},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf};
fn save(path:PathBuf,magic:&[u8],x:&[u32]){let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).unwrap());f.write_all(magic).unwrap();f.write_all(&(x.len() as u64).to_le_bytes()).unwrap();for x in x{f.write_all(&x.to_le_bytes()).unwrap();}f.flush().unwrap();}
fn next(s:&mut u64)->u32{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;(*s>>16)as u32}
fn main(){
 let dir=PathBuf::from(std::env::var_os("E060_SCALAR_DIR").unwrap());std::fs::create_dir(&dir).unwrap();
 let mut r=Vec::<f32>::new();let mut d=Vec::<f32>::new();
 let threshold=1e-12f32;let low=2f32.powi(-60);let high=2f32.powi(60);
 let denominators=[0,0x8000_0000,1,0x007f_ffff,0x0080_0000,low.to_bits(),threshold.to_bits()-2,threshold.to_bits()-1,threshold.to_bits(),threshold.to_bits()+1,threshold.to_bits()+2,0x3eaa_aaaa,0x3eaa_aaab,0x3f00_0000,0x3f00_0001,0x3f7f_ffff,0x3f80_0000,0x3f80_0001,0x4040_0000,0x4b80_0000,high.to_bits()-2,high.to_bits()-1,high.to_bits(),high.to_bits()+1,high.to_bits()+2,0x7f7f_ffff,0x7f80_0000,0x7fc0_1234,0xffc0_5678,0xbf80_0000,0xff80_0000];
 let numerators=[0,0x8000_0000,1,0x8000_0001,0x007f_ffff,0x0080_0000,0x0080_0001,low.to_bits()-2,low.to_bits()-1,low.to_bits(),low.to_bits()+1,low.to_bits()+2,threshold.to_bits()-1,threshold.to_bits(),threshold.to_bits()+1,0x3eaa_aaab,0x3f00_0000,0x3f7f_ffff,0x3f80_0000,0x3f80_0001,high.to_bits(),0x7f7f_ffff,0x7f80_0000,0xff80_0000,0x7fc0_1234,0xffc0_5678];
 for db in denominators{for rb in numerators{let den=f32::from_bits(db);let mut reg=f32::from_bits(rb);if den.is_finite()&&den>0.0&&reg>den{reg=den;}r.push(reg);d.push(den);}}
 // Dense representable neighborhoods at all source guard boundaries.
 for center in [threshold.to_bits(),low.to_bits(),high.to_bits(),0x3f80_0000u32]{for k in -512i32..=512{let den=f32::from_bits((center as i64+k as i64) as u32);for rb in [0,1,low.to_bits()-1,low.to_bits(),low.to_bits()+1,den.to_bits(),den.to_bits()-1,(den*0.5).to_bits()]{let reg=f32::from_bits(rb);r.push(if reg>den {den}else{reg});d.push(den);}}}
 let curated=r.len();let mut rng=0x0600_2026_1017_5090u64;
 for k in 0..2_097_152usize{
  let bits=next(&mut rng);let den=match k%4{
   0=>f32::from_bits((88+(bits%100))<<23 | (next(&mut rng)&0x7f_ffff)),
   1=>f32::from_bits(bits&0x7fff_ffff),
   2=>f32::from_bits(0x3f80_0000|(bits&0x7f_ffff)),
   _=>f32::from_bits(0x5d00_0000|(bits&0x7f_ffff)),
  };
  let reg=match k%11{0=>0.0,1=>f32::from_bits(1),2=>low,3=>f32::from_bits(low.to_bits()-1),4=>den,5=>f32::from_bits(den.to_bits().saturating_sub(1)),_=>{let v=f32::from_bits(next(&mut rng)&0x7fff_ffff);if den.is_finite()&&den>0.0&&v>den{den}else{v}}};
  r.push(reg);d.push(den);
 }
 let n=r.len();assert_eq!(n,d.len());let mut selected=0usize;let mut fallback=0usize;let mut uniform=0usize;let mut input=Vec::with_capacity(2*n);
 for (&reg,&den) in r.iter().zip(&d){let num=if reg>0.0{reg}else{0.0};let eligible=den>threshold&&den<=high&&(num==0.0||num>=low);if eligible{assert!(num<=den && den.is_finite() && num.is_finite());selected+=1;}else if den>threshold{fallback+=1;}else{uniform+=1;}input.push(reg.to_bits());input.push(den.to_bits());}
 save(dir.join("inputs.bin"),b"E060SCALIN1",&input);
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let ptx=compile_ptx_with_opts(include_str!("scalar.cu"),CompileOptions{arch:Some("compute_120"),..Default::default()}).unwrap();std::fs::write(dir.join("scalar.ptx"),ptx.to_src()).unwrap();let module=ctx.load_module(ptx).unwrap();
 let dr=stream.clone_htod(&r).unwrap();let dd=stream.clone_htod(&d).unwrap();let sentinel=0xa55a_06e0u32;let seed=vec![sentinel;n+32];let ni=n as i32;let mut outputs=Vec::new();
 for name in ["scalar_baseline","scalar_candidate"]{let f=module.load_function(name).unwrap();let mut out=stream.clone_htod(&seed).unwrap();unsafe{stream.launch_builder(&f).arg(&dr).arg(&dd).arg(&mut out).arg(&ni).launch(LaunchConfig::for_num_elems(n as u32)).unwrap();}let raw=stream.clone_dtoh(&out).unwrap();stream.synchronize().unwrap();assert_eq!(&raw[..16],&seed[..16]);assert_eq!(&raw[n+16..],&seed[n+16..]);save(dir.join(format!("{name}.bin")),b"E060SCALOUT1",&raw);outputs.push(raw);}
 let rr=stream.clone_dtoh(&dr).unwrap();let rd=stream.clone_dtoh(&dd).unwrap();stream.synchronize().unwrap();assert_eq!(rr.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),r.iter().map(|v|v.to_bits()).collect::<Vec<_>>());assert_eq!(rd.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),d.iter().map(|v|v.to_bits()).collect::<Vec<_>>());let mut after=Vec::with_capacity(2*n);for(i,j)in rr.iter().zip(&rd){after.push(i.to_bits());after.push(j.to_bits());}save(dir.join("inputs-after.bin"),b"E060SCALIN1",&after);
 let mismatches:Vec<_>=(0..n).filter(|&i|outputs[0][i+16]!=outputs[1][i+16]).collect();let examples:Vec<_>=mismatches.iter().take(20).map(|&i|serde_json::json!({"index":i,"regret_bits":r[i].to_bits(),"sum_bits":d[i].to_bits(),"baseline_bits":outputs[0][i+16],"candidate_bits":outputs[1][i+16]})).collect();
 let report=serde_json::json!({"id":"E060-scalar-control","cases":n,"curated":curated,"random":2_097_152,"shared_refinement_cases":selected,"native_fallback_cases":fallback,"uniform_cases":uniform,"mismatches":mismatches.len(),"examples":examples,"immutable_input_words":2*n,"output_guard_words":64,"kernel_launches":2,"solver_executions":0,"performance_measured":false,"candidate_accepted":false});
 let text=serde_json::to_vec_pretty(&report).unwrap();let mut file=OpenOptions::new().write(true).create_new(true).open(dir.join("report.json")).unwrap();file.write_all(&text).unwrap();file.flush().unwrap();println!("E060_SCALAR {}",report);if !mismatches.is_empty(){std::process::exit(20);}
}
'''
(H/'probe.rs').write_text(rs,encoding='utf-8',newline='\n')
executor='''"""One fixed scalar-control build/run; preserve outputs on numerical rejection."""
import json,os,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 for n,h in P['input_sha256'].items():old.pin(n,h)
 old.custody()
verify();E=H/'execution';assert not E.exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3;E.mkdir()
 env=old.env();env['E060_SCALAR_DIR']=str(E/'raw')
 old.child(P['rustc_command'],E,'rustc',env,180);verify()
 old.save(E/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'compiler_terminal':True,'kernel_launches':0})
 old.child([str(H/'probe.exe')],E,'probe',env,180);verify()
 report=old.read(E/'raw/report.json');assert report['mismatches']==0
 assert (E/'raw/inputs.bin').read_bytes()==(E/'raw/inputs-after.bin').read_bytes()
 old.save(E/'complete.json',{'at':old.now(),'raw_report_sha256':old.sha(E/'raw/report.json'),'all_owned_children_terminal':True,'all_scalar_bits_exact':True,'no_performance_measurement':True})
 print(json.dumps(report),flush=True)
'''
(H/'execute.py').write_text(executor,encoding='utf-8',newline='\n')
cmd=[x.replace(str(RES),str(H)) for x in p['rustc_command']]
inputs=[*H.iterdir(),*S.iterdir(),Path(__file__),RES/'report.json',RES/'protocol.json',ROOT/'runs/accepted-E051/common_e051.py',ROOT/'comparisons/D098-static-root-check/report.json']
pinmap={str(n):old.sha(n) for n in inputs if n.is_file()};pinmap.update({n:h for n,h in p['input_sha256'].items() if Path(n).suffix in ['.rlib','.lib']})
old.save(H/'protocol.json',{'id':H.name,'at':old.now(),'status':'FROZEN_PRE_SCALAR_NATIVE','rustc_command':cmd,'input_sha256':pinmap,'seed':'0600202610175090','random_cases':2097152,'curated_contract':'31denominators x26regrets plus4guard neighborhoods(-512..512) x8numerator constructions. Positive finite selected numerators never exceed denominator. Exact zero, signs, tiny/subnormal, threshold/upper-guard neighbors, NaN/inf fallback included.','candidate_expression_extraction':{'source_sha256':old.sha(S/'candidate.cu'),'preparation':prep,'division':divide},'gates':'Zero output bit mismatches, all input words immutable and all64guards exact. Stop on any mismatch; no math/window/guard/arity variants or timing rescue. Sampled GPU evidence is not a mathematical proof for every float pair. Only full kernel/solver controls and fixed performance policy can advance later.','no_source_activation':True,'no_timing_score':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E060');e.update(stage='Direct scalar exactness controls',reason='Allocated resource gate passed62->64nominal but same2048registers/warp,64local bytes and same occupancy. Candidate exactness still unproven; fixed scalar matrix tests guard boundaries/native fallback before full kernel and timed solves.');st.update(updated_at=old.now(),stage='E060 scalar exactness control',activity='Resource prerequisite passed; testing actual division result bits before full-kernel/solver work.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'random_cases':2097152,'resource_registers':[62,64],'source_activated':False}),flush=True)
