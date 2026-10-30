//! Offline geometry fixtures across stack depths. No solve, no live-server access.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
use serde_json::{json,Value};
use solver::preflop::{equity::EquityTable,PreflopConfig,PreflopSolver};
use std::{path::Path,sync::Arc};
use poker_reference_v1::Game;
use state::State;
fn collect(
    s: &PreflopSolver, i: usize, path: Vec<usize>, seats: [usize; 2],
    dead_money: f64, nodes: &mut Vec<Value>,
) -> usize {
    let local = nodes.len();
    nodes.push(Value::Null);
    let n = &s.nodes[i];
    let mask = (1u32 << seats[0]) | (1u32 << seats[1]);
    assert_eq!(n.live & !mask, 0, "third live player in HU export");
    let actor = if n.kind == 0 {
        Some(seats.iter().position(|&p| p == n.actor as usize).expect("live actor"))
    } else { None };
    let winner = if n.kind == 1 {
        Some(seats.iter().position(|&p| p == n.winner as usize).expect("live winner"))
    } else { None };
    let invested = [n.invested[seats[0]], n.invested[seats[1]]];
    assert!((n.pot - invested.iter().sum::<f64>() - dead_money).abs() < 1e-8);
    let leaf = match n.kind {
        0 => Value::Null,
        1 => {
            assert_eq!(n.live.count_ones(), 1);
            let utilities: [f64; 2] = std::array::from_fn(|p|
                if Some(p) == winner { n.pot - invested[p] } else { -invested[p] });
            json!({"type":"fold", "utilities":utilities})
        },
        2 => {
            assert_eq!(n.live, mask);
            assert!((invested[0] - invested[1]).abs() < 1e-8, "unequal matched investments");
            // Preflop stack excludes the separately contributed dead ante.
            let remaining = s.cfg.stack + s.cfg.ante - invested[0];
            assert!(remaining >= -1e-8);
            let offsets = invested.map(|v| n.pot / 2. - v);
            json!({"type":if remaining > 1e-8 {"postflop"} else {"showdown"},
                "starting_pot":n.pot,"effective_stack":remaining.max(0.),
                "value_offsets":offsets})
        },
        _ => panic!("unsupported preflop node kind"),
    };
    let children: Vec<usize> = (0..n.actions.len()).map(|a| {
        let mut next = path.clone(); next.push(a);
        collect(s, s.child(i, a), next, seats, dead_money, nodes)
    }).collect();
    nodes[local] = json!({"original_node":i,"path":path,"kind":n.kind,
        "original_actor":n.actor,"actor":actor,"children":children,
        "strategy":if n.kind == 0 {s.average_strategy(i)} else {vec![]},
        "pot":n.pot,"invested":invested,"original_invested":n.invested,
        "original_live":n.live,"winner":winner,"original_winner":n.winner,
        "r":[n.r.get(seats[0]),n.r.get(seats[1])],"leaf":leaf,
        "actions":n.actions.iter().map(|a|json!({"kind":a.kind,"to":a.to,"label":a.label})).collect::<Vec<_>>()});
    local
}

fn post(g:&Game,branch:usize,s:State,h:u64,out:&mut Vec<Value>){
 if s.kind==1{post(g,branch,s.deal(),(h<<3)|5,out);return;}
 if s.kind>=2{return;}
 assert!(h<(1u64<<59));let acts=s.actions(&g.configs[branch]);assert!(acts.len()<=4);
 out.push(json!({"hi":((1u64<<63)|(h<<4)|branch as u64).to_string(),"actor":s.player,"phase":s.street+1,"n":acts.len()}));
 for(a,act)in acts.into_iter().enumerate(){post(g,branch,s.act(&g.configs[branch],act),(h<<3)|(a as u64+1),out);}
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),1);
 let out=Path::new(&args[0]);assert!(!out.exists());
 rayon::ThreadPoolBuilder::new().num_threads(2).build_global()?;
 let cache="cache/preflop_eq169.bin";let bytes=std::fs::read(cache)?;
 assert_eq!(bytes.len(),4+169*169*4);assert_eq!(u32::from_le_bytes(bytes[..4].try_into()?),20000);
 let eq=Arc::new(EquityTable::load_or_build(cache,20000));std::fs::create_dir(out)?;
 let mut fixtures=vec![];
 for stack in [20.,40.,60.,100.,150.,200.,400.]{
  let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["BTN","SB","BB"],"stack":stack,
   "posts":[0.,0.5,1.],"ante":0.,"limp":false,"open_raises":[2.],"raise_mults":[3.],
   "max_raises":3,"add_allin":true,"rake_pct":5.,"rake_cap":2.,"no_flop_no_drop":true,"realization":"balanced"}))?;
  let s=PreflopSolver::new(cfg,eq.clone())?;assert_eq!(s.iteration,0);assert!(s.nodes.len()<10000);
  let open=s.nodes[0].actions.iter().position(|a|a.kind=="raise"&&(a.to-2.).abs()<1e-9).unwrap();
  let next=s.child(0,open);let fold=s.nodes[next].actions.iter().position(|a|a.kind=="fold").unwrap();
  let path=vec![open,fold];let(root,reaches)=s.walk(&path)?;let seats=[2,0];
  assert_eq!(s.nodes[root].actor,2);assert_eq!(s.nodes[root].live,(1<<2)|1);
  let dead=s.nodes[root].pot-seats.iter().map(|&p|s.nodes[root].invested[p]).sum::<f64>();
  let mut nodes=vec![];collect(&s,root,path.clone(),seats,dead,&mut nodes);assert!(nodes.len()<=16);
  let doc=json!({"schema":"hu-context-v1","save":"none: unsolved geometry fixture","iteration":0,
    "config":s.cfg,"root_path":path,"original_seats":seats,"positions":["BB","BTN"],"postflop_order":[0,1],
    "dead_money":dead,"rake_fraction":0.05,"rake_cap":2.,"incoming_class_mass":[reaches[2],reaches[0]],
    "class_base":null,"nodes":nodes,"limitations":["Unsolved uniform-policy geometry fixture; not learned incoming ranges or strategy evidence."]});
  let source=serde_json::to_string(&doc)?;let name=format!("stack-{}",stack as u32);
  std::fs::write(out.join(format!("{name}-context.json")),&source)?;
  let g=Game::new(&doc);let mut obs=vec![];
  for i in 0..g.kinds.len(){
   if g.kinds[i]==0{obs.push(json!({"hi":(i+1).to_string(),"actor":g.actors[i],"phase":0,"n":g.arities[i]}));}
   if g.kinds[i]==2{post(&g,i,State::root(&g.configs[i]),1,&mut obs);}
  }
  let queries=json!({"context_source":source,"observations":obs,"scope":"All public histories only; no dealt cards or strategy."});
  std::fs::write(out.join(format!("{name}-queries.json")),serde_json::to_vec(&queries)?)?;
  fixtures.push(json!({"stack":stack,"preflop_nodes":nodes.len(),"public_decisions":obs.len(),"name":name}));
 }
 std::fs::write(out.join("manifest.json"),serde_json::to_vec(&json!({"fixtures":fixtures,"solved":false,"production_modified":false}))?)?;
 println!("{} unsolved native geometry fixtures",fixtures.len());Ok(())
}
