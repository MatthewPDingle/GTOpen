//! Size-sweep reports ("dynamic sizing", feature #8): for each board, solve
//! one single-size tree per candidate size of ONE player's first bet on the
//! root street, keep the size with the highest EV for that player, refine
//! between the best size's neighbours with a golden-section search, and
//! report ties when EV gaps sit inside the solves' combined exploitability.
//! The pure math lives in `solver::size_sweep`; this file drives the solves
//! through the ordinary report machinery (`solve_board`).
//!
//! On disk a sweep is `<name>.json` with `"kind": "sweep"` (per-board points
//! and verdicts plus the all-board summary, no line summaries), and, unless
//! `keep_variants` is off, one ordinary browsable report per grid size named
//! `<name> size <label>` with `"sweep_parent": <name>`. Refinement solves
//! are recorded as points only: their sizes differ per board.

use super::*;
use solver::size_sweep::{self, BoardSweep, SizePoint};

#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct SweepSpec {
    /// The player whose first bet on the root street is swept: 0 = OOP, 1 = IP.
    pub player: usize,
    /// Candidate sizes, % pot.
    #[serde(default = "dflt_sizes")]
    pub sizes: Vec<f64>,
    /// Convergence target per solve, % pot.
    #[serde(default = "dflt_target")]
    pub target: f64,
    /// Golden-section refinement solves per board (0 = grid only).
    #[serde(default = "dflt_refine")]
    pub refine: usize,
    #[serde(default = "dflt_iters")]
    pub max_iterations: u32,
    /// Write each grid size as an ordinary browsable report.
    #[serde(default = "dflt_keep")]
    pub keep_variants: bool,
}
fn dflt_sizes() -> Vec<f64> {
    size_sweep::DEFAULT_SIZES.to_vec()
}
fn dflt_target() -> f64 {
    size_sweep::DEFAULT_TARGET
}
fn dflt_refine() -> usize {
    size_sweep::DEFAULT_REFINE
}
fn dflt_iters() -> u32 {
    1000
}
fn dflt_keep() -> bool {
    true
}

const MAX_SIZES: usize = 12;
const MAX_REFINE: usize = 8;

/// Root street index (0 flop, 1 turn, 2 river) of a checked board.
fn street_of(board: &str) -> usize {
    solver::cards::parse_cards(board)
        .map(|c| c.len().clamp(3, 5) - 3)
        .unwrap_or(0)
}

/// The spot with `player`'s first bet on `street` replaced by one size.
pub(crate) fn spot_with_size(
    spot: &SpotRequest,
    player: usize,
    street: usize,
    size: f64,
) -> Result<SpotRequest, String> {
    let mut sr = spot.clone();
    let side = if player == 0 { &mut sr.oop } else { &mut sr.ip };
    let Some(st) = side.get_mut(street) else {
        return Err("sizing needs flop, turn and river entries for both players".into());
    };
    st.bet = size_sweep::size_token(size);
    Ok(sr)
}

fn variant_name(name: &str, size: f64) -> String {
    format!("{} size {}", name.trim(), size_sweep::size_label(size))
}

pub(crate) fn validate(spec: &SweepSpec, req: &ReportRequest) -> Result<(), String> {
    if spec.player > 1 {
        return Err("sweep player must be 0 (OOP) or 1 (IP)".into());
    }
    let grid = size_sweep::normalize_sizes(&spec.sizes);
    if grid.len() != spec.sizes.len() {
        return Err("sweep sizes must be distinct positive numbers (% pot)".into());
    }
    if grid.is_empty() || grid.len() > MAX_SIZES {
        return Err(format!("give 1 to {MAX_SIZES} sweep sizes"));
    }
    if grid.iter().any(|s| *s > 1000.0) {
        return Err("sweep sizes are % pot and at most 1000".into());
    }
    if !(spec.target.is_finite() && spec.target > 0.0) {
        return Err("sweep target must be a positive % of the pot".into());
    }
    if spec.refine > MAX_REFINE {
        return Err(format!("at most {MAX_REFINE} refinement solves per board"));
    }
    if spec.max_iterations == 0 {
        return Err("sweep max_iterations must be positive".into());
    }
    if req
        .villain
        .as_ref()
        .is_some_and(|v| v.player == spec.player)
    {
        return Err("the swept player must be the hero, not the locked villain".into());
    }
    for street in 0..3 {
        let mut probe = spot_with_size(&req.spot, spec.player, street, grid[0])?;
        probe.board = "AhKs2d".into();
        probe.to_spot_config()?;
    }
    for &s in &grid {
        report_path(&variant_name(&req.name, s))?;
    }
    Ok(())
}

