use super::*;

fn publication_fixture() -> solver::preflop::PreflopSolver {
    static EQ: std::sync::OnceLock<Arc<solver::preflop::equity::EquityTable>> = std::sync::OnceLock::new();
    let eq = EQ.get_or_init(|| Arc::new(solver::preflop::equity::EquityTable::build(1))).clone();
    let cfg = serde_json::from_value(serde_json::json!({"positions":["SB","BB"],
        "posts":[0.5,1.0],"stack":2.0,"limp":true,"open_raises":[],
        "raise_mults":[3.0],"max_raises":1,"add_allin":false,"realization":"raw"})).unwrap();
    solver::preflop::PreflopSolver::new(cfg, eq).unwrap()
}

#[test]
fn terminal_stop_publication_clears_cancellation_before_waiting_reader_evaluates() {
    for reason in ["stopped","error"] {
        let mut fixture=publication_fixture();fixture.iterate();
        let actual=fixture.gaps_and_evs();
        assert!(actual.0.iter().chain(&actual.1).any(|x|*x!=0.0),"fixture must distinguish real evaluation from cancellation zeros");
        let flag=Arc::new(AtomicBool::new(true));fixture.set_stop_flag(Some(flag.clone()));
        let canceled=fixture.gaps_and_evs();
        assert!(canceled.0.iter().chain(&canceled.1).all(|x|*x==0.0));
        let iteration=fixture.iteration;
        let solver=Arc::new(Mutex::new(fixture));
        let status=Arc::new(Mutex::new(PreflopStatus {state:"running".into(),iteration,
            published_iteration:iteration,accuracy_iteration:Some(iteration),gap_total:0.001,
            gaps:vec![0.001;2],evs:vec![1.0;2],stop_reason:"target_reached".into(),..Default::default()}));
        let mut held=lock_unpoisoned(&solver);
        let read_solver=solver.clone();let read_status=status.clone();
        let (ready_tx,ready_rx)=std::sync::mpsc::channel();
        let (result_tx,result_rx)=std::sync::mpsc::channel();
        let reader=std::thread::spawn(move || {
            ready_tx.send(()).unwrap();
            let s=pf_solver_lock(&read_solver);
            pf_reject_if_running(&read_status).unwrap();
            result_tx.send((s.gaps_and_evs(),read_status.lock().unwrap().publication())).unwrap();
        });
        ready_rx.recv_timeout(std::time::Duration::from_secs(10)).unwrap();
        let error=(reason=="error").then(||"injected worker failure".to_string());
        pf_finish_preflop(&mut held,&status,reason,true,error);
        assert!(flag.load(Ordering::Relaxed),"clear the solver attachment, never erase caller cancellation");
        {
            let st=status.lock().unwrap();assert_eq!(st.state,"stopped");assert_eq!(st.stop_reason,reason);
            assert_eq!(st.accuracy_iteration,None);assert!(st.gaps.is_empty()&&st.evs.is_empty());
            assert!(st.preview_note.contains("interrupted player sweep"));
            assert_eq!(st.published_iteration,iteration);
            if reason=="error" {assert_eq!(st.error,"injected worker failure");}
        }
        assert!(result_rx.try_recv().is_err(),"reader cannot cross solver generation commit");
        drop(held);
        let (after,publication)=result_rx.recv_timeout(std::time::Duration::from_secs(10)).unwrap();
        reader.join().unwrap();assert_eq!(after,actual);assert_eq!(publication.gap_total,None);
        assert!(!publication.converged);assert_eq!(publication.published_iteration,iteration);
    }
}

#[test]
fn completed_finish_preserves_measured_accuracy_and_clears_attached_stop() {
    let mut s=publication_fixture();s.iterate();let actual=s.gaps_and_evs();
    let flag=Arc::new(AtomicBool::new(true));s.set_stop_flag(Some(flag));
    let status=Mutex::new(PreflopStatus {state:"running".into(),iteration:s.iteration,
        published_iteration:s.iteration,accuracy_iteration:Some(s.iteration),gap_total:0.001,
        ..Default::default()});
    pf_finish_preflop(&mut s,&status,"target_reached",false,None);
    let st=status.lock().unwrap();assert_eq!(st.state,"done");assert!(st.publication().converged);
    assert_eq!(st.accuracy_iteration,Some(s.iteration));assert_eq!(st.gap_total,0.001);
    assert_eq!(s.gaps_and_evs(),actual);
}

