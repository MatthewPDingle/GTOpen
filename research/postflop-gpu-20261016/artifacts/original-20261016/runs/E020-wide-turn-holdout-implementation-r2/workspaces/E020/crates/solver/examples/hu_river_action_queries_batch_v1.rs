//! Shared-query export of a bounded list of complete river action trees.
//! Private opponent enumeration and showdown labels are separate from features.
#![allow(dead_code)]
#[path = "research_sampled/state.rs"] mod state;
#[path = "research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path = "research_sampled/observation_v1.rs"] mod observation_v1;
#[path = "research_sampled/policy_bank_v1.rs"] mod policy_bank_v1;
use poker_reference_v1::{Game, Key, key};
use observation_v1::Observation;
use state::State;
use serde::Deserialize;
use serde_json::{Value, json};
use solver::tree::{TreeConfig, Action, KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN};
use std::{collections::BTreeMap, fs::OpenOptions, io::{Read, Write}};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request { format:u32, hi:String, lo:String }
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct BatchRequest {format:u32, targets:Vec<Request>}

#[derive(Default)]
struct Queries {
    observations:Vec<Observation>, arities:Vec<usize>, ids:BTreeMap<Key,usize>,
}
impl Queries {
    fn add(&mut self, game:&Game, raw:Key, n:usize)->usize {
        let o=Observation::decode(raw); assert_eq!(o.legal_actions(game),n);
        let canonical=o.key();
        if let Some(&i)=self.ids.get(&canonical) { assert_eq!(self.arities[i],n); return i; }
        assert!(self.observations.len()<250_000,"query budget exceeded");
        let i=self.observations.len(); self.ids.insert(canonical,i);
        self.observations.push(o); self.arities.push(n); i
    }
    fn document(&self, game:&Game, context:&str, request:&str)->Value {
        let rows:Vec<_>=self.observations.iter().zip(&self.arities).map(|(o,&n)| {
            let k=o.key(); let features=o.features();
            let history:Vec<_>=policy_bank_v1::own_history(game,k).into_iter().map(|(prior,a,arity)| {
                let i=*self.ids.get(&prior).expect("missing actual own-history ancestor");
                assert_eq!(self.observations[i].actor,o.actor); assert_eq!(self.arities[i],arity);
                json!([i,a,arity])
            }).collect();
            json!({"hi":k.0.to_string(),"lo":k.1.to_string(),"actor":o.actor,"phase":o.phase,"n":n,
                "active_features":features.iter().enumerate().filter_map(|(i,&x)|if x==1. {Some(i)}else{None}).collect::<Vec<_>>(),
                "own_history":history})
        }).collect();
        json!({"format":2,"context_source":context,"batch_source":request,"observations":rows})
    }
}

fn parents(game:&Game, destination:usize)->Vec<(usize,usize)> {
    let mut parent=vec![None;game.kinds.len()];
    for node in 0..game.kinds.len() { if game.kinds[node]==0 {
        for a in 0..game.arities[node]as usize {
            let child=game.children[node*4+a]as usize;
            assert!(parent[child].replace((node,a)).is_none(),"context is not a tree");
        }
    }}
    let mut path=Vec::new(); let mut node=destination;
    while let Some((p,a))=parent[node] { path.push((p,a)); node=p; assert!(path.len()<game.kinds.len()); }
    assert_eq!(node,0); path.reverse(); path
}

fn trace(game:&Game,deal:&[u8;9],target:&Observation,pre:&[(usize,usize)],queries:&mut Queries)
    ->(Vec<[usize;3]>,usize,State) {
    let mut path=Vec::new();
    for &(node,a) in pre {
        let actor=game.actors[node]as usize; let n=game.arities[node]as usize;
        let i=queries.add(game,key(deal,actor,Some(node),0,0,0),n); path.push([i,a,n]);
    }
    let cfg=&game.configs[target.public_id]; let mut state=State::root(cfg); let mut history=1u64;
    for &token in &target.history {
        if token==5 { assert_eq!(state.kind,KIND_CHANCE); state=state.deal(); }
        else {
            assert_eq!(state.kind,KIND_ACTION); let actions=state.actions(cfg); let a=token as usize-1;
            assert!(a<actions.len());
            let i=queries.add(game,key(deal,state.player as usize,None,target.public_id,state.street as usize,history),actions.len());
            path.push([i,a,actions.len()]); state=state.act(cfg,actions[a]);
        }
        history=(history<<3)|token as u64;
    }
    assert_eq!(state.kind,KIND_ACTION); assert_eq!(state.street,2); assert_eq!(state.player as usize,target.actor);
    let raw=key(deal,target.actor,None,target.public_id,2,history);
    assert_eq!(Observation::decode(raw),*target,"other private cards affected hero observation");
    let i=queries.add(game,raw,state.actions(cfg).len()); (path,i,state)
}

