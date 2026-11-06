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
  solve-cli datagen sizes JOB [--per-job N]   (estimated GPU memory per example)
  solve-cli datagen inputs JOB [INDEX] [--per-job N] [--max-vram GB]
  solve-cli datagen spot JOB INDEX          (the example as a solve-cli spot config)
  solve-cli datagen verify FILE.jsonl [--sample K] [--max-mean D] [--max-diff D]
  solve-cli datagen block LOGIN";

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
                let ex = datagen::example_inputs_capped(job, i, o.max_vram.filter(|&x| x > 0.0));
                println!("{}", serde_json::to_string(&ex).unwrap());
            }
        }
        "sizes" => {
            // Survey of tree sizes (estimated GPU memory) over a job's examples.
            let job: u64 = o.positional.first().and_then(|s| s.parse().ok()).unwrap_or(1);
            let mut rows = Vec::new();
            for i in 0..o.per_job {
                let ex = datagen::example_inputs(job, i);
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
            let cfg = datagen::example_inputs(job, index).spot_config();
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
        "run" => run_loop(&o, env),
        "verify" => verify(&o, env),
        _ => {
            eprintln!("{USAGE}");
            std::process::exit(1);
        }
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
            || h.generator_version != datagen::GENERATOR_VERSION
            || h.menu != datagen::MENU
        {
            errors.push(format!(
                "header is {} v{} generator v{} menu {}; this build expects {} v{} generator v{} menu {}",
                h.format, h.format_version, h.generator_version, h.menu,
                datagen::FORMAT, datagen::FORMAT_VERSION, datagen::GENERATOR_VERSION, datagen::MENU
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
            let expect = datagen::example_inputs_capped(h.job, i as u32, h.max_vram_gb);
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
