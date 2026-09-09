use solver::preflop::{contextual::{self, Entry}, BucketPolicy, PreflopConfig, PreflopSolver, ProfileResponse, SeatProfile};
use solver::preflop::equity::EquityTable;
use std::sync::{Arc, OnceLock};

fn cfg() -> PreflopConfig {
    serde_json::from_value(serde_json::json!({"positions":["BTN","SB","BB"],"stack":100,"posts":[0,0.5,1],"limp":true,"open_raises":[2.5],"raise_mults":[3],"max_raises":3,"add_allin":false,"realization":"raw"})).unwrap()
}
fn table() -> Arc<EquityTable> {
    static TABLE: OnceLock<Arc<EquityTable>> = OnceLock::new();
    TABLE.get_or_init(||Arc::new(EquityTable::build(100))).clone()
}
fn profile(active: bool) -> SeatProfile {
    let p = BucketPolicy {call:vec![0.4;169],raise:vec![0.2;169],jam:vec![0.0;169],raise_size:"min".into(),raise_multiples: Vec::new(), raise_sizes:vec![]};
    SeatProfile {name:"fixture".into(),buckets:vec![Some(p.clone());5],vs_raise_bands:None,postflop:None,limp_defense:None,
        response:Some(ProfileResponse{cold_reraise:Some(p),contextual_reraise:active.then(||contextual::MODEL_ID.into()),..Default::default()})}
}
fn solver(active: bool) -> PreflopSolver {
    let mut s=PreflopSolver::new(cfg(),table()).unwrap();
    s.set_table(vec![false;3],vec![Some(profile(active));3]).unwrap();s
}
fn path(s: &PreflopSolver, kinds: &[&str]) -> (usize,Vec<usize>) {
    let mut node=0;let mut path=Vec::new();
    for kind in kinds {
        let action=s.nodes[node].actions.iter().position(|a|a.kind==*kind).unwrap();
        path.push(action);node=s.child(node,action);
    }
    (node,path)
}

#[test]
fn contextual_runtime_tracks_real_entry_and_depth_matches_preview() {
    let s=solver(true);
    for (kinds,entry,raises) in [
        (vec!["raise","raise"],Entry::Cold,2),
        (vec!["raise","raise","fold"],Entry::Raised,2),
        (vec!["call","raise","raise"],Entry::Called,2),
        (vec!["raise","raise","fold","raise"],Entry::Raised,3),
    ] {
        let (node,p)=path(&s,&kinds);let nd=&s.nodes[node];
        let input=s.contextual_input(node).unwrap();assert_eq!(input.entry,entry);assert_eq!(input.raises,raises);
        let predicted=contextual::predict(contextual::MODEL_ID,&s.cfg,nd.actor as usize,&input).unwrap().policy.unwrap();
        let sigma=s.average_strategy(node);
        let call=nd.actions.iter().position(|a|a.kind=="call").unwrap();
        let has_raise=nd.actions.iter().any(|a|a.kind=="raise");
        for h in 0..169 {
            let expected=predicted.call[h]+if has_raise {0.0}else{predicted.raise[h]};
            assert!((sigma[call*169+h]-expected).abs()<1e-6);
            assert!(((0..nd.actions.len()).map(|a|sigma[a*169+h]).sum::<f32>()-1.0).abs()<1e-6);
        }
        let status=s.node_view(&p).unwrap().contextual_prediction.unwrap();assert!(status.active);assert_eq!(status.context.entry,entry);
    }
    let entries=s.contextual_cache_entries();assert!(entries>0);
    for node in 0..s.nodes.len() {if s.nodes[node].kind==0 {s.average_strategy(node);}}
    let warmed=s.contextual_cache_entries();assert!(warmed>=entries);
    for node in 0..s.nodes.len() {if s.nodes[node].kind==0 {s.average_strategy(node);}}
    assert_eq!(s.contextual_cache_entries(),warmed);
}

#[test]
fn contextual_old_profiles_and_outside_support_keep_exact_probabilities() {
    let legacy=solver(false);assert_eq!(legacy.contextual_cache_entries(),0);
    let p=profile(false);let json=serde_json::to_string(&p).unwrap();assert!(!json.contains("contextual_reraise"));
    let (node,_)=path(&legacy,&["raise","raise"]);let expected=legacy.average_strategy(node);
    for (players,sb) in [(3,1.0),(8,0.5)] {
        let mut config=cfg();config.positions=(0..players).map(|s|s.to_string()).collect();
        config.posts=vec![0.0;players];config.posts[players-2]=sb;config.posts[players-1]=1.0;
        // Keep the large-table guard test tiny while retaining bucket-4 nodes.
        config.limp=false;config.max_raises=2;
        let mut s=PreflopSolver::new(config,table()).unwrap();
        s.set_table(vec![false;players],vec![Some(profile(true));players]).unwrap();
        let (node,path)=path(&s,&["raise","raise"]);
        let status=s.node_view(&path).unwrap().contextual_prediction.unwrap();assert!(!status.active);assert!(status.note.contains("inactive"));
        let contextual=s.average_strategy(node);
        s.set_table(vec![false;players],vec![Some(profile(false));players]).unwrap();
        assert_eq!(contextual,s.average_strategy(node));assert_eq!(s.contextual_cache_entries(),0);
    }
    assert!(!expected.is_empty());
}

#[test]
fn contextual_adaptation_locks_and_hero_take_precedence() {
    let mut s=solver(true);let (node,p)=path(&s,&["raise","raise","fold"]);
    s.seat_profiles[0].as_mut().unwrap().response.as_mut().unwrap().adaptive_from=Some(0.05);
    assert!(!s.contextual_status(node).unwrap().active);
    assert!(s.contextual_status(node).unwrap().note.contains("Adaptive"));
    s.seat_profiles[0].as_mut().unwrap().response.as_mut().unwrap().adaptive_from=None;
    s.lock_point(&p,None).unwrap();assert!(s.contextual_status(node).unwrap().note.contains("Point lock"));
    s.unlock_point(&p).unwrap();
    s.set_hero(Some(0)).unwrap();assert!(s.contextual_status(node).unwrap().note.contains("Hero mode"));
}

#[test]
fn contextual_save_rebuild_preserves_history_and_version() {
    let s=solver(true);let (_,p)=path(&s,&["call","raise","raise"]);
    let file=std::env::temp_dir().join(format!("gtopen-contextual-{}.bin",std::process::id()));
    s.save_game(file.to_str().unwrap()).unwrap();
    let restored=PreflopSolver::load_game(file.to_str().unwrap(),table()).unwrap();
    std::fs::remove_file(file).unwrap();
    assert_eq!(serde_json::to_value(s.node_view(&p).unwrap()).unwrap(),serde_json::to_value(restored.node_view(&p).unwrap()).unwrap());
    assert_eq!(restored.seat_profiles[0].as_ref().unwrap().response.as_ref().unwrap().contextual_reraise.as_deref(),Some(contextual::MODEL_ID));
}

#[test]
fn contextual_version_is_validated_before_table_mutation() {
    let mut s=solver(false);let mut p=profile(true);
    p.response.as_mut().unwrap().contextual_reraise=Some("nonexistent".into());
    assert!(s.set_table(vec![false;3],vec![Some(p);3]).unwrap_err().contains("unknown contextual"));
    assert!(s.seat_profiles[0].as_ref().unwrap().response.as_ref().unwrap().contextual_reraise.is_none());
}