fn write_json_atomic(path: &std::path::Path, v: &serde_json::Value) -> Result<(), String> {
    let text = serde_json::to_string(v).map_err(|e| e.to_string())?;
    let tmp = path.with_extension("json.tmp");
    std::fs::write(&tmp, text).map_err(|e| e.to_string())?;
    std::fs::rename(&tmp, path).map_err(|e| e.to_string())
}

struct Variant {
    size: f64,
    req: ReportRequest,
    path: std::path::PathBuf,
    lines_dir: std::path::PathBuf,
    rows: Vec<serde_json::Value>,
}

/// The sweep file: per-board rows + the all-board summary.
fn sweep_json(
    req: &ReportRequest,
    spec: &SweepSpec,
    grid: &[f64],
    variants: &[Variant],
    rows: &[serde_json::Value],
    boards: &[BoardSweep],
    complete: bool,
) -> serde_json::Value {
    serde_json::json!({
        "name": req.name,
        "kind": "sweep",
        "created": std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0),
        "spot": req.spot,
        "villain": req.villain,
        "sweep": spec,
        "grid": grid,
        "target_pct": spec.target,
        "complete": complete,
        "lines": false,
        "variants": variants.iter().map(|v| serde_json::json!({"size": v.size, "name": v.req.name})).collect::<Vec<_>>(),
        "flops": rows,
        "summary": size_sweep::summarize(grid, boards),
    })
}

/// How often the choosing player bets at his first decision of the street
/// (root for OOP, after a root check for IP), reach-weighted.
fn bet_freq(b: &BoardSolve, player: usize) -> Option<f64> {
    let node = if player == 0 {
        b.root.as_ref()?
    } else {
        &b.vs_check
    };
    if node.get("actor")?.as_u64()? as usize != player {
        return None;
    }
    let kinds = node.get("kinds")?.as_array()?;
    let freqs = node.get("freqs")?.as_array()?;
    let check: f64 = kinds
        .iter()
        .zip(freqs)
        .filter(|(k, _)| k.as_str() == Some("check"))
        .filter_map(|(_, f)| f.as_f64())
        .sum();
    Some((1.0 - check).clamp(0.0, 1.0))
}

/// One candidate size solved on one board: the summary point and the
/// details the Best size view shows.
fn solve_size(
    stop: &AtomicBool,
    req: &ReportRequest,
    spec: &SweepSpec,
    board: &str,
    size: f64,
    refined: bool,
    storage: Storage,
    cap_mb: f64,
    lines_dir: Option<&std::path::Path>,
) -> Result<(SizePoint, serde_json::Value, BoardSolve), BoardErr> {
    let sr =
        spot_with_size(&req.spot, spec.player, street_of(board), size).map_err(BoardErr::Failed)?;
    let b = solve_board(
        stop,
        &sr,
        board,
        req.villain.as_ref(),
        spec.max_iterations,
        spec.target,
        storage,
        cap_mb,
        lines_dir,
    )?;
    let pot = req.spot.starting_pot;
    let ev = |p: usize| {
        b.players
            .get(p)
            .and_then(|x| x.get("ev"))
            .and_then(|x| x.as_f64())
            .unwrap_or(0.0)
    };
    let point = SizePoint {
        size,
        ev_pct: ev(spec.player) / pot * 100.0,
        exploit_pct: b.adapt_exploit_pct.unwrap_or(b.exploit_pct),
        refined,
    };
    let detail = serde_json::json!({
        "size": size, "refined": refined, "ev_pct": point.ev_pct, "exploit_pct": point.exploit_pct,
        "ev": [ev(0), ev(1)], "bet_freq": bet_freq(&b, spec.player),
        "iterations": b.iterations, "seconds": b.seconds, "engine": b.engine,
    });
    Ok((point, detail, b))
}

