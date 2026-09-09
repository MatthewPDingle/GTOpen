use solver::preflop::{contextual::{self,ContextualInput,Entry}, evidence::{self,EvidenceContext,LimpEvidenceContext},
    BucketPolicy,PreflopConfig,PreflopSolver,ProfileResponse,SeatProfile};
use solver::preflop::equity::EquityTable;
use std::sync::{Arc,OnceLock};

fn cfg(n:usize,sb:f64)->PreflopConfig {
    let mut posts=vec![0.0;n];posts[n-2]=sb;posts[n-1]=1.0;
    serde_json::from_value(serde_json::json!({"positions":(0..n).map(|s|s.to_string()).collect::<Vec<_>>(),
        "stack":100,"posts":posts,"limp":true,"open_raises":[2.5],"raise_mults":[3],"max_raises":3,"add_allin":false,"realization":"raw"})).unwrap()
}
fn policy(call:f32)->BucketPolicy {
    BucketPolicy{call:vec![call;169],raise:vec![0.3;169],jam:vec![0.0;169],raise_size:"min".into(),raise_multiples: Vec::new(), raise_sizes:vec![(2.5,2.0),(3.0,1.0)]}
}
fn profile()->SeatProfile {
    let p=policy(0.2);let defense=policy(0.4);
    let rows=vec![(3,0),(3,-1),(3,-2),(8,5)].into_iter().map(|(players,role)|serde_json::json!({
        "players":players,"role":role,"open_raise":30,"open_limp":20,"iso_raise":30,"limp_behind":20,
        "opening":p,"responses":{"raise":0,"squeeze":0,"reraise":0,"cold_reraise":0,
        "limps_paid_1":0,"limps_free_1":0,"limp_defense":1,"raise_3.5":1}})).collect::<Vec<_>>();
    let stats=serde_json::from_value(serde_json::json!({"vpip":50,"pfr":30,"threebet":8,"fold_to_3bet":50,"squeeze":4,
        "dataset":{"site":"Fixture","min_players":3,"max_players":6,"ante":false,"small_blind_bb":0.5,
        "empirical_opening":true,"scope":"Synthetic test metadata.","rows":rows,"response_policies":[p,defense],
        "response_notes":{"reraise":"Direct coverage: 999,999 decisions. Deliberately unstructured prose."}}})).unwrap();
    SeatProfile{name:"fixture".into(),buckets:vec![Some(p.clone());5],vs_raise_bands:Some(vec![(3.5,defense.clone()),(999.0,p.clone())]),
        postflop:None,limp_defense:Some(defense.clone()),response:Some(ProfileResponse{
            source_stats:Some(stats),cold_reraise:Some(p.clone()),limp_unopened:Some(defense),
            limp_contexts:vec![solver::preflop::LimpContextPolicy{limpers:1,free_check:false,policy:p}],..Default::default()})}
}
fn input()->ContextualInput {ContextualInput{entry:Entry::Cold,raises:2,pot:11.0,invested:1.0,to_call:7.5}}
fn table()->Arc<EquityTable> {
    static T:OnceLock<Arc<EquityTable>>=OnceLock::new();T.get_or_init(||Arc::new(EquityTable::build(100))).clone()
}
fn path(s:&PreflopSolver,kinds:&[&str])->(usize,Vec<usize>) {
    let(mut node,mut path)=(0,vec![]);
    for kind in kinds {let a=s.nodes[node].actions.iter().position(|a|a.kind==*kind).unwrap();path.push(a);node=s.child(node,a);}
    (node,path)
}

