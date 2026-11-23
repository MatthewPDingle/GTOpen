//! `solve-cli datagen`: generate, inspect and verify leaf-value training
//! data (see `solver::datagen` and docs/contribute-compute.md).

use super::{solve_quiet, EnvOpts};
use solver::datagen::{self, ExampleInputs, ExampleRecord, JobHeader, RealHeader};
use solver::datagen_mix::{self, Book, MixSync};
use solver::{Solver, Spot};
use std::io::{BufRead, Write};
use std::path::{Path, PathBuf};
use std::sync::Arc;

const USAGE: &str = "usage:
  solve-cli datagen run --contributor LOGIN [--out DIR] [--jobs N] [--hours H]
                        [--worker I --workers W] [--max-vram GB] [--per-job N] [--target PCT] [--max-iters N]
  solve-cli datagen job JOB [--contributor LOGIN] [--out DIR] [--max-vram GB] [--per-job N] [--target PCT] [--max-iters N]
  solve-cli datagen sizes JOB [--per-job N]   (estimated GPU memory per example)
  solve-cli datagen inputs JOB [INDEX] [--per-job N] [--max-vram GB]
  solve-cli datagen spot JOB INDEX          (the example as a solve-cli spot config)
  solve-cli datagen tree-sizes FILE.jsonl...   (the estimated tree size of every example, for weighing the pool)
  solve-cli datagen verify FILE.jsonl [--sample K] [--max-mean D] [--max-diff D] [--max-vram GB]
                        (a pooled job file or a real-range game file; --max-vram: re-solve only trees that fit)
  solve-cli datagen block LOGIN
  solve-cli datagen mixes                   (the published game mixes and the one being solved now)
  solve-cli datagen situations NAME DIR [DIR ...] [--out FILE]
                        (a situation list for a game mix from `datagen leaves` folders: one entry per leaf)
  solve-cli datagen baseline < examples.jsonl   (Preflop Lab's realization-model values per example)
  solve-cli datagen leafnet NET.bin < examples.jsonl   (a trained leaf net's values per example)
  solve-cli datagen leaves GAME.bin [--out DIR] [--leaves N] [--boards M] [--seed S] [--boards-from EARLIER_DIR]
                        [--tokens W]
                        (a solved preflop game's heads-up flop leaves as examples: DIR/inputs.jsonl, DIR/leaves.json;
                         --boards-from: give each line the flops an earlier export of the same game gave it;
                         --tokens: give every hand a range does not hold this share of its largest weight,
                         0.0001 say, so the flop solves also price the hands just outside each range)
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
    boards_from: Option<PathBuf>,
    /// `datagen leaves`: weight of hands a range does not hold, as a share of its largest (0 = none).
    tokens: f32,
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
        boards_from: None,
        tokens: 0.0,
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
            "--boards-from" => { o.boards_from = Some(PathBuf::from(need(i))); i += 1; }
            "--tokens" => {
                o.tokens = num(need(i), a);
                if !(o.tokens >= 0.0 && o.tokens <= 0.001) {
                    eprintln!("--tokens is a share of a range's largest weight, from 0 to 0.001 (0.0001 is usual)");
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
        tree_bytes: None,
    })
}

fn job_path(out: &Path, contributor: &str, job: u64) -> PathBuf {
    out.join(contributor).join(format!("job-{job}.jsonl"))
}

/// Where this machine remembers the published game mixes and their
/// situation lists: `<out>/.mix`, or the folder in `GTOPEN_MIX_DIR`.
fn mix_dir(o: &Opts) -> PathBuf {
    std::env::var("GTOPEN_MIX_DIR").ok().filter(|v| !v.is_empty()).map(PathBuf::from).unwrap_or_else(|| o.out.join(".mix"))
}

/// Why a job's mix cannot be used.
enum MixProblem {
    /// The job names a mix that was never published: the job is wrong.
    Unknown(String),
    /// This machine cannot tell right now (no network, an old build, a list
    /// that will not download): nothing is wrong with the job.
    Later(String),
}

/// The mixes with mix `id` ready to draw from. The published list is read
/// again when it was last read a while ago or does not hold the mix.
fn mix_for(o: &Opts, id: u32) -> Result<MixSync, MixProblem> {
    let mut sync = MixSync::open(&mix_dir(o));
    let mut read = sync.refresh_if_due();
    if read.is_none() && !sync.book.mixes.contains_key(&id) {
        read = Some(sync.refresh());
    }
    if let Some(needs) = sync.book.too_new.get(&id) {
        return Err(MixProblem::Later(format!(
            "game mix {id} needs generator v{needs} and this build is v{}: update GTOpen (git pull, rebuild)",
            datagen::GENERATOR_VERSION)));
    }
    if !sync.book.mixes.contains_key(&id) {
        return Err(match read {
            Some(Err(e)) => MixProblem::Later(format!("game mix {id} is not known here and the published list could not be read ({e})")),
            _ => MixProblem::Unknown(format!("game mix {id} is not a published mix")),
        });
    }
    sync.load_lists(id).map_err(MixProblem::Later)?;
    Ok(sync)
}

/// The inputs of example `index` of job `job`: from the game mix its number
/// carries, or as generator v4 drew them for an older job number.
fn job_inputs(sync: &mut Option<MixSync>, o: &Opts, job: u64, index: u32, cap: Option<f64>) -> ExampleInputs {
    let id = datagen::job_mix(job);
    if id == 0 {
        return datagen::example_inputs_capped(job, index, cap);
    }
    if sync.is_none() {
        *sync = Some(mix_for(o, id).unwrap_or_else(|e| match e {
            MixProblem::Unknown(msg) | MixProblem::Later(msg) => fail(msg),
        }));
    }
    sync.as_ref().unwrap().book.inputs(id, job, index, cap).unwrap_or_else(|e| fail(e))
}

/// Solve a whole job of game mix `mix` into `<out>/<contributor>/job-<job>.jsonl`
/// (written to a .part file first, renamed when complete).
fn run_job(job: u64, contributor: &str, o: &Opts, env: &EnvOpts, book: &Book, mix: u32) -> Result<PathBuf, String> {
    let key = book.mixes.get(&mix).ok_or_else(|| format!("game mix {mix} is not known"))?.key();
    let path = job_path(&o.out, contributor, job);
    std::fs::create_dir_all(path.parent().unwrap()).map_err(|e| e.to_string())?;
    let part = path.with_extension("jsonl.part");
    let mut f = std::fs::File::create(&part).map_err(|e| format!("{}: {e}", part.display()))?;
    let engine = if use_gpu() { "gpu" } else { "cpu" };
    let cap = vram_cap(o);
    let header = JobHeader::new(job, contributor, o.per_job, o.target, o.max_iters, engine, cap, Some((mix, key)));
    writeln!(f, "{}", serde_json::to_string(&header).unwrap()).map_err(|e| e.to_string())?;
    let t0 = std::time::Instant::now();
    for index in 0..o.per_job {
        let (inputs, tree_bytes) = book.sized_inputs(mix, job, index, cap)?;
        let mut rec = solve_example(&inputs, o, env)?;
        rec.tree_bytes = Some(tree_bytes);
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
            let mut sync = None;
            for i in indices {
                let ex = job_inputs(&mut sync, &o, job, i, o.max_vram.filter(|&x| x > 0.0));
                println!("{}", serde_json::to_string(&ex).unwrap());
            }
        }
        "sizes" => {
            // Survey of tree sizes (estimated GPU memory) over a job's examples.
            let job: u64 = o.positional.first().and_then(|s| s.parse().ok()).unwrap_or(1);
            let mut rows = Vec::new();
            let mut sync = None;
            for i in 0..o.per_job {
                let ex = job_inputs(&mut sync, &o, job, i, None);
                let spot = Spot::new(ex.spot_config()).expect("spot");
                let gb = spot.vram_estimate_bytes() as f64 / 1e9;
                println!("{i:4} {:7} pot {:6.2} stack {:6.1} spr {:5.1} nodes {:8} vram {:6.2} GB",
                    ex.pot_type, ex.pot_bb, ex.stack_bb, ex.stack_bb / ex.pot_bb, spot.tree.nodes.len(), gb);
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
            let cfg = job_inputs(&mut None, &o, job, index, None).spot_config();
            println!("{}", serde_json::to_string_pretty(&cfg).unwrap());
        }
        "job" => {
            let job: u64 = o.positional.first().and_then(|s| s.parse().ok()).unwrap_or_else(|| {
                eprintln!("{USAGE}");
                std::process::exit(1)
            });
            let who = o.contributor.clone().unwrap_or_else(|| "local".into());
            let mix = datagen::job_mix(job);
            if mix == 0 {
                fail(format!("job {job} is a job number of generator v4 or older, which this build checks but no longer solves \
                              (`datagen run` picks the job numbers of the current game mix)"));
            }
            let sync = mix_for(&o, mix).unwrap_or_else(|e| match e {
                MixProblem::Unknown(msg) | MixProblem::Later(msg) => fail(msg),
            });
            match run_job(job, &who, &o, env, &sync.book, mix) {
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
        "tree-sizes" => tree_sizes(&o),
        "mixes" => mixes(&o),
        "situations" => situations(&o),
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
const LEAF_JOB_BASE: u64 = datagen::LEAF_JOB_BASE;

fn fail(msg: String) -> ! {
    eprintln!("{msg}");
    std::process::exit(1)
}

/// Export a solved preflop game's heads-up flop leaves (the ones the learned
/// model corrects) as datagen examples, so exact flop solves can score the
/// realization models on the ranges a real preflop solution produces
/// (tools/datagen/leafcheck.py). The leaves are split evenly over the pot
/// types (limped, single-raised, 3-bet, 4-bet), taking the ones that carry
/// the most chips within each type (the chance of the line, with every
/// seat's actions counted, folds included, times the pot), so rarer pot
/// types are still checked. Each gets `--boards` random flops.
///
/// With `--tokens W` every hand a range does not hold is exported at that
/// share of the range's largest weight ([`datagen::export_range`]), so the
/// flop solves give those hands a value too.
///
/// With `--boards-from EARLIER_DIR` a line that an earlier export of the same
/// game holds gets that export's flops, and every other flop is drawn from the
/// line's name instead of the leaf's rank. Solve a game again (with another
/// net, say) and its leaves can then be compared flop for flop with the
/// earlier solve's: without this most of the difference between two exports
/// is which flops each leaf happened to draw.
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
    let earlier = o.boards_from.as_ref().map(|dir| {
        let text = |name: &str| std::fs::read_to_string(dir.join(name)).unwrap_or_else(|e| fail(format!("{}: {e}", dir.join(name).display())));
        let (positions, kept) = datagen::leaf_boards(&text("leaves.json"), &text("inputs.jsonl")).unwrap_or_else(|e| fail(format!("{}: {e}", dir.display())));
        if positions != s.cfg.positions {
            fail(format!("{}: an export of another game (seats {positions:?}, this game {:?})", dir.display(), s.cfg.positions));
        }
        kept
    });
    let (mut kept_leaves, mut kept_boards) = (0usize, 0usize);
    std::fs::create_dir_all(&o.out).unwrap_or_else(|e| fail(format!("{}: {e}", o.out.display())));
    let r3 = |w: &[f32]| datagen::export_range(w, o.tokens);
    let r2 = |x: f64| (x * 100.0).round() / 100.0;
    let mut inputs = String::new();
    let mut described = Vec::new();
    for (rank, leaf) in all.iter().enumerate() {
        let job = LEAF_JOB_BASE + rank as u64;
        let line = datagen::line_key(&leaf.path);
        let before = earlier.as_ref().and_then(|k| k.get(&line));
        if let Some(b) = before {
            if (b.pot_bb - leaf.pot_bb).abs() > 0.011 || (b.stack_bb - leaf.stack_bb).abs() > 0.011 {
                fail(format!("{}: an export of another game (the line {line} has pot {} and stack {} there, {} and {} here)",
                             o.boards_from.as_ref().unwrap().display(), b.pot_bb, b.stack_bb, leaf.pot_bb, leaf.stack_bb));
            }
            kept_leaves += 1;
        }
        for index in 0..o.boards {
            let board = match (before.and_then(|b| b.boards.get(index as usize)), &earlier) {
                (Some(board), _) => {
                    kept_boards += 1;
                    board.clone()
                }
                (None, Some(_)) => datagen::line_flop(o.seed, &line, index),
                (None, None) => {
                    let mut rng = datagen::Rng::new(o.seed.wrapping_mul(0x9E37_79B9_7F4A_7C15) ^ job.wrapping_mul(31) ^ index as u64);
                    datagen::random_flop(&mut rng)
                }
            };
            let ex = ExampleInputs {
                job, index, board,
                pot_type: POT_TYPES[leaf.raises.min(3) as usize].to_string(),
                pot_bb: r2(leaf.pot_bb), stack_bb: r2(leaf.stack_bb),
                rake_pct: s.cfg.rake_pct / 100.0, rake_cap_bb: s.cfg.rake_cap,
                range: [r3(&leaf.range[0]), r3(&leaf.range[1])], attempt: 0, pot_scale: 1.0, situation: None,
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
    let mut summary = serde_json::json!({
        "game": game, "realization": s.cfg.realization, "iteration": s.iteration, "positions": s.cfg.positions,
        "leaves_in_game": s.hu_flop_leaves().len(), "exported": all.len(), "boards_per_leaf": o.boards,
        "chip_share_covered": covered / total.max(1e-12), "leaves": described,
    });
    if o.tokens > 0.0 {
        summary["tokens"] = serde_json::json!(o.tokens);
    }
    if earlier.is_some() {
        // how much of this export can be compared flop for flop with the earlier one
        summary["boards_kept"] = serde_json::json!({"leaves": kept_leaves, "examples": kept_boards});
    }
    let write = |name: &str, text: String| {
        let p = o.out.join(name);
        std::fs::write(&p, text).unwrap_or_else(|e| fail(format!("{}: {e}", p.display())));
    };
    write("inputs.jsonl", inputs);
    write("leaves.json", serde_json::to_string_pretty(&summary).unwrap());
    let per_type: Vec<String> = POT_TYPES.iter().zip(&quota).map(|(t, q)| format!("{q} {t}")).collect();
    println!("{} leaves ({}) x {} boards ({:.0}% of the chips that reach heads-up flops) -> {}",
             all.len(), per_type.join(", "), o.boards, 100.0 * covered / total.max(1e-12), o.out.join("inputs.jsonl").display());
    if earlier.is_some() {
        println!("{kept_leaves} of the {} lines are in the earlier export and keep its flops ({kept_boards} examples)", all.len());
    }
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

/// Lines a long run prints once and then only hourly, however often their cause comes round.
#[derive(Default)]
struct Said(std::collections::HashMap<String, (String, std::time::Instant)>);

impl Said {
    fn say(&mut self, about: &str, line: String) {
        match self.0.get(about) {
            Some((last, when)) if *last == line && when.elapsed().as_secs() < 3600 => {}
            _ => {
                println!("{line}");
                self.0.insert(about.to_string(), (line, std::time::Instant::now()));
            }
        }
    }
    fn forget(&mut self, about: &str) {
        self.0.remove(about);
    }
}

/// `datagen mixes`: the published game mixes as this machine sees them.
fn mixes(o: &Opts) {
    let mut sync = MixSync::open(&mix_dir(o));
    match sync.refresh() {
        Ok(skipped) => skipped.iter().for_each(|s| println!("note: {s}")),
        Err(e) => println!("could not read the published list ({e}); showing what this machine has"),
    }
    let (current, passed) = sync.choose();
    passed.iter().for_each(|p| println!("note: {p}"));
    for m in sync.book.mixes.values() {
        let state = if m.withdrawn { "withdrawn" } else if Some(m.id) == current { "CURRENT" } else { "earlier" };
        println!("mix {:3}  {state:9}  key {}  {} ({})", m.id, m.key(), m.note, m.summary());
    }
    for (id, needs) in &sync.book.too_new {
        println!("mix {id:3}  needs generator v{needs} (this build is v{}): update GTOpen to solve it", datagen::GENERATOR_VERSION);
    }
}

/// `datagen situations NAME DIR...`: a situation list for a game mix, one
/// entry per leaf of each `datagen leaves` folder (its ranges, pot, stack
/// and rake; the flops are left to the generator). Prints the file's SHA-256
/// and the part to put in a mix. The ranges must be the output of a GTOpen
/// solve: the list is published in the public dataset.
fn situations(o: &Opts) {
    let Some((name, dirs)) = o.positional.split_first().filter(|(_, d)| !d.is_empty()) else { fail(USAGE.into()) };
    if !datagen::plain_name(name) {
        fail(format!("the list name {name:?} must be letters, digits, - or _ only"));
    }
    let mut text = String::new();
    let mut n = 0usize;
    for dir in dirs {
        let dir = PathBuf::from(dir);
        let game = dir.file_name().map(|x| x.to_string_lossy().into_owned()).unwrap_or_default();
        let read = |file: &str| std::fs::read_to_string(dir.join(file)).unwrap_or_else(|e| fail(format!("{}: {e}", dir.join(file).display())));
        let described: serde_json::Value = serde_json::from_str(&read("leaves.json")).unwrap_or_else(|e| fail(format!("{}: {e}", dir.join("leaves.json").display())));
        let mut lines = std::collections::HashMap::new();
        for leaf in described["leaves"].as_array().map(|a| a.as_slice()).unwrap_or(&[]) {
            if let (Some(job), Some(path)) = (leaf["job"].as_u64(), leaf["path"].as_array()) {
                let path: Vec<String> = path.iter().map(|x| x.as_str().map(String::from).unwrap_or_else(|| x.to_string())).collect();
                lines.insert(job, datagen::line_key(&path));
            }
        }
        let mut seen = std::collections::BTreeSet::new();
        for line in read("inputs.jsonl").lines().filter(|l| !l.trim().is_empty()) {
            let ex: ExampleInputs = serde_json::from_str(line).unwrap_or_else(|e| fail(format!("{}: {e}", dir.join("inputs.jsonl").display())));
            if !seen.insert(ex.job) {
                continue; // one entry per leaf, whatever flops it was exported with
            }
            let s = datagen_mix::Situation {
                kind: "situation".into(),
                id: format!("{game}:{}", ex.job.saturating_sub(LEAF_JOB_BASE)),
                pot_type: ex.pot_type, pot_bb: ex.pot_bb, stack_bb: ex.stack_bb,
                rake_pct: ex.rake_pct, rake_cap_bb: ex.rake_cap_bb, range: ex.range, weight: 1.0,
                about: Some(serde_json::json!({"game": game, "line": lines.get(&ex.job)})),
            };
            text.push_str(&serde_json::to_string(&s).unwrap());
            text.push('\n');
            n += 1;
        }
    }
    let header = serde_json::json!({"type": "header", "format": datagen_mix::SITUATIONS_FORMAT, "format_version": 1,
                                    "list": name, "situations": n});
    let text = format!("{header}\n{text}");
    if let Err(e) = datagen_mix::SituationList::parse(&text) {
        fail(format!("the list would not be accepted: {e}"));
    }
    let out = if o.out.extension().map(|e| e == "jsonl").unwrap_or(false) { o.out.clone() } else { o.out.join(format!("{name}.jsonl")) };
    if let Some(parent) = out.parent().filter(|p| !p.as_os_str().is_empty()) {
        std::fs::create_dir_all(parent).unwrap_or_else(|e| fail(format!("{}: {e}", parent.display())));
    }
    std::fs::write(&out, &text).unwrap_or_else(|e| fail(format!("{}: {e}", out.display())));
    let sha = datagen_mix::sha256_hex(text.as_bytes());
    println!("{n} situations -> {}", out.display());
    println!("publish it as situations/{name}.jsonl in the dataset (python tools/datagen/validate.py --publish-situations {}),", out.display());
    println!("then add a mix to tools/datagen/mixes.json with this part (set the share):");
    println!("{}", serde_json::json!({"kind": "situations", "share": 0.5, "list": name, "sha256": sha}));
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
    // The game mix is read again before every job (at most every few minutes), so a new one is picked up
    // without anyone restarting anything. The folder remembers the newest list for a start without a network.
    let mut sync = MixSync::open(&mix_dir(o));
    let mut said = Said::default();
    let mut mix: Option<u32> = None;
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
        match sync.refresh_if_due() {
            Some(Err(e)) => said.say("read", format!("could not look for a new game mix ({e}); carrying on with the one this machine has")),
            Some(Ok(skipped)) => {
                said.forget("read");
                for s in skipped {
                    said.say(&s, format!("published game mixes: {s}"));
                }
            }
            None => {}
        }
        let (chosen, passed) = sync.choose();
        for p in passed {
            said.say(&p, format!("game {p}; solving the mix before it meanwhile"));
        }
        let Some(id) = chosen else {
            eprintln!("no game mix can be drawn on this machine: update GTOpen (git pull) and start again");
            std::process::exit(1);
        };
        if let Some((newer, needs)) = sync.book.needs_update() {
            said.say("update", format!(
                "PLEASE UPDATE: the pool has moved to game mix {newer}, which needs a newer GTOpen (generator v{needs}, this is v{}). \
                 Stop this window, run  git pull  and start it again. Until then this machine keeps solving mix {id}, which still counts.",
                datagen::GENERATOR_VERSION));
        }
        if mix != Some(id) {
            let m = &sync.book.mixes[&id];
            match mix {
                None => println!("game mix {id}: {} ({})", m.note, m.summary()),
                Some(old) => println!("NEW GAME MIX: moving from mix {old} to mix {id}: {} ({}). Nothing to do on your side.", m.note, m.summary()),
            }
            if let Some(note) = m.card_note(vram_cap(o)) {
                println!("game mix {id}: {note}");
            }
            mix = Some(id);
            k = o.worker;
        }
        let job = datagen::mix_job(&login, id, k);
        k += o.workers;
        if job_path(&o.out, &login, job).exists() {
            continue; // finished in an earlier run
        }
        let tj = std::time::Instant::now();
        match run_job(job, &login, o, env, &sync.book, id) {
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

/// `datagen tree-sizes FILE...`: the estimated tree size of every example of
/// pooled job files, one line `{"job":J,"index":I,"tree_bytes":B}` each, in
/// the files' order. An example that records its size (generator v6 on) is
/// read; for an older one the tree is built to count it (no solve, no GPU,
/// about a fifth of a second of one core each, all cores used). Training
/// uses the sizes to weigh the pool as its mix intends (tools/leafnet/balance.py).
fn tree_sizes(o: &Opts) {
    use rayon::prelude::*;
    if o.positional.is_empty() {
        eprintln!("{USAGE}");
        std::process::exit(1);
    }
    let mut out = std::io::stdout().lock();
    for file in &o.positional {
        let text = std::fs::read_to_string(file).unwrap_or_else(|e| fail(format!("{file}: {e}")));
        let records: Vec<ExampleRecord> = text
            .lines()
            .filter(|l| !l.trim().is_empty())
            .map(|l| serde_json::from_str::<serde_json::Value>(l).unwrap_or_else(|e| fail(format!("{file}: not JSON ({e})"))))
            .filter(|v| v["type"] == "example")
            .map(|v| serde_json::from_value(v).unwrap_or_else(|e| fail(format!("{file}: bad example ({e})"))))
            .collect();
        let sizes: Vec<u64> = records
            .par_iter()
            .map(|r| r.tree_bytes.unwrap_or_else(|| datagen::estimated_vram_bytes(&r.inputs)))
            .collect();
        for (r, bytes) in records.iter().zip(sizes) {
            writeln!(out, "{{\"job\":{},\"index\":{},\"tree_bytes\":{bytes}}}", r.inputs.job, r.inputs.index).ok();
        }
    }
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
    let mut real: Option<RealHeader> = None;
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
            Some("header") if n == 0 && v["format"].as_str() == Some(datagen::REAL_FORMAT) => {
                match serde_json::from_value::<RealHeader>(v) {
                    Ok(h) => real = Some(h),
                    Err(e) => errors.push(format!("bad header: {e}")),
                }
            }
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
    if let Some(h) = &real {
        verify_real(file, h, &records, done_seen, errors, o, env);
    }
    let mut resolved = Vec::new();
    // generator v5 on: the game mix the job says it was drawn from
    let mut book: Option<Book> = None;
    if let Some(h) = header.as_ref().filter(|h| h.generator_version > datagen::LAST_CODED_GENERATOR
                                                 && datagen::ACCEPTED_GENERATORS.contains(&h.generator_version)) {
        match h.mix {
            None => errors.push("the header names no game mix".into()),
            Some(id) if datagen::job_mix(h.job) != id => {
                errors.push(format!("job {} is not a job number of game mix {id}", h.job))
            }
            Some(id) => match mix_for(o, id) {
                Ok(sync) => {
                    let mix = &sync.book.mixes[&id];
                    if mix.withdrawn {
                        errors.push(format!("game mix {id} was withdrawn: its jobs are no longer accepted"));
                    } else if h.mix_key.as_deref() != Some(mix.key().as_str()) {
                        errors.push(format!("drawn from another version of game mix {id} (key {}, the published mix has {})",
                                            h.mix_key.as_deref().unwrap_or("none"), mix.key()));
                    } else {
                        book = Some(sync.book);
                    }
                }
                Err(MixProblem::Unknown(msg)) => errors.push(msg),
                Err(MixProblem::Later(msg)) => {
                    // nothing wrong with the upload: this machine cannot check it now
                    eprintln!("cannot check {file} now: {msg}");
                    std::process::exit(3);
                }
            },
        }
    } else if let Some(h) = header.as_ref().filter(|h| datagen::job_mix(h.job) != 0) {
        errors.push(format!("job {} is not a job number of generator v{}", h.job, h.generator_version));
    }
    if let Some(h) = &header {
        if h.format != datagen::FORMAT
            || h.format_version != datagen::FORMAT_VERSION
            || !datagen::ACCEPTED_GENERATORS.contains(&h.generator_version)
            || h.menu != datagen::MENU
        {
            errors.push(format!(
                "header is {} v{} generator v{} menu {}; this build expects {} v{} generator {:?} menu {}",
                h.format, h.format_version, h.generator_version, h.menu,
                datagen::FORMAT, datagen::FORMAT_VERSION, datagen::ACCEPTED_GENERATORS, datagen::MENU
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
            // the tree size every example records from generator v6 on is drawn again with the inputs
            let sized = h.generator_version >= datagen_mix::CARD_RULES_GENERATOR;
            let expect = if h.generator_version <= datagen::LAST_CODED_GENERATOR {
                Some((datagen::example_inputs_for(h.generator_version, h.job, i as u32, h.max_vram_gb), None))
            } else if sized {
                // no book: the mix itself was refused above
                book.as_ref().and_then(|b| b.sized_inputs(h.mix.unwrap_or(0), h.job, i as u32, h.max_vram_gb).ok())
                    .map(|(e, bytes)| (e, Some(bytes)))
            } else {
                book.as_ref().and_then(|b| b.inputs(h.mix.unwrap_or(0), h.job, i as u32, h.max_vram_gb).ok()).map(|e| (e, None))
            };
            if expect.as_ref().map(|e| e.0 != r.inputs).unwrap_or(false) {
                errors.push(format!("example {i}: inputs differ from job {} as generated", h.job));
            } else if sized && expect.as_ref().map(|e| e.1 != r.tree_bytes).unwrap_or(false) {
                errors.push(format!("example {i}: tree_bytes {:?} is not the size of its tree ({:?})",
                                    r.tree_bytes, expect.as_ref().and_then(|e| e.1)));
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
                resolve_check(i, &records[i], &ro, o, env, &mut errors, &mut resolved);
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
        "mix": header.as_ref().and_then(|h| h.mix),
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

/// Solve example `i` again and compare it with the uploaded record.
fn resolve_check(i: usize, r: &ExampleRecord, ro: &Opts, o: &Opts, env: &EnvOpts,
                 errors: &mut Vec<String>, resolved: &mut Vec<datagen::VerifyResult>) {
    match solve_example(&r.inputs, ro, env) {
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
                errors.push(format!("example {i}: re-solve differs (mean {mean:.4}, max {max:.4} pot)"));
            }
            resolved.push(datagen::VerifyResult { index: i as u32, mean_abs_diff: mean, max_abs_diff: max });
        }
        Err(e) => errors.push(format!("example {i}: re-solve failed ({e})")),
    }
}

/// Check a real-range game file (`datagen::REAL_FORMAT`): the header, every
/// example's inputs and values for plausibility, and a re-solve of a
/// sample. The ranges come from a preflop solve, so there is nothing to
/// regenerate them from; any ranges are valid inputs, and what a re-solve
/// protects is the values. With --max-vram only trees estimated to fit
/// that many GB are re-solved (the others still get the cheap checks), so
/// a validator that shares its GPU can keep the biggest trees off it.
fn verify_real(file: &str, h: &RealHeader, records: &[ExampleRecord], done_seen: bool,
               mut errors: Vec<String>, o: &Opts, env: &EnvOpts) -> ! {
    if h.format_version != datagen::REAL_FORMAT_VERSION || h.menu != datagen::MENU {
        errors.push(format!(
            "header is {} v{} menu {}; this build expects v{} menu {}",
            h.format, h.format_version, h.menu, datagen::REAL_FORMAT_VERSION, datagen::MENU
        ));
    }
    for (what, name) in [("contributor", &h.contributor), ("set", &h.set), ("game", &h.game)] {
        if !datagen::plain_name(name) {
            errors.push(format!("{what} {name:?} is not a plain name (letters, digits, - or _)"));
        }
    }
    if records.len() as u32 != h.examples {
        errors.push(format!("{} examples, header says {}", records.len(), h.examples));
    }
    if records.is_empty() {
        errors.push("no examples".into());
    }
    if h.target_pct > 1.0 {
        errors.push(format!("accuracy target {}% pot is looser than 1%", h.target_pct));
    }
    if !done_seen {
        errors.push("file is incomplete (no done line)".into());
    }
    let mut seen = std::collections::HashSet::new();
    for (i, r) in records.iter().enumerate() {
        if r.inputs.job < LEAF_JOB_BASE || !seen.insert((r.inputs.job, r.inputs.index)) {
            errors.push(format!("example {i}: leaf/board {}/{} repeats or is not a leaf number", r.inputs.job, r.inputs.index));
            continue;
        }
        if let Some(msg) = datagen::check_real_inputs(&r.inputs) {
            errors.push(format!("example {i}: {msg}"));
            continue;
        }
        if let Some(msg) = sanity(r) {
            errors.push(format!("example {i}: {msg}"));
        }
        if r.exploit_pct_pot > h.target_pct * 1.5 && r.iterations < h.max_iterations {
            errors.push(format!("example {i}: exploitability {}% above target", r.exploit_pct_pot));
        }
    }
    let mut resolved = Vec::new();
    let mut over_cap = 0usize;
    if errors.is_empty() {
        // a fixed shuffle of the examples, from the game's name: the same file is always sampled the same way
        let mut seed = 0xcbf2_9ce4_8422_2325u64;
        for b in h.set.bytes().chain(h.game.bytes()) {
            seed = (seed ^ b as u64).wrapping_mul(0x0000_0100_0000_01b3);
        }
        let mut rng = datagen::Rng::new(seed ^ 0x5EED ^ records.len() as u64);
        let mut order: Vec<usize> = (0..records.len()).collect();
        for i in (1..order.len()).rev() {
            order.swap(i, rng.below(i as u64 + 1) as usize);
        }
        let cap = o.max_vram.filter(|&x| x > 0.0);
        let ro = Opts { target: h.target_pct, max_iters: h.max_iterations, ..parse(&[]) };
        for i in order {
            if resolved.len() >= o.sample {
                break;
            }
            if let Some(gb) = cap {
                if datagen::estimated_vram_bytes(&records[i].inputs) as f64 / 1e9 > gb {
                    over_cap += 1;
                    continue;
                }
            }
            let before = resolved.len();
            resolve_check(i, &records[i], &ro, o, env, &mut errors, &mut resolved);
            if resolved.len() == before {
                break; // the re-solve itself failed: reported above
            }
        }
        if errors.is_empty() && resolved.is_empty() && o.sample > 0 {
            // nothing else stands behind a real-range file's values
            errors.push(format!("no example was re-solved: none of the {} fits --max-vram", records.len()));
        }
    }
    let summary = serde_json::json!({
        "file": file,
        "ok": errors.is_empty(),
        "kind": "real",
        "contributor": h.contributor,
        "set": h.set,
        "game": h.game,
        "examples": records.len(),
        "errors": errors,
        "resolved": resolved,
        "skipped_over_cap": over_cap,
    });
    println!("{summary}");
    std::io::stdout().flush().ok();
    std::process::exit(if errors.is_empty() { 0 } else { 2 })
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
