//! Standalone research only; never load its policy saves in the ordinary app.
use solver::preflop::{PreflopConfig,PreflopSolver,equity::EquityTable,gpu::PreflopGpu};
use serde_json::{json,Value};
use std::{sync::Arc,path::Path,time::Instant};
fn write(p:impl AsRef<Path>,v:&Value)->Result<(),String>{std::fs::write(p,serde_json::to_vec(v).unwrap()).map_err(|e|e.to_string())}
fn paths(s:&PreflopSolver)->Vec<Vec<usize>>{
 let mut out=Vec::new();let mut prefix=Vec::new();
 for _ in 0..s.n{let (node,_)=s.walk(&prefix).unwrap();let n=&s.nodes[node];if n.kind!=0{break;}out.push(prefix.clone());
  if prefix.is_empty() || n.actor as usize==s.n.saturating_sub(3){if let Some(a)=n.actions.iter().position(|a|a.label.starts_with("Raise")){
   let mut p=prefix.clone();p.push(a);for _ in 0..s.n{let (i,_)=s.walk(&p).unwrap();let n=&s.nodes[i];if n.kind!=0{break;}out.push(p.clone());if let Some(f)=n.actions.iter().position(|a|a.label=="Fold"){p.push(f);}else{break;}}
  }}if let Some(f)=n.actions.iter().position(|a|a.label=="Fold"){prefix.push(f);}else{break;}
}out.sort();out.dedup();out
}
fn leaves(s:&PreflopSolver)->Vec<Value>{
 let mut out=Vec::new();
 for mut path in paths(s){
  let (i,_)=s.walk(&path).unwrap();let nd=&s.nodes[i];
  if nd.actor as usize!=s.n-1 || nd.raises!=1{continue;}
  let Some(call)=nd.actions.iter().position(|a|a.label.starts_with("Call")) else{continue;};
  path.push(call);
  loop{let (i,_)=s.walk(&path).unwrap();let nd=&s.nodes[i];if nd.kind!=0{break;}
   let Some(f)=nd.actions.iter().position(|a|a.label=="Fold") else{break;};path.push(f);
  }
  let (i,r)=s.walk(&path).unwrap();let nd=&s.nodes[i];if nd.kind!=2 || nd.live.count_ones()!=2{continue;}
  let seats:Vec<_>=s.postflop_order().into_iter().filter(|p|nd.live&(1<<p)!=0).collect();
  let view=s.node_view(&path).unwrap();let weights:Vec<_>=seats.iter().map(|&p|view.reaches_all[p].clone()).collect();
  out.push(json!({"id":format!("bb-call-{}",out.len()),"path":path,"pot":nd.pot,"stack":seats.iter().map(|&p|s.cfg.stack-nd.invested[p]).fold(f64::INFINITY,f64::min),"weights":weights,"positions":seats.iter().map(|&p|s.cfg.positions[p].clone()).collect::<Vec<_>>(),"independent_branch_mass":r.iter().map(|w|w.iter().map(|&v|v as f64).sum::<f64>()).product::<f64>()}));
 }out
}
fn main()->Result<(),String>{
 rayon::ThreadPoolBuilder::new().num_threads(16).build_global().map_err(|e|e.to_string())?;
 let a:Vec<String>=std::env::args().skip(1).collect();
 let valid=match a.first().map(String::as_str){Some("oracle")=>a.len()==5 || (a.len()==6 && a[5]=="zeros"),Some("solve")=>a.len()==6 || (a.len()==7 && a[6]=="resume"),Some("evaluate")=>a.len()==5,_=>false};
 if !valid{return Err("oracle OUTPUT KERNEL MODEL PLAYERS | solve SOURCE DIR MODEL STEPS KERNEL [resume] | evaluate SAVE OUTPUT MODEL KERNEL".into());}
 let model=&a[3];if model!="balanced" && model!="candidate" && model!="original"{return Err("model: balanced/candidate/original".into());}
 let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",20000));
 if a[0]=="oracle"{
  let np:usize=a[4].parse().map_err(|_|"players")?;if ![2,3,8].contains(&np){return Err("oracle players 2/3/8".into());}
  let mut posts=vec![0.;np];posts[np-2]=0.5;posts[np-1]=1.;
  let cfg:PreflopConfig=serde_json::from_value(json!({"positions":(0..np).map(|p|format!("P{p}")).collect::<Vec<_>>(),"stack":30,"posts":posts,"limp":np==2,"open_raises":[2],"raise_mults":[3],"max_raises":if np==2 {3}else{1},"add_allin":true,"rake_pct":0,"rake_cap":0,"realization":"balanced"})).map_err(|e|e.to_string())?;
  let mut s=PreflopSolver::new(cfg,eq)?;s.research_seed_quality_fixture_averages()?;
  if a.get(5).is_some_and(|x|x=="zeros"){PreflopGpu::seed_interface_sparse_fixture(&mut s)?;}
  let mut pths=vec![Vec::new();s.nodes.len()];let mut selected=Vec::new();let mut nodes=Vec::new();
  for (i,n) in s.nodes.iter().enumerate(){let children:Vec<_>=(0..n.actions.len()).map(|a|{let c=s.child(i,a);pths[c]=pths[i].iter().copied().chain([a]).collect();c}).collect();
   if n.kind==0 && n.live.count_ones()==2 && selected.len()<128{selected.push(pths[i].clone());}
   nodes.push(json!({"kind":n.kind,"actor":n.actor,"children":children,"pot":n.pot,"invested":n.invested,"live":n.live,"winner":n.winner,"r":n.r,"sigma":if n.kind==0{s.average_strategy(i)}else{vec![]},"path":pths[i]}));
  }
  let before=s.arena_snapshot();let source=std::fs::read_to_string(&a[2]).map_err(|e|e.to_string())?;
  let mut g=PreflopGpu::new(&s,23000)?;let plan=g.enable_learned_interface_research(&s,&source,model=="candidate")?;
  let frontier=g.research_frontier_action_values(&s,&selected)?;let (gaps,evs)=g.gaps_and_evs()?;g.sync_to_cpu(&mut s)?;
  if before!=s.arena_snapshot(){return Err("oracle evaluation modified policy".into());}
  write(&a[1],&json!({"config":s.cfg,"model":model,"plan":plan,"nodes":nodes,"frontier":frontier,"evs":evs,"gaps":gaps}))?;return Ok(());
 }
 let loaded=PreflopSolver::load_game(&a[1],eq.clone())?;
 let mut s=if a[0]=="evaluate" || a.get(6).is_some_and(|x|x=="resume"){loaded}else{PreflopSolver::new(loaded.cfg.clone(),eq)?};
 let mut g=PreflopGpu::new(&s,23000)?;let kernel=if a[0]=="solve"{&a[5]}else{&a[4]};
 let plan=if model=="original"{Value::Null}else{g.enable_learned_interface_research(&s,&std::fs::read_to_string(kernel).map_err(|e|e.to_string())?,model=="candidate")?};
 if a[0]=="evaluate"{
  let before=s.arena_snapshot();let selected=paths(&s);let mut v=g.research_frontier_action_values(&s,&selected)?;
  v["prefixes"]=json!(selected.iter().map(|p|{let (i,r)=s.walk(p).unwrap();let actor=s.nodes[i].actor as usize;json!({"path":p,"opponent_prefix_mass":r.iter().enumerate().filter(|(q,_)|*q!=actor).map(|(_,w)|w.iter().map(|&x|x as f64).sum::<f64>()).product::<f64>()})}).collect::<Vec<_>>());
  v["model"]=json!(model);v["iteration"]=json!(s.iteration);g.sync_to_cpu(&mut s)?;if before!=s.arena_snapshot(){return Err("evaluation modified policy".into());}write(&a[2],&v)?;return Ok(());
 }
 let out=Path::new(&a[2]);std::fs::create_dir_all(out).map_err(|e|e.to_string())?;let steps:u32=a[4].parse().map_err(|_|"steps")?;let start=s.iteration;let time=Instant::now();
 for _ in 0..steps{g.iterate(&mut s)?;if s.iteration%25==0{println!("iteration {} elapsed {:.2}",s.iteration,time.elapsed().as_secs_f64());}}
 let learning_seconds=time.elapsed().as_secs_f64();let (gaps,evs)=g.gaps_and_evs()?;g.sync_to_cpu(&mut s)?;drop(g);
 if gaps.iter().chain(&evs).any(|x|!x.is_finite()) || evs.iter().sum::<f64>().abs()>0.0002{return Err(format!("nonfinite or unbalanced evaluation: {evs:?}"));}
 let rows:Vec<_>=paths(&s).iter().map(|p|json!({"path":p,"view":s.node_view(p).unwrap()})).collect();s.save_game(out.join("policy.gtop").to_str().unwrap())?;
 write(out.join(format!("iteration-{}.json",s.iteration)),&json!({"model":model,"config":s.cfg,"start_iteration":start,"iteration":s.iteration,"learning_seconds":learning_seconds,"gaps":gaps,"evs":evs,"plan":plan,"views":rows,"leaves":leaves(&s),"warning":"Offline research only. Save metadata remains Balanced. Larger games reset legal pair chance at heads-up entry, ignoring folded-card bunching. Gap freezes range-conditioned values; not full-game exploitability."}))?;
 println!("completed {}",s.iteration);Ok(())
}
