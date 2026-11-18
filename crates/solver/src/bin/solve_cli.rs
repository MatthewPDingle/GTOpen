//! Minimal CLI: solve a spot from a JSON config file and print progress.
//!
//! Usage: solve-cli <config.json> [max_iterations] [target_exploit_pct] [--save PATH]
//!        solve-cli resume <save.gto> [iteration_delta] [target_exploit_pct] [--save PATH]
//!
//! `--save` writes a GTOpen save after the run (magic `GTOSOLVE2`, or
//! `GTOSOLVE3` for an ICM tree, which older binaries refuse rather than
//! continue as a chip-EV game); `resume` continues one. On resume the
//! iteration positional is a DELTA added to the save's iteration count
//! (default 300, zero rejected). The save header carries the algorithm and the
//! isomorphism switch, which a resume adopts; SOLVER_ALGO/SOLVER_ISO override
//! them only when set explicitly. `--` ends option parsing, for paths that
//! start with `--`.
//!
//! Env vars:
//!   SOLVER_STORAGE=f32|i16   arena storage (default i16 compressed)
//!   SOLVER_ALGO=dcfr|cfr+|pcfr+   algorithm (default dcfr; on resume: the save's)
//!   SOLVER_ISO=0             disable suit isomorphism (on resume: the save's)
//!   SOLVER_THREADS=N         rayon thread count (default: rayon's own)
//!   (storage/threads apply to every mode; algo/iso apply to a fresh solve and
//!    batch/realization/datagen)
//!   SOLVER_GPU=1             solve on the GPU (requires `--features gpu`
//!                            build; forces f32 storage)

use solver::{Algorithm, RunOptions, Solver, Spot, SpotConfig, Storage};
use std::sync::atomic::AtomicBool;
use std::sync::Arc;

#[path = "../datagen_cli.rs"]
mod datagen_cli;

/// Settings every mode honors, parsed once before subcommand dispatch.
struct EnvOpts {
    storage: Storage,
    algo: Algorithm,
    /// Whether SOLVER_ALGO was present, not just equal to the default: a
    /// resumed save keeps its recorded algorithm unless the user opts in.
    algo_explicit: bool,
    iso: bool,
    iso_explicit: bool,
}

impl EnvOpts {
    fn from_env() -> Self {
        if let Ok(t) = std::env::var("SOLVER_THREADS") {
            match t.parse::<usize>() {
                Ok(n) if n > 0 => {
                    rayon::ThreadPoolBuilder::new().num_threads(n).build_global().ok();
                }
                _ => eprintln!(
                    "warning: SOLVER_THREADS={t:?} is not a positive integer — using rayon's default"
                ),
            }
        }
        let storage = match std::env::var("SOLVER_STORAGE").as_deref() {
            Ok("f32") => Storage::F32,
            Ok("i16") | Err(_) => Storage::Compressed,
            Ok(other) => {
                eprintln!("warning: SOLVER_STORAGE={other:?} unknown (f32|i16) — using i16");
                Storage::Compressed
            }
        };
        let (algo, algo_explicit) = match std::env::var("SOLVER_ALGO") {
            Ok(s) => (
                Algorithm::parse(&s).unwrap_or_else(|e| {
                    eprintln!("bad SOLVER_ALGO: {e}");
                    std::process::exit(1)
                }),
                true,
            ),
            Err(_) => (Algorithm::Dcfr, false),
        };
        let (iso, iso_explicit) = match std::env::var("SOLVER_ISO") {
            Ok(v) => (v != "0", true),
            Err(_) => (true, false),
        };
        EnvOpts { storage, algo, algo_explicit, iso, iso_explicit }
    }

    /// The GPU engine needs full-precision arenas; otherwise the env choice.
    fn storage_for(&self, use_gpu: bool) -> Storage {
        if use_gpu {
            Storage::F32
        } else {
            self.storage
        }
    }
}

#[cfg(target_os = "linux")]
fn peak_rss_mb() -> Option<f64> {
    let status = std::fs::read_to_string("/proc/self/status").ok()?;
    parse_peak_rss_mb(&status)
}

#[cfg(any(target_os = "linux", test))]
fn parse_peak_rss_mb(status: &str) -> Option<f64> {
    let kb = status
        .lines()
        .find(|line| line.starts_with("VmHWM:"))?
        .split_whitespace()
        .nth(1)?
        .parse::<u64>()
        .ok()?;
    Some(kb as f64 / 1024.0)
}

#[cfg(target_os = "macos")]
fn peak_rss_mb() -> Option<f64> {
    let mut usage = std::mem::MaybeUninit::<libc::rusage>::uninit();
    // SAFETY: usage points to writable, correctly aligned storage. getrusage
    // initializes it on success; we do not read it when the call fails.
    if unsafe { libc::getrusage(libc::RUSAGE_SELF, usage.as_mut_ptr()) } != 0 {
        return None;
    }
    // SAFETY: the successful getrusage call initialized usage.
    let usage = unsafe { usage.assume_init() };
    macos_peak_rss_mb(usage.ru_maxrss)
}

