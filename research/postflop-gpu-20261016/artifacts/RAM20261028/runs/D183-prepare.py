import ast,hashlib,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status());H=ROOT/'runs/D183-plan-phase-diagnostic';H.mkdir(exist_ok=False)
p=h.REPO/'crates/solver/src/gpu/plan.rs';base=p.read_bytes();source=base.decode();eol='\r\n' if b'\r\n' in base else '\n';original=source;insertions=[]
begin='        d183_begin();'+eol;anchor='        let n = spot.tree.nodes.len();';assert source.count(anchor)==1;source=source.replace(anchor,begin+anchor,1);insertions.append((begin+anchor,anchor))
boundaries=[('preamble','        // --- DFS over representative branches:'),('DFS_buffers','        while let Some(it) = stack.pop() {'),('representative_DFS','        // Terminal CFVs stay resident'),('CFV_width_count','        let mut parity_max = [0usize; 2];'),('CFV_slots','        // --- Level-ordered work lists'),('classify_nodes','        let flatten_nodes = |by:'),('flatten_node_lists','        let mut edge_by_level:'),('chance_edge_lists','        // --- River slot assignment'),('river_slot_assignment','        let num_slots = slots.len();'),('river_tables','        // --- Per-node scalar arrays'),('scalar_arrays','        // Packing adds host copy/restore work.'),('full_or_compact_selection','        // --- Per-hand arrays'),('hand_tables','        // Node IDs describe ownership;'),('reach_compaction','        GpuPlan {'+eol+'            num_levels,')]
for label,anchor in boundaries:
 assert source.count(anchor)==1,(label,source.count(anchor));add='        d183_mark("'+label+'");'+eol;source=source.replace(anchor,add+anchor,1);insertions.append((add+anchor,anchor))
reverse=source
for a,b in reversed(insertions):assert reverse.count(a)==1;reverse=reverse.replace(a,b,1)
assert reverse.encode()==base
helper='''
thread_local! { static D183_MARKS:std::cell::RefCell<(Option<std::time::Instant>,Vec<(&'static str,f64)>)>=std::cell::RefCell::new((None,Vec::with_capacity(32))); }
fn d183_begin(){D183_MARKS.with(|s|{let mut s=s.borrow_mut();s.1.clear();s.0=Some(std::time::Instant::now());});}
fn d183_mark(label:&'static str){let now=std::time::Instant::now();D183_MARKS.with(|s|{let mut s=s.borrow_mut();let last=s.0.replace(now).unwrap();s.1.push((label,now.duration_since(last).as_secs_f64()*1000.));});}
pub fn d183_marks()->Vec<(&'static str,f64)>{D183_MARKS.with(|s|s.borrow().1.clone())}
'''
(H/'baseline-plan.rs').write_bytes(base);(H/'observed-plan.rs').write_bytes(source.encode()+helper.encode());shutil.copyfile(h.REPO/'bench_spot.json',H/'bench_spot.json')
decl=original[original.index('pub struct GpuPlan {'):original.index('\nimpl GpuPlan {')];fields=re.findall(r'^    pub (\w+): ([^\r\n]+),',decl,re.M);assert len(fields)>50 and len(set(x[0] for x in fields))==len(fields)
records=h.read(ROOT/'runs/B310/report.json')['results'];fixtures=[]
for iso in [True,False]:
 for r in records:fixtures.append({'id':r['fixture_id']+('-iso-on' if iso else '-iso-off'),'fixture':r['fixture_id'],'config':r['config'],'use_iso':iso,'expected_nodes':r['nodes']})
