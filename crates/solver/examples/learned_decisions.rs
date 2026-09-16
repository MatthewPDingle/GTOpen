//! Offline learned continuation decision screen. Research saves must never be
//! loaded in the ordinary app: their sidecar selects the experimental payoff.
use solver::preflop::{PreflopSolver,PreflopConfig,equity::EquityTable,gpu::PreflopGpu};
use serde_json::{json,Value};
use std::{sync::Arc,path::Path,time::Instant};
fn read(p:&str)->Result<String,String>{std::fs::read_to_string(p).map_err(|e|e.to_string())}
fn write(p:impl AsRef<Path>,v:&Value)->Result<(),String>{std::fs::write(p,serde_json::to_vec_pretty(v).unwrap()).map_err(|e|e.to_string())}
fn paths(s:&PreflopSolver)->Vec<Vec<usize>>{
 let mut result=Vec::new();let mut prefix=Vec::new();
 for _ in 0..s.n{
  let (node,_)=s.walk(&prefix).unwrap();let nd=&s.nodes[node];if nd.kind!=0{break;}
  result.push(prefix.clone());
  if prefix.is_empty() || nd.actor as usize==s.n-3 {
   if let Some(raise)=nd.actions.iter().position(|a|a.label.starts_with("Raise")){
    let mut response=prefix.clone();response.push(raise);
    for _ in 0..s.n {let (i,_)=s.walk(&response).unwrap();let n=&s.nodes[i];if n.kind!=0{break;}
     result.push(response.clone());if let Some(f)=n.actions.iter().position(|a|a.label=="Fold"){response.push(f);}else{break;}
    }
   }
  }
  if let Some(f)=nd.actions.iter().position(|a|a.label=="Fold"){prefix.push(f);}else{break;}
 }
 result.sort();result.dedup();result
}
fn main()->Result<(),String>{
 rayon::ThreadPoolBuilder::new().num_threads(16).build_global().map_err(|e|e.to_string())?;
 let a:Vec<String>=std::env::args().skip(1).collect();
 let valid=match a.first().map(String::as_str){Some("check")=>a.len()==4,Some("solve")=>a.len()==6 || (a.len()==7 && a[6]=="resume"),Some("evaluate")=>a.len()==5,_=>false};
 if !valid{return Err("check KERNEL FIXTURES OUTPUT | solve SOURCE OUTPUT_DIR MODEL STEPS KERNEL [resume] | evaluate SAVE OUTPUT MODEL KERNEL".into());}
 if a[0]!="check" && a[3]!="candidate" && a[3]!="balanced" {return Err("model must be candidate or balanced".into());}
 let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",20000));
 if a[0]=="check"{
  let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["SB","BB"],"stack":30,"posts":[0.5,1],"limp":true,"open_raises":[2],"raise_mults":[3],"max_raises":2,"add_allin":false,"rake_pct":0,"rake_cap":0,"realization":"balanced"})).map_err(|e|e.to_string())?;
  let s=PreflopSolver::new(cfg,eq)?;let mut g=PreflopGpu::new(&s,23000)?;
  g.enable_learned_research(&s,&read(&a[1])?)?;
  let fixtures:Value=serde_json::from_str(&read(&a[2])?).map_err(|e|e.to_string())?;
  let result=g.check_learned_inference(&fixtures)?;write(&a[3],&result)?;println!("{result}");return Ok(());
 }
 if a[0]=="solve"{
  let out=Path::new(&a[2]);std::fs::create_dir_all(out).map_err(|e|e.to_string())?;
  let loaded=PreflopSolver::load_game(&a[1],eq.clone())?;
  let mut s=if a.get(6).is_some_and(|v|v=="resume"){loaded}else{PreflopSolver::new(loaded.cfg.clone(),eq)?};
  if s.cfg.realization!="balanced" || s.cfg.rake_pct!=0.0{return Err("matched zero-rake Balanced source required".into());}
  let mut g=PreflopGpu::new(&s,23000)?;let start=s.iteration;
  let coverage=if a[3]=="candidate"{g.enable_learned_research(&s,&read(&a[5])?)?}else if a[3]=="balanced"{Value::Null}else{return Err("model".into())};
  let steps:u32=a[4].parse().map_err(|_|"steps")?;let t=Instant::now();
  for _ in 0..steps{g.iterate(&mut s)?;if s.iteration%25==0{println!("iteration {} elapsed {:.2}",s.iteration,t.elapsed().as_secs_f64());}}
  let (gaps,evs)=g.gaps_and_evs()?;g.sync_to_cpu(&mut s)?;drop(g);
  if gaps.iter().chain(&evs).any(|x|!x.is_finite()){return Err("nonfinite evaluation".into());}
  let rows:Vec<_>=paths(&s).iter().map(|p|json!({"path":p,"view":s.node_view(p).unwrap()})).collect();
  s.save_game(out.join("policy.gtop").to_str().unwrap())?;
  let result=json!({"model":a[3],"source":a[1],"config":s.cfg,"start_iteration":start,"iteration":s.iteration,"nodes":s.nodes.len(),"seconds":t.elapsed().as_secs_f64(),"gaps":gaps,"evs":evs,"coverage":coverage,"views":rows,
   "warning":"Offline research policy. Ordinary save metadata remains Balanced; do not load in the live app. Candidate gaps freeze range-conditioned leaf predictions and are not full-game exploitability or a convergence guarantee."});
  write(out.join(format!("iteration-{}.json",s.iteration)),&result)?;println!("completed {}",s.iteration);return Ok(());
 }
 if a[0]=="evaluate"{
  let s=PreflopSolver::load_game(&a[1],eq.clone())?;let before=s.arena_snapshot();let mut g=PreflopGpu::new(&s,23000)?;
  let coverage=if a[3]=="candidate"{g.enable_learned_research(&s,&read(&a[4])?)?}else{Value::Null};
  let selected=paths(&s);let mut result=g.research_frontier_action_values(&s,&selected)?;
  result["model"]=json!(a[3]);result["coverage"]=coverage;result["iteration"]=json!(s.iteration);
  result["prefixes"]=json!(selected.iter().map(|p|{let (node,r)=s.walk(p).unwrap();let actor=s.nodes[node].actor as usize;
   json!({"path":p,"opponent_prefix_mass":r.iter().enumerate().filter(|(q,_)|*q!=actor).map(|(_,r)|r.iter().map(|&w|w as f64).sum::<f64>()).product::<f64>(),"invested":s.nodes[node].invested[actor]})}).collect::<Vec<_>>());
  let mut copy=PreflopSolver::load_game(&a[1],eq)?;g.sync_to_cpu(&mut copy)?;
  if s.arena_snapshot()!=before || copy.arena_snapshot()!=before{return Err("read-only evaluation mutated policy".into());}write(&a[2],&result)?;return Ok(());
 }
 Err("unknown command".into())
}