pub(crate) fn start(
    state: Arc<AppState>,
    req: ReportRequest,
    path: std::path::PathBuf,
    flops: Vec<(String, u32)>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let mut spec = req.sweep.clone().expect("sweep request");
    let grid = size_sweep::normalize_sizes(&spec.sizes);
    spec.sizes = grid.clone();
    let street0 = street_of(&flops[0].0);
    let mut variants = Vec::new();
    if spec.keep_variants {
        for &size in &grid {
            let name = variant_name(&req.name, size);
            let mut vreq = req.clone();
            vreq.spot =
                spot_with_size(&req.spot, spec.player, street0, size).map_err(bad_request)?;
            vreq.name = name.clone();
            vreq.sweep = None;
            vreq.sweep_parent = Some(req.name.clone());
            vreq.target = spec.target;
            vreq.max_iterations = spec.max_iterations;
            variants.push(Variant {
                size,
                path: report_path(&name).map_err(bad_request)?,
                lines_dir: report_lines_dir(&name).map_err(bad_request)?,
                req: vreq,
                rows: Vec::new(),
            });
        }
    }
    if state.report.lock().unwrap().running {
        return Err((StatusCode::CONFLICT, "a report is already running".into()));
    }
    // a sweep's own name holds no line summaries; a re-run must not inherit
    // boards from an older run of any of its variants
    let _ = std::fs::remove_dir_all(report_lines_dir(&req.name).map_err(bad_request)?);
    for v in &variants {
        let _ = std::fs::remove_dir_all(&v.lines_dir);
        std::fs::create_dir_all(&v.lines_dir).map_err(|e| bad_request(e.to_string()))?;
    }
    claim_report(&state, &req.name, flops.len())?;
    let solves_per_board = grid.len() + spec.refine;
    let app = state.clone();
    std::thread::spawn(move || {
        let t0 = std::time::Instant::now();
        // Same unwind guard as report_run: a panic must not leave the
        // report status running forever.
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            run(&app, &req, &spec, &grid, &path, &flops, &mut variants, t0)
        }));
        let mut r = lock_unpoisoned(&app.report);
        r.running = false;
        r.step.clear();
        r.seconds = t0.elapsed().as_secs_f64();
        match outcome {
            Ok((done, err)) => {
                r.done = done;
                r.error = err;
            }
            Err(p) => {
                let msg = format!("report crashed: {}", panic_msg(p.as_ref()));
                eprintln!("sweep worker panicked: {}", panic_msg(p.as_ref()));
                r.error = msg.clone();
                drop(r);
                mark_report_failed(&path, &msg);
            }
        }
    });
    Ok(Json(
        serde_json::json!({"ok": true, "kind": "sweep", "solves_per_board": solves_per_board}),
    ))
}

