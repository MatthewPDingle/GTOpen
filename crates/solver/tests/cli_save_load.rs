//! End-to-end checks for `solve-cli`'s single-spot save/resume grammar.
//!
//! Each test gets its own tiny spot (a few combos, one flop bet size, short
//! stack) so a real solve stays well under a second. The binary is the one
//! Cargo just built for this package. Every invocation runs in a fresh scratch
//! directory with a cleared solver environment, so the developer's
//! SOLVER_ALGO/SOLVER_ISO/SOLVER_GPU settings cannot change the result.

use solver::{Algorithm, Solver};
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::time::{SystemTime, UNIX_EPOCH};

const CONFIG: &str = r#"{
  "board": "Th9h2c",
  "range_oop": "AA,KK",
  "range_ip": "QQ,JJ",
  "tree": {
    "starting_pot": 10.0,
    "effective_stack": 10.0,
    "oop": [{"bet": [{"PotPct": 50}], "raise": [], "donk": []}, {}, {}],
    "ip":  [{"bet": [{"PotPct": 50}], "raise": [], "donk": []}, {}, {}]
  }
}"#;

/// Every switch the CLI reads, except the two thread/GPU defaults set below.
const SOLVER_ENV: [&str; 8] = [
    "SOLVER_GPU",
    "SOLVER_GPU_PROFILE",
    "SOLVER_GPU_TIMECHK",
    "SOLVER_STORAGE",
    "SOLVER_ALGO",
    "SOLVER_ISO",
    "SOLVER_THREADS",
    "SOLVER_BATCH_SAVE",
];

/// Unique scratch directory with the tiny spot written to `spot.json`.
fn workdir(name: &str) -> PathBuf {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let dir = std::env::temp_dir().join(format!(
        "gtopen-solve-cli-{name}-{}-{nonce}",
        std::process::id()
    ));
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("spot.json"), CONFIG).unwrap();
    dir
}

/// Run the CLI in `dir` with only the given solver variables set.
fn solve_cli_env(dir: &Path, args: &[&str], envs: &[(&str, &str)]) -> Output {
    let mut cmd = Command::new(env!("CARGO_BIN_EXE_solve-cli"));
    cmd.args(args).current_dir(dir);
    for key in SOLVER_ENV {
        cmd.env_remove(key);
    }
    cmd.env("SOLVER_GPU", "0").env("SOLVER_THREADS", "1");
    for (key, value) in envs {
        cmd.env(key, value);
    }
    cmd.output().unwrap()
}

fn solve_cli(dir: &Path, args: &[&str]) -> Output {
    solve_cli_env(dir, args, &[])
}

fn assert_ok(out: &Output) {
    assert!(
        out.status.success(),
        "solve-cli failed ({}):\nstdout:\n{}\nstderr:\n{}",
        out.status,
        String::from_utf8_lossy(&out.stdout),
        String::from_utf8_lossy(&out.stderr),
    );
}

fn load(path: &Path) -> Solver {
    Solver::load(path.to_str().unwrap()).unwrap()
}

/// Rewrite the JSON header line in place, leaving the magic and arenas
/// byte-identical (the idiom from `save_header.rs`).
fn doctor_header(path: &Path, edit: impl FnOnce(&mut serde_json::Value)) {
    const MAGIC_LEN: usize = 10; // b"GTOSOLVE2\n"
    let bytes = std::fs::read(path).unwrap();
    let nl = MAGIC_LEN + bytes[MAGIC_LEN..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[MAGIC_LEN..nl]).unwrap();
    edit(&mut header);
    let mut out = bytes[..MAGIC_LEN].to_vec();
    out.extend_from_slice(serde_json::to_string(&header).unwrap().as_bytes());
    out.extend_from_slice(&bytes[nl..]); // '\n' + arenas untouched
    std::fs::write(path, out).unwrap();
}

#[test]
fn fresh_save_then_resume_adds_the_delta() {
    let dir = workdir("resume");
    let out = solve_cli(&dir, &["spot.json", "3", "0", "--save", "base.gto"]);
    assert_ok(&out);
    let first = load(&dir.join("base.gto")).iteration;
    assert_eq!(first, 3, "the fresh solve should stop at its cap");

    let out = solve_cli(
        &dir,
        &["resume", "base.gto", "4", "0", "--save", "next.gto"],
    );
    assert_ok(&out);
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(
        stdout.contains(&format!("saved iteration {first}")),
        "resume should print the saved iteration:\n{stdout}"
    );
    assert!(
        stdout.contains("running up to 4 more"),
        "resume should print the delta:\n{stdout}"
    );
    assert!(
        stdout.contains(&format!("stop iteration {}", first + 4)),
        "resume should print the absolute stop iteration:\n{stdout}"
    );
    // `check_every` is 10, but the final `iteration >= max_iterations` check
    // must still measure the real exploitability for a short delta.
    let done = stdout.lines().find(|l| l.starts_with("done:")).unwrap_or("");
    assert!(
        done.contains(&format!("done: iter {}", first + 4)),
        "done line should report the stop iteration:\n{stdout}"
    );
    assert!(!done.contains("NaN"), "a short delta must not report NaN:\n{stdout}");
    assert_eq!(load(&dir.join("next.gto")).iteration, first + 4);
}

