//! `solve-cli datagen`: generate, inspect and verify leaf-value training
//! data (see `solver::datagen` and docs/contribute-compute.md).

use super::{solve_quiet, EnvOpts};
use solver::datagen::{self, ExampleInputs, ExampleRecord, JobHeader};
use solver::{Solver, Spot};
use std::io::{BufRead, Write};
use std::path::{Path, PathBuf};
use std::sync::Arc;

const USAGE: &str = "usage:
  solve-cli datagen run --contributor LOGIN [--out DIR] [--jobs N] [--hours H]
                        [--worker I --workers W] [--max-vram GB] [--per-job N] [--target PCT] [--max-iters N]
  solve-cli datagen job JOB [--contributor LOGIN] [--out DIR] [--max-vram GB] [--per-job N] [--target PCT] [--max-iters N]
  solve-cli datagen sizes JOB [--per-job N] [--generator V]   (estimated GPU memory per example)
  solve-cli datagen inputs JOB [INDEX] [--per-job N] [--max-vram GB] [--generator V]
  solve-cli datagen spot JOB INDEX [--generator V]   (the example as a solve-cli spot config)
      (--generator: regenerate under an older supported generator version, e.g. 2)
  solve-cli datagen verify FILE.jsonl [--sample K] [--max-mean D] [--max-diff D]
  solve-cli datagen block LOGIN
  solve-cli datagen baseline < examples.jsonl   (Preflop Lab's realization-model values per example)
  solve-cli datagen leafnet NET.bin < examples.jsonl   (a trained leaf net's values per example)
  solve-cli datagen leaves GAME.bin [--out DIR] [--leaves N] [--boards M] [--seed S]
                        (a solved preflop game's heads-up flop leaves as examples: DIR/inputs.jsonl, DIR/leaves.json)
  solve-cli datagen solve DIR [--target PCT] [--max-iters N]   (solve DIR/inputs.jsonl into DIR/solved.jsonl; resumes)";

struct Opts {
    positional: Vec<String>,
    contributor: Option<String>,
    out: PathBuf,
    jobs: Option<u64>,
    hours: Option<f64>,
    worker: u64,
    workers: u64,
    per_job: u32,
    target: f64,
    max_iters: u32,
    sample: usize,
    max_mean: f64,
    max_diff: f64,
    /// None = detect from the GPU; Some(0) = uncapped.
    max_vram: Option<f64>,
    leaves: usize,
    boards: u32,
    seed: u64,
    /// Generator version for `inputs`, `spot` and `sizes` (default: this build's).
    generator: u32,
}

fn parse(rest: &[String]) -> Opts {
    let mut o = Opts {
        positional: Vec::new(),
        contributor: None,
        out: PathBuf::from("datagen_out"),
        jobs: None,
        hours: None,
        worker: 0,
        workers: 1,
        per_job: datagen::DEFAULT_PER_JOB,
        target: 0.5,
        max_iters: 1000,
        sample: 3,
        max_mean: 0.01,
        max_diff: 0.06,
        max_vram: None,
        leaves: 40,
        boards: 8,
        seed: 1,
        generator: datagen::GENERATOR_VERSION,
    };
    let mut i = 0;
    let need = |i: usize| -> &String {
        rest.get(i + 1).unwrap_or_else(|| {
            eprintln!("{} needs a value\n{USAGE}", rest[i]);
            std::process::exit(1)
        })
    };
    fn num<T: std::str::FromStr>(s: &str, name: &str) -> T {
        s.parse().unwrap_or_else(|_| {
            eprintln!("{name}: bad value {s:?}");
            std::process::exit(1)
        })
    }
    while i < rest.len() {
        let a = rest[i].as_str();
        match a {
            "--contributor" => { o.contributor = Some(need(i).clone()); i += 1; }
            "--out" => { o.out = PathBuf::from(need(i)); i += 1; }
            "--jobs" => { o.jobs = Some(num(need(i), a)); i += 1; }
            "--hours" => { o.hours = Some(num(need(i), a)); i += 1; }
            "--worker" => { o.worker = num(need(i), a); i += 1; }
            "--workers" => { o.workers = num::<u64>(need(i), a).max(1); i += 1; }
            "--per-job" => { o.per_job = num::<u32>(need(i), a).max(1); i += 1; }
            "--target" => { o.target = num(need(i), a); i += 1; }
            "--max-iters" => { o.max_iters = num(need(i), a); i += 1; }
            "--sample" => { o.sample = num(need(i), a); i += 1; }
            "--max-mean" => { o.max_mean = num(need(i), a); i += 1; }
            "--max-diff" => { o.max_diff = num(need(i), a); i += 1; }
            "--max-vram" => { o.max_vram = Some(num(need(i), a)); i += 1; }
            "--leaves" => { o.leaves = num::<usize>(need(i), a).max(1); i += 1; }
            "--boards" => { o.boards = num::<u32>(need(i), a).max(1); i += 1; }
            "--seed" => { o.seed = num(need(i), a); i += 1; }
            "--generator" => {
                o.generator = num(need(i), a);
                if !datagen::SUPPORTED_GENERATOR_VERSIONS.contains(&o.generator) {
                    eprintln!("--generator: this build regenerates versions {:?}", datagen::SUPPORTED_GENERATOR_VERSIONS);
                    std::process::exit(1);
                }
                i += 1;
            }
            _ if a.starts_with("--") => {
                eprintln!("unknown option {a}\n{USAGE}");
                std::process::exit(1);
            }
            _ => o.positional.push(a.to_string()),
        }
        i += 1;
    }
    o
}

/// Tree-size cap for drawing examples: --max-vram, else 80% of the GPU's
/// memory (whole GB), else 8 GB on a CPU-only machine.
fn vram_cap(o: &Opts) -> Option<f64> {
    match o.max_vram {
        Some(x) if x <= 0.0 => None,
        Some(x) => Some(x.floor()),
        None => Some(detected_cap_gb()),
    }
}

fn detected_cap_gb() -> f64 {
    #[cfg(feature = "gpu")]
    if use_gpu() {
        if let Some((_free, total_mb)) = solver::gpu::vram_info_mb() {
            return ((total_mb as f64 / 1000.0) * 0.8).floor().max(2.0);
        }
    }
    8.0
}

fn use_gpu() -> bool {
    cfg!(feature = "gpu") && std::env::var("SOLVER_GPU").map(|v| v != "0").unwrap_or(true)
}

/// Solve one example's inputs; returns the record.
fn solve_example(inputs: &ExampleInputs, o: &Opts, env: &EnvOpts) -> Result<ExampleRecord, String> {
    let t0 = std::time::Instant::now();
    let gpu = use_gpu();
    let spot = Spot::new(inputs.spot_config())?;
    let mut solver = Solver::with_storage(Arc::new(spot), env.storage_for(gpu));
    solver.algo = env.algo;
    solver.use_isomorphism = env.iso;
    let (iterations, exploit) = solve_quiet(&mut solver, o.max_iters, o.target, gpu);
    solver.ensure_symmetric();
    let values = datagen::extract_values(&solver)?;
    Ok(ExampleRecord {
        kind: "example".into(),
        inputs: inputs.clone(),
        values,
        iterations,
        exploit_pct_pot: (exploit * 10_000.0).round() / 10_000.0,
        seconds: (t0.elapsed().as_secs_f64() * 100.0).round() / 100.0,
    })
}

fn job_path(out: &Path, contributor: &str, job: u64) -> PathBuf {
    out.join(contributor).join(format!("job-{job}.jsonl"))
}

/// Solve a whole job into `<out>/<contributor>/job-<job>.jsonl` (written to
/// a .part file first, renamed when complete).
fn run_job(job: u64, contributor: &str, o: &Opts, env: &EnvOpts) -> Result<PathBuf, String> {
    let path = job_path(&o.out, contributor, job);
    std::fs::create_dir_all(path.parent().unwrap()).map_err(|e| e.to_string())?;
    let part = path.with_extension("jsonl.part");
    let mut f = std::fs::File::create(&part).map_err(|e| format!("{}: {e}", part.display()))?;
    let engine = if use_gpu() { "gpu" } else { "cpu" };
    let cap = vram_cap(o);
    let header = JobHeader::new(job, contributor, o.per_job, o.target, o.max_iters, engine, cap);
    writeln!(f, "{}", serde_json::to_string(&header).unwrap()).map_err(|e| e.to_string())?;
    let t0 = std::time::Instant::now();
    for index in 0..o.per_job {
        let inputs = datagen::example_inputs_capped(job, index, cap);
        let rec = solve_example(&inputs, o, env)?;
        println!(
            "  job {job} #{index:3}  {:8} {:6} pot {:6.2}bb stack {:6.1}bb  iter {:4}  exploit {:5.2}%  [{:.1}s]",
            rec.inputs.board,
            rec.inputs.pot_type,
            rec.inputs.pot_bb,
            rec.inputs.stack_bb,
            rec.iterations,
            rec.exploit_pct_pot,
            rec.seconds
        );
        writeln!(f, "{}", serde_json::to_string(&rec).unwrap()).map_err(|e| e.to_string())?;
    }
    let done = serde_json::json!({
        "type": "done", "examples": o.per_job, "seconds": (t0.elapsed().as_secs_f64() * 10.0).round() / 10.0,
    });
    writeln!(f, "{done}").map_err(|e| e.to_string())?;
    f.sync_all().ok();
    drop(f);
    std::fs::rename(&part, &path).map_err(|e| e.to_string())?;
    Ok(path)
}

pub fn run(rest: &[String], env: &EnvOpts) {
    let Some(cmd) = rest.first() else {
        eprintln!("{USAGE}");
        std::process::exit(1);
    };
    let o = parse(&rest[1..]);
    match cmd.as_str() {
        "block" => {
            let login = o.positional.first().unwrap_or_else(|| {
                eprintln!("{USAGE}");
                std::process::exit(1)
            });
            println!("{}", datagen::contributor_base(login));
        }
        "inputs" => {
            let job: u64 = o.positional.first().and_then(|s| s.parse().ok()).unwrap_or_else(|| {
                eprintln!("{USAGE}");
                std::process::exit(1)
            });
            let indices: Vec<u32> = match o.positional.get(1) {
                Some(s) => vec![s.parse().expect("index")],
                None => (0..o.per_job).collect(),
            };
            for i in indices {
                let ex = datagen::example_inputs_capped_v(o.generator, job, i, o.max_vram.filter(|&x| x > 0.0));
                println!("{}", serde_json::to_string(&ex).unwrap());
            }
        }
        "sizes" => {
            // Survey of tree sizes (estimated GPU memory) over a job's examples.
            let job: u64 = o.positional.first().and_then(|s| s.parse().ok()).unwrap_or(1);
            let mut rows = Vec::new();
            for i in 0..o.per_job {
                let ex = datagen::example_inputs_v(o.generator, job, i);
                let spot = Spot::new(ex.spot_config()).expect("spot");
                let gb = spot.vram_estimate_bytes() as f64 / 1e9;
                println!("{i:4} {:7}{} pot {:6.2} stack {:6.1} spr {:5.1} nodes {:8} vram {:6.2} GB",
                    ex.pot_type, if ex.straddle { " (straddled)" } else { "" }, ex.pot_bb, ex.stack_bb,
                    ex.stack_bb / ex.pot_bb, spot.tree.nodes.len(), gb);
                rows.push(gb);
            }
            rows.sort_by(|a, b| a.partial_cmp(b).unwrap());
            let q = |f: f64| rows[((rows.len() - 1) as f64 * f) as usize];
            println!("vram GB: median {:.2}  p90 {:.2}  p99 {:.2}  max {:.2}", q(0.5), q(0.9), q(0.99), q(1.0));
        }
        "spot" => {
            let (Some(job), Some(index)) = (
                o.positional.first().and_then(|s| s.parse::<u64>().ok()),
                o.positional.get(1).and_then(|s| s.parse::<u32>().ok()),
            ) else {
                eprintln!("{USAGE}");
                std::process::exit(1)
            };
            let cfg = datagen::example_inputs_v(o.generator, job, index).spot_config();
            println!("{}", serde_json::to_string_pretty(&cfg).unwrap());
        }
        "job" => {
            let job: u64 = o.positional.first().and_then(|s| s.parse().ok()).unwrap_or_else(|| {
                eprintln!("{USAGE}");
                std::process::exit(1)
            });
            let who = o.contributor.clone().unwrap_or_else(|| "local".into());
            match run_job(job, &who, &o, env) {
                Ok(p) => println!("wrote {}", p.display()),
                Err(e) => {
                    eprintln!("job {job} failed: {e}");
                    std::process::exit(1);
                }
            }
        }
        "baseline" => baseline(None),
        "leafnet" => {
            let path = o.positional.first().unwrap_or_else(|| {
                eprintln!("{USAGE}");
                std::process::exit(1)
            });
            let net = solver::preflop::leafnet::LeafNet::load(path).unwrap_or_else(|e| {
                eprintln!("leafnet: {e}");
                std::process::exit(1)
            });
            baseline(Some(net));
        }
        "leaves" => leaves(&o),
        "solve" => solve_dir(&o, env),
        "run" => run_loop(&o, env),
        "verify" => verify(&o, env),
        _ => {
            eprintln!("{USAGE}");
            std::process::exit(1);
        }
    }
}

/// For each example line on stdin, the per-class values today's Preflop Lab
/// realization models give the same heads-up flop (no board: the models
/// price the preflop matchup). One output line per input line, in order:
/// {"job","index","models":{name:[oop values, ip values]}}. Used by
/// tools/datagen/gonogo.py to score a trained net against these models.
/// With a leaf net, the line also has "leafnet" values and the raw
/// "residual" (net output) for checking against the numpy net.
fn baseline(net: Option<solver::preflop::leafnet::LeafNet>) {
    use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
    let samples = std::env::var("PREFLOP_EQ_SAMPLES").ok().and_then(|v| v.parse().ok()).unwrap_or(20_000);
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", samples));
    let models = ["static", "balanced", "calibrated", "raw"];
    let mut solvers: Vec<PreflopSolver> = models.iter().map(|m| {
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions": ["SB", "BB"], "stack": 100.0, "posts": [0.5, 1.0], "limp": false,
            "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 1, "add_allin": false,
            "rake_pct": 0.0, "rake_cap": 0.0, "realization": m,
        })).expect("baseline config");
        let s = PreflopSolver::new(cfg, eq.clone()).unwrap_or_else(|e| {
            eprintln!("baseline: {e}");
            std::process::exit(1)
        });
        if !s.realization_note.is_empty() {
            eprintln!("baseline: {} (run from the GTOpen folder)", s.realization_note);
            std::process::exit(1);
        }
        s
    }).collect();
    let stdout = std::io::stdout();
    let mut out = std::io::BufWriter::new(stdout.lock());
    for (n, line) in std::io::stdin().lock().lines().enumerate() {
        let line = line.expect("stdin");
        if line.trim().is_empty() {
            continue;
        }
        let ex: ExampleInputs = match serde_json::from_str(&line) {
            Ok(x) => x,
            Err(e) => {
                eprintln!("baseline: line {}: {e}", n + 1);
                std::process::exit(1)
            }
        };
        let mut by_model = serde_json::Map::new();
        for (m, s) in models.iter().zip(solvers.iter_mut()) {
            match s.hu_leaf_values([&ex.range[0], &ex.range[1]], ex.pot_bb, ex.stack_bb,
                                     ex.rake_pct * 100.0, ex.rake_cap_bb) { // datagen rake is a fraction
                Ok(v) => {
                    let r = |x: &Vec<f32>| x.iter().map(|&y| (y as f64 * 1e5).round() / 1e5).collect::<Vec<_>>();
                    by_model.insert(m.to_string(), serde_json::json!([r(&v[0]), r(&v[1])]));
                }
                Err(e) => {
                    eprintln!("baseline: job {} #{}: {e}", ex.job, ex.index);
                    std::process::exit(1)
                }
            }
        }
        let mut row = serde_json::json!({"job": ex.job, "index": ex.index, "models": by_model});
        if let Some(net) = &net {
            use solver::preflop::leafnet::{LeafNet, LeafSpot, POT_TYPES};
            let bal: Vec<Vec<f32>> = row["models"]["balanced"].as_array().unwrap().iter()
                .map(|v| v.as_array().unwrap().iter().map(|x| x.as_f64().unwrap() as f32).collect()).collect();
            let spot = LeafSpot {
                range: [&ex.range[0], &ex.range[1]], balanced: [&bal[0], &bal[1]],
                pot_bb: ex.pot_bb, stack_bb: ex.stack_bb, rake_frac: ex.rake_pct, rake_cap_bb: ex.rake_cap_bb,
                pot_type: POT_TYPES.iter().position(|t| *t == ex.pot_type).unwrap_or(1),
            };
            let residual = net.residual(&LeafNet::features(&spot));
            let values = net.values(&spot);
            row["leafnet"] = serde_json::json!(values);
            row["residual"] = serde_json::json!(residual);
        }
        writeln!(out, "{row}").expect("stdout");
    }
}