#[cfg(any(target_os = "macos", test))]
fn macos_peak_rss_mb(bytes: i64) -> Option<f64> {
    // Darwin reports ru_maxrss in bytes, unlike Linux's KiB. Keep the CLI's
    // existing binary-megabyte conversion and MB label.
    u64::try_from(bytes)
        .ok()
        .map(|bytes| bytes as f64 / (1024.0 * 1024.0))
}

#[cfg(not(any(target_os = "linux", target_os = "macos")))]
fn peak_rss_mb() -> Option<f64> {
    None
}

fn format_peak_rss(mb: Option<f64>) -> String {
    match mb {
        Some(mb) => format!("peak_rss {mb:.0} MB"),
        None => "peak_rss unavailable".to_string(),
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        usage();
        std::process::exit(1);
    }
    // The env-var settings are CLI-wide: read them before dispatching, so
    // batch, realization and flops modes honor them too.
    let env = EnvOpts::from_env();
    if args[1] == "flops" {
        run_flops(&args[2..]);
        return;
    }
    if args[1] == "datagen" {
        datagen_cli::run(&args[2..], &env);
        return;
    }
    if args[1] == "realization" {
        run_realization(&args[2..], &env);
        return;
    }
    if args[1] == "batch" {
        run_batch(&args[2..], &env);
        return;
    }

    let opts = match parse(&args[1..]) {
        Ok(o) => o,
        Err(err) => {
            eprintln!("{err}");
            std::process::exit(1);
        }
    };

    let use_gpu = std::env::var("SOLVER_GPU").map(|v| v == "1").unwrap_or(false);
    let storage = env.storage_for(use_gpu);

    // A save rebuilds its spot from the header config; a JSON config builds
    // one. A fresh solve applies the env switches; resume keeps whatever the
    // save recorded unless the env was set explicitly (see `resume_settings`).
    let mut solver = match &opts.mode {
        Mode::Config(path) => {
            let config_text = std::fs::read_to_string(path).expect("cannot read config");
            let config: SpotConfig =
                serde_json::from_str(&config_text).expect("invalid config JSON");
            let t0 = std::time::Instant::now();
            let spot = Spot::new(config).expect("failed to build spot");
            let mut solver = Solver::with_storage(Arc::new(spot), storage);
            solver.algo = env.algo;
            solver.use_isomorphism = env.iso;
            print_stats("tree built", t0.elapsed().as_secs_f64(), &solver, storage);
            solver
        }
        Mode::Resume(path) => {
            let t0 = std::time::Instant::now();
            let mut solver = match Solver::load_with_storage(path, storage) {
                Ok(s) => s,
                Err(err) => {
                    eprintln!("cannot load {path}: {err}");
                    std::process::exit(1);
                }
            };
            resume_settings(&mut solver, &env);
            if solver.algo == Algorithm::PcfrPlus && solver.iteration > 0 && !solver.has_preds() {
                eprintln!(
                    "warning: PCFR+ prediction state is not stored in saves; this is a warm start and may differ from an uninterrupted run, including after the first resumed iteration"
                );
            }
            print_stats(
                &format!("loaded {path}"),
                t0.elapsed().as_secs_f64(),
                &solver,
                storage,
            );
            solver
        }
    };

    // `resume`'s positional is a delta: `Solver::run` stops at an ABSOLUTE
    // iteration, so a base save at 300 with the default 300 would otherwise
    // run zero iterations and report the NaN fallback.
    let stop_iteration = match &opts.mode {
        Mode::Config(_) => opts.iterations,
        Mode::Resume(_) => {
            let saved = solver.iteration;
            let Some(stop) = saved.checked_add(opts.iterations) else {
                eprintln!(
                    "resume: saved iteration {saved} + {} overflows u32",
                    opts.iterations
                );
                std::process::exit(1);
            };
            println!(
                "resume: saved iteration {saved}, running up to {} more (stop iteration {stop}, or earlier on target {}% pot)",
                opts.iterations, opts.target_exploit_pct,
            );
            stop
        }
    };

    let run_opts = RunOptions {
        max_iterations: stop_iteration,
        target_exploit_pct: opts.target_exploit_pct,
        check_every: 10,
    };

    if use_gpu {
        run_gpu(&mut solver, &run_opts);
    } else {
        let stop = AtomicBool::new(false);
        let final_progress = solver.run(&run_opts, &stop, |p| {
            println!(
                "iter {:5}  exploitability {:8.4} chips ({:.3}% pot)  [{:.1}s]",
                p.iteration, p.exploit_chips, p.exploit_pct_pot, p.elapsed_secs
            );
        });
        println!(
            "done: iter {} exploitability {:.3}% pot in {:.1}s  {}",
            final_progress.iteration,
            final_progress.exploit_pct_pot,
            final_progress.elapsed_secs,
            format_peak_rss(peak_rss_mb()),
        );
    }

    if let Some(save_path) = &opts.save {
        match solver.save(save_path) {
            Ok(()) => println!(
                "saved {save_path}: iter {}, {:.1} MB on disk",
                solver.iteration,
                std::fs::metadata(save_path)
                    .map(|m| m.len() as f64 / 1e6)
                    .unwrap_or(f64::NAN),
            ),
            Err(err) => {
                eprintln!("save failed: {err}");
                std::process::exit(1);
            }
        }
    }
}

