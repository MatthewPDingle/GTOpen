//! Three-player jobs of `solve-cli datagen` (see `solver::datagen3`): the
//! generator's job loop for a three-player game mix, and the check of such
//! a job file.

use super::{fail, mix_for, use_gpu, MixProblem, Opts};
use solver::datagen::{self, JobHeader};
use solver::datagen3::{self, Inputs3, Record3, Skipped3};
use solver::datagen_mix::Book;
use solver::multiway::{MwSolver, MwSpot, NP};
use std::io::{BufRead, Write};
use std::path::{Path, PathBuf};
use std::sync::Arc;

/// Re-solves of a check may differ from the upload by this much (fractions
/// of the pot: reach-weighted mean, and the largest class with real reach).
/// Wider than the heads-up pool's limits: a three-player game has more than
/// one equilibrium, and two cards do not round alike.
pub const MAX_MEAN3: f64 = 0.03;
pub const MAX_DIFF3: f64 = 0.30;
/// A check re-solves only examples whose estimated solve is at most this
/// big (GB), so a validator stays quick and fits beside a generator.
pub const RECHECK_GB: f64 = 8.0;
/// Most examples of one job file a check solves again.
pub const RECHECK_MOST: usize = 2;

pub fn job_path3(out: &Path, contributor: &str, job: u64) -> PathBuf {
    out.join(contributor).join(format!("job3-{job}.jsonl"))
}

fn header3(job: u64, contributor: &str, o: &Opts, examples: u32, cap: Option<f64>, mix: (u32, String)) -> JobHeader {
    let engine = if use_gpu() { "gpu" } else { "cpu" };
    let mut h = JobHeader::new(job, contributor, examples, o.target, o.max_iters, engine, cap, Some(mix));
    h.format = datagen3::FORMAT3.into();
    h.format_version = datagen3::FORMAT3_VERSION;
    h.menu = datagen3::MENU3.into();
    h
}

/// What a solve gives back: iterations, each player's gap in chips, each
/// player's root value per hand, how it ended.
type Solved = (u32, [f64; NP], [Vec<f32>; NP], &'static str);

fn gaps_of(spot: &MwSpot, best: &[Vec<f32>; NP], avg: &[Vec<f32>; NP]) -> [f64; NP] {
    let denom = spot.root_triple_mass();
    std::array::from_fn(|p| {
        let w = &spot.weights[p];
        let dot = |v: &[f32]| w.iter().zip(v).map(|(&a, &b)| a as f64 * b as f64).sum::<f64>() / denom;
        (dot(&best[p]) - dot(&avg[p])).max(0.0)
    })
}

/// `GTOPEN_TRACE=1` prints every accuracy check of a solve (for timing a card).
fn trace(iteration: u32, pct: f64, t0: std::time::Instant) {
    if std::env::var("GTOPEN_TRACE").map_or(false, |v| v == "1") {
        eprintln!("    iter {iteration:4}  exploit {pct:7.3}% of pot  {:7.1} s", t0.elapsed().as_secs_f64());
    }
}

fn ended(pct: f64, iteration: u32, t0: std::time::Instant, o: &Opts) -> Option<&'static str> {
    if pct <= o.target {
        Some("target")
    } else if iteration >= o.max_iters {
        Some("iterations")
    } else if t0.elapsed().as_secs_f64() >= o.max_minutes * 60.0 {
        Some("time")
    } else {
        None
    }
}