#[test]
fn resume_stops_early_on_target() {
    let dir = workdir("target");
    assert_ok(&solve_cli(&dir, &["spot.json", "3", "0", "--save", "base.gto"]));
    // check_every is 10: the first target check after iteration 3 is at 10,
    // so a target this loose must stop there instead of running all 100.
    let out = solve_cli(&dir, &["resume", "base.gto", "100", "50", "--save", "early.gto"]);
    assert_ok(&out);
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(
        stdout.contains("done: iter 10"),
        "expected the first check (iteration 10) to stop the run:\n{stdout}"
    );
    assert_eq!(load(&dir.join("early.gto")).iteration, 10);
}

#[test]
fn resume_with_zero_delta_is_rejected() {
    let dir = workdir("zero");
    let out = solve_cli(&dir, &["resume", "base.gto", "0"]);
    assert!(!out.status.success());
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(
        stderr.contains("iteration delta must be at least 1"),
        "expected an iterations message, got:\n{stderr}"
    );
}

#[test]
fn fresh_zero_iterations_is_rejected() {
    let dir = workdir("fresh-zero");
    let out = solve_cli(&dir, &["spot.json", "0"]);
    assert!(!out.status.success());
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(
        stderr.contains("max_iterations must be at least 1"),
        "a zero-iteration run would print the NaN fallback, got:\n{stderr}"
    );
}

#[test]
fn save_load_save_is_byte_identical() {
    let dir = workdir("roundtrip");
    let out = solve_cli(&dir, &["spot.json", "2", "0", "--save", "base.gto"]);
    assert_ok(&out);

    // Load with full-precision storage: the on-disk format is f32, so the
    // compressed in-RAM encoding would quantize the bytes on the way back out.
    let base = dir.join("base.gto");
    let copy = dir.join("copy.gto");
    // `Solver::save` re-materializes isomorphic siblings, so it needs `&mut`.
    let mut loaded = load(&base);
    loaded.save(copy.to_str().unwrap()).unwrap();
    assert_eq!(
        std::fs::read(&base).unwrap(),
        std::fs::read(&copy).unwrap(),
        "a save that is only loaded and re-saved must not change"
    );
}

#[test]
fn unknown_option_exits_non_zero() {
    let dir = workdir("unknown");
    let out = solve_cli(&dir, &["spot.json", "--nope"]);
    assert!(!out.status.success());
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(
        stderr.contains("unknown option --nope"),
        "expected an unknown-option message, got:\n{stderr}"
    );
}

#[test]
fn batch_rejects_save_flag() {
    let dir = workdir("batch");
    let out = solve_cli(&dir, &["batch", "spot.json", "Th9h2c", "--save", "x.gto"]);
    assert!(!out.status.success());
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(
        stderr.contains("--save applies only to single-spot or resume mode"),
        "expected the batch-mode rejection, got:\n{stderr}"
    );
}

/// A fresh solve applies SOLVER_ALGO/SOLVER_ISO and records them; a resume
/// without those variables keeps the recorded settings instead of falling
/// back to the process defaults.
#[test]
fn fresh_save_records_env_and_resume_keeps_it() {
    let dir = workdir("env-keep");
    let out = solve_cli_env(
        &dir,
        &["spot.json", "2", "0", "--save", "base.gto"],
        &[("SOLVER_ALGO", "cfr+"), ("SOLVER_ISO", "0")],
    );
    assert_ok(&out);
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(
        stdout.contains("algo CfrPlus, isomorphism off"),
        "a fresh solve must honor the env:\n{stdout}"
    );
    let base = load(&dir.join("base.gto"));
    assert_eq!(base.algo, Algorithm::CfrPlus);
    assert!(!base.use_isomorphism, "the save must record SOLVER_ISO=0");

    let out = solve_cli(&dir, &["resume", "base.gto", "1", "0", "--save", "next.gto"]);
    assert_ok(&out);
    let stdout = String::from_utf8_lossy(&out.stdout);
    let loaded_line = stdout.lines().find(|l| l.starts_with("loaded ")).unwrap_or("");
    assert!(
        loaded_line.contains("algo CfrPlus, isomorphism off"),
        "resume must keep the save's settings, not the defaults:\n{stdout}"
    );
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(
        !stderr.contains("SOLVER_ALGO=") && !stderr.contains("SOLVER_ISO="),
        "nothing was overridden, so there should be no warning:\n{stderr}"
    );
    let done = stdout.lines().find(|l| l.starts_with("done:")).unwrap_or("");
    assert!(
        !done.contains("NaN"),
        "a 1-iteration resume must still measure exploitability:\n{stdout}"
    );
    let next = load(&dir.join("next.gto"));
    assert_eq!(next.algo, Algorithm::CfrPlus);
    assert!(!next.use_isomorphism);
    assert_eq!(next.iteration, 3);
}