#[test]
fn measured_requires_matching_hand_probabilities_not_just_source_stats() {
    let config=cfg(3,0.5);let mut p=profile();let q=EvidenceContext::default();
    let before=serde_json::to_value(&p).unwrap();
    assert_eq!(evidence::profile_evidence(&config,0,&p,&q).unwrap().kind,"measured");
    assert_eq!(serde_json::to_value(&p).unwrap(),before);
    // A different legal size route does not fabricate different hand evidence.
    let b=p.buckets[0].as_mut().unwrap();b.raise_sizes=vec![(2.5,20.0),(3.0,10.0)];b.raise_size="max".into();
    assert_eq!(evidence::profile_evidence(&config,0,&p,&q).unwrap().kind,"measured");
    p.buckets[0].as_mut().unwrap().call[0]=0.21;
    assert_eq!(evidence::profile_evidence(&config,0,&p,&q).unwrap().kind,"saved_policy");
    let q=EvidenceContext{bucket:4,..Default::default()};
    let e=evidence::profile_evidence(&config,0,&p,&q).unwrap();
    assert_eq!(e.kind,"measured");assert!(e.sample_count.is_none(),"Never turn prose into numeric evidence");
}

#[test]
fn format_transfer_is_explicit_and_legacy_profiles_are_conservative() {
    let p=profile();
    for c in [cfg(8,0.5),cfg(3,1.0),{let mut c=cfg(3,0.5);c.ante=0.1;c}] {
        let e=evidence::profile_evidence(&c,0,&p,&EvidenceContext::default()).unwrap();
        assert_eq!(e.kind,"extrapolated");assert!(e.summary.contains("unvalidated"));
    }
    let mut p=profile();p.response.as_mut().unwrap().source_stats.as_mut().unwrap().dataset=None;
    assert_eq!(evidence::profile_evidence(&cfg(3,0.5),0,&p,&EvidenceContext::default()).unwrap().kind,"saved_policy");
    assert_eq!(evidence::generated_evidence(&cfg(3,0.5),0,&p)["unopened"].kind,"stat_derived");
    p.response=None;
    assert_eq!(evidence::profile_evidence(&cfg(3,0.5),0,&p,&EvidenceContext::default()).unwrap().kind,"saved_policy");
    let serialized=serde_json::to_string(&p).unwrap();
    assert!(!serialized.contains("model_evidence"));
    let old:SeatProfile=serde_json::from_str(&serialized).unwrap();
    assert_eq!(evidence::profile_evidence(&cfg(3,0.5),0,&old,&EvidenceContext::default()).unwrap().kind,"saved_policy");
}

#[test]
fn contextual_counts_are_pooled_and_overrides_do_not_claim_measured_evidence() {
    let mut p=profile();p.response.as_mut().unwrap().contextual_reraise=Some(contextual::MODEL_ID.into());
    let q=EvidenceContext{bucket:4,cold:true,context:Some(input()),..Default::default()};
    let e=evidence::profile_evidence(&cfg(3,0.5),2,&p,&q).unwrap();
    assert_eq!(e.kind,"contextual_estimate");assert!(e.sample_count.unwrap()>0);
    assert!(e.details.iter().any(|d|d.contains("Counts pool prices")));
    p.response.as_mut().unwrap().adaptive_from=Some(0.05);
    let e=evidence::profile_evidence(&cfg(3,0.5),2,&p,&q).unwrap();
    assert_eq!(e.kind,"adaptive");assert!(e.summary.contains("preview"));assert!(e.sample_count.is_none());
    p.response.as_mut().unwrap().contextual_reraise=None;
    assert_eq!(evidence::profile_evidence(&cfg(3,0.5),2,&p,&q).unwrap().kind,"adaptive");
    p.response.as_mut().unwrap().contextual_reraise=Some(contextual::MODEL_ID.into());
    p.response.as_mut().unwrap().adaptive_from=None;
    let mut q=q;q.context.as_mut().unwrap().invested=1.0;
    let e=evidence::profile_evidence(&cfg(3,1.0),2,&p,&q).unwrap();
    assert_eq!(e.kind,"fallback");assert!(e.details.iter().any(|d|d.contains("inactive")));
    assert!(e.sample_count.is_none(),"Unsupported formats are not zero-coverage contexts");
}