#[cfg(feature = "gpu")]
fn solve_gpu(spot: &Arc<MwSpot>, o: &Opts) -> Result<Solved, String> {
    use solver::multiway::gpu::{MwGpuOptions, MwGpuSolver};
    // One solve-cli at a time on a card: the free memory read below is only
    // true while no other solve is about to allocate. Held until the solve ends.
    let _turn = solver::gpu_turn::take();
    let (free, total) = solver::gpu::vram_info_mb().ok_or("the graphics card's memory could not be read")?;
    let budget = free.saturating_sub(1024).min(total * 88 / 100).saturating_sub((o.reserve_gb * 1000.0) as u64) * 1_000_000;
    let opts = MwGpuOptions { budget_bytes: Some(budget), ..Default::default() };
    let mut g = MwGpuSolver::with_options(spot.clone(), solver::Algorithm::Dcfr, &opts)?;
    let pot = spot.tree.config.starting_pot;
    let t0 = std::time::Instant::now();
    loop {
        g.iterate()?;
        g.synchronize()?;
        let late = t0.elapsed().as_secs_f64() >= o.max_minutes * 60.0;
        if g.iteration % 20 == 0 || g.iteration >= o.max_iters || late {
            let (best, avg) = g.root_values_all()?;
            let gaps = gaps_of(spot, &best, &avg);
            let pct = gaps.iter().sum::<f64>() / NP as f64 / pot * 100.0;
            trace(g.iteration, pct, t0);
            if let Some(why) = ended(pct, g.iteration, t0, o) {
                return Ok((g.iteration, gaps, avg, why));
            }
        }
    }
}

fn solve_cpu(spot: &Arc<MwSpot>, o: &Opts) -> Result<Solved, String> {
    use solver::multiway::solver::Dealt;
    let mut s = MwSolver::new(spot.clone(), solver::Storage::Compressed);
    let pot = spot.tree.config.starting_pot;
    let t0 = std::time::Instant::now();
    loop {
        s.iterate();
        let late = t0.elapsed().as_secs_f64() >= o.max_minutes * 60.0;
        if s.iteration % 20 == 0 || s.iteration >= o.max_iters || late {
            let w = &spot.weights;
            let reach = [&w[0][..], &w[1][..], &w[2][..]];
            let best: [Vec<f32>; NP] = std::array::from_fn(|p| s.node_values(0, p, reach, Dealt::default(), true));
            let avg: [Vec<f32>; NP] = std::array::from_fn(|p| s.node_values(0, p, reach, Dealt::default(), false));
            let gaps = gaps_of(spot, &best, &avg);
            let pct = gaps.iter().sum::<f64>() / NP as f64 / pot * 100.0;
            trace(s.iteration, pct, t0);
            if let Some(why) = ended(pct, s.iteration, t0, o) {
                return Ok((s.iteration, gaps, avg, why));
            }
        }
    }
}

/// Solve one example; an error means this machine could not (the tree did
/// not fit the card right now, say), not that the example is wrong.
pub fn solve_example3(inputs: &Inputs3, tree_bytes: u64, o: &Opts) -> Result<Record3, String> {
    let t0 = std::time::Instant::now();
    let spot = Arc::new(MwSpot::new(inputs.spot_config())?);
    #[cfg(feature = "gpu")]
    let solved = if use_gpu() { solve_gpu(&spot, o) } else { solve_cpu(&spot, o) };
    #[cfg(not(feature = "gpu"))]
    let solved = solve_cpu(&spot, o);
    let (iterations, gaps, cfv, why) = solved?;
    let pot = spot.tree.config.starting_pot;
    let r4 = |x: f64| (x * 10_000.0).round() / 10_000.0;
    Ok(Record3 {
        kind: "example".into(),
        inputs: inputs.clone(),
        values: datagen3::class_values(&spot, &cfv),
        iterations,
        exploit_pct_pot: r4(gaps.iter().sum::<f64>() / NP as f64 / pot * 100.0),
        gaps_pct_pot: gaps.map(|g| r4(g / pot * 100.0)),
        ended: why.into(),
        seconds: (t0.elapsed().as_secs_f64() * 100.0).round() / 100.0,
        tree_bytes,
    })
}