/// Job numbers of leaf-check examples (far above contributor blocks).
const LEAF_JOB_BASE: u64 = 900_000_000_000;

fn fail(msg: String) -> ! {
    eprintln!("{msg}");
    std::process::exit(1)
}

/// Export a solved preflop game's heads-up flop leaves (the ones the learned
/// model corrects) as datagen examples, so exact flop solves can score the
/// realization models on the ranges a real preflop solution produces
/// (tools/datagen/leafcheck.py). The leaves are split evenly over the pot
/// types (limped, single-raised, 3-bet, 4-bet), taking the ones that carry
/// the most chips (reach x pot) within each type, since by chips alone a
/// deep-stacked game is mostly 4-bet pots. Each gets `--boards` random flops.
fn leaves(o: &Opts) {
    use solver::preflop::{equity::EquityTable, leafnet::POT_TYPES, PreflopSolver};
    let game = o.positional.first().unwrap_or_else(|| fail(USAGE.into()));
    let samples = std::env::var("PREFLOP_EQ_SAMPLES").ok().and_then(|v| v.parse().ok()).unwrap_or(20_000);
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", samples));
    let s = PreflopSolver::load_game(game, eq).unwrap_or_else(|e| fail(format!("{game}: {e}")));
    let mut all = s.hu_flop_leaves();
    let total: f64 = all.iter().map(|l| l.reach * l.pot_bb).sum();
    all.sort_by(|a, b| (b.reach * b.pot_bb).partial_cmp(&(a.reach * a.pot_bb)).unwrap());
    // even split over pot types; a type with fewer leaves passes its share on
    let mut by_type: Vec<Vec<_>> = vec![Vec::new(); POT_TYPES.len()];
    for leaf in all {
        by_type[leaf.raises.min(3) as usize].push(leaf);
    }
    let mut quota = vec![0usize; POT_TYPES.len()];
    let mut left = o.leaves;
    while left > 0 && (0..POT_TYPES.len()).any(|t| quota[t] < by_type[t].len()) {
        for t in 0..POT_TYPES.len() {
            if left > 0 && quota[t] < by_type[t].len() {
                quota[t] += 1;
                left -= 1;
            }
        }
    }
    let mut all: Vec<_> = by_type.into_iter().zip(&quota).flat_map(|(v, &q)| v.into_iter().take(q)).collect();
    all.sort_by(|a, b| (b.reach * b.pot_bb).partial_cmp(&(a.reach * a.pot_bb)).unwrap());
    let covered: f64 = all.iter().map(|l| l.reach * l.pot_bb).sum();
    std::fs::create_dir_all(&o.out).unwrap_or_else(|e| fail(format!("{}: {e}", o.out.display())));
    let r3 = |w: &[f32]| w.iter().map(|&x| (x * 1000.0).round() / 1000.0).collect::<Vec<f32>>();
    let r2 = |x: f64| (x * 100.0).round() / 100.0;
    let mut inputs = String::new();
    let mut described = Vec::new();
    for (rank, leaf) in all.iter().enumerate() {
        let job = LEAF_JOB_BASE + rank as u64;
        for index in 0..o.boards {
            let mut rng = datagen::Rng::new(o.seed.wrapping_mul(0x9E37_79B9_7F4A_7C15) ^ job.wrapping_mul(31) ^ index as u64);
            let ex = ExampleInputs {
                job, index, board: datagen::random_flop(&mut rng),
                pot_type: POT_TYPES[leaf.raises.min(3) as usize].to_string(),
                pot_bb: r2(leaf.pot_bb), stack_bb: r2(leaf.stack_bb),
                rake_pct: s.cfg.rake_pct / 100.0, rake_cap_bb: s.cfg.rake_cap,
                range: [r3(&leaf.range[0]), r3(&leaf.range[1])], attempt: 0,
                straddle: s.cfg.utg_straddle,
            };
            inputs.push_str(&serde_json::to_string(&ex).unwrap());
            inputs.push('\n');
        }
        described.push(serde_json::json!({
            "job": job, "path": leaf.path, "positions": leaf.positions, "pot_bb": leaf.pot_bb,
            "stack_bb": leaf.stack_bb, "raises": leaf.raises, "reach": leaf.reach,
            "chip_share": leaf.reach * leaf.pot_bb / total.max(1e-12),
        }));
    }
    let summary = serde_json::json!({
        "game": game, "realization": s.cfg.realization, "iteration": s.iteration, "positions": s.cfg.positions,
        "leaves_in_game": s.hu_flop_leaves().len(), "exported": all.len(), "boards_per_leaf": o.boards,
        "chip_share_covered": covered / total.max(1e-12), "leaves": described,
    });
    let write = |name: &str, text: String| {
        let p = o.out.join(name);
        std::fs::write(&p, text).unwrap_or_else(|e| fail(format!("{}: {e}", p.display())));
    };
    write("inputs.jsonl", inputs);
    write("leaves.json", serde_json::to_string_pretty(&summary).unwrap());
    let per_type: Vec<String> = POT_TYPES.iter().zip(&quota).map(|(t, q)| format!("{q} {t}")).collect();
    println!("{} leaves ({}) x {} boards ({:.0}% of the chips that reach heads-up flops) -> {}",
             all.len(), per_type.join(", "), o.boards, 100.0 * covered / total.max(1e-12), o.out.join("inputs.jsonl").display());
}