#[test]
fn absent_supported_context_reports_zero_observed_coverage_not_zero_probability() {
    let mut p=profile();p.response.as_mut().unwrap().contextual_reraise=Some(contextual::MODEL_ID.into());
    // Three-handed BTN has no recorded cold re-raise decisions. This is a
    // hypothetical preview; an actual BTN continuation has already entered.
    let q=EvidenceContext{bucket:4,context:Some(ContextualInput{invested:0.0,..input()}),..Default::default()};
    let e=evidence::profile_evidence(&cfg(3,0.5),0,&p,&q).unwrap();
    assert_eq!(e.kind,"contextual_estimate");
    assert_eq!((e.sample_count,e.session_count,e.observed_classes),(Some(0),Some(0),Some(0)));
    assert!(e.summary.contains("borrows other contexts"));
    assert!(e.details.iter().any(|d|d.contains("not zero probability")));
}

#[test]
fn node_metadata_follows_limp_band_defense_contextual_and_point_lock_precedence() {
    let mut s=PreflopSolver::new(cfg(3,0.5),table()).unwrap();
    s.set_table(vec![false;3],vec![Some(profile());3]).unwrap();
    for (kinds,expected) in [(vec!["call"],"limps_paid_1"),(vec!["raise"],"raise_3.5"),(vec!["call","raise","call"],"limp_defense")] {
        let(node,p)=path(&s,&kinds);let sigma=s.average_strategy(node);
        let e=s.node_view(&p).unwrap().model_evidence.unwrap();
        assert_eq!(e.policy_key.as_deref(),Some(expected));assert_eq!(e.kind,"measured");
        assert_eq!(s.average_strategy(node),sigma);
    }
    for p in s.seat_profiles.iter_mut().flatten() {p.response.as_mut().unwrap().contextual_reraise=Some(contextual::MODEL_ID.into());}
    let(node,p)=path(&s,&["raise","raise"]);let before=s.average_strategy(node);let cache=s.contextual_cache_entries();
    assert_eq!(s.node_view(&p).unwrap().model_evidence.unwrap().kind,"contextual_estimate");
    assert_eq!(s.average_strategy(node),before);assert_eq!(s.contextual_cache_entries(),cache);
    s.lock_point(&p,None).unwrap();
    assert_eq!(s.node_view(&p).unwrap().model_evidence.unwrap().kind,"manual_lock");
    s.unlock_point(&p).unwrap();
    s.seat_profiles[2].as_mut().unwrap().response.as_mut().unwrap().adaptive_from=Some(0.05);
    assert_eq!(s.node_model_evidence(node,None).unwrap().kind,"adaptive");
    // Frozen solver strategy is not described as newly learned adaptation.
    s.seat_frozen[2]=true;
    assert_eq!(s.node_model_evidence(node,None).unwrap().kind,"frozen_solver");
    s.hero=Some(2);
    assert_eq!(s.node_model_evidence(node,None).unwrap().kind,"solver");
}

#[test]
fn unavailable_and_invalid_editor_requests_cannot_masquerade_as_solved_ranges() {
    let s=PreflopSolver::new(cfg(3,0.5),table()).unwrap();
    assert_eq!(s.node_view(&[]).unwrap().model_evidence.unwrap().kind,"unavailable");
    assert_eq!(evidence::profile_evidence(&cfg(3,0.5),2,&profile(),&EvidenceContext::default()).unwrap().kind,"unavailable");
    assert!(evidence::profile_evidence(&cfg(3,0.5),3,&profile(),&EvidenceContext::default()).is_err());
    assert!(evidence::profile_evidence(&cfg(3,0.5),0,&profile(),&EvidenceContext{bucket:1,limp_context:Some(LimpEvidenceContext{limpers:0,free_check:false}),..Default::default()}).is_err());
    let q=EvidenceContext{bucket:0,context:Some(input()),..Default::default()};
    assert!(evidence::profile_evidence(&cfg(3,0.5),0,&profile(),&q).is_err());
}

#[test]
fn explicit_jam_conversion_is_an_assumption_and_not_measured_jamming() {
    let mut p=profile();p.response.as_mut().unwrap().source_stats.as_mut().unwrap().raise_size="jam".into();
    let b=p.buckets[0].as_mut().unwrap();
    for h in 0..169 {b.jam[h]+=b.raise[h];b.raise[h]=0.0;}
    let e=evidence::profile_evidence(&cfg(3,0.5),0,&p,&EvidenceContext::default()).unwrap();
    assert_eq!(e.kind,"fallback");assert!(e.summary.contains("jams"));
    assert!(e.details.iter().any(|d|d.contains("not a measured jam")));
    assert_eq!(e.sizing.unwrap().kind,"assumption");
}