/// The lines of an unfinished job file that can be kept: the examples (and
/// skips) in order from index 0, when the file starts with this very header.
fn kept_lines(part: &Path, header: &str, job: u64) -> Vec<String> {
    let Ok(text) = std::fs::read_to_string(part) else { return Vec::new() };
    let mut lines = text.lines();
    let same = |a: &str, b: &str| serde_json::from_str::<serde_json::Value>(a).ok() == serde_json::from_str::<serde_json::Value>(b).ok();
    if !lines.next().map_or(false, |first| same(first, header)) {
        return Vec::new();
    }
    let mut kept = Vec::new();
    for line in lines {
        let index = kept.len() as u32;
        let ok = match serde_json::from_str::<serde_json::Value>(line) {
            Ok(v) if v["type"] == "example" => {
                serde_json::from_value::<Record3>(v).map_or(false, |r| r.inputs.job == job && r.inputs.index == index)
            }
            Ok(v) if v["type"] == "skipped" => {
                serde_json::from_value::<Skipped3>(v).map_or(false, |s| s.job == job && s.index == index)
            }
            _ => false,
        };
        if !ok {
            break; // a line cut short when the machine went down, or the done line
        }
        kept.push(line.to_string());
    }
    kept
}

/// Solve a whole three-player job of game mix `mix` into
/// `<out>/<contributor>/job3-<job>.jsonl`. The job is written to a .part
/// file an example at a time and renamed when complete; a .part file left
/// by an earlier run of the same job is carried on from where it stopped.
pub fn run_job3(job: u64, contributor: &str, o: &Opts, book: &Book, mix: u32, cap: Option<f64>) -> Result<PathBuf, String> {
    let key = book.mixes.get(&mix).ok_or_else(|| format!("game mix {mix} is not known"))?.key();
    let per_job = if o.per_job_set { o.per_job } else { datagen3::DEFAULT_PER_JOB3 };
    let path = job_path3(&o.out, contributor, job);
    std::fs::create_dir_all(path.parent().unwrap()).map_err(|e| e.to_string())?;
    let part = path.with_extension("jsonl.part");
    let header = serde_json::to_string(&header3(job, contributor, o, per_job, cap, (mix, key))).unwrap();
    let kept = kept_lines(&part, &header, job);
    let mut f = std::fs::File::create(&part).map_err(|e| format!("{}: {e}", part.display()))?;
    writeln!(f, "{header}").map_err(|e| e.to_string())?;
    for line in &kept {
        writeln!(f, "{line}").map_err(|e| e.to_string())?;
    }
    f.sync_all().ok();
    if !kept.is_empty() {
        println!("  job {job}: carrying on after {} of {per_job} examples from an earlier run", kept.len());
    }
    // How often each example was started: a machine that goes down (or a watchdog that
    // stops a stuck generator) twice in the same example leaves that one out next time,
    // so one bad solve cannot hold a machine for good.
    let tries = part.with_extension("part.tries");
    let t0 = std::time::Instant::now();
    for index in kept.len() as u32..per_job {
        let (inputs, tree_bytes) = book.sized_inputs3(mix, job, index, cap)?;
        let fits = cap.map_or(true, |c| tree_bytes as f64 <= c * 1e9);
        let before = std::fs::read_to_string(&tries).ok()
            .and_then(|t| t.trim().split_once(' ').map(|(i, n)| (i.parse::<u32>().ok(), n.parse::<u32>().unwrap_or(0))))
            .filter(|(i, _)| *i == Some(index)).map_or(0, |(_, n)| n);
        std::fs::write(&tries, format!("{index} {}\n", before + 1)).ok();
        let mut result = if !fits {
            Err("no draw fits this card".to_string())
        } else if before >= 2 {
            Err("stopped twice before it finished".to_string())
        } else {
            solve_example3(&inputs, tree_bytes, o)
        };
        let fits = fits && before < 2;
        if fits && result.is_err() && use_gpu() {
            // something else may have had the card's memory for a moment: one more try
            eprintln!("  job {job} #{index:3}  could not be solved ({}); trying once more in a minute", result.as_ref().unwrap_err());
            std::thread::sleep(std::time::Duration::from_secs(60));
            result = solve_example3(&inputs, tree_bytes, o);
        }
        let line = match result {
            Ok(rec) => {
                println!(
                    "  job {job} #{index:3}  {:8} {:6} pot {:6.2}bb stack {:6.1}bb  {:4.1} GB  iter {:4}  exploit {:5.2}%  [{:.1} min, {}]",
                    rec.inputs.board, rec.inputs.pot_type, rec.inputs.pot_bb, rec.inputs.stack_bb, tree_bytes as f64 / 1e9,
                    rec.iterations, rec.exploit_pct_pot, rec.seconds / 60.0, rec.ended
                );
                serde_json::to_string(&rec).unwrap()
            }
            Err(reason) => {
                println!("  job {job} #{index:3}  {:8} {:6} pot {:6.2}bb stack {:6.1}bb  {:4.1} GB  left out: {reason}",
                         inputs.board, inputs.pot_type, inputs.pot_bb, inputs.stack_bb, tree_bytes as f64 / 1e9);
                let reason: String = reason.chars().filter(|c| !c.is_control()).take(200).collect();
                serde_json::to_string(&Skipped3 { kind: "skipped".into(), job, index, reason }).unwrap()
            }
        };
        writeln!(f, "{line}").map_err(|e| e.to_string())?;
        f.sync_all().ok();
    }
    let done = serde_json::json!({
        "type": "done", "examples": per_job, "seconds": (t0.elapsed().as_secs_f64() * 10.0).round() / 10.0,
    });
    writeln!(f, "{done}").map_err(|e| e.to_string())?;
    f.sync_all().ok();
    drop(f);
    std::fs::remove_file(&tries).ok();
    std::fs::rename(&part, &path).map_err(|e| e.to_string())?;
    Ok(path)
}