h.save(H/'fixtures.json',fixtures);h.save(H/'schema.json',{'header':'D183_PLAN_RAW1\\0\\0\\0','fields':fields,'encoding':'Each field: u32 littleendian UTF8-name length/name, u64 payload extent, then recursively encoded field. usize/u64=>u64, u32/i32/f32bits=>u32, bool=>u8. Vec/arrays include u64 element count. LevelSpan=>u32start/u32count. Every field including all unreachable/default metadata retained; no exclusions.'})
prefix='''#![allow(dead_code,unused_imports)]
pub use solver::*;
#[path="observed-plan.rs"]mod observed;
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::Path,time::Instant};
use serde_json::{json,Value};
trait Encode {fn size(&self)->u64;fn encode(&self,w:&mut impl Write);}
macro_rules! primitive{($t:ty,$n:expr,$f:expr)=>{impl Encode for $t{fn size(&self)->u64{$n}fn encode(&self,w:&mut impl Write){w.write_all(&($f)(*self)).unwrap();}}};}
primitive!(u32,4,|x:u32|x.to_le_bytes());primitive!(i32,4,|x:i32|x.to_le_bytes());primitive!(f32,4,|x:f32|x.to_bits().to_le_bytes());primitive!(u64,8,|x:u64|x.to_le_bytes());primitive!(usize,8,|x:usize|(x as u64).to_le_bytes());primitive!(bool,1,|x:bool|[x as u8]);
impl<T:Encode> Encode for Vec<T>{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(self.len() as u64).encode(w);for x in self{x.encode(w);}}}
impl<T:Encode,const N:usize> Encode for [T;N]{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(N as u64).encode(w);for x in self{x.encode(w);}}}
impl Encode for solver::gpu::plan::LevelSpan{fn size(&self)->u64{8}fn encode(&self,w:&mut impl Write){self.start.encode(w);self.count.encode(w);}}
impl Encode for observed::LevelSpan{fn size(&self)->u64{8}fn encode(&self,w:&mut impl Write){self.start.encode(w);self.count.encode(w);}}
fn field(w:&mut impl Write,name:&str,v:&impl Encode){assert!(name.len()<256);(name.len() as u32).encode(w);w.write_all(name.as_bytes()).unwrap();let bytes=v.size();assert!(bytes<=2*1024*1024*1024);bytes.encode(w);v.encode(w);}
'''
for arm,ty in [('baseline','solver::gpu::plan::GpuPlan'),('observed','observed::GpuPlan')]:
 prefix+='fn dump_'+arm+'(p:&'+ty+',path:&Path){let mut w=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).unwrap());w.write_all(b"D183_PLAN_RAW1\\0\\0\\0").unwrap();\n'+''.join(' field(&mut w,"'+name+'",&p.'+name+');\n' for name,typ in fields)+'w.flush().unwrap();w.get_ref().sync_all().unwrap();assert!(w.get_ref().metadata().unwrap().len()<=2*1024*1024*1024);}\n'