const USAGE: &str = "\
usage: solve-cli <config.json> [max_iterations] [target_exploit_pct] [--save PATH]
       solve-cli resume <save.gto> [iteration_delta] [target_exploit_pct] [--save PATH]
       solve-cli batch <config.json> <boards-file|b1,b2,..> [max_iterations] [target]
       solve-cli realization <config.json> <boards-file|b1,b2,..> [max_iterations] [target] [out.jsonl]
       solve-cli datagen <run|job|inputs|verify|block> ...   (value-net training data)
       solve-cli flops <n|all>   (canonical flop classes; n = deterministic weighted subset)

defaults: max_iterations 300 for a fresh solve and batch, 1000 for realization;
resume iteration_delta 300, added to the save's iteration; target_exploit_pct 0.3.
For a fresh solve or resume, the iteration count must be at least 1 and
target_exploit_pct a finite percentage >= 0. --save may appear anywhere before
--; -- ends option parsing (for paths starting with --).";

fn usage() {
    eprintln!("{USAGE}");
}

/// Single-spot invocation, shared by a fresh config solve and `resume`.
#[derive(Debug, PartialEq)]
enum Mode {
    Config(String),
    Resume(String),
}

#[derive(Debug, PartialEq)]
struct Opts {
    mode: Mode,
    /// Fresh: absolute iteration cap. Resume: iterations ADDED to the saved
    /// count, so `run` always has at least one iteration to perform.
    iterations: u32,
    target_exploit_pct: f64,
    save: Option<String>,
}

/// Parse `[--] [resume] <path> [iters] [target] [--save PATH]`. Errors are
/// user-facing messages; `main` prints and exits, tests inspect them.
fn parse(rest: &[String]) -> Result<Opts, String> {
    let mut positional: Vec<&str> = Vec::new();
    let mut save: Option<String> = None;
    // `--` ends option parsing, so a positional path may start with `--`.
    let mut options_done = false;
    let mut i = 0;
    while i < rest.len() {
        let a = rest[i].as_str();
        if options_done {
            positional.push(a);
        } else {
            match a {
                "--" => options_done = true,
                "--save" => {
                    let value = need(rest, i, a)?;
                    set_save(&mut save, value)?;
                    i += 1; // skip the value too
                }
                _ if a.starts_with("--") => return Err(format!("unknown option {a}\n{USAGE}")),
                _ => positional.push(a),
            }
        }
        i += 1;
    }

    let Some(&first) = positional.first() else {
        return Err(format!("missing a spot config or save path\n{USAGE}"));
    };
    let (mode, next) = if first == "resume" {
        let Some(&path) = positional.get(1) else {
            return Err(format!("resume needs a save path\n{USAGE}"));
        };
        (Mode::Resume(path.to_string()), 2)
    } else {
        (Mode::Config(first.to_string()), 1)
    };
    let resuming = matches!(mode, Mode::Resume(_));
    let iters_label = if resuming { "iteration delta" } else { "max_iterations" };
    let iterations: u32 = match positional.get(next) {
        None => 300,
        Some(text) => count(text, iters_label)?,
    };
    if iterations == 0 {
        // `Solver::run`'s loop is `iteration < max_iterations`, so zero would
        // run nothing and report the NaN fallback as if it were a result.
        return Err(if resuming {
            "resume: iteration delta must be at least 1".into()
        } else {
            "max_iterations must be at least 1".into()
        });
    }
    let target_exploit_pct = match positional.get(next + 1) {
        None => 0.3,
        Some(text) => {
            let target: f64 = num(text, "target_exploit_pct")?;
            // f64 parsing accepts "nan"/"inf"; NaN silently disables the
            // early stop and infinity stops at the first check, so refuse
            // both rather than run something other than what was asked.
            if !target.is_finite() || target < 0.0 {
                return Err(format!(
                    "target_exploit_pct {text:?} must be a finite percentage >= 0"
                ));
            }
            target
        }
    };
    let extra = positional.get(next + 2..).unwrap_or_default();
    if !extra.is_empty() {
        return Err(format!("too many positional arguments: {extra:?}\n{USAGE}"));
    }
    Ok(Opts { mode, iterations, target_exploit_pct, save })
}

fn need<'a>(rest: &'a [String], i: usize, flag: &str) -> Result<&'a str, String> {
    rest.get(i + 1)
        .map(String::as_str)
        .ok_or_else(|| format!("{flag} needs a value\n{USAGE}"))
}

/// Record the `--save` destination, rejecting the shapes that would otherwise
/// be silently ignored or misinterpreted.
fn set_save(slot: &mut Option<String>, value: &str) -> Result<(), String> {
    if let Some(prev) = slot {
        return Err(format!(
            "--save given more than once (already {prev:?}, then {value:?})\n{USAGE}"
        ));
    }
    if value.is_empty() {
        return Err(format!("--save needs a non-empty path\n{USAGE}"));
    }
    if value.starts_with("--") {
        return Err(format!(
            "--save value {value:?} looks like an option, not a path; write --save ./{value} for a file with that literal name"
        ));
    }
    *slot = Some(value.to_string());
    Ok(())
}

