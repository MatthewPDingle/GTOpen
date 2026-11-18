//! The Preflop Lab's plan line: how much memory a game needs and where it
//! will solve, from what the card offers.
use super::*;

const GB: f64 = (1u64 << 30) as f64 / 1e6; // MB in the GB the lab shows
/// A game the GPU's large-game mode does not cover.
const NO_LARGE: f64 = f64::INFINITY;

#[test]
fn a_game_that_fits_the_card_solves_there() {
    let card = PfCard::Ready { budget_mb: 30_000, total_mb: 34_190 };
    let plan = pf_engine_plan_on(card, 1_000.0, 1_000_000, 2_400.0, NO_LARGE);
    assert_eq!((plan.engine, plan.card), ("gpu", "fits"));
    assert!(plan.reason.is_empty());
    assert_eq!(plan.gpu_limit_mb, 34_190.0 - 512.0);
    // both tables, the tree, and the copy a GPU solve keeps in RAM
    assert_eq!(plan.ram_mb, 1_000.0 + 400.0 + 1_000.0);
    assert_eq!((plan.gpu_need_mb, plan.gpu_free_mb, plan.gpu_total_mb), (2_400.0, 30_000.0, 34_190.0));
}

#[test]
fn a_game_bigger_than_the_card_solves_on_the_cpu_and_says_so() {
    // an 11.5M-node 8-max game on a 32 GB card: 15.6 GB of tables, 33.8 GB on the card
    let card = PfCard::Ready { budget_mb: 32_000, total_mb: 34_190 };
    let plan = pf_engine_plan_on(card, 15_611.0, 11_546_836, 33_784.0, NO_LARGE);
    assert_eq!((plan.engine, plan.card), ("cpu", "too_big"));
    assert_eq!(
        plan.reason,
        "too big for this graphics card (needs 31.5 GB there, the card can give 31.4 GB)"
    );
    // no second copy on the CPU
    assert!((plan.ram_mb - (15_611.0 + 11_546_836.0 * 400.0 / 1e6)).abs() < 1e-6);
}

#[test]
fn a_game_too_big_for_the_normal_gpu_solve_uses_large_game_mode() {
    // the same 8-max game: 33.8 GB in the normal solve, 19.1 GB a part at a time
    let card = PfCard::Ready { budget_mb: 33_678, total_mb: 34_190 };
    let plan = pf_engine_plan_on(card, 15_611.0, 11_546_836, 33_784.0, 19_095.0);
    assert_eq!((plan.engine, plan.card, plan.gpu_mode), ("gpu", "fits", "large"));
    assert!(plan.reason.is_empty());
    // the line shows what this mode needs, and RAM holds the second copy as on any GPU solve
    assert_eq!(plan.gpu_need_mb, 19_095.0);
    assert!((plan.ram_mb - (2.0 * 15_611.0 + 11_546_836.0 * 400.0 / 1e6)).abs() < 1e-6);
    // a game that fits the normal solve never uses the mode, whatever it would need there
    for large in [1_000.0, 2_400.0, 5_000.0, NO_LARGE] {
        let normal = pf_engine_plan_on(card, 1_000.0, 1_000_000, 2_400.0, large);
        assert_eq!((normal.engine, normal.gpu_mode, normal.gpu_need_mb), ("gpu", "", 2_400.0));
    }
    // too big even a part at a time: the CPU, and the reason names the least the card would need
    let huge = pf_engine_plan_on(card, 30_000.0, 22_000_000, 65_000.0, 37_000.0);
    assert_eq!((huge.engine, huge.card, huge.gpu_mode), ("cpu", "too_big", ""));
    assert_eq!(huge.gpu_need_mb, 37_000.0);
    assert_eq!(huge.reason, "too big for this graphics card (needs 34.5 GB there, the card can give 31.4 GB)");
    // a busy card: the mode takes a game the normal solve has no room for right now
    let shared = PfCard::Ready { budget_mb: 9_000, total_mb: 34_190 };
    let plan = pf_engine_plan_on(shared, 5_000.0, 3_000_000, 11_000.0, 6_500.0);
    assert_eq!((plan.engine, plan.card, plan.gpu_mode), ("gpu", "fits", "large"));
    let plan = pf_engine_plan_on(shared, 9_000.0, 5_000_000, 20_000.0, 11_500.0);
    assert_eq!((plan.engine, plan.card), ("cpu", "busy"));
    assert_eq!(plan.reason, "the graphics card has too little free right now (needs 10.7 GB, 8.4 GB free)");
}

