//! Legal projection of observed ordinary raise sizes, independent of hand policy.
use solver::preflop::{BucketPolicy, PreflopConfig, PreflopSolver, SeatProfile, NUM_BUCKETS};
use solver::preflop::equity::EquityTable;
use std::sync::{Arc,OnceLock};

fn cfg(sb:f64)->PreflopConfig {
    serde_json::from_value(serde_json::json!({"positions":["CO","BTN","SB","BB"],
        "posts":[0,0,sb,1],"stack":100,"ante":0.1,"limp":true,"open_raises":[2.5],
        "raise_mults":[3,5],"max_raises":2,"add_allin":true,"realization":"raw"})).unwrap()
}
fn table()->Arc<EquityTable> {
    static TABLE:OnceLock<Arc<EquityTable>>=OnceLock::new();
    TABLE.get_or_init(||Arc::new(EquityTable::build(100))).clone()
}
fn policy()->BucketPolicy {
    serde_json::from_value(serde_json::json!({"call":vec![0.2;169],"raise":vec![0.6;169],
        "jam":vec![0.1;169],"raise_size":"min"})).unwrap()
}
fn install(s:&mut PreflopSolver,seat:usize,policy:BucketPolicy) {
    let mut profiles=vec![None;s.cfg.posts.len()];
    profiles[seat]=Some(SeatProfile{name:"sizing fixture".into(),buckets:vec![Some(policy);NUM_BUCKETS],
        vs_raise_bands:None,limp_defense:None,postflop:None,response:None});
    s.set_table(vec![false;profiles.len()],profiles).unwrap();
}
fn node(s:&PreflopSolver,path:&[&str])->usize {
    let mut n=0;
    for kind in path {
        let i=s.nodes[n].actions.iter().position(|a|a.kind==*kind).unwrap();
        n=s.child(n,i);
    }
    n
}
fn check(s:&PreflopSolver,n:usize,expected:&[(&str,f64,f32)]) {
    let strategy=s.average_strategy(n);
    for (a,action) in s.nodes[n].actions.iter().enumerate() {
        let p=expected.iter().find(|(kind,to,_)|*kind==action.kind && (*to-action.to).abs()<1e-9).map(|x|x.2).unwrap_or(0.0);
        for h in 0..169 {assert!((strategy[a*169+h]-p).abs()<1e-6,"{} to {}: {} != {p}",action.kind,action.to,strategy[a*169+h]);}
    }
    for h in 0..169 {assert!(((0..s.nodes[n].actions.len()).map(|a|strategy[a*169+h]).sum::<f32>()-1.0).abs()<1e-6);}
}

#[test]
fn iso_3bet_and_squeeze_use_correct_units_with_blinds_and_dead_antes() {
    for sb in [0.5,1.0] {
        let mut c=cfg(sb);c.open_raises=vec![2.0,6.0,10.0];
        let mut s=PreflopSolver::new(c,table()).unwrap();let mut p=policy();
        p.raise_sizes=vec![(6.0,3.0),(10.0,1.0)];install(&mut s,1,p);
        check(&s,node(&s,&["call"]),&[("fold",0.0,0.1),("call",1.0,0.2),("raise",6.0,0.45),("raise",10.0,0.15),("jam",100.0,0.1)]);
        for (seat,path) in [(1,vec!["raise"]),(2,vec!["raise","call"])] {
            let mut s=PreflopSolver::new(cfg(sb),table()).unwrap();let mut p=policy();
            p.raise_multiples=vec![(3.0,3.0),(5.0,1.0)];install(&mut s,seat,p);
            check(&s,node(&s,&path),&[("fold",0.0,0.1),("call",2.5,0.2),("raise",7.5,0.45),("raise",12.5,0.15),("jam",100.0,0.1)]);
        }
    }
}