/// `datagen sizes3 [--contributor LOGIN] [--jobs N]`: what the first jobs
/// of the current three-player mix hold for this card: each example's pot,
/// hands and estimated size, and on a GPU build what the card would really
/// plan for it. For tuning the estimate against real cards.
pub fn sizes3(o: &Opts) {
    let cap = super::vram_cap(o);
    let mut sync = solver::datagen_mix::MixSync::open(&super::mix_dir(o));
    let _ = sync.refresh_if_due();
    let Some(id) = sync.book.open_ids().into_iter().find(|id| sync.book.mixes[id].players == 3) else {
        fail("no three-player game mix is published".into());
    };
    let login = o.contributor.clone().unwrap_or_else(|| "sizes".into());
    println!("game mix {id}, card cap {}", cap.map_or("none".to_string(), |c| format!("{c} GB")));
    for k in 0..o.jobs.unwrap_or(1) {
        let job = datagen::mix_job(&login, id, k);
        for index in 0..(if o.per_job_set { o.per_job } else { datagen3::DEFAULT_PER_JOB3 }) {
            let t = std::time::Instant::now();
            let (ex, bytes) = sync.book.sized_inputs3(id, job, index, cap).unwrap_or_else(|e| fail(e));
            let nh = ex.hand_counts().unwrap_or([0; NP]);
            let (entries, _) = ex.tree_size().unwrap_or((0, 0));
            #[allow(unused_mut)]
            let mut real = String::new();
            #[cfg(feature = "gpu")]
            if use_gpu() {
                if let Ok(spot) = MwSpot::new(ex.spot_config()) {
                    let (full, min) = solver::multiway::gpu::estimate_device_bytes(&spot, solver::Algorithm::Dcfr);
                    real = format!("  card plan {:5.1} GB whole, {:5.1} GB least", full as f64 / 1e9, min as f64 / 1e9);
                }
            }
            println!("  job {k} #{index:2}  {:8} {:6} pot {:6.2}bb stack {:6.1}bb  hands {:4} {:4} {:4}  {:5.2}B entries  est {:5.1} GB  attempt {:2}  [{:.1}s]{real}",
                     ex.board, ex.pot_type, ex.pot_bb, ex.stack_bb, nh[0], nh[1], nh[2], entries as f64 / 1e9,
                     bytes as f64 / 1e9, ex.attempt, t.elapsed().as_secs_f64());
        }
    }
}