labels=[x[0] for x in boundaries]
main='''
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let out=Path::new(&args[1]);let order=&args[2];assert!(order=="BO"||order=="OB");let fixtures:Vec<Value>=serde_json::from_str(include_str!("fixtures.json")).unwrap();assert_eq!(fixtures.len(),6);
 for f in fixtures{
  let id=f["id"].as_str().unwrap();let cfg:SpotConfig=serde_json::from_value(f["config"].clone()).unwrap();let spot=Spot::new(cfg).unwrap();assert_eq!(spot.tree.nodes.len() as u64,f["expected_nodes"].as_u64().unwrap());let iso=f["use_iso"].as_bool().unwrap();
  let (b,o,bms,oms)=if order=="BO"{let t=Instant::now();let b=solver::gpu::plan::GpuPlan::build(&spot,iso);let bm=t.elapsed().as_secs_f64()*1000.;let t=Instant::now();let o=observed::GpuPlan::build(&spot,iso);let om=t.elapsed().as_secs_f64()*1000.;(b,o,bm,om)}else{let t=Instant::now();let o=observed::GpuPlan::build(&spot,iso);let om=t.elapsed().as_secs_f64()*1000.;let t=Instant::now();let b=solver::gpu::plan::GpuPlan::build(&spot,iso);let bm=t.elapsed().as_secs_f64()*1000.;(b,o,bm,om)};
  let marks=observed::d183_marks();assert_eq!(marks.iter().map(|x|x.0).collect::<Vec<_>>(),EXPECTED_LABELS);assert!(marks.iter().all(|x|x.1.is_finite()&&x.1>=0.));assert!(marks.iter().map(|x|x.1).sum::<f64>()<=oms);assert!(bms.is_finite()&&bms>=0.&&oms.is_finite()&&oms>=0.);
  dump_baseline(&b,&out.join(format!("{id}-baseline.plan.bin")));dump_observed(&o,&out.join(format!("{id}-observed.plan.bin")));
  println!("D183_PLAN {}",json!({"stage":"fixture","id":id,"fixture":f["fixture"],"config":f["config"],"use_iso":iso,"nodes":spot.tree.nodes.len(),"hands":spot.hands.each_ref().map(|x|x.len()),"order":order,"baseline_plan_ms":bms,"observed_plan_ms":oms,"phase_ms":marks,"all_fields_retained":FIELD_COUNT,"GPU_context_or_kernel_calls":0,"solver_runs":0,"performance_candidate":false}));std::io::stdout().flush().unwrap();
 }
 println!("D183_PLAN {}",json!({"stage":"complete","cases":6,"GPU_context_or_kernel_calls":0,"solver_runs":0,"candidate_accepted":false}));
}
'''.replace('EXPECTED_LABELS','vec!'+json.dumps(labels)).replace('FIELD_COUNT',str(len(fields)))
(H/'probe.rs').write_text(prefix+main,encoding='utf-8',newline='\n');deps=ROOT/'reference/accepted-e080-deps';command=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:command+=['--extern',name+'='+str(deps/file)]
command+=['-o',str(H/'probe.exe')]
historycmd=['git','log','--all','--oneline','--','crates/solver/src/gpu/plan.rs'];hist=subprocess.check_output(historycmd,cwd=h.REPO,text=True)
h.save(H/'source-review.json',{'id':'D183','at':h.now(),'previous_goal_turn_classification':'progress: E098 completed both86unit suites,18exactscience/138checkpoints and fixed samequality speed screen; rejection and all terminal evidence published, changing next action.','scope':'Instrument exact original CPU GpuPlan build with14 phase marks only; compare every original plan field against original accepted E080 library. Six unchanged canonicalSpot cases (3fixtures x iso on/off),3fixed fresh-process BO/OB/BO paired observations. No production source changes/GPU calls/solves/optimizer/speed result.','phase_labels':labels,'all_public_fields':fields,'byte_exact_original_reversal':True,'base_plan_sha256':h.sha(p),'observed_plan_sha256':h.sha(H/'observed-plan.rs'),'all_local_ref_plan_history':hist,'historical_counterevidence':'D080 indexed river-slot lookup only4.7015ms observed isolated savings and declined; not reopened. E079 overlaps existing wholeplan/context and failed fixture tradeoff; E080 overlaps zero scans and staysaccepted. E095 earlierzero worker failed actual budget/errorCPUcost beforeGPU; closed. E098 hostznver3codegen rejected; defaulttarget/16workers retained. No ordering/fusion/planner candidate admitted by this diagnostic.','timing_limits':'CPU-only component clocks exclude Spot construction, serialization/comparison/destruction and all GPU init/solve/readback. Observer/cache/allocator effects assessed with full original outer-clock pair and ordered fresh processes. Components cannot establish complete-cycle savings/headroom, CPU integration cost or a >=1% gain. All future exactness/complete1%/strictfixture/fresh16/broad/material/holdout/cumulative/application gates unchanged.','raw_limits':'36wholeplan files <=2GiB each,<=72GiB raw+16GiB headroom. All fields include unreachable/default regions, float bit patterns, vector counts/order and spans. Independent entirebyte streamed reader, no field/precision/order exclusions. Every producer exit and compiler terminal required.'})
files=[Path(__file__),ROOT/'runs/D183-execute.py',ROOT/'runs/D183-audit.py',ROOT/'epoch/common.py',ROOT/'runs/E098-primary-checkpoint/report.json',ROOT/'comparisons/D173-constructor-diagnostic/report.json',ROOT/'runs/B310/report.json']+[p for p in H.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
for script in ['D183-execute.py','D183-audit.py']:ast.parse((ROOT/'runs'/script).read_text())
h.save(H/'protocol.json',{'id':'D183','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_CPU_NATIVE','rustc_command':command,'sequence':[{'id':'P1','order':'BO'},{'id':'P2','order':'OB'},{'id':'P3','order':'BO'}],'required_free_bytes':128*1024**3,'raw_files':36,'max_raw_file_bytes':2*1024**3,'field_count':len(fields),'phase_labels':labels,'input_sha256':{str(p):h.sha(p) for p in files},'source_sha256':h.custody(),'scope':'One Rust compiler,3CPU-only native probes,1fullrawreader, every field pair byteexact. No repeats/exclusions/alternateinputs/optimizer/CUDAcontext/kernel/solver/speed/adoption. Stop on mismatch; retain all originals; reader-only mechanical repairs preserve outputs.'})
for name in ['protocol.json','source-review.json','schema.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D183','title':'CPU GPU-plan phase observation','kind':'diagnostic','status':'staged','accepted':False,'correctness':'pending_all_field_raw_comparison','measurement_epoch':'RAM20261028','stage':'Frozen CPU-only diagnostic','reason':'Measure14 exact planner phases; compare every public field for all3canonical fixtures with iso on/off. Fixed3fresh paired processes. No GPU kernels or optimization candidate.','evidence':[{'label':'Original source, scope and timing limits','url':'evidence/'+H.name+'/source-review.json'},{'label':'Frozen component observation','url':'evidence/'+H.name+'/protocol.json'}]});s.update(updated_at=h.now(),active_experiment='D183',stage='CPU planning phase diagnostic',activity='E098 closed. Measure CPU planning phases and exact whole-plan fields before selecting a distinct change. E080 with16workers remains live; no new gain.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