#[allow(clippy::too_many_arguments)]
fn run(
    app: &AppState,
    req: &ReportRequest,
    spec: &SweepSpec,
    grid: &[f64],
    path: &std::path::Path,
    flops: &[(String, u32)],
    variants: &mut [Variant],
    t0: std::time::Instant,
) -> (usize, String) {
    let mut rows: Vec<serde_json::Value> = Vec::new();
    let mut boards: Vec<BoardSweep> = Vec::new();
    let mut err = String::new();
    let mut stopped = false;
    let write_all = |rows: &[serde_json::Value],
                     boards: &[BoardSweep],
                     variants: &[Variant],
                     complete: bool| {
        let mut res = write_json_atomic(
            path,
            &sweep_json(req, spec, grid, variants, rows, boards, complete),
        );
        for v in variants {
            if let Err(e) = write_report(&v.path, &v.req, &v.rows, complete) {
                res = res.and(Err(e));
            }
        }
        res
    };
    // claim the files up front (empty partials), like report_run
    let _ = write_all(&rows, &boards, variants, false);
    let storage = Storage::Compressed;
    let cap_mb = mem_cap_mb();
    let stop = &app.report_stop;
    let status = |i: usize, board: &str, step: String| {
        let mut r = app.report.lock().unwrap();
        r.done = i;
        r.board = board.to_string();
        r.step = step;
        r.seconds = t0.elapsed().as_secs_f64();
    };
    'boards: for (i, (board, weight)) in flops.iter().enumerate() {
        if stop.load(Ordering::Relaxed) {
            stopped = true;
            break;
        }
        let mut points: Vec<SizePoint> = Vec::new();
        let mut details: Vec<serde_json::Value> = Vec::new();
        // variant rows are committed only once the whole board is done, so
        // a STOP mid-board leaves every file at the same set of boards
        let mut vrows: Vec<serde_json::Value> = Vec::new();
        for (k, &size) in grid.iter().enumerate() {
            status(
                i,
                board,
                format!(
                    "size {}% ({}/{})",
                    size_sweep::size_token(size),
                    k + 1,
                    grid.len()
                ),
            );
            let lines_dir = variants.get(k).map(|v| v.lines_dir.as_path());
            match solve_size(
                stop, req, spec, board, size, false, storage, cap_mb, lines_dir,
            ) {
                Ok((p, d, b)) => {
                    points.push(p);
                    details.push(d);
                    vrows.push(b.row(board, *weight));
                }
                Err(BoardErr::Stopped) => {
                    stopped = true;
                    break 'boards;
                }
                Err(BoardErr::Failed(e)) => {
                    err = e;
                    break 'boards;
                }
            }
        }
        let mut n_refine = 0;
        let refined = size_sweep::refine(&mut points, spec.refine, |size| {
            n_refine += 1;
            status(
                i,
                board,
                format!(
                    "refine {}% ({}/{})",
                    size_sweep::size_token(size),
                    n_refine,
                    spec.refine
                ),
            );
            let (p, d, _) = solve_size(stop, req, spec, board, size, true, storage, cap_mb, None)?;
            details.push(d);
            Ok(p)
        });
        let edge = match refined {
            Ok(edge) => edge,
            Err(BoardErr::Stopped) => {
                stopped = true;
                break;
            }
            Err(BoardErr::Failed(e)) => {
                err = e;
                break;
            }
        };
        let Some(verdict) = size_sweep::verdict(&points, edge) else {
            continue;
        };
        details.sort_by(|a, b| {
            a["size"]
                .as_f64()
                .unwrap_or(0.0)
                .partial_cmp(&b["size"].as_f64().unwrap_or(0.0))
                .unwrap()
        });
        rows.push(serde_json::json!({
            "board": board, "weight": weight, "points": details, "verdict": verdict,
        }));
        boards.push(BoardSweep {
            board: board.clone(),
            weight: *weight,
            points,
            verdict,
        });
        for (v, row) in variants.iter_mut().zip(vrows) {
            v.rows.push(row);
        }
        app.report_cache.lock().unwrap().clear();
        let _ = write_all(&rows, &boards, variants, false);
    }
    let done = rows.len();
    if let Err(e) = write_all(&rows, &boards, variants, err.is_empty() && !stopped) {
        if err.is_empty() {
            err = e;
        }
    }
    if !err.is_empty() {
        mark_report_failed(path, &err);
        for v in variants.iter() {
            mark_report_failed(&v.path, &err);
        }
    }
    (done, err)
}

/// The variant report names a sweep file lists (for delete).
pub(crate) fn variant_names(sweep: &serde_json::Value) -> Vec<String> {
    sweep
        .get("variants")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|v| v.get("name")?.as_str().map(str::to_string))
                .collect()
        })
        .unwrap_or_default()
}

#[cfg(test)]
mod tests {
    use super::*;

    /// River, OOP to act with a perfectly polarized range (sets + air) into
    /// a pure bluff-catcher: the bettor's equilibrium EV rises with the bet
    /// size, so the sweep must pick the largest candidate and flag the edge.
    fn polar_river() -> ReportRequest {
        let spot: SpotRequest = serde_json::from_value(serde_json::json!({
            "board": "Ks9h5d3c2s",
            "range_oop": "KK,99,QJs,QTs,JTs",
            "range_ip": "AK",
            "starting_pot": 10.0,
            "effective_stack": 100.0,
            "allin_threshold": 100,
            "max_raises": 0,
            "oop": [
                {"bet": "50", "raise": "", "donk": ""},
                {"bet": "50", "raise": "", "donk": ""},
                {"bet": "50", "raise": "", "donk": ""}
            ],
            "ip": [
                {"bet": "", "raise": "", "donk": ""},
                {"bet": "", "raise": "", "donk": ""},
                {"bet": "", "raise": "", "donk": ""}
            ]
        }))
        .unwrap();
        serde_json::from_value::<ReportRequest>(serde_json::json!({
            "name": "unit sweep", "spot": spot, "boards": ["Ks9h5d3c2s"],
            "sweep": {"player": 0, "sizes": [25, 50, 100, 200], "target": 0.05,
                      "refine": 3, "max_iterations": 4000, "keep_variants": false}
        }))
        .unwrap()
    }

