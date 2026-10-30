//! Visible-history queries for exact conditional river Fold/Call references.
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
use solver::tree::{Action, KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN};
use std::{collections::BTreeMap, fs::OpenOptions, io::{Read, Write}};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request { format:u32, hi:String, lo:String }

#[derive(Default)]
struct Queries {
    observations:Vec<Observation>, arities:Vec<usize>, ids:BTreeMap<Key,usize>,
}
impl Queries {
    fn add(&mut self, game:&Game, raw:Key, n:usize)->usize {
        let o=Observation::decode(raw); assert_eq!(o.legal_actions(game),n);
        let canonical=o.key();
        if let Some(&i)=self.ids.get(&canonical) { assert_eq!(self.arities[i],n); return i; }
        assert!(self.observations.len()<25_000,"query budget exceeded");
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

fn export(context_source:&str,request_source:&str)->Value {
    let input:Request=serde_json::from_str(request_source).unwrap(); assert_eq!(input.format,1);
    let target=Observation::decode((input.hi.parse().unwrap(),input.lo.parse().unwrap()));
    let context:Value=serde_json::from_str(context_source).unwrap(); let game=Game::new(&context);
    assert_eq!(target.phase,3); let n=target.legal_actions(&game); assert!(n>=2);
    let pre=parents(&game,target.public_id); let cfg=&game.configs[target.public_id];
    let mut mask=0u64;
    for &c in &target.cards { assert!(c<52 && mask&(1u64<<c)==0); mask|=1u64<<c; }
    let hero_rank=solver::evaluator::evaluate7(&target.cards);
    let mut queries=Queries::default(); let mut pairs=Vec::new(); let mut target_index=None; let mut geometry=None;
    let mut counts=[0usize;3];
    for a in 0u8..52 { for b in a+1..52 {
        if mask&((1u64<<a)|(1u64<<b))!=0 {continue;}
        let mut deal=[0u8;9]; let opponent=1-target.actor;
        deal[target.actor*2..target.actor*2+2].copy_from_slice(&target.cards[..2]);
        deal[opponent*2..opponent*2+2].copy_from_slice(&[a,b]);
        // Preserve the observed flop, turn and river order for earlier queries.
        deal[4..].copy_from_slice(&target.cards[2..]);
        let (path,i,state)=trace(&game,&deal,&target,&pre,&mut queries);
        if let Some(old)=target_index { assert_eq!(old,i); } else { target_index=Some(i); }
        let actions=state.actions(cfg); assert_eq!(actions.len(),n);
        assert!(matches!(actions[0],Action::Fold) && matches!(actions[1],Action::Call(_)));
        let fold=state.act(cfg,actions[0]); let call=state.act(cfg,actions[1]);
        assert_eq!(fold.kind,KIND_TERM_FOLD); assert_eq!(call.kind,KIND_TERM_SHOWDOWN);
        let pot=state.put.iter().sum::<f64>(); let cost=call.put[target.actor]-state.put[target.actor];
        let gross=cfg.rake_pct*(pot+cost); let rake=if cfg.rake_cap>0. {gross.min(cfg.rake_cap)}else{gross};
        let payout=call.payouts(cfg); let folded=fold.payouts(cfg)[1];
        let endpoints=[payout[1]-folded,payout[2]-folded,payout[0]-folded];
        for (actual,want) in endpoints.iter().zip([-cost,(pot+cost-rake)/2.-cost,pot-rake]) { assert!((*actual-want).abs()<1e-9); }
        let g=json!({"pot":pot,"amount_to_call":cost,"rake":rake,"legal_actions":n,
            "endpoints_loss_tie_win":endpoints,"fold_value_without_branch_offset":folded,"call_ends_showdown":true});
        if let Some(old)=&geometry {assert_eq!(old,&g);} else {geometry=Some(g);}
        let rank=solver::evaluator::evaluate7(&[a,b,deal[4],deal[5],deal[6],deal[7],deal[8]]);
        let outcome=if hero_rank<rank {0}else if hero_rank==rank {1}else{2}; counts[outcome]+=1;
        pairs.push(json!({"cards":[a,b],"path":path,"outcome_loss_tie_win":outcome}));
    }}
    assert_eq!(pairs.len(),990); assert_eq!(counts.iter().sum::<usize>(),990);
    json!({"format":1,"context_source":context_source,"request_source":request_source,
        "target":{"hi":target.key().0.to_string(),"lo":target.key().1.to_string(),"actor":target.actor,
            "cards":target.cards,"phase":3,"n":n,"query_index":target_index.unwrap()},
        "geometry":geometry.unwrap(),"pairs":pairs,"counts_loss_tie_win":counts,
        "queries":queries.document(&game,context_source,request_source),
        "scope":"One fixed visible river decision; all legal opponent pairs; labels never enter visible features."})
}

fn bounded_read(path:&str,limit:u64)->Result<String,Box<dyn std::error::Error>> {
    let mut text=String::new(); std::fs::File::open(path)?.take(limit+1).read_to_string(&mut text)?;
    if text.len()as u64>limit {return Err("Input file budget exceeded".into());} Ok(text)
}
fn main()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();
    if args.len()!=3 {return Err("Expected CONTEXT REQUEST OUTPUT".into());}
    let context=bounded_read(&args[0],16*1024*1024)?; let request=bounded_read(&args[1],1024)?;
    let result=export(&context,&request);
    let mut file=OpenOptions::new().write(true).create_new(true).open(&args[2])?;
    serde_json::to_writer(&mut file,&result)?; file.write_all(b"\n")?; file.sync_all()?;
    println!("{}",json!({"passed":true,"opponent_pairs":990,
        "observations":result["queries"]["observations"].as_array().unwrap().len()})); Ok(())
}