#[test]
fn projection_respects_minraise_seat_menu_allin_threshold_and_extreme_targets() {
    let mut c=cfg(0.5);c.raise_mults_by_seat=Some(vec![vec![],vec![1.1,3.0,40.0],vec![],vec![]]);
    let mut s=PreflopSolver::new(c,table()).unwrap();let mut p=policy();
    p.raise_multiples=vec![(1.1,1.0),(40.0,1.0)];install(&mut s,1,p);
    // 1.1x is below the legal minimum. 40x converts to an all-in menu item;
    // the observed ordinary size still maps to the largest ordinary raise.
    check(&s,node(&s,&["raise"]),&[("fold",0.0,0.1),("call",2.5,0.2),("raise",4.0,0.3),("raise",7.5,0.3),("jam",100.0,0.1)]);
    let mut p=policy();p.raise_multiples=vec![(f64::MAX,1.0)];install(&mut s,1,p);
    check(&s,node(&s,&["raise"]),&[("fold",0.0,0.1),("call",2.5,0.2),("raise",7.5,0.6),("jam",100.0,0.1)]);
    let mut c=cfg(0.5);c.open_raises=vec![100.0];
    let mut s=PreflopSolver::new(c,table()).unwrap();let mut p=policy();p.raise_sizes=vec![(5.0,1.0)];install(&mut s,0,p);
    check(&s,0,&[("fold",0.0,0.1),("call",1.0,0.2),("jam",100.0,0.7)]);
    let mut c=cfg(0.5);c.max_raises=1;
    let mut s=PreflopSolver::new(c,table()).unwrap();let mut p=policy();p.raise_multiples=vec![(3.0,1.0)];install(&mut s,1,p);
    check(&s,node(&s,&["raise"]),&[("fold",0.0,0.1),("call",2.5,0.9)]);
}

#[test]
fn ties_go_smaller_and_legacy_empty_distributions_keep_min_max() {
    let mut c=cfg(0.5);c.open_raises=vec![2.0,8.0];
    let mut s=PreflopSolver::new(c,table()).unwrap();let mut p=policy();p.raise_sizes=vec![(4.0,1.0)];install(&mut s,0,p);
    check(&s,0,&[("fold",0.0,0.1),("call",1.0,0.2),("raise",2.0,0.6),("jam",100.0,0.1)]);
    for (rule,to) in [("min",2.0),("max",8.0)] {
        let mut p=policy();p.raise_size=rule.into();install(&mut s,0,p);
        check(&s,0,&[("fold",0.0,0.1),("call",1.0,0.2),("raise",to,0.6),("jam",100.0,0.1)]);
    }
}

#[test]
fn legacy_serialization_and_invalid_distributions_are_safe() {
    let p=policy();assert!(p.raise_multiples.is_empty());
    let serialized=serde_json::to_value(&p).unwrap();assert!(serialized.get("raise_multiples").is_none());
    let mut s=PreflopSolver::new(cfg(0.5),table()).unwrap();
    for (absolute,multiples) in [(vec![(6.0,1.0)],vec![(3.0,1.0)]),(vec![],vec![(0.0,1.0)]),
        (vec![],vec![(3.0,-1.0)]),(vec![],vec![(3.0,f64::INFINITY)]),
        (vec![],vec![(3.0,f64::MAX),(4.0,f64::MAX)])] {
        let mut p=policy();p.raise_sizes=absolute;p.raise_multiples=multiples;
        let profile=SeatProfile{name:"invalid".into(),buckets:vec![Some(p.clone());NUM_BUCKETS],
            vs_raise_bands:None,limp_defense:None,postflop:None,response:None};
        assert!(s.set_table(vec![false;4],vec![Some(profile),None,None,None]).is_err());
        assert!(s.lock_point(&[],Some(p)).is_err());
    }
    let mut p=policy();p.raise_multiples=vec![(3.0,2.0),(5.0,1.0)];
    let restored:BucketPolicy=serde_json::from_str(&serde_json::to_string(&p).unwrap()).unwrap();
    assert_eq!(restored.raise_multiples,p.raise_multiples);assert!(restored.raise_sizes.is_empty());
    // Historical binaries ignore unknown fields. They must retain min/max,
    // never read a three-times sample as an absolute three-big-blind raise.
    #[derive(serde::Deserialize)]
    struct LegacySizing { #[serde(default)] raise_sizes:Vec<(f64,f64)>, raise_size:String }
    let old:LegacySizing=serde_json::from_str(&serde_json::to_string(&p).unwrap()).unwrap();
    assert!(old.raise_sizes.is_empty());assert_eq!(old.raise_size,"min");
}
