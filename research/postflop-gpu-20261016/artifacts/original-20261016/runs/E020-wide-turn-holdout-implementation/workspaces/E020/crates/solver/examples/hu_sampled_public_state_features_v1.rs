//! Research-only public betting-state catalog. No policy, cards or training targets.
#![allow(dead_code)]
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
use observation_v1::Observation;
use poker_reference_v1::{Game,key};
use solver::tree::Action;
use state::State;
use serde_json::{Value,json};
use std::collections::BTreeSet;

fn record(g:&Game,branch:usize,s:State,history:&[u8])->Value {
    assert_eq!(s.kind,0);let cfg=&g.configs[branch];let me=s.player as usize;let opp=1-me;
    let actions=s.actions(cfg);assert!((2..=4).contains(&actions.len()));
    let pot=s.put[0]+s.put[1];let remaining=s.put.map(|p|cfg.effective_stack-(p-cfg.starting_pot/2.));
    assert!(pot>0.&&remaining.iter().all(|x|x.is_finite()&&*x>=-1e-9));
    let facing=(s.put[opp]-s.put[me]).max(0.);assert!(facing<=remaining[me]+1e-9);
    let mut costs=[0.;4];let mut kinds=Vec::new();let mut calls=0;
    for (i,&action) in actions.iter().enumerate() {
        let after=s.act(cfg,action);let cost=after.put[me]-s.put[me];
        assert!(cost>=-1e-9&&cost<=remaining[me]+1e-9);
        assert!((after.put[opp]-s.put[opp]).abs()<1e-9);
        assert!((after.put.iter().sum::<f64>()-pot-cost).abs()<1e-8);
        let kind=match action {
            Action::Fold=>{assert_eq!(cost,0.);"fold"},
            Action::Check=>{assert_eq!(cost,0.);assert!(facing<1e-9);"check"},
            Action::Call(_)=>{assert!((cost-facing).abs()<1e-9);calls+=1;"call"},
            Action::Bet(_)=>{assert!(facing<1e-9);"bet"},
            Action::Raise(_)=>{assert!(facing>0.&&cost>facing);"raise"},
        };
        costs[i]=cost;kinds.push(kind);
    }
    assert_eq!(calls,usize::from(facing>1e-9));
    let h=history.iter().fold(1u64,|h,&a|(h<<3)|a as u64);
    // A legal card fixture checks public lookup against the existing native
    // observation decoder. Cards are not exported or used in numeric fields.
    let o=Observation::decode(key(&[0,1,2,3,4,5,6,7,8],me,None,branch,s.street as usize,h));
    assert_eq!(o.history,history);assert_eq!(o.phase,s.street as usize+1);
    assert_eq!(o.legal_actions(g),actions.len());
    json!({"public_id":branch,"actor":me,"phase":s.street+1,"history":history,
        "legal_actions":actions.len(),"action_kinds":kinds,"action_costs":costs,
        "pot":pot,"remaining_actor":remaining[me],"remaining_opponent":remaining[opp],
        "amount_to_call":facing,"call_price":facing/(pot+facing),
        "effective_remaining":remaining[0].min(remaining[1]),
        "starting_pot":cfg.starting_pot,"initial_effective_stack":cfg.effective_stack,
        "rake_fraction":cfg.rake_pct,"rake_cap":cfg.rake_cap})
}

fn walk(g:&Game,branch:usize,s:State,h:&mut Vec<u8>,rows:&mut Vec<Value>) {
    assert!(h.len()<=19&&rows.len()<100000);
    if s.kind==1 {h.push(5);walk(g,branch,s.deal(),h,rows);h.pop();return;}
    if s.kind>=2{return;}
    rows.push(record(g,branch,s,h));
    for (i,a) in s.actions(&g.configs[branch]).into_iter().enumerate(){
        h.push(i as u8+1);walk(g,branch,s.act(&g.configs[branch],a),h,rows);h.pop();
    }
}

fn catalog(g:&Game)->Vec<Value>{
    let mut rows=Vec::new();
    for branch in 0..g.kinds.len(){if g.kinds[branch]==2{
        walk(g,branch,State::root(&g.configs[branch]),&mut Vec::new(),&mut rows);
    }}
    let mut keys=BTreeSet::new();
    for row in &rows {assert!(keys.insert(format!("{}:{}:{}:{}",row["public_id"],row["actor"],row["phase"],row["history"])));}
    assert!(!rows.is_empty());rows
}

fn main()->Result<(),Box<dyn std::error::Error>>{
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),2);
    let destination=std::path::Path::new(&args[1]);assert!(!destination.exists());
    let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
    let game=Game::new(&context);let rows=catalog(&game);let mut checked=0;
    // Synthetic public-geometry controls vary stack and pot independently.
    for (pot,stack) in [(4.,100.),(5.5,20.),(40.,200.),(120.,30.),(10.,1000.)]{
        let mut changed=context.clone();
        for node in changed["nodes"].as_array_mut().unwrap(){if node["leaf"]["type"]=="postflop"{
            node["leaf"]["starting_pot"]=json!(pot);node["leaf"]["effective_stack"]=json!(stack);
        }}
        let other=Game::new(&changed);let variants=catalog(&other);checked+=variants.len();
        for row in variants.iter().filter(|r|r["history"].as_array().unwrap().is_empty()){
            assert_eq!(row["pot"],json!(pot));assert_eq!(row["remaining_actor"],json!(stack));
            assert_eq!(row["amount_to_call"],json!(0.));
        }
        if pot==4.&&stack==100.{
            for branch in 0..other.kinds.len(){if other.kinds[branch]!=2{continue;}
                let cfg=&other.configs[branch];let root=State::root(cfg);
                let (index,action)=root.actions(cfg).into_iter().enumerate().find(|(_,a)|matches!(a,Action::Bet(v) if (*v-2.).abs()<1e-9)).unwrap();
                let facing=root.act(cfg,action);let row=record(&other,branch,facing,&[index as u8+1]);
                assert_eq!(row["pot"],json!(6.));assert_eq!(row["amount_to_call"],json!(2.));
                assert_eq!(row["remaining_actor"],json!(100.));assert_eq!(row["remaining_opponent"],json!(98.));
                assert_eq!(row["call_price"],json!(0.25));
                let (call_index,call)=facing.actions(cfg).into_iter().enumerate().find(|(_,a)|matches!(a,Action::Call(_))).unwrap();
                let next=facing.act(cfg,call);assert_eq!(next.kind,1);
                let turn=record(&other,branch,next.deal(),&[index as u8+1,call_index as u8+1,5]);
                assert_eq!(turn["pot"],json!(8.));assert_eq!(turn["remaining_actor"],json!(98.));
                assert_eq!(turn["remaining_opponent"],json!(98.));assert_eq!(turn["amount_to_call"],json!(0.));
            }
        }
    }
    let count=rows.len();
    let output=json!({"format":1,"passed":true,"scope":"Public postflop betting geometry only; no new policy or strength claim.",
        "rows":rows,"decision_templates":count,"synthetic_geometry_templates_checked":checked,
        "synthetic_stack_pot_variants":5,"public_lookup_matches_native_observation":true,
        "known_half_pot_bet_call_turn_values_checked":true,"training_started":false,"production_modified":false});
    let file=std::fs::OpenOptions::new().write(true).create_new(true).open(destination)?;
    serde_json::to_writer(file,&output)?;
    println!("{}",json!({"passed":true,"decision_templates":count,"synthetic_templates_checked":checked}));Ok(())
}