/// Check a three-player job file: the header and its game mix, every
/// example's inputs and size drawn again from (mix, job, index, cap), the
/// values for plausibility, and a re-solve of up to [`RECHECK_MOST`] of the
/// smaller examples. Prints the same one-line summary as the heads-up check
/// (with `"players": 3`) and exits 0, 2 (refused) or 3 (cannot tell now).
pub fn verify3(file: &str, o: &Opts) -> ! {
    let mut errors: Vec<String> = Vec::new();
    let reader = std::io::BufReader::new(std::fs::File::open(file).unwrap_or_else(|e| fail(format!("{file}: {e}"))));
    let mut header: Option<JobHeader> = None;
    let mut records: Vec<Record3> = Vec::new();
    let mut lines_seen = 0u32;
    let mut skipped = 0u32;
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
            Some("example") => match serde_json::from_value::<Record3>(v) {
                Ok(r) => {
                    if r.inputs.index != lines_seen {
                        errors.push(format!("example {}: out of order (line {} of the job)", r.inputs.index, lines_seen));
                    }
                    lines_seen += 1;
                    records.push(r);
                }
                Err(e) => errors.push(format!("line {}: bad example ({e})", n + 1)),
            },
            Some("skipped") => match serde_json::from_value::<Skipped3>(v) {
                Ok(s) => {
                    if s.index != lines_seen {
                        errors.push(format!("skipped example {}: out of order (line {} of the job)", s.index, lines_seen));
                    }
                    lines_seen += 1;
                    skipped += 1;
                }
                Err(e) => errors.push(format!("line {}: bad skipped line ({e})", n + 1)),
            },
            Some("done") => done_seen = true,
            _ => errors.push(format!("line {}: unexpected record", n + 1)),
        }
    }
    let mut resolved = Vec::new();
    if let Some(h) = &header {
        if h.format_version != datagen3::FORMAT3_VERSION || h.menu != datagen3::MENU3
            || h.generator_version < datagen3::PLAYERS3_GENERATOR || !datagen::ACCEPTED_GENERATORS.contains(&h.generator_version)
        {
            errors.push(format!("header is {} v{} generator v{} menu {}; this build expects v{} generator v{} on, menu {}",
                                h.format, h.format_version, h.generator_version, h.menu,
                                datagen3::FORMAT3_VERSION, datagen3::PLAYERS3_GENERATOR, datagen3::MENU3));
        }
        let mut book: Option<Book> = None;
        match h.mix {
            None => errors.push("the header names no game mix".into()),
            Some(id) if datagen::job_mix(h.job) != id => errors.push(format!("job {} is not a job number of game mix {id}", h.job)),
            Some(id) => match mix_for(o, id) {
                Ok(sync) => {
                    let mix = &sync.book.mixes[&id];
                    if mix.withdrawn {
                        errors.push(format!("game mix {id} was withdrawn: its jobs are no longer accepted"));
                    } else if mix.players != 3 {
                        errors.push(format!("game mix {id} is not a three-player mix"));
                    } else if h.mix_key.as_deref() != Some(mix.key().as_str()) {
                        errors.push(format!("drawn from another version of game mix {id} (key {}, the published mix has {})",
                                            h.mix_key.as_deref().unwrap_or("none"), mix.key()));
                    } else {
                        book = Some(sync.book);
                    }
                }
                Err(MixProblem::Unknown(msg)) => errors.push(msg),
                Err(MixProblem::Later(msg)) => {
                    eprintln!("cannot check {file} now: {msg}");
                    std::process::exit(3);
                }
            },
        }
        if lines_seen != h.examples {
            errors.push(format!("{lines_seen} examples, header says {}", h.examples));
        }
        if h.examples == 0 || h.examples > 1000 {
            errors.push(format!("a job of {} examples", h.examples));
        }
        if h.target_pct > 1.0 {
            errors.push(format!("accuracy target {}% pot is looser than 1%", h.target_pct));
        }
        if !done_seen {
            errors.push("file is incomplete (no done line)".into());
        }
        if let Some(book) = book.as_ref().filter(|_| errors.is_empty()) {
            // drawing an example again builds its tree, which is the slow part: all cores, an example each
            use rayon::prelude::*;
            let mix = h.mix.unwrap_or(0);
            let found: Vec<String> = records.par_iter().filter_map(|r| {
                let i = r.inputs.index;
                if r.inputs.job != h.job {
                    return Some(format!("example {i}: belongs to job {}", r.inputs.job));
                }
                match book.sized_inputs3(mix, h.job, i, h.max_vram_gb) {
                    Ok((ex, _)) if ex != r.inputs => return Some(format!("example {i}: inputs differ from job {} as generated", h.job)),
                    Ok((_, bytes)) if bytes != r.tree_bytes => {
                        return Some(format!("example {i}: tree_bytes {} is not the size of its tree ({bytes})", r.tree_bytes))
                    }
                    Ok(_) => {}
                    Err(e) => return Some(format!("example {i}: {e}")),
                }
                if let Some(msg) = datagen3::sanity3(r) {
                    return Some(format!("example {i}: {msg}"));
                }
                if r.exploit_pct_pot > h.target_pct * 1.5 && r.ended == "target" {
                    return Some(format!("example {i}: exploitability {}% above its target", r.exploit_pct_pot));
                }
                if !["target", "iterations", "time"].contains(&r.ended.as_str()) || r.iterations == 0
                    || (r.ended == "iterations" && r.iterations < h.max_iterations) {
                    return Some(format!("example {i}: ended {:?} after {} iterations", r.ended, r.iterations));
                }
                None
            }).collect();
            errors.extend(found);
        }
        if errors.is_empty() && use_gpu() {
            // re-solve a deterministic sample of the smaller examples
            let cap = o.max_vram.filter(|c| *c > 0.0).unwrap_or(RECHECK_GB).min(super::detected_cap_gb());
            let small: Vec<usize> = (0..records.len()).filter(|&i| records[i].tree_bytes as f64 <= cap * 1e9).collect();
            let mut rng = datagen::Rng::new(h.job ^ 0x5EED);
            let mut picks: Vec<usize> = Vec::new();
            while picks.len() < o.sample.min(RECHECK_MOST).min(small.len()) {
                let i = small[rng.below(small.len() as u64) as usize];
                if !picks.contains(&i) {
                    picks.push(i);
                }
            }
            for i in picks {
                let r = &records[i];
                // the same number of iterations as the upload ran, so the two are like for like
                let ro = Opts { target: -1.0, max_iters: r.iterations, max_minutes: f64::INFINITY, reserve_gb: o.reserve_gb, ..super::parse(&[]) };
                match solve_example3(&r.inputs, r.tree_bytes, &ro) {
                    Ok(mine) => {
                        let (mean, max) = datagen3::compare_values3(&mine.values, &r.values);
                        let reach_ok = (0..NP).all(|p| mine.values.reach[p].iter().zip(&r.values.reach[p])
                            .all(|(x, y)| (x - y).abs() <= 1e-3 * x.abs().max(1.0)));
                        if !reach_ok {
                            errors.push(format!("example {}: reach differs from a re-solve", r.inputs.index));
                        }
                        if (mine.exploit_pct_pot - r.exploit_pct_pot).abs() > 0.25 + 0.25 * mine.exploit_pct_pot {
                            errors.push(format!("example {}: exploitability {}% where a re-solve has {}%",
                                                r.inputs.index, r.exploit_pct_pot, mine.exploit_pct_pot));
                        }
                        if mean > MAX_MEAN3.max(o.max_mean) || max > MAX_DIFF3.max(o.max_diff) {
                            errors.push(format!("example {}: re-solve differs (mean {mean:.4}, max {max:.4} pot)", r.inputs.index));
                        }
                        resolved.push(datagen::VerifyResult { index: r.inputs.index, mean_abs_diff: mean, max_abs_diff: max });
                    }
                    // this machine could not solve it now: says nothing about the upload
                    Err(e) => eprintln!("example {}: not re-solved here ({e})", r.inputs.index),
                }
            }
        }
    } else {
        errors.push("missing header".into());
    }
    let summary = serde_json::json!({
        "file": file,
        "ok": errors.is_empty(),
        "players": 3,
        "job": header.as_ref().map(|h| h.job),
        "contributor": header.as_ref().map(|h| h.contributor.clone()),
        "mix": header.as_ref().and_then(|h| h.mix),
        "examples": records.len(),
        "skipped": skipped,
        "errors": errors,
        "resolved": resolved,
    });
    println!("{summary}");
    std::io::stdout().flush().ok();
    std::process::exit(if errors.is_empty() { 0 } else { 2 });
}