#[test]
fn a_busy_card_is_named_as_the_reason() {
    let card = PfCard::Ready { budget_mb: (8.0 * GB) as u64, total_mb: 34_190 };
    let plan = pf_engine_plan_on(card, 9_000.0, 5_000_000, 20.0 * GB, NO_LARGE);
    assert_eq!((plan.engine, plan.card), ("cpu", "busy"));
    assert_eq!(plan.reason, "the graphics card has too little free right now (needs 20.0 GB, 8.0 GB free)");
    // exactly at the budget still fits
    let fits = pf_engine_plan_on(PfCard::Ready { budget_mb: 20_000, total_mb: 34_190 }, 9_000.0, 5_000_000, 20_000.0, NO_LARGE);
    assert_eq!(fits.engine, "gpu");
}

#[test]
fn no_usable_card_has_a_plain_reason() {
    for (card, name, words) in [
        (PfCard::NoEngine, "unsupported", "has no graphics card support"),
        (PfCard::Off, "off", "switched off"),
        (PfCard::Missing, "none", "no NVIDIA graphics card found"),
    ] {
        let plan = pf_engine_plan_on(card, 100.0, 50_000, 300.0, NO_LARGE);
        assert_eq!((plan.engine, plan.card), ("cpu", name));
        assert!(plan.reason.contains(words), "{}", plan.reason);
        assert_eq!(plan.gpu_free_mb, 0.0);
    }
    let huge = pf_engine_plan_on(PfCard::Ready { budget_mb: 30_000, total_mb: 34_190 }, 100.0, 50_000, f64::INFINITY, NO_LARGE);
    assert_eq!((huge.engine, huge.card), ("cpu", "too_big"));
}

#[test]
fn reasons_use_no_engine_words() {
    for card in [PfCard::NoEngine, PfCard::Missing, PfCard::Ready { budget_mb: 1_000, total_mb: 34_190 },
        PfCard::Ready { budget_mb: 1_000, total_mb: 2_000 }] {
        let reason = pf_engine_plan_on(card, 9_000.0, 5_000_000, 20_000.0, NO_LARGE).reason.to_lowercase();
        assert!(!reason.contains("arena") && !reason.contains("vram") && !reason.contains("cuda"), "{reason}");
    }
}

/// A built game's status carries the plan, and it says what the estimate
/// said before the build.
#[tokio::test]
async fn estimate_and_status_report_the_same_plan() {
    let cfg: solver::preflop::PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "stack": 20.0, "posts": [0.0, 0.5, 1.0], "limp": true,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 2, "add_allin": true,
        "rake_pct": 0.0, "rake_cap": 0.0, "realization": "raw"
    })).unwrap();
    let est = pf_estimate(Json(cfg.clone())).await.unwrap().0;
    let eq = Arc::new(solver::preflop::equity::EquityTable::build(1000));
    let mut built = solver::preflop::PreflopSolver::new(cfg, eq).unwrap();
    let size = PfSize::of(&built);
    let mut status = PreflopStatus { state: "idle".into(), size: Some(size), ..Default::default() };
    let state = Arc::new(AppState::default());
    // a profiled seat's strategies are stored on the card too: the mirror picks that up
    for _ in 0..150 {
        built.iterate();
    }
    let stats = solver::preflop::archetypes().into_iter().next().unwrap().1;
    let profile = built.generate_profile(1, &stats, "profile").unwrap().0;
    built.set_table(vec![false; 3], vec![None, Some(profile), None]).unwrap();
    let mut with_profile = status.clone();
    with_profile.mirror_trust(&built);
    #[cfg(feature = "gpu")]
    assert!(with_profile.size.unwrap().gpu_policy_mb > size.gpu_policy_mb);
    assert_eq!(with_profile.size.unwrap().gpu_tree_mb, size.gpu_tree_mb);
    status.plan = None;
    *state.preflop.lock().unwrap() = Some(PreflopSession {
        solver: Arc::new(Mutex::new(built)),
        stop: Arc::new(AtomicBool::new(false)),
        status: Arc::new(Mutex::new(status)),
        worker: None,
    });
    let status = serde_json::to_value(pf_status(State(state.clone())).await.0).unwrap();
    for reply in [&est, &status] {
        let plan = &reply["plan"];
        assert!(plan["engine"] == "gpu" || plan["engine"] == "cpu", "{plan}");
        assert!(plan["ram_mb"].as_f64().unwrap() > est["arena_mb"].as_f64().unwrap());
    }
    assert_eq!(est["plan"], status["plan"], "the estimate before the build and the built game agree");
    assert!(status.get("size").is_none(), "the measurements stay on the server");
    // no session: no plan
    let empty = serde_json::to_value(pf_status(State(Arc::new(AppState::default()))).await.0).unwrap();
    assert!(empty["plan"].is_null());
}