#[test]
fn failed_snapshot_keeps_host_generation_and_readers_see_one_successful_commit() {
    let solver = Arc::new(Mutex::new(publication_fixture()));
    let status = Arc::new(Mutex::new(PreflopStatus {iteration:9,published_iteration:0,
        state:"running".into(),..Default::default()}));
    {
        let mut s = lock_unpoisoned(&solver);
        let before = serde_json::to_value(s.node_view(&[]).unwrap()).unwrap();
        assert!(pf_publish_gpu_snapshot(&mut s,&status,9, |_| Err("staged transfer failed".into())).is_err());
        assert_eq!(s.iteration,0);
        assert_eq!(status.lock().unwrap().published_iteration,0);
        assert_eq!(serde_json::to_value(s.node_view(&[]).unwrap()).unwrap(),before);
    }
    let (staged_tx, staged_rx) = std::sync::mpsc::channel();
    let (release_tx, release_rx) = std::sync::mpsc::channel();
    let worker_solver = solver.clone();
    let worker_status = status.clone();
    let worker = std::thread::spawn(move || {
        let mut s = lock_unpoisoned(&worker_solver);
        pf_publish_gpu_snapshot(&mut s,&worker_status,1, |s| {
            // Real CPU arena update stands in for the staged GPU copy. A reader
            // must not get through between this write and the metadata commit.
            s.iterate();
            staged_tx.send(()).unwrap();
            release_rx.recv().unwrap();
            Ok(())
        }).unwrap();
    });
    staged_rx.recv_timeout(std::time::Duration::from_secs(10)).unwrap();
    assert!(solver.try_lock().is_err());
    assert_eq!(status.lock().unwrap().published_iteration,0);
    release_tx.send(()).unwrap();
    worker.join().unwrap();
    let s = pf_solver_lock(&solver);
    let publication = status.lock().unwrap().publication();
    assert_eq!(s.iteration,1);
    assert_eq!(publication.published_iteration,1);
    assert_eq!(publication.accuracy_iteration,None);
    assert!(!publication.converged);
    assert!(s.node_view(&[]).unwrap().strategy_note.is_none());
}

#[test]
fn detached_running_session_reads_snapshot_but_rejects_policy_mutations() {
    let solver = Arc::new(Mutex::new(publication_fixture()));
    let status = Arc::new(Mutex::new(PreflopStatus {iteration:9,published_iteration:0,
        state:"running".into(),..Default::default()}));
    // Equivalent to a GPU worker computing outside this lock: the host is
    // readable, and the independent live counter is newer than its arenas.
    let s = pf_solver_lock(&solver);
    assert_eq!(s.iteration,0);
    assert_eq!(status.lock().unwrap().publication().published_iteration,0);
    assert!(s.node_view(&[]).unwrap().strategy_note.is_some());
    assert_eq!(pf_reject_if_running(&status).unwrap_err().0,StatusCode::CONFLICT);
    drop(s);
    // Same guard is used by table, HERO, point-lock/unlock and evaluate routes;
    // save additionally checks running before and after acquiring the lock.
    status.lock().unwrap().state = "stopped".into();
    let _s = pf_solver_lock(&solver);
    assert!(pf_reject_if_running(&status).is_ok());
}

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
    assert_eq!(parse("?multiway_model=coupled_deck_v1").unwrap().0.model().unwrap(), "coupled_deck_v1");
    assert!(parse("?model=coupled_preview64_v1").is_err());
    for model in ["unknown", "legacy_product", "coupled_preview32_v1", "coupled_preview32_v2", "coupled_preview64_v1", "coupled_preview128_v1", ""] {
        assert!(parse(&format!("?multiway_model={model}")).unwrap().0.model().is_err());
    }
    assert!(parse("?multiway_model=coupled_deck_v1&multiway_model=coupled_preview64_v1").is_err());
}

#[tokio::test]
async fn production_capabilities_do_not_offer_experimental_payoff_models() {
    let Json(caps)=pf_capabilities().await;
    assert_eq!(caps["early_preview_v1"],true);
    assert_eq!(caps["fresh_build_multiway_models"],serde_json::json!(["coupled_deck_v1"]));
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
    let cfg:solver::preflop::PreflopConfig = serde_json::from_value(serde_json::json!({"positions":["BTN","SB","BB"],
        "posts":[0,0.5,1],"stack":100,"open_raises":[2.5],"raise_mults":[3],"realization":"raw"})).unwrap();
    for model in ["not-supported","coupled_preview64_v1","coupled_preview32_v2","coupled_preview128_v1"] {
        let result = pf_build(State(state.clone()),Query(PfBuildOptions {multiway_model:Some(model.into())}),Json(cfg.clone())).await;
        assert!(result.is_err());
    }
    assert_eq!(state.status.lock().unwrap().state,"preserved");
    assert!(!state.report_stop.load(Ordering::Relaxed));
    assert!(state.preflop.is_poisoned());
}