const MAX_NODES:usize=500_000;
const MAX_BYTES:usize=64_000_000;

fn shape(state:State,cfg:&TreeConfig)->usize {
    assert_eq!(state.street,2); assert_ne!(state.kind,KIND_CHANCE);
    if state.kind!=KIND_ACTION {return 1;}
    let mut total=1;
    for a in state.actions(cfg) {total+=shape(state.act(cfg,a),cfg);assert!(total<=MAX_NODES/990,"public subtree exceeds budget");}
    total
}

fn action_document(action:Action,before:State,after:State,cfg:&TreeConfig)->Value {
    let (kind,to)=match action {
        Action::Fold=>("fold",None),Action::Check=>("check",None),
        Action::Call(v)=>("call",Some(v)),Action::Bet(v)=>("bet",Some(v)),Action::Raise(v)=>("raise",Some(v)),
    };
    let actor=before.player as usize;
    json!({"kind":kind,"to":to,"paid":after.put[actor]-before.put[actor],
        "all_in":matches!(action,Action::Call(_)|Action::Bet(_)|Action::Raise(_)) &&
            (after.put[actor]-(cfg.starting_pot/2.+cfg.effective_stack)).abs()<1e-8})
}

fn tree(game:&Game,deal:&[u8;9],target:&Observation,state:State,history:u64,outcome:usize,
    queries:&mut Queries,nodes:&mut Vec<Value>)->usize {
    let cfg=&game.configs[target.public_id];assert_eq!(state.street,2);assert_ne!(state.kind,KIND_CHANCE);
    let value=if state.kind==KIND_ACTION {
        let actions=state.actions(cfg);let n=actions.len();assert!((2..=4).contains(&n));
        let i=queries.add(game,key(deal,state.player as usize,None,target.public_id,2,history),n);
        let mut children=Vec::new();let mut edges=Vec::new();
        for (a,&action) in actions.iter().enumerate() {
            let child=state.act(cfg,action);edges.push(action_document(action,state,child,cfg));
            children.push(tree(game,deal,target,child,(history<<3)|(a as u64+1),outcome,queries,nodes));
        }
        json!({"kind":"decision","actor":state.player,"put":state.put,"query_index":i,
            "children":children,"actions":edges})
    } else {
        assert!(state.kind==KIND_TERM_FOLD||state.kind==KIND_TERM_SHOWDOWN);
        let p=state.payouts(cfg);
        let v=if state.kind==KIND_TERM_FOLD {if target.actor==state.player as usize {p[1]}else{p[0]}}
            else {match outcome {0=>p[1],1=>p[2],2=>p[0],_=>panic!("outcome")}};
        let offset=game.offsets[target.public_id*2+target.actor];
        json!({"kind":if state.kind==KIND_TERM_FOLD {"fold"}else{"showdown"},"put":state.put,
            "folded":if state.kind==KIND_TERM_FOLD {Some(state.player)}else{None},"payoff":v+offset})
    };
    assert!(nodes.len()<MAX_NODES,"node budget exceeded");let i=nodes.len();nodes.push(value);i
}

