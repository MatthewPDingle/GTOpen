use super::*;

#[test]
fn early_preview_is_opt_in_and_skips_uniform_first_pass() {
    let old: PfSolveRequest = serde_json::from_str("{}").unwrap();
    assert!(!old.early_preview);
    assert_eq!(old.check_every, 50);
    let explicit: PfSolveRequest = serde_json::from_str(r#"{"early_preview":true}"#).unwrap();
    assert!(explicit.early_preview);
    assert!(!pf_preview_due(0, true));
    assert!(!pf_preview_due(1, true));
    assert!(pf_preview_due(2, true));
    assert!(!pf_preview_due(3, true));
    assert!(pf_preview_due(10, true));
    assert!(pf_preview_due(20, true));
    for i in 0..101 { assert!(!pf_preview_due(i, false)); }
    assert!(serde_json::from_str::<PfSolveRequest>(r#"{"early_preview_v1":true}"#).is_err());
    assert!(serde_json::from_str::<PfSolveRequest>(r#"{"early_preview":2}"#).is_err());
}

#[test]
fn live_counter_never_claims_a_newer_published_strategy() {
    let st = PreflopStatus { iteration:49, published_iteration:10, accuracy_iteration:None,
        state:"running".into(), ..Default::default() };
    let p = st.publication();
    assert_eq!(p.published_iteration,10);
    assert_eq!(p.accuracy_iteration,None);
    assert_eq!(p.gap_total,None);
    assert!(!p.converged);
}

#[test]
fn a_gap_is_tied_to_its_snapshot_and_limit_is_not_convergence() {
    let mut st = PreflopStatus { iteration:60, published_iteration:60, accuracy_iteration:Some(50),
        gap_total:0.02, stop_reason:"iteration_limit".into(), ..Default::default() };
    assert!(!st.publication().converged);
    assert_eq!(st.publication().accuracy_iteration,Some(50));
    st.stop_reason="target_reached".into();
    assert!(!st.publication().converged);
    st.accuracy_iteration=Some(60);
    assert!(st.publication().converged);
}

#[test]
fn changed_models_and_loaded_native_saves_do_not_inherit_a_gap_claim() {
    let mut st = PreflopStatus { iteration:50, published_iteration:50, accuracy_iteration:Some(50),
        gaps:vec![0.0;3], evs:vec![1.0;3], stop_reason:"target_reached".into(), ..Default::default() };
    st.invalidate_accuracy(0);
    assert_eq!(st.published_iteration,0);
    assert!(st.gaps.is_empty() && st.evs.is_empty());
    assert!(!st.publication().converged);
    let loaded = PreflopStatus {iteration:74,published_iteration:74,state:"stopped".into(),..Default::default()};
    assert_eq!(loaded.publication().accuracy_iteration,None);
    assert!(!loaded.publication().converged);
}

#[test]
fn publication_is_additive_to_existing_node_export_json() {
    let out = PfPublished {result:serde_json::json!({"pot_bb":3.0,"range_oop":"AA"}),
        publication:PreflopStatus {published_iteration:2,..Default::default()}.publication()};
    let value=serde_json::to_value(out).unwrap();
    assert_eq!(value["pot_bb"],3.0);
    assert_eq!(value["range_oop"],"AA");
    assert_eq!(value["publication"]["published_iteration"],2);
    assert_eq!(value["publication"]["accuracy_iteration"],serde_json::Value::Null);
}

#[test]
fn fresh_build_model_query_is_strict_and_defaults_to_reference() {
    let parse = |query: &str| Query::<PfBuildOptions>::try_from_uri(&format!("/api/preflop/spot{query}").parse().unwrap());
    assert_eq!(parse("").unwrap().0.model().unwrap(), "coupled_deck_v1");
    assert_eq!(parse("?multiway_model=coupled_preview64_v1").unwrap().0.model().unwrap(), "coupled_preview64_v1");
    assert!(parse("?model=coupled_preview64_v1").is_err());
    for model in ["unknown", "legacy_product", "coupled_preview32_v1", ""] {
        assert!(parse(&format!("?multiway_model={model}")).unwrap().0.model().is_err());
    }
    assert!(parse("?multiway_model=coupled_deck_v1&multiway_model=coupled_preview64_v1").is_err());
}

#[tokio::test]
async fn rejected_model_does_not_even_access_session_or_stop_path() {
    let state = Arc::new(AppState {
        session: Mutex::new(None), status: Mutex::new(StatusInfo {state:"preserved".into(),..Default::default()}),
        preflop: Mutex::new(None), report:Mutex::new(ReportStatus::default()),
        report_stop:Arc::new(AtomicBool::new(false)), report_cache:Mutex::new(None),
    });
    // Any attempt to stop/join/build through the session path would panic.
    // Validation must return before accessing it, with no cache or solver work.
    let _ = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        let _guard = state.preflop.lock().unwrap();
        panic!("intentional poisoned sentinel");
    }));
    let cfg = serde_json::from_value(serde_json::json!({"positions":["BTN","SB","BB"],
        "posts":[0,0.5,1],"stack":100,"open_raises":[2.5],"raise_mults":[3],"realization":"raw"})).unwrap();
    let result = pf_build(State(state.clone()),Query(PfBuildOptions {multiway_model:Some("not-supported".into())}),Json(cfg)).await;
    assert!(result.is_err());
    assert_eq!(state.status.lock().unwrap().state,"preserved");
    assert!(!state.report_stop.load(Ordering::Relaxed));
    assert!(state.preflop.is_poisoned());
}