fn num<T: std::str::FromStr>(text: &str, name: &str) -> Result<T, String> {
    text.parse()
        .map_err(|_| format!("{name} {text:?} is not a valid number"))
}

/// Iteration counts: parse as u64 first so an overflow names the limit
/// instead of the generic "not a valid number" (and negatives still fail).
fn count(text: &str, name: &str) -> Result<u32, String> {
    let n: u64 = text
        .parse()
        .map_err(|_| format!("{name} {text:?} is not a valid number"))?;
    u32::try_from(n).map_err(|_| format!("{name} {text} is too large (max {})", u32::MAX))
}

/// Keep the save header's algorithm/isomorphism unless the user opted in via
/// an explicitly set env var; a defaulted env value must not silently re-price
/// a resumed game.
fn resume_settings(solver: &mut Solver, env: &EnvOpts) {
    if env.algo_explicit && solver.algo != env.algo {
        eprintln!(
            "warning: SOLVER_ALGO={} overrides the save's algorithm {}",
            env.algo.name(),
            solver.algo.name()
        );
        solver.algo = env.algo;
    }
    if env.iso_explicit && solver.use_isomorphism != env.iso {
        eprintln!(
            "warning: SOLVER_ISO={} overrides the save's isomorphism setting {}",
            env.iso as u8, solver.use_isomorphism as u8
        );
        solver.use_isomorphism = env.iso;
    }
}

fn print_stats(prefix: &str, elapsed: f64, solver: &Solver, storage: Storage) {
    println!(
        "{prefix} in {elapsed:.2}s: iter {}, {} nodes ({} action nodes), hands {}/{}, arenas {:.1} MB, storage {:?}, algo {:?}, isomorphism {}",
        solver.iteration,
        solver.spot.tree.nodes.len(),
        solver.spot.num_action_nodes(),
        solver.spot.hands[0].len(),
        solver.spot.hands[1].len(),
        solver.arena_bytes() as f64 / 1e6,
        storage,
        solver.algo,
        if solver.use_isomorphism { "on" } else { "off" },
    );
}

/// Batch mode: solve the same tree/range config across many boards, printing
/// one row per board and writing batch_results.json. The basis for
/// multi-flop aggregate analysis.
fn run_batch(rest: &[String], env: &EnvOpts) {
    if let Some(flag) = rest.iter().find(|a| a.starts_with("--")) {
        eprintln!("{flag}: options are not accepted in batch mode; --save applies only to single-spot or resume mode (batch writes batch_results.json; use SOLVER_BATCH_SAVE=1 for per-board saves)");
        std::process::exit(1);
    }
    if rest.len() < 2 {
        eprintln!("usage: solve-cli batch <config.json> <boards-file|b1,b2,..> [max_iterations] [target]");
        std::process::exit(1);
    }
    let use_gpu = cfg!(feature = "gpu")
        && std::env::var("SOLVER_GPU").map(|v| v == "1").unwrap_or(true);
    let save_each = std::env::var("SOLVER_BATCH_SAVE").map(|v| v == "1").unwrap_or(false);
    let config_text = std::fs::read_to_string(&rest[0]).expect("cannot read config");
    let base: SpotConfig = serde_json::from_str(&config_text).expect("invalid config JSON");
    let boards: Vec<String> = match std::fs::read_to_string(&rest[1]) {
        Ok(text) => text
            .split(|c: char| c.is_whitespace() || c == ',')
            .filter(|s| !s.is_empty())
            .map(str::to_string)
            .collect(),
        Err(_) => rest[1].split(',').map(str::to_string).collect(),
    };
    let max_iterations: u32 = rest.get(2).and_then(|s| s.parse().ok()).unwrap_or(300);
    let target: f64 = rest.get(3).and_then(|s| s.parse().ok()).unwrap_or(0.3);
    println!(
        "batch: {} boards, target {target}% pot, max {max_iterations} iters, {}",
        boards.len(),
        if use_gpu { "GPU" } else { "CPU" },
    );

    let t_all = std::time::Instant::now();
    let mut rows = Vec::new();
    for board in &boards {
        let t0 = std::time::Instant::now();
        let mut cfg = base.clone();
        cfg.board = board.clone();
        let pot = cfg.tree.starting_pot;
        let spot = match Spot::new(cfg) {
            Ok(s) => s,
            Err(err) => {
                println!("{board:>8}  ERROR: {err}");
                rows.push(serde_json::json!({"board": board, "error": err}));
                continue;
            }
        };
        let mut solver = Solver::with_storage(Arc::new(spot), env.storage_for(use_gpu));
        solver.algo = env.algo;
        solver.use_isomorphism = env.iso;
        let (iters, pct) = solve_quiet(&mut solver, max_iterations, target, use_gpu);
        let secs = t0.elapsed().as_secs_f64();

        // range-average root EVs per player (pot-share convention), weighted
        // by reach x valid like the app's own aggregates: per-hand EV is
        // normalized by `valid` (blocker-adjusted opponent mass), so a
        // reach-only average over-weights blocked hands and breaks
        // EV_OOP + EV_IP = pot.
        solver.ensure_symmetric();
        let view = solver.node_view(&[]).unwrap();
        let avg_ev = |p: usize| -> f64 {
            let (mut n, mut d) = (0f64, 0f64);
            for h in &view.players[p].hands {
                if let Some(ev) = h.ev {
                    let w = h.reach as f64 * h.valid as f64;
                    n += ev as f64 * w;
                    d += w;
                }
            }
            n / d
        };
        let (ev_oop, ev_ip) = (avg_ev(0), avg_ev(1));
        println!(
            "{board:>8}  iter {iters:4}  exploit {pct:6.3}% pot  EV {ev_oop:6.2}/{ev_ip:6.2}  [{secs:.1}s]"
        );
        rows.push(serde_json::json!({
            "board": board, "iterations": iters, "exploit_pct_pot": pct,
            "ev_oop": ev_oop, "ev_ip": ev_ip, "seconds": secs,
            "pot": pot,
        }));
        if save_each {
            std::fs::create_dir_all("saves").ok();
            let name = format!("saves/batch_{board}.gto");
            if let Err(err) = solver.save(&name) {
                println!("          save failed: {err}");
            }
        }
    }
    std::fs::write(
        "batch_results.json",
        serde_json::to_string_pretty(&rows).unwrap(),
    )
    .expect("cannot write batch_results.json");
    println!(
        "batch done: {} boards in {:.1}s -> batch_results.json",
        boards.len(),
        t_all.elapsed().as_secs_f64()
    );
}