fn target_export(game:&Game,input:&Request,queries:&mut Queries,total_nodes:&mut usize)->Value {
    assert_eq!(input.format,1);
    let target=Observation::decode((input.hi.parse().unwrap(),input.lo.parse().unwrap()));
    assert_eq!(target.phase,3);let n=target.legal_actions(&game);assert!((2..=4).contains(&n));
    let pre=parents(&game,target.public_id);let cfg=&game.configs[target.public_id];
    let mut mask=0u64;for &c in &target.cards {assert!(c<52 && mask&(1u64<<c)==0);mask|=1u64<<c;}
    let hero_rank=solver::evaluator::evaluate7(&target.cards);
    let history=target.history.iter().fold(1u64,|h,&t|(h<<3)|t as u64);
    let mut pairs=Vec::new();let mut nodes=Vec::new();let mut target_index=None;
    let mut expected_shape=None;let mut counts=[0usize;3];
    for a in 0u8..52 {for b in a+1..52 {
        if mask&((1u64<<a)|(1u64<<b))!=0 {continue;}
        let mut deal=[0u8;9];let opponent=1-target.actor;
        deal[target.actor*2..target.actor*2+2].copy_from_slice(&target.cards[..2]);
        deal[opponent*2..opponent*2+2].copy_from_slice(&[a,b]);deal[4..].copy_from_slice(&target.cards[2..]);
        let (path,i,state)=trace(game,&deal,&target,&pre,queries);
        if let Some(old)=target_index {assert_eq!(old,i);} else {target_index=Some(i);}
        if expected_shape.is_none() {expected_shape=Some(shape(state,cfg));}
        let rank=solver::evaluator::evaluate7(&[a,b,deal[4],deal[5],deal[6],deal[7],deal[8]]);
        let outcome=if hero_rank<rank {0}else if hero_rank==rank {1}else{2};counts[outcome]+=1;
        let before=nodes.len();let root=tree(game,&deal,&target,state,history,outcome,queries,&mut nodes);
        assert_eq!(nodes.len()-before,expected_shape.unwrap());assert_eq!(nodes[root]["query_index"],json!(i));
        pairs.push(json!({"cards":[a,b],"path":path,"outcome_loss_tie_win":outcome,"root":root,"node_start":before}));
    }}
    assert_eq!(pairs.len(),990);assert_eq!(nodes.len(),990*expected_shape.unwrap());
    *total_nodes+=nodes.len();assert!(*total_nodes<=MAX_NODES,"total batch node budget exceeded");
    json!({"format":1,
        "target":{"hi":target.key().0.to_string(),"lo":target.key().1.to_string(),"actor":target.actor,
            "cards":target.cards,"phase":3,"n":n,"query_index":target_index.unwrap(),"branch":target.public_id},
        "geometry":{"rake_fraction":cfg.rake_pct,"rake_cap":cfg.rake_cap,
            "branch_offset":game.offsets[target.public_id*2+target.actor],"starting_pot":cfg.starting_pot,
            "effective_stack":cfg.effective_stack,"nodes_per_pair":expected_shape.unwrap()},
        "pairs":pairs,"nodes":nodes,"counts_loss_tie_win":counts,
        "scope":"Complete river continuation for one visible state, all opponent pairs. No policy, training, or self-play change."})
}

fn export(context_source:&str,request_source:&str)->Value {
    let batch:BatchRequest=serde_json::from_str(request_source).unwrap();assert_eq!(batch.format,1);
    assert!(!batch.targets.is_empty()&&batch.targets.len()<=32,"one to 32 targets required");
    let game=Game::new(&serde_json::from_str(context_source).unwrap());
    let mut queries=Queries::default();let mut targets=Vec::new();let mut seen=std::collections::BTreeSet::new();let mut nodes=0;
    for input in &batch.targets {
        let key=(input.hi.parse().unwrap(),input.lo.parse().unwrap());let o=Observation::decode(key);
        assert_eq!(key,o.key(),"target must be canonical");assert!(seen.insert(key),"duplicate target");
        targets.push(target_export(&game,input,&mut queries,&mut nodes));
    }
    json!({"format":2,"context_source":context_source,"request_source":request_source,
        "targets":targets,"queries":queries.document(&game,context_source,request_source),
        "total_nodes":nodes,"scope":"Shared visible queries only; complete unchanged river values for every target."})
}

fn bounded_read(path:&str,limit:u64)->Result<String,Box<dyn std::error::Error>> {
    let mut text=String::new();std::fs::File::open(path)?.take(limit+1).read_to_string(&mut text)?;
    if text.len()as u64>limit {return Err("Input file budget exceeded".into());}Ok(text)
}

fn main()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();
    if args.len()!=3 {return Err("Expected CONTEXT REQUEST OUTPUT".into());}
    let context=bounded_read(&args[0],16*1024*1024)?;let request=bounded_read(&args[1],64*1024)?;
    let result=export(&context,&request);let mut bytes=serde_json::to_vec(&result)?;
    bytes.push(b'\n');if bytes.len()>MAX_BYTES {return Err("Output byte budget exceeded".into());}
    let mut file=OpenOptions::new().write(true).create_new(true).open(&args[2])?;
    file.write_all(&bytes)?;file.sync_all()?;
    println!("{}",json!({"passed":true,"opponent_pairs":990,"nodes":result["total_nodes"],
        "observations":result["queries"]["observations"].as_array().unwrap().len(),"bytes":bytes.len()}));Ok(())
}

