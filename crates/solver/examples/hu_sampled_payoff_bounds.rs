//! Enumerate all public terminals and all winner assignments for fixed BB context.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
use poker_reference_v1::Game;
use state::State;
use serde_json::{Value,json};

fn record(bounds:&mut [[f64;2];2],values:[f64;2]) {
 for p in 0..2 {assert!(values[p].is_finite());bounds[p][0]=bounds[p][0].min(values[p]);bounds[p][1]=bounds[p][1].max(values[p]);}
}
fn post(g:&Game,b:usize,s:State,bounds:&mut [[f64;2];2],terminals:&mut usize){
 let cfg=&g.configs[b];
 if s.kind==1{post(g,b,s.deal(),bounds,terminals);return;}
 if s.kind>=2{
  *terminals+=1;let v=s.payouts(cfg);let off=[g.offsets[b*2],g.offsets[b*2+1]];
  if s.kind==2 {let loser=s.player as usize;let mut u=[v[0]+off[0],v[0]+off[1]];u[loser]=v[1]+off[loser];record(bounds,u);}
  else{for winner in [-1,0,1]{record(bounds,std::array::from_fn(|p|off[p]+if winner<0{v[2]}else if winner==p as i32{v[0]}else{v[1]}));}}
  return;
 }
 for a in s.actions(cfg){post(g,b,s.act(cfg,a),bounds,terminals);}
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),2);assert!(!std::path::Path::new(&args[1]).exists());
 let c:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;let g=Game::new(&c);
 let mut bounds=[[f64::INFINITY,f64::NEG_INFINITY];2];let mut terminals=0;
 for n in 0..g.kinds.len(){match g.kinds[n]{
  1=>{record(&mut bounds,[g.offsets[n*2],g.offsets[n*2+1]]);terminals+=1;},
  2=>post(&g,n,State::root(&g.configs[n]),&mut bounds,&mut terminals),
  3=>{let cfg=&g.configs[n];let amount=cfg.starting_pot/2.;let gross=cfg.rake_pct*2.*amount;let rake=if cfg.rake_cap>0.{gross.min(cfg.rake_cap)}else{gross};
   for winner in [-1,0,1]{record(&mut bounds,std::array::from_fn(|p|g.offsets[n*2+p]+if winner<0{-rake/2.}else if winner==p as i32{amount-rake}else{-amount}));}terminals+=1;},
  0=>{},_=>panic!()
 }}
 // A looser independent cash-flow envelope: stacks 200 each, dead SB 0.5.
 assert!(bounds.iter().all(|b|b[0]>=-200.-1e-9&&b[1]<=200.5+1e-9));
 let out=json!({"utility_bounds":bounds,"paired_difference_bounds":bounds.map(|b|[b[0]-b[1],b[1]-b[0]]),
  "public_terminal_templates":terminals,"cash_flow_envelope":[-200.,200.5],
  "scope":"All native public terminals and winner assignments; conservative over physically possible winners. Fixed registered BB context only."});
 std::fs::write(&args[1],serde_json::to_vec_pretty(&out)?)?;println!("{}",out);Ok(())
}