/// Canonical flop classes: `flops all` prints "board weight" per class
/// (1755 lines); `flops <n>` prints a deterministic weighted systematic
/// sample of n boards, one per line, ready to pipe into batch/realization.
fn run_flops(rest: &[String]) {
    let all = solver::cards::canonical_flops();
    match rest.first().map(|s| s.as_str()) {
        None | Some("all") => {
            for (b, w) in &all {
                println!("{b} {w}");
            }
            eprintln!("{} strategically distinct flops", all.len());
        }
        Some(n) => {
            let n: usize = n.parse().expect("flops: n must be a number or 'all'");
            for (b, _) in solver::cards::canonical_flops_subset(n) {
                println!("{b}");
            }
        }
    }
}

/// M5 Phase A: solve each board and append per-class realization
/// observations (JSONL) — a header line, then per board one meta line and
/// its class rows. R is conditional on the bet-size menu, so the header
/// carries the full config.
fn run_realization(rest: &[String], env: &EnvOpts) {
    if let Some(flag) = rest.iter().find(|a| a.starts_with("--")) {
        eprintln!("{flag}: options are not accepted in realization mode; --save applies only to single-spot or resume mode (realization writes observations to realization_obs.jsonl)");
        std::process::exit(1);
    }
    if rest.len() < 2 {
        eprintln!("usage: solve-cli realization <config.json> <boards-file|b1,b2,..> [max_iterations] [target] [out.jsonl]");
        std::process::exit(1);
    }
    use std::io::Write;
    let use_gpu = cfg!(feature = "gpu")
        && std::env::var("SOLVER_GPU").map(|v| v == "1").unwrap_or(true);
    let config_text = std::fs::read_to_string(&rest[0]).expect("cannot read config");
    let base: SpotConfig = serde_json::from_str(&config_text).expect("invalid config JSON");
    let boards: Vec<String> = match std::fs::read_to_string(&rest[1]) {
        Ok(text) => text
            .split(|c: char| c.is_whitespace() || c == ',')
            .filter(|s| !s.is_empty())
            .map(str::to_string)
            .collect(),
        Err(_) => rest[1].split(',').map(str::to_string).collect(),
    };
    let max_iterations: u32 = rest.get(2).and_then(|s| s.parse().ok()).unwrap_or(1000);
    let target: f64 = rest.get(3).and_then(|s| s.parse().ok()).unwrap_or(0.3);
    let out_path = rest
        .get(4)
        .cloned()
        .unwrap_or_else(|| "realization_obs.jsonl".to_string());
    let mut out = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&out_path)
        .expect("cannot open output");
    writeln!(
        out,
        "{}",
        serde_json::json!({
            "type": "header", "spot_config": &base, "n_boards": boards.len(),
            "max_iterations": max_iterations, "target_pct": target,
        })
    )
    .unwrap();
    println!(
        "realization: {} boards, target {target}% pot, max {max_iterations} iters, {} -> {out_path}",
        boards.len(),
        if use_gpu { "GPU" } else { "CPU" },
    );
    let t_all = std::time::Instant::now();
    let mut wrote = 0usize;
    for board in &boards {
        let t0 = std::time::Instant::now();
        let mut cfg = base.clone();
        cfg.board = board.clone();
        let spot = match Spot::new(cfg) {
            Ok(s) => s,
            Err(err) => {
                println!("{board:>8}  ERROR: {err}");
                continue;
            }
        };
        let mut solver = Solver::with_storage(Arc::new(spot), env.storage_for(use_gpu));
        solver.algo = env.algo;
        solver.use_isomorphism = env.iso;
        let (iters, pct) = solve_quiet(&mut solver, max_iterations, target, use_gpu);
        let secs = t0.elapsed().as_secs_f64();
        solver.ensure_symmetric();
        let obs = solver
            .realization_observations()
            .expect("observation extraction failed");
        writeln!(
            out,
            "{}",
            serde_json::json!({
                "type": "board", "board": board, "iterations": iters,
                "exploit_pct_pot": pct, "seconds": secs, "n_obs": obs.len(),
            })
        )
        .unwrap();
        for o in &obs {
            let mut v = serde_json::to_value(o).unwrap();
            v["type"] = serde_json::json!("obs");
            writeln!(out, "{v}").unwrap();
        }
        wrote += obs.len();
        println!(
            "{board:>8}  iter {iters:4}  exploit {pct:6.3}% pot  {:3} classes  [{secs:.1}s]",
            obs.len()
        );
    }
    println!(
        "realization done: {} boards, {wrote} observations in {:.1}s -> {out_path}",
        boards.len(),
        t_all.elapsed().as_secs_f64()
    );
}

