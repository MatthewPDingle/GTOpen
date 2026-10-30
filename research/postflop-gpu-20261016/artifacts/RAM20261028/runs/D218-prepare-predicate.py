import ast,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();assert h.read(ROOT/'runs/D217-nullable-lock-direct/report.json')['status']=='pass_all3_kernel_direct_nullable_lock_raw_equivalence'
S=ROOT/'runs/E106-source-r2';R=ROOT/'runs/E106-resource-host';H=ROOT/'runs/D218-lock-map-boundaries';H.mkdir(exist_ok=False)
for arm in ['baseline','candidate']:
 d=H/arm;d.mkdir();src=(R/arm/'mod.rs').read_bytes().decode('utf-8');a=src.index('        static PTX:');b=src.index('            .clone()?;',a)+len('            .clone()?;');old=src[a:b];binding='        assert_eq!(arch,"compute_120");\n        println!("D218_PTX '+arm+'");\n        let ptx=cudarc::nvrtc::Ptx::from_src(include_str!("../'+arm+'.ptx"));';src=src[:a]+binding+src[b:];assert src.replace(binding,old,1)==(R/arm/'mod.rs').read_bytes().decode('utf-8')
 flag='Some(self.locks_absent)' if arm=='candidate' else 'None::<bool>'
 src+='''
impl GpuSolver{
 pub fn d218_state(&self)->serde_json::Value{self.stream.synchronize().unwrap();let offsets=self.stream.clone_dtoh(&self.d_lock_off).unwrap();let sigma=self.stream.clone_dtoh(&self.d_lock_sigma).unwrap();self.stream.synchronize().unwrap();serde_json::json!({"offsets":offsets,"sigma_bits":sigma.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),"absent":FLAG,"wrapper_bytes":std::mem::size_of::<Self>(),"training_graphs_present":self.graphs.is_some(),"eval_graphs_present":[self.eval_graphs[0].is_some(),self.eval_graphs[1].is_some()]})}
}
'''.replace('FLAG',flag)
 (d/'mod.rs').write_bytes(src.encode('utf-8'));shutil.copyfile(R/arm/'arena.rs',d/'arena.rs');shutil.copyfile(S/(arm+'.cu'),d/'kernels.cu');p=R/'baseline-compute_120.ptx' if arm=='baseline' else R/'execution/candidate-compute_120.ptx';shutil.copyfile(p,H/(arm+'.ptx'))