#[test]
fn sizing_evidence_is_independent_of_hands_and_requires_matching_units_and_weights() {
    let config=cfg(3,0.5);let mut p=profile();let request=EvidenceContext::default();
    let e=evidence::profile_evidence(&config,0,&p,&request).unwrap();
    assert_eq!(e.kind,"measured");assert_eq!(e.sizing.as_ref().unwrap().kind,"measured");
    assert_eq!(e.sizing.unwrap().basis,"bb");
    // Weight scaling, repeated bins and order do not change the distribution.
    p.buckets[0].as_mut().unwrap().raise_sizes=vec![(3.0,10.0),(2.5,15.0),(2.5,5.0)];
    assert_eq!(evidence::profile_evidence(&config,0,&p,&request).unwrap().sizing.unwrap().kind,"measured");
    let b=p.buckets[0].as_mut().unwrap();b.raise_sizes.clear();b.raise_multiples=vec![(3.0,1.0),(5.0,2.0)];
    let e=evidence::profile_evidence(&config,0,&p,&request).unwrap();
    assert_eq!(e.kind,"measured");assert_eq!(e.sizing.as_ref().unwrap().kind,"stored_policy");assert_eq!(e.sizing.unwrap().basis,"previous");
    let original=p.response.as_mut().unwrap().source_stats.as_mut().unwrap().dataset.as_mut().unwrap().rows[0].opening.as_mut().unwrap();
    original.raise_sizes.clear();original.raise_multiples=vec![(3.0,1.0),(5.0,2.0)];
    p.buckets[0].as_mut().unwrap().call[0]=0.21;
    let e=evidence::profile_evidence(&config,0,&p,&request).unwrap();
    assert_eq!(e.kind,"saved_policy");assert_eq!(e.sizing.unwrap().kind,"measured");
    p.buckets[0].as_mut().unwrap().raise_multiples.clear();
    assert_eq!(evidence::profile_evidence(&config,0,&p,&request).unwrap().sizing.unwrap().kind,"fallback");
    let e=evidence::profile_evidence(&cfg(8,0.5),0,&profile(),&request).unwrap();
    assert_eq!(e.sizing.as_ref().unwrap().kind,"extrapolated");assert!(e.sizing.unwrap().summary.contains("unvalidated"));
}

#[test]
fn contextual_hand_prediction_reports_the_actual_stored_size_source() {
    let mut p=profile();p.response.as_mut().unwrap().contextual_reraise=Some(contextual::MODEL_ID.into());
    let request=EvidenceContext{bucket:4,cold:true,context:Some(input()),..Default::default()};
    let e=evidence::profile_evidence(&cfg(3,0.5),2,&p,&request).unwrap();
    assert_eq!(e.kind,"contextual_estimate");assert_eq!(e.sizing.as_ref().unwrap().kind,"measured");
    assert_eq!(e.sizing.unwrap().policy_key.as_deref(),Some("cold_reraise"));
    p.response.as_mut().unwrap().cold_reraise.as_mut().unwrap().raise_sizes.clear();
    let e=evidence::profile_evidence(&cfg(3,0.5),2,&p,&request).unwrap();
    assert_eq!(e.kind,"contextual_estimate");assert_eq!(e.sizing.unwrap().kind,"fallback");
    p.response.as_mut().unwrap().contextual_reraise=None;p.response.as_mut().unwrap().cold_reraise=None;
    let e=evidence::profile_evidence(&cfg(3,0.5),2,&p,&request).unwrap();
    assert_eq!(e.kind,"fallback");assert_eq!(e.sizing.unwrap().kind,"fallback");
}

#[test]
fn conflicting_size_units_are_rejected_in_supplied_dataset_policies() {
    let mut p=profile();let d=p.response.as_mut().unwrap().source_stats.as_mut().unwrap().dataset.as_mut().unwrap();
    d.response_policies[0].raise_multiples=vec![(3.0,1.0)];
    assert!(d.validate().is_err());
}