/// Solve every example of DIR/inputs.jsonl into DIR/solved.jsonl, skipping
/// the ones already there (so an interrupted run resumes).
fn solve_dir(o: &Opts, env: &EnvOpts) {
    let dir = PathBuf::from(o.positional.first().unwrap_or_else(|| fail(USAGE.into())));
    let text = std::fs::read_to_string(dir.join("inputs.jsonl"))
        .unwrap_or_else(|e| fail(format!("{}: {e}", dir.join("inputs.jsonl").display())));
    let out = dir.join("solved.jsonl");
    let mut done = std::collections::HashSet::new();
    if let Ok(old) = std::fs::read_to_string(&out) {
        for line in old.lines() {
            if let Ok(r) = serde_json::from_str::<ExampleRecord>(line) {
                done.insert((r.inputs.job, r.inputs.index));
            }
        }
    }
    let todo: Vec<ExampleInputs> = text.lines().filter(|l| !l.trim().is_empty())
        .map(|l| serde_json::from_str(l).unwrap_or_else(|e| fail(format!("inputs.jsonl: {e}"))))
        .filter(|ex: &ExampleInputs| !done.contains(&(ex.job, ex.index))).collect();
    println!("{} to solve ({} already in {})", todo.len(), done.len(), out.display());
    let mut f = std::fs::OpenOptions::new().create(true).append(true).open(&out)
        .unwrap_or_else(|e| fail(format!("{}: {e}", out.display())));
    let t0 = std::time::Instant::now();
    for (n, ex) in todo.iter().enumerate() {
        let rec = solve_example(ex, o, env).unwrap_or_else(|e| fail(format!("job {} #{}: {e}", ex.job, ex.index)));
        writeln!(f, "{}", serde_json::to_string(&rec).unwrap()).unwrap_or_else(|e| fail(e.to_string()));
        f.flush().ok();
        println!("  {}/{}  leaf {} board {} {:8} pot {:6.2}bb  iter {:4}  exploit {:5.2}%  [{:.1}s, {:.0}s total]",
                 n + 1, todo.len(), ex.job - LEAF_JOB_BASE, ex.index, ex.board, ex.pot_bb, rec.iterations,
                 rec.exploit_pct_pot, rec.seconds, t0.elapsed().as_secs_f64());
    }
}

