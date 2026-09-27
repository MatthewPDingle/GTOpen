//! Fixed-policy postflop-only contributions for physical private-first deals.
#[allow(dead_code)]
#[path="research_sampled/state.rs"] mod state;
#[allow(dead_code)]
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[allow(dead_code)]
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[allow(dead_code)]
#[path="research_sampled/batch_queries_v1.rs"] mod batch_queries_v1;
#[allow(dead_code)]
#[path="research_sampled/policy_bank_v1.rs"] mod policy_bank_v1;
use poker_reference_v1::{Game,Key,key};
use batch_queries_v1::Queries;
use state::State;
use serde_json::{Value,json};

fn post(g:&Game,d:&[u8;9],b:usize,s:State,h:u64,w:i32,p:&impl Fn(Key,usize)->[f64;4])->f64 {
    let cfg=&g.configs[b];
    if s.kind==1{return post(g,d,b,s.deal(),(h<<3)|5,w,p);}
    if s.kind>=2 {
        let v=s.payouts(cfg);
        return g.offsets[b*2]+if s.kind==2{if s.player==0{v[1]}else{v[0]}}
            else if w<0{v[2]}else if w==0{v[0]}else{v[1]};
    }
    let actions=s.actions(cfg);let row=p(key(d,s.player as usize,None,b,s.street as usize,h),actions.len());
    actions.into_iter().enumerate().map(|(a,act)|row[a]*post(g,d,b,s.act(cfg,act),(h<<3)|(a as u64+1),w,p)).sum()
}
fn pre(g:&Game,d:&[u8;9],node:usize,w:i32,p:&impl Fn(Key,usize)->[f64;4])->f64 {
    match g.kinds[node] {
        1|3=>0.,
        2=>post(g,d,node,State::root(&g.configs[node]),1,w,p),
        0=>{let n=g.arities[node] as usize;let row=p(key(d,g.actors[node]as usize,Some(node),0,0,0),n);
            (0..n).map(|a|row[a]*pre(g,d,g.children[node*4+a]as usize,w,p)).sum()},
        _=>panic!("unexpected preflop node")
    }
}
fn main()->Result<(),Box<dyn std::error::Error>> {
    let a:Vec<_>=std::env::args().skip(1).collect();assert!(a.len()==4||a.len()==5);
    let cs=std::fs::read_to_string(&a[1])?;let bs=std::fs::read_to_string(&a[2])?;
    let c:Value=serde_json::from_str(&cs)?;let batch:Value=serde_json::from_str(&bs)?;
    assert_eq!(batch["format"],"variable-continuation-pairs-v1");
    let deals:Vec<[u8;9]>=serde_json::from_value(batch["deals"].clone())?;
    assert!(!deals.is_empty()&&deals.len()<=256);
    let g=Game::new(&c);let q=Queries::build(&g,&deals,1_000_000)?;
    let out=a.last().unwrap();assert!(!std::path::Path::new(out).exists());
    if a[0]=="queries" {
        assert_eq!(a.len(),4);
        let index:std::collections::BTreeMap<_,_>=q.observations.iter().enumerate().map(|(i,o)|(o.key(),i)).collect();
        let rows:Vec<_>=q.observations.iter().enumerate().map(|(i,o)|{
            let k=o.key();let own:Vec<_>=policy_bank_v1::own_history(&g,k).into_iter()
                .map(|(prior,action,n)|json!([index[&prior],action,n])).collect();
            json!({"hi":k.0.to_string(),"lo":k.1.to_string(),"actor":o.actor,"phase":o.phase,"n":q.arities[i],
                "own_history":own,"active_features":o.features().iter().enumerate().filter(|(_,v)|**v!=0.).map(|(i,_)|i).collect::<Vec<_>>()})
        }).collect();
        std::fs::write(out,serde_json::to_vec(&json!({"format":"variable-continuation-queries-v1",
            "context_source":cs,"batch_source":bs,"observations":rows}))?)?;
    } else {
        assert_eq!(a[0],"evaluate");assert_eq!(a.len(),5);
        let transport:Value=serde_json::from_slice(&std::fs::read(&a[3])?)?;
        assert_eq!(transport["format"],"variable-continuation-policy-v1");
        assert_eq!(transport["context_source"].as_str(),Some(cs.as_str()));
        assert_eq!(transport["batch_source"].as_str(),Some(bs.as_str()));
        let rows=transport["policies"].as_array().unwrap();assert_eq!(rows.len(),q.observations.len());
        let mut policies=Vec::new();
        for (i,row) in rows.iter().enumerate() {
            let o=&q.observations[i];let k=o.key();let n=q.arities[i];
            assert_eq!(row["hi"],k.0.to_string());assert_eq!(row["lo"],k.1.to_string());
            let p:[f64;4]=serde_json::from_value(row["probabilities"].clone())?;
            assert!(p.iter().all(|v|v.is_finite()&&*v>=0.)&&p[n..].iter().all(|v|*v==0.)&&(p[..n].iter().sum::<f64>()-1.).abs()<1e-12);
            policies.push(p);
        }
        let policy=|k:Key,n:usize|{let i=q.lookup(k).unwrap();assert_eq!(n,q.arities[i]);policies[i]};
        let rows:Vec<_>=deals.iter().enumerate().map(|(i,d)|{
            let ranks:[u32;2]=std::array::from_fn(|p|solver::evaluator::evaluate7(&[d[p*2],d[p*2+1],d[4],d[5],d[6],d[7],d[8]]));
            let w=if ranks[0]==ranks[1]{-1}else{(ranks[1]>ranks[0])as i32};
            let values=[0.,pre(&g,d,g.children[1]as usize,w,&policy),pre(&g,d,g.children[2]as usize,w,&policy),0.];
            json!({"deal_index":i,"variable_action_values":values})
        }).collect();
        std::fs::write(out,serde_json::to_vec(&json!({"format":"variable-continuation-values-v1","rows":rows}))?)?;
    }Ok(())
}