/// Solve to target/max without per-check prints; returns (iterations, exploit%).
fn solve_quiet(solver: &mut Solver, max_iterations: u32, target: f64, use_gpu: bool) -> (u32, f64) {
    #[cfg(feature = "gpu")]
    let pot = solver.spot.tree.config.starting_pot;
    #[cfg(feature = "gpu")]
    if use_gpu {
        // spots too big for VRAM fall back to the CPU engine, like the server
        // Budget from the card's real free memory (Windows reports free VRAM
        // loosely, so also cap at 88% of the card): an oversized plan would
        // otherwise spill into shared system memory and crawl.
        let budget = match solver::gpu::vram_info_mb() {
            Some((free, total)) => free.saturating_sub(1024).min(total * 88 / 100) * 1_000_000,
            None => u64::MAX,
        };
        let mut gpu = match solver::gpu::GpuSolver::new_with_budget(solver, budget) {
            Ok(g) => g,
            Err(err) => {
                eprintln!("  gpu unavailable ({err}) — solving on CPU");
                return solve_quiet(solver, max_iterations, target, false);
            }
        };
        loop {
            gpu.iterate().expect("gpu iterate failed");
            let check = gpu.iteration % 20 == 0 || gpu.iteration >= max_iterations;
            if check {
                let e = gpu.exploitability(solver).expect("gpu exploitability failed");
                let pct = e / pot * 100.0;
                if pct <= target || gpu.iteration >= max_iterations {
                    gpu.sync_to_cpu(solver).expect("gpu sync failed");
                    return (gpu.iteration, pct);
                }
            }
        }
    }
    let _ = use_gpu;
    let opts = RunOptions {
        max_iterations,
        target_exploit_pct: target,
        check_every: 20,
    };
    let stop = AtomicBool::new(false);
    let p = solver.run(&opts, &stop, |_| {});
    (p.iteration, p.exploit_pct_pot)
}

#[cfg(not(feature = "gpu"))]
fn run_gpu(_solver: &mut Solver, _opts: &RunOptions) {
    eprintln!("SOLVER_GPU=1 requires a build with `--features gpu`");
    std::process::exit(1);
}