    #[test]
    fn sweep_requests_validate() {
        let req = polar_river();
        let spec = req.sweep.clone().unwrap();
        validate(&spec, &req).unwrap();
        for bad in [
            serde_json::json!({"player": 2}),
            serde_json::json!({"player": 0, "sizes": []}),
            serde_json::json!({"player": 0, "sizes": [33, 33]}),
            serde_json::json!({"player": 0, "sizes": [-5]}),
            serde_json::json!({"player": 0, "target": 0}),
            serde_json::json!({"player": 0, "refine": 9}),
        ] {
            let spec: SweepSpec = serde_json::from_value(bad.clone()).unwrap();
            assert!(validate(&spec, &req).is_err(), "{bad}");
        }
        let spec: SweepSpec = serde_json::from_value(serde_json::json!({"player": 1})).unwrap();
        assert_eq!(spec.sizes, size_sweep::DEFAULT_SIZES.to_vec());
        assert_eq!(spec.target, 0.15);
        assert!(spec.keep_variants);
        assert!(
            serde_json::from_value::<SweepSpec>(serde_json::json!({"player": 0, "size": [5]}))
                .is_err()
        );
        let sr = spot_with_size(&req.spot, 1, 0, 12.5).unwrap();
        assert_eq!(sr.ip[0].bet, "12.5");
        assert_eq!(sr.oop[0].bet, "50");
        assert_eq!(variant_name("BTN v BB", 12.5), "BTN v BB size 12_5");
    }

    #[test]
    fn polarized_river_bettor_picks_the_largest_size() {
        let req = polar_river();
        let spec = req.sweep.clone().unwrap();
        let stop = AtomicBool::new(false);
        let board = "Ks9h5d3c2s";
        let mut points = Vec::new();
        let mut freqs = Vec::new();
        for &size in &spec.sizes {
            let (p, d, _) = solve_size(
                &stop,
                &req,
                &spec,
                board,
                size,
                false,
                Storage::F32,
                1e6,
                None,
            )
            .unwrap_or_else(|e| match e {
                BoardErr::Failed(e) => panic!("{e}"),
                BoardErr::Stopped => panic!("stopped"),
            });
            assert!(
                p.exploit_pct <= 0.05 + 1e-9,
                "{size}: exploit {}",
                p.exploit_pct
            );
            freqs.push(d["bet_freq"].as_f64().unwrap());
            points.push(p);
        }
        for w in points.windows(2) {
            assert!(
                w[1].ev_pct > w[0].ev_pct,
                "EV must rise with size: {points:?}"
            );
        }
        // and by the textbook amount: value bets win P + bP/(1+b) against a
        // caller who calls 1/(1+b), bluffs and checks win 0, so the bettor's
        // EV is proportional to (1+2b)/(1+b)
        let theory = |pct: f64| {
            let b = pct / 100.0;
            (1.0 + 2.0 * b) / (1.0 + b)
        };
        for p in &points {
            let ratio = p.ev_pct / points[0].ev_pct;
            let want = theory(p.size) / theory(points[0].size);
            assert!(
                (ratio - want).abs() < 0.005,
                "{}: EV ratio {ratio} vs theory {want}",
                p.size
            );
        }
        // polarized bettor: bets all value + some air; a bigger bet bluffs
        // MORE (b/(1+b) of the value), so the bet frequency rises too
        for w in freqs.windows(2) {
            assert!(w[1] > w[0] - 1e-3, "bet frequencies {freqs:?}");
        }
        let edge = size_sweep::refine(&mut points, spec.refine, |_| -> Result<SizePoint, ()> {
            panic!("an edge optimum must not refine")
        })
        .unwrap();
        let v = size_sweep::verdict(&points, edge).unwrap();
        assert_eq!(v.best, 200.0);
        assert!(v.edge);
        assert_eq!(
            v.ties,
            vec![200.0],
            "EV gaps here are far above solver noise"
        );
    }
}