fn run_loop(o: &Opts, env: &EnvOpts) {
    let Some(login) = o.contributor.clone() else {
        eprintln!("datagen run needs --contributor <your GitHub login>\n{USAGE}");
        std::process::exit(1);
    };
    let login = login.trim().to_string();
    if login.is_empty() || !login.chars().all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_') {
        eprintln!("--contributor must be a GitHub login (letters, digits, - or _)");
        std::process::exit(1);
    }
    let t0 = std::time::Instant::now();
    println!(
        "datagen: contributor {login}, worker {}/{}, {} examples per job, target {}% pot, {}, trees up to {} -> {}",
        o.worker,
        o.workers,
        o.per_job,
        o.target,
        if use_gpu() { "GPU" } else { "CPU" },
        vram_cap(o).map(|c| format!("{c} GB")).unwrap_or_else(|| "any size".into()),
        o.out.join(&login).display()
    );
    let mut done = 0u64;
    let mut k = o.worker;
    loop {
        if let Some(n) = o.jobs {
            if done >= n {
                break;
            }
        }
        if let Some(h) = o.hours {
            if t0.elapsed().as_secs_f64() >= h * 3600.0 {
                println!("time limit reached");
                break;
            }
        }
        let job = datagen::contributor_job(&login, k);
        k += o.workers;
        if job_path(&o.out, &login, job).exists() {
            continue; // finished in an earlier run
        }
        let tj = std::time::Instant::now();
        match run_job(job, &login, o, env) {
            Ok(p) => {
                done += 1;
                println!(
                    "finished job {job} in {:.1} min -> {} ({done} this run)",
                    tj.elapsed().as_secs_f64() / 60.0,
                    p.display()
                );
            }
            Err(e) => {
                eprintln!("job {job} failed: {e}");
                std::process::exit(1);
            }
        }
    }
    println!("datagen: {done} jobs in {:.1} h", t0.elapsed().as_secs_f64() / 3600.0);
}