#[cfg(feature = "gpu")]
fn run_gpu(solver: &mut Solver, opts: &RunOptions) {
    let pot = solver.spot.tree.config.starting_pot;
    // A save can record an algorithm the GPU engine cannot run (pcfr+) or a
    // tree the device cannot hold; report that instead of panicking through
    // `expect`.
    let mut gpu = match solver::gpu::GpuSolver::new(solver) {
        Ok(gpu) => gpu,
        Err(err) => {
            eprintln!("cannot start the GPU solver: {err}");
            std::process::exit(1);
        }
    };
    let start_iteration = gpu.iteration;

    if std::env::var("SOLVER_GPU_PROFILE").map(|v| v == "1").unwrap_or(false) {
        // warm up (JIT + caches), then profile a few iterations
        for _ in 0..3 {
            gpu.iterate().expect("gpu iterate failed");
        }
        gpu.synchronize().unwrap();
        let mut total = solver::gpu::Profile::default();
        for _ in 0..5 {
            let p = gpu.iterate_profiled().expect("profile failed");
            for k in 0..7 {
                total.ms[k] += p.ms[k];
                total.launches[k] += p.launches[k];
            }
        }
        let sum: f64 = total.ms.iter().sum();
        println!("--- kernel profile (5 iterations, sync-per-launch) ---");
        for (k, name) in solver::gpu::KERNEL_NAMES.iter().enumerate() {
            println!(
                "{:>12}: {:8.1} ms ({:4.1}%)  {:5} launches",
                name,
                total.ms[k],
                total.ms[k] / sum * 100.0,
                total.launches[k]
            );
        }
        println!("{:>12}: {:8.1} ms", "TOTAL", sum);
        // The caller still expects a usable host solver (and may pass
        // `--save`): without this the save would write the iteration-0
        // arenas that are still on the host while the device holds the
        // profiled ones.
        gpu.sync_to_cpu(solver).expect("gpu sync failed");
        return;
    }
    let start = std::time::Instant::now();
    let mut gpu_secs = 0f64;
    loop {
        let t = std::time::Instant::now();
        gpu.iterate().expect("gpu iterate failed");
        gpu.synchronize().expect("gpu sync failed");
        gpu_secs += t.elapsed().as_secs_f64();
        let check = gpu.iteration % opts.check_every.max(1) == 0
            || gpu.iteration >= opts.max_iterations;
        if check {
            // best response runs on the GPU too — no arena download needed
            let tchk = std::time::Instant::now();
            let e = gpu.exploitability(solver).expect("gpu exploitability failed");
            let chk_ms = tchk.elapsed().as_secs_f64() * 1e3;
            if std::env::var("SOLVER_GPU_TIMECHK").is_ok() {
                println!("   check took {chk_ms:.0} ms");
            }
            let pct = e / pot * 100.0;
            println!(
                "iter {:5}  exploitability {:8.4} chips ({:.3}% pot)  [{:.1}s, gpu {:.1}s]",
                gpu.iteration,
                e,
                pct,
                start.elapsed().as_secs_f64(),
                gpu_secs,
            );
            if pct <= opts.target_exploit_pct || gpu.iteration >= opts.max_iterations {
                gpu.sync_to_cpu(solver).expect("gpu sync failed");
                // A resumed solve starts at the saved iteration, so divide by
                // the iterations THIS invocation ran, not the cumulative count.
                let ran = gpu.iteration.saturating_sub(start_iteration).max(1);
                println!(
                    "done: iter {} exploitability {:.3}% pot in {:.1}s (gpu kernels {:.2}s = {:.0} ms/iter)  {}",
                    gpu.iteration,
                    pct,
                    start.elapsed().as_secs_f64(),
                    gpu_secs,
                    gpu_secs * 1000.0 / ran as f64,
                    format_peak_rss(peak_rss_mb()),
                );
                break;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn peak_rss_macos_converts_bytes_to_mb() {
        assert_eq!(macos_peak_rss_mb(1_048_576), Some(1.0));
        assert_eq!(macos_peak_rss_mb(1_572_864), Some(1.5));
        assert_eq!(macos_peak_rss_mb(0), Some(0.0));
        assert_eq!(macos_peak_rss_mb(-1), None);
    }

    #[test]
    fn peak_rss_linux_parses_high_water_mark_in_kib() {
        let status = "Name:\tsolve-cli\nVmHWM:\t1536 kB\nVmRSS:\t1024 kB\n";
        assert_eq!(parse_peak_rss_mb(status), Some(1.5));
        for status in [
            "",
            "VmRSS: 1024 kB",
            "VmHWM:",
            "VmHWM: invalid kB",
            "VmHWM: -1 kB",
        ] {
            assert_eq!(parse_peak_rss_mb(status), None);
        }
    }

    #[test]
    fn peak_rss_formats_measurement_or_explicit_unavailable() {
        assert_eq!(format_peak_rss(Some(12.0)), "peak_rss 12 MB");
        assert_eq!(format_peak_rss(None), "peak_rss unavailable");
        assert_eq!(
            format_peak_rss(parse_peak_rss_mb("")),
            "peak_rss unavailable"
        );
    }

    #[cfg(any(target_os = "macos", target_os = "linux"))]
    #[test]
    fn peak_rss_current_process_is_available() {
        let mb = peak_rss_mb().expect("current process peak RSS should be available");
        assert!(mb.is_finite() && mb > 0.0, "unexpected peak RSS: {mb}");
    }

    fn parse_args(args: &[&str]) -> Result<Opts, String> {
        parse(&args.iter().map(|a| a.to_string()).collect::<Vec<_>>())
    }

    #[test]
    fn config_mode_defaults() {
        let o = parse_args(&["spot.json"]).unwrap();
        assert_eq!(o.mode, Mode::Config("spot.json".into()));
        assert_eq!(o.iterations, 300);
        assert_eq!(o.target_exploit_pct, 0.3);
        assert_eq!(o.save, None);
    }

    #[test]
    fn config_mode_explicit_iters_target_and_save() {
        let o = parse_args(&["spot.json", "500", "0.2", "--save", "out.gto"]).unwrap();
        assert_eq!(o.mode, Mode::Config("spot.json".into()));
        assert_eq!(o.iterations, 500);
        assert_eq!(o.target_exploit_pct, 0.2);
        assert_eq!(o.save.as_deref(), Some("out.gto"));
    }

    #[test]
    fn resume_mode_delta_and_save() {
        let o = parse_args(&["resume", "base.gto", "25", "0.1", "--save", "next.gto"]).unwrap();
        assert_eq!(o.mode, Mode::Resume("base.gto".into()));
        assert_eq!(o.iterations, 25);
        assert_eq!(o.target_exploit_pct, 0.1);
        assert_eq!(o.save.as_deref(), Some("next.gto"));
    }

    #[test]
    fn resume_mode_defaults_to_300_more() {
        let o = parse_args(&["resume", "base.gto"]).unwrap();
        assert_eq!(o.mode, Mode::Resume("base.gto".into()));
        assert_eq!(o.iterations, 300);
        assert_eq!(o.target_exploit_pct, 0.3);
    }

    #[test]
    fn save_needs_a_value() {
        let err = parse_args(&["spot.json", "--save"]).unwrap_err();
        assert!(err.contains("--save needs a value"), "{err}");
    }

    #[test]
    fn resume_rejects_zero_delta() {
        let err = parse_args(&["resume", "base.gto", "0"]).unwrap_err();
        assert!(err.contains("iteration delta must be at least 1"), "{err}");
    }

    #[test]
    fn fresh_rejects_zero_iterations() {
        // `Solver::run` would perform no iteration and return its NaN
        // progress fallback, printing it as the result.
        let err = parse_args(&["spot.json", "0"]).unwrap_err();
        assert!(err.contains("max_iterations must be at least 1"), "{err}");
    }

    #[test]
    fn duplicate_save_is_rejected() {
        let err = parse_args(&["spot.json", "--save", "a.gto", "--save", "b.gto"]).unwrap_err();
        assert!(err.contains("--save given more than once"), "{err}");
        assert!(err.contains("a.gto"), "should name the first value: {err}");
        // Repeating the same path is just as likely a scripting bug.
        let err = parse_args(&["spot.json", "--save", "a.gto", "--save", "a.gto"]).unwrap_err();
        assert!(err.contains("--save given more than once"), "{err}");
    }

    #[test]
    fn save_value_that_looks_like_an_option_is_rejected() {
        let err = parse_args(&["spot.json", "--save", "--oops"]).unwrap_err();
        assert!(err.contains("looks like an option"), "{err}");
        assert!(err.contains("./--oops"), "should suggest the literal form: {err}");
        let err = parse_args(&["spot.json", "--save", ""]).unwrap_err();
        assert!(err.contains("non-empty path"), "{err}");
    }

    #[test]
    fn double_dash_ends_option_parsing() {
        let o = parse_args(&["--", "--weird.json", "10", "0.2"]).unwrap();
        assert_eq!(o.mode, Mode::Config("--weird.json".into()));
        assert_eq!(o.iterations, 10);
        // A literal `--save` after `--` is a positional: here it lands in the
        // iterations slot and fails as a number, proving it was not a flag.
        let err = parse_args(&["--", "spot.json", "--save", "x.gto"]).unwrap_err();
        assert!(err.contains("max_iterations"), "{err}");
        let err = parse_args(&["--", "spot.json", "10", "0.2", "--save", "x.gto"]).unwrap_err();
        assert!(err.contains("too many positional arguments"), "{err}");
        // A single-dash path was already positional and stays that way.
        let o = parse_args(&["-spot.json"]).unwrap();
        assert_eq!(o.mode, Mode::Config("-spot.json".into()));
    }

    #[test]
    fn target_must_be_finite_and_non_negative() {
        for bad in ["nan", "NaN", "inf", "-inf", "-0.1", "-1"] {
            let err = parse_args(&["spot.json", "10", bad]).unwrap_err();
            assert!(err.contains("target_exploit_pct"), "{bad}: {err}");
            assert!(err.contains("finite"), "{bad}: {err}");
        }
        // 0 is the established "never stop early" value.
        assert_eq!(parse_args(&["spot.json", "10", "0"]).unwrap().target_exploit_pct, 0.0);
        assert_eq!(
            parse_args(&["spot.json", "10", "1e6"]).unwrap().target_exploit_pct,
            1e6
        );
    }

    #[test]
    fn iteration_overflow_names_the_limit() {
        let err = parse_args(&["spot.json", "4294967296"]).unwrap_err();
        assert!(err.contains("too large"), "{err}");
        assert!(err.contains(&u32::MAX.to_string()), "{err}");
        let err = parse_args(&["resume", "base.gto", "4294967296"]).unwrap_err();
        assert!(err.contains("iteration delta"), "{err}");
    }

    #[test]
    fn too_many_positionals_are_rejected() {
        let err = parse_args(&["spot.json", "10", "0.3", "extra"]).unwrap_err();
        assert!(err.contains("too many positional arguments"), "{err}");
        let err = parse_args(&["resume", "base.gto", "10", "0.3", "extra"]).unwrap_err();
        assert!(err.contains("too many positional arguments"), "{err}");
    }

    #[test]
    fn unknown_option_is_rejected() {
        let err = parse_args(&["spot.json", "--foo"]).unwrap_err();
        assert!(err.contains("unknown option --foo"), "{err}");
        // A bare `--load` is an unknown option, not a path to solve.
        let err = parse_args(&["--load", "base.gto"]).unwrap_err();
        assert!(err.contains("unknown option --load"), "{err}");
    }

    #[test]
    fn missing_paths_are_rejected() {
        let err = parse_args(&["--save", "out.gto"]).unwrap_err();
        assert!(err.contains("missing a spot config or save path"), "{err}");
        let err = parse_args(&["resume"]).unwrap_err();
        assert!(err.contains("resume needs a save path"), "{err}");
    }

    #[test]
    fn bad_numbers_name_the_positional() {
        let err = parse_args(&["spot.json", "many"]).unwrap_err();
        assert!(err.contains("max_iterations"), "{err}");
        let err = parse_args(&["spot.json", "10", "soon"]).unwrap_err();
        assert!(err.contains("target_exploit_pct"), "{err}");
        let err = parse_args(&["resume", "base.gto", "many"]).unwrap_err();
        assert!(err.contains("iteration delta"), "{err}");
    }
}