shutil.copyfile(h.REPO/'bench_spot.json',H/'bench_spot.json')
probe='''#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
use serde_json::json;
use std::{sync::Arc,io::Write};
fn set_map(s:&mut Solver,pattern:&str){s.locks.clear();let root=&s.spot.tree.nodes[0];let n=root.num_children as usize*s.spot.hands[root.player as usize].len();assert!(n>1);match pattern{
 "empty"=>{},"valid_root"=>{s.locks.insert(0,vec![1.0/root.num_children as f32;n]);},"empty_root"=>{s.locks.insert(0,vec![]);},"empty_terminal"=>{let i=s.spot.tree.nodes.iter().position(|n|n.kind!=solver::tree::KIND_ACTION).unwrap();s.locks.insert(i as u32,vec![]);},"one_zero_root"=>{s.locks.insert(0,vec![0.0]);},_=>panic!("pattern")}}
fn record(s:&Solver,b:&baseline::GpuSolver,c:&candidate::GpuSolver,id:usize,stage:&str,pattern:&str)->serde_json::Value{
 let mut locks:Vec<_>=s.locks.iter().map(|(&node,v)|json!({"node":node,"bits":v.iter().map(|x|x.to_bits()).collect::<Vec<_>>()})).collect();locks.sort_by_key(|v|v["node"].as_u64().unwrap());let expected_absent=s.locks.is_empty();let bs=b.d218_state();let cs=c.d218_state();assert_eq!(bs["wrapper_bytes"],4448);assert_eq!(cs["wrapper_bytes"],4448);assert_eq!(cs["absent"],expected_absent);assert_eq!(bs["offsets"],cs["offsets"]);assert_eq!(bs["sigma_bits"],cs["sigma_bits"]);assert!(!bs["training_graphs_present"].as_bool().unwrap()&&!cs["training_graphs_present"].as_bool().unwrap());assert_eq!(bs["eval_graphs_present"],json!([false,false]));assert_eq!(cs["eval_graphs_present"],json!([false,false]));
 json!({"case":id,"stage":stage,"pattern":pattern,"node_count":s.spot.tree.nodes.len(),"CPU_locks":locks,"expected_absent":expected_absent,"baseline":bs,"candidate":cs})}
fn main(){let out=std::path::PathBuf::from(std::env::args().nth(1).unwrap());let mut config:SpotConfig=serde_json::from_str(include_str!("bench_spot.json")).unwrap();config.board="Ks7h2dQhTc".into();let spot=Arc::new(Spot::new(config).unwrap());let mut records=Vec::new();let mut id=0;
 for storage in [store::Storage::Compressed,store::Storage::F32]{for algo in [Algorithm::Dcfr,Algorithm::CfrPlus]{for initial in ["empty","valid_root","empty_root","empty_terminal","one_zero_root"]{
  let mut s=Solver::with_storage(spot.clone(),storage);s.algo=algo;set_map(&mut s,initial);let mut b=baseline::GpuSolver::new(&s).unwrap();let mut c=candidate::GpuSolver::new(&s).unwrap();records.push(record(&s,&b,&c,id,"constructor",initial));
  for pattern in ["valid_root","empty_root","empty"]{set_map(&mut s,pattern);b.update_locks(&s).unwrap();c.update_locks(&s).unwrap();records.push(record(&s,&b,&c,id,"update",pattern));}
  drop(c);drop(b);drop(s);println!("D218_CASE {}",json!({"id":id,"exact":true}));std::io::stdout().flush().unwrap();id+=1;
 }}}
 assert_eq!(id,20);assert_eq!(records.len(),80);let mut f=std::fs::OpenOptions::new().create_new(true).write(true).open(out).unwrap();f.write_all(serde_json::to_string_pretty(&json!({"cases":20,"constructor_pairs":20,"update_pairs":60,"records":records,"application_kernel_launches":0,"solver_iterations":0,"malformed_vectors_only_constructor_and_table_updates_never_kernel_inputs":true})).unwrap().as_bytes()).unwrap();f.sync_all().unwrap();println!("D218_COMPLETE 20 cases 80 states no kernels");}
'''
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n');deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')];script=ROOT/'runs/D218-execute-predicate.py';ast.parse(script.read_text(encoding='utf-8'));paths=[Path(__file__),script,R/'protocol.json',R/'report.json',ROOT/'runs/D217-nullable-lock-direct/report.json',ROOT/'runs/D217-nullable-lock-direct/execution/complete.json',S/'manifest.json',S/'source-review.json',ROOT/'epoch/common.py']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{'id':'D218','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_CONSTRUCTOR_TABLE_GPU_PROCESS','rustc_command':cmd,'cases':20,'constructor_pairs':20,'update_pairs':60,'state_pairs':80,'required_free_bytes':66*1024**3,'input_sha256':{str(p):h.sha(p) for p in paths},'scope':'Fresh20case host predicate/actual lock table boundaries:2storage x2algorithms x5initial maps(empty,valid,empty root vector,empty terminal vector,onezero root). Each thenupdatesvalid/emptyvector/emptymap. All original buffers retained, true lockmapemptiness vs dummy sigma. Original/candidate states fullreadback; old sealedPTX, no NVRTC/training/evaluation/kernel launches. Malformed vector states tested only as constructor/table boundary data and never consumed by kernels. Original public finite locks/graph numerical workflows separatelypassedD216. No post-upload-error recovery, universal malformed-input support or performance claim. Genuinefailureclosesform, mechanical observer/reader repair retained without nativecase repeats.'})
for name in ['protocol.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D218','title':'Lock-map absence and dummy-buffer boundaries','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'20 constructor pairs and60table updates frozen','reason':'Actual lock-table and predicate readback for empty/nonempty/empty-vector maps. Malformed vectors are never consumed by solver kernels. No speed score.','evidence':[{'label':'Frozen boundary protocol','url':'evidence/'+H.name+'/protocol.json'}]});s.update(updated_at=h.now(),active_experiment='D218',stage='No-lock host predicate boundary checks',activity='All8397direct kernel pairs passed. Next validate map absence versus dummy sigma and lock-update boundaries, before large canonical states. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