/// An explicitly set env var overrides a resumed save, but says so and names
/// both values (the save's and the env's) instead of silently re-pricing it.
#[test]
fn resume_env_override_warns_and_wins() {
    let dir = workdir("env-override");
    assert_ok(&solve_cli(&dir, &["spot.json", "2", "0", "--save", "base.gto"]));
    let base = load(&dir.join("base.gto"));
    assert_eq!((base.algo, base.use_isomorphism), (Algorithm::Dcfr, true));

    let out = solve_cli_env(
        &dir,
        &["resume", "base.gto", "1", "0", "--save", "next.gto"],
        &[("SOLVER_ALGO", "cfr+"), ("SOLVER_ISO", "0")],
    );
    assert_ok(&out);
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(
        stderr.contains("SOLVER_ALGO=cfr+ overrides the save's algorithm dcfr"),
        "the algorithm warning must name both values:\n{stderr}"
    );
    assert!(
        stderr.contains("SOLVER_ISO=0 overrides the save's isomorphism setting 1"),
        "the isomorphism warning must name both values:\n{stderr}"
    );
    let next = load(&dir.join("next.gto"));
    assert_eq!(next.algo, Algorithm::CfrPlus);
    assert!(!next.use_isomorphism);
    assert_eq!(next.iteration, 3);
}

/// Saves written before the header carried engine settings ran dcfr with
/// isomorphism on; a resume must use those defaults, not whatever this process
/// was configured with, and must write the fields from then on.
#[test]
fn legacy_save_without_engine_settings_resumes_with_defaults() {
    let dir = workdir("legacy");
    let out = solve_cli_env(
        &dir,
        &["spot.json", "2", "0", "--save", "base.gto"],
        &[("SOLVER_ALGO", "cfr+"), ("SOLVER_ISO", "0")],
    );
    assert_ok(&out);
    let base = dir.join("base.gto");
    doctor_header(&base, |h| {
        let obj = h.as_object_mut().unwrap();
        obj.remove("algo");
        obj.remove("use_isomorphism");
    });
    let stripped = load(&base);
    assert_eq!((stripped.algo, stripped.use_isomorphism), (Algorithm::Dcfr, true));

    let out = solve_cli(&dir, &["resume", "base.gto", "1", "0", "--save", "next.gto"]);
    assert_ok(&out);
    let stdout = String::from_utf8_lossy(&out.stdout);
    let loaded_line = stdout.lines().find(|l| l.starts_with("loaded ")).unwrap_or("");
    assert!(
        loaded_line.contains("algo Dcfr, isomorphism on"),
        "a legacy save must resume with the pre-field defaults:\n{stdout}"
    );
    let next = load(&dir.join("next.gto"));
    assert_eq!((next.algo, next.use_isomorphism), (Algorithm::Dcfr, true));
    assert_eq!(next.iteration, 3);
}

/// Resuming must continue the arenas, not restart from zero. With f32 storage
/// (so loading cannot quantize) 10 iterations + a 5-iteration resume must be
/// byte-identical to a single 15-iteration solve, header included.
#[test]
fn resume_continues_the_arenas_not_restarts_them() {
    let dir = workdir("continuation");
    let f32 = &[("SOLVER_STORAGE", "f32")];
    assert_ok(&solve_cli_env(
        &dir,
        &["spot.json", "10", "0", "--save", "base.gto"],
        f32,
    ));
    assert_ok(&solve_cli_env(
        &dir,
        &["resume", "base.gto", "5", "0", "--save", "resumed.gto"],
        f32,
    ));
    assert_ok(&solve_cli_env(
        &dir,
        &["spot.json", "15", "0", "--save", "continuous.gto"],
        f32,
    ));
    assert_eq!(
        std::fs::read(dir.join("resumed.gto")).unwrap(),
        std::fs::read(dir.join("continuous.gto")).unwrap(),
        "a resumed solve must produce the same state as one uninterrupted run"
    );
}
