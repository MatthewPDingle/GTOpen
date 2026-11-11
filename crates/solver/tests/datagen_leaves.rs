//! `solve-cli datagen leaves --boards-from`: a game solved again keeps, line by line, the flops an earlier
//! export gave it, so the two exports can be compared flop for flop.

use solver::datagen::{line_flop, line_key};
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::Arc;

const SAMPLES: u32 = 2000;

fn config(stack: f64) -> PreflopConfig {
    serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "stack": stack, "posts": [0.0, 0.5, 1.0], "limp": true,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 4, "add_allin": false,
        "rake_pct": 5.0, "rake_cap": 3.0, "realization": "balanced",
    }))
    .expect("config")
}

/// A game solved for `iterations`, saved under `dir`.
fn solved(dir: &Path, eq: &Arc<EquityTable>, name: &str, stack: f64, iterations: usize) -> PathBuf {
    let mut s = PreflopSolver::new(config(stack), eq.clone()).expect("solver");
    for _ in 0..iterations {
        s.iterate();
    }
    let path = dir.join(name);
    s.save_game(path.to_str().unwrap()).expect("save");
    path
}

fn leaves(dir: &Path, game: &Path, out: &str, extra: &[&str]) -> std::process::Output {
    Command::new(env!("CARGO_BIN_EXE_solve-cli"))
        .current_dir(dir)
        .env("PREFLOP_EQ_SAMPLES", SAMPLES.to_string())
        .args(["datagen", "leaves", game.to_str().unwrap(), "--out", out, "--leaves", "12", "--boards", "2", "--seed", "5"])
        .args(extra)
        .output()
        .expect("solve-cli runs")
}

/// line -> (the leaf's rank in the export, its flops in index order), and the export's leaves.json.
fn read(dir: &Path) -> (HashMap<String, (u64, Vec<String>)>, serde_json::Value) {
    let summary: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(dir.join("leaves.json")).unwrap()).unwrap();
    let mut boards: HashMap<u64, Vec<(u64, String)>> = HashMap::new();
    for line in std::fs::read_to_string(dir.join("inputs.jsonl")).unwrap().lines() {
        let v: serde_json::Value = serde_json::from_str(line).unwrap();
        boards.entry(v["job"].as_u64().unwrap()).or_default()
            .push((v["index"].as_u64().unwrap(), v["board"].as_str().unwrap().to_string()));
    }
    let mut out = HashMap::new();
    for leaf in summary["leaves"].as_array().unwrap() {
        let path: Vec<String> = leaf["path"].as_array().unwrap().iter().map(|x| x.as_str().unwrap().to_string()).collect();
        let job = leaf["job"].as_u64().unwrap();
        let mut b = boards.remove(&job).unwrap();
        b.sort();
        out.insert(line_key(&path), (job, b.into_iter().map(|x| x.1).collect()));
    }
    (out, summary)
}

#[test]
fn a_game_solved_again_keeps_its_flops_line_by_line() {
    let dir = std::env::temp_dir().join(format!("gtopen_leaves_{}", std::process::id()));
    std::fs::remove_dir_all(&dir).ok();
    std::fs::create_dir_all(dir.join("cache")).unwrap();
    // the table the CLI will load from its working folder
    let eq = Arc::new(EquityTable::load_or_build(dir.join("cache").join("preflop_eq169.bin").to_str().unwrap(), SAMPLES));
    let early = solved(&dir, &eq, "early.gtop", 100.0, 3);
    let late = solved(&dir, &eq, "late.gtop", 100.0, 150);
    let other = solved(&dir, &eq, "other.gtop", 60.0, 3);

    let run = leaves(&dir, &early, "a", &[]);
    assert!(run.status.success(), "{}", String::from_utf8_lossy(&run.stderr));
    let run = leaves(&dir, &late, "b", &["--boards-from", "a"]);
    assert!(run.status.success(), "{}", String::from_utf8_lossy(&run.stderr));
    assert!(String::from_utf8_lossy(&run.stdout).contains("keep its flops"));
    let run = leaves(&dir, &late, "plain", &[]);
    assert!(run.status.success(), "{}", String::from_utf8_lossy(&run.stderr));

    let (a, _) = read(&dir.join("a"));
    let (b, summary) = read(&dir.join("b"));
    let (plain, plain_summary) = read(&dir.join("plain"));
    let shared: Vec<&String> = b.keys().filter(|line| a.contains_key(*line)).collect();
    assert!(shared.len() >= 6, "only {} of {} lines are in both exports", shared.len(), b.len());
    // the point of the option: some line changed its rank between the two solves, and without the option
    // its flops changed with it
    let moved: Vec<&&String> = shared.iter().filter(|line| a[**line].0 != b[**line].0).collect();
    assert!(!moved.is_empty(), "no line changed rank: the test shows nothing");
    assert!(moved.iter().any(|line| plain[**line].1 != a[**line].1));
    for line in &shared {
        assert_eq!(b[*line].1, a[*line].1, "{line}");
    }
    // a line the earlier export does not hold draws from its own name
    for (line, (_, boards)) in b.iter().filter(|(line, _)| !a.contains_key(*line)) {
        assert_eq!(boards, &[line_flop(5, line, 0), line_flop(5, line, 1)], "{line}");
    }
    assert_eq!(summary["boards_kept"], serde_json::json!({"leaves": shared.len(), "examples": 2 * shared.len()}));
    // without the option nothing changes: no note, and the same leaves in the same order
    assert!(plain_summary.get("boards_kept").is_none());
    assert_eq!(plain.iter().map(|(l, v)| (l.clone(), v.0)).collect::<HashMap<_, _>>(),
               b.iter().map(|(l, v)| (l.clone(), v.0)).collect::<HashMap<_, _>>());

    // more flops than the earlier export had: the first two are kept, the rest come from the line's name
    let run = Command::new(env!("CARGO_BIN_EXE_solve-cli"))
        .current_dir(&dir)
        .env("PREFLOP_EQ_SAMPLES", SAMPLES.to_string())
        .args(["datagen", "leaves", late.to_str().unwrap(), "--out", "more", "--leaves", "12", "--boards", "4", "--seed", "5",
               "--boards-from", "a"])
        .output()
        .unwrap();
    assert!(run.status.success(), "{}", String::from_utf8_lossy(&run.stderr));
    let (more, _) = read(&dir.join("more"));
    for line in &shared {
        assert_eq!(more[*line].1[..2], a[*line].1[..]);
        assert_eq!(more[*line].1[2..], [line_flop(5, line, 2), line_flop(5, line, 3)]);
    }

    // an export of another game is refused
    let run = leaves(&dir, &other, "o", &[]);
    assert!(run.status.success(), "{}", String::from_utf8_lossy(&run.stderr));
    let run = leaves(&dir, &late, "c", &["--boards-from", "o"]);
    assert!(!run.status.success());
    assert!(String::from_utf8_lossy(&run.stderr).contains("another game"), "{}", String::from_utf8_lossy(&run.stderr));
    assert!(!dir.join("c").join("inputs.jsonl").exists());
    std::fs::remove_dir_all(&dir).ok();
}