fn verify(o: &Opts, env: &EnvOpts) {
    let Some(file) = o.positional.first() else {
        eprintln!("{USAGE}");
        std::process::exit(1);
    };
    let mut errors: Vec<String> = Vec::new();
    let reader = std::io::BufReader::new(std::fs::File::open(file).unwrap_or_else(|e| {
        eprintln!("{file}: {e}");
        std::process::exit(1)
    }));
    let mut header: Option<JobHeader> = None;
    let mut records: Vec<ExampleRecord> = Vec::new();
    let mut done_seen = false;
    for (n, line) in reader.lines().enumerate() {
        let line = match line {
            Ok(l) => l,
            Err(e) => {
                errors.push(format!("line {}: {e}", n + 1));
                break;
            }
        };
        if line.trim().is_empty() {
            continue;
        }
        let v: serde_json::Value = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(e) => {
                errors.push(format!("line {}: bad JSON ({e})", n + 1));
                continue;
            }
        };
        match v["type"].as_str() {
            Some("header") if n == 0 => match serde_json::from_value::<JobHeader>(v) {
                Ok(h) => header = Some(h),
                Err(e) => errors.push(format!("bad header: {e}")),
            },
            Some("example") => match serde_json::from_value::<ExampleRecord>(v) {
                Ok(r) => records.push(r),
                Err(e) => errors.push(format!("line {}: bad example ({e})", n + 1)),
            },
            Some("done") => done_seen = true,
            _ => errors.push(format!("line {}: unexpected record", n + 1)),
        }
    }
    let mut resolved = Vec::new();
    if let Some(h) = &header {
        if h.format != datagen::FORMAT
            || h.format_version != datagen::FORMAT_VERSION
            || !datagen::SUPPORTED_GENERATOR_VERSIONS.contains(&h.generator_version)
            || h.menu != datagen::MENU
        {
            errors.push(format!(
                "header is {} v{} generator v{} menu {}; this build expects {} v{} generator {} menu {}",
                h.format, h.format_version, h.generator_version, h.menu,
                datagen::FORMAT, datagen::FORMAT_VERSION,
                datagen::SUPPORTED_GENERATOR_VERSIONS.map(|v| format!("v{v}")).join(" or "), datagen::MENU
            ));
        }
        if records.len() as u32 != h.examples {
            errors.push(format!("{} examples, header says {}", records.len(), h.examples));
        }
        if h.target_pct > 1.0 {
            errors.push(format!("accuracy target {}% pot is looser than 1%", h.target_pct));
        }
        if !done_seen {
            errors.push("file is incomplete (no done line)".into());
        }
        for (i, r) in records.iter().enumerate() {
            if r.inputs.job != h.job || r.inputs.index != i as u32 {
                errors.push(format!("example {i}: job/index {}/{} out of order", r.inputs.job, r.inputs.index));
                continue;
            }
            let expect = datagen::example_inputs_capped_v(h.generator_version, h.job, i as u32, h.max_vram_gb);
            if expect != r.inputs {
                errors.push(format!("example {i}: inputs differ from job {} as generated", h.job));
            }
            if let Some(msg) = sanity(r) {
                errors.push(format!("example {i}: {msg}"));
            }
            if r.exploit_pct_pot > h.target_pct * 1.5 && r.iterations < h.max_iterations {
                errors.push(format!("example {i}: exploitability {}% above target", r.exploit_pct_pot));
            }
        }
        if errors.is_empty() && !records.is_empty() {
            // re-solve a deterministic sample of examples
            let mut rng = datagen::Rng::new(h.job ^ 0x5EED);
            let mut picks: Vec<usize> = Vec::new();
            while picks.len() < o.sample.min(records.len()) {
                let i = rng.below(records.len() as u64) as usize;
                if !picks.contains(&i) {
                    picks.push(i);
                }
            }
            let ro = Opts { target: h.target_pct, max_iters: h.max_iterations, ..parse(&[]) };
            for i in picks {
                let r = &records[i];
                match solve_example(&r.inputs, &ro, env) {
                    Ok(mine) => {
                        let (mean, max) = datagen::compare_values(&mine.values, &r.values);
                        let reach_ok = mine
                            .values
                            .reach
                            .iter()
                            .zip(r.values.reach.iter())
                            .all(|(a, b)| a.iter().zip(b.iter()).all(|(x, y)| (x - y).abs() <= 1e-3 * x.abs().max(1.0)));
                        if !reach_ok {
                            errors.push(format!("example {i}: reach differs from a re-solve"));
                        }
                        if mean > o.max_mean || max > o.max_diff {
                            errors.push(format!(
                                "example {i}: re-solve differs (mean {mean:.4}, max {max:.4} pot)"
                            ));
                        }
                        resolved.push(datagen::VerifyResult { index: i as u32, mean_abs_diff: mean, max_abs_diff: max });
                    }
                    Err(e) => errors.push(format!("example {i}: re-solve failed ({e})")),
                }
            }
        }
    } else {
        errors.push("missing header".into());
    }
    let summary = serde_json::json!({
        "file": file,
        "ok": errors.is_empty(),
        "job": header.as_ref().map(|h| h.job),
        "contributor": header.as_ref().map(|h| h.contributor.clone()),
        "examples": records.len(),
        "errors": errors,
        "resolved": resolved,
    });
    println!("{summary}");
    std::io::stdout().flush().ok();
    if !errors.is_empty() {
        std::process::exit(2);
    }
}

/// Cheap plausibility checks on one record.
fn sanity(r: &ExampleRecord) -> Option<String> {
    // pot-share values net future bets: within [-stack/pot, 1 + stack/pot]
    let spr = r.inputs.stack_bb / r.inputs.pot_bb;
    for p in 0..2 {
        if r.values.reach[p].len() != 169 || r.values.value[p].len() != 169 || r.values.eq[p].len() != 169 {
            return Some("wrong vector length".into());
        }
        for k in 0..169 {
            let reach = r.values.reach[p][k];
            if !reach.is_finite() || reach < 0.0 {
                return Some(format!("bad reach for class {k}"));
            }
            if let Some(e) = r.values.eq[p][k] {
                if !(-1e-3..=1.001).contains(&e) {
                    return Some(format!("equity {e} out of range"));
                }
            }
            if let Some(v) = r.values.value[p][k] {
                if !v.is_finite() || (v as f64) < -spr - 1e-3 || v as f64 > 1.0 + spr + 1e-3 {
                    return Some(format!("value {v} out of range"));
                }
            }
        }
    }
    if !(r.exploit_pct_pot.is_finite() && r.exploit_pct_pot >= 0.0) {
        return Some("bad exploitability".into());
    }
    None
}
