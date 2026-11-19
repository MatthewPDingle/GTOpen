//! Game mixes end to end through `solve-cli`: a solved game's leaves become a situation list, a published
//! mix names it, a generator that was built before that mix existed solves it, and the job passes the same
//! check the pool's validator runs. See `solver::datagen_mix`.

use solver::datagen;
use solver::datagen_mix::{self, Book};
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
use std::path::Path;
use std::process::{Command, Output};
use std::sync::Arc;

const SAMPLES: u32 = 2000;

fn cli(dir: &Path, args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_solve-cli"))
        .current_dir(dir)
        .env("PREFLOP_EQ_SAMPLES", SAMPLES.to_string())
        .env("SOLVER_GPU", "0")
        .env("GTOPEN_MIX_URL", dir.join("published").join("mixes.json"))
        .env("GTOPEN_SITUATIONS_URL", dir.join("published"))
        .env("GTOPEN_MIX_EVERY_S", "0")
        .env_remove("GTOPEN_MIX_DIR")
        .args(args)
        .output()
        .expect("solve-cli runs")
}

fn text(out: &Output) -> String {
    format!("{}{}", String::from_utf8_lossy(&out.stdout), String::from_utf8_lossy(&out.stderr))
}

/// The last JSON line a command printed.
fn answer(out: &Output) -> serde_json::Value {
    let stdout = String::from_utf8_lossy(&out.stdout);
    let line = stdout.lines().rev().find(|l| l.starts_with('{')).unwrap_or_else(|| panic!("no JSON in: {}", text(out)));
    serde_json::from_str(line).unwrap()
}

fn rows(path: &Path) -> Vec<serde_json::Value> {
    std::fs::read_to_string(path).unwrap().lines().map(|l| serde_json::from_str(l).unwrap()).collect()
}

fn write_rows(path: &Path, rows: &[serde_json::Value]) {
    std::fs::write(path, rows.iter().map(|r| format!("{r}\n")).collect::<String>()).unwrap();
}

#[test]
fn a_new_mix_reaches_a_generator_and_its_jobs_pass_the_check() {
    let dir = std::env::temp_dir().join(format!("gtopen_mix_{}", std::process::id()));
    std::fs::remove_dir_all(&dir).ok();
    std::fs::create_dir_all(dir.join("cache")).unwrap();
    std::fs::create_dir_all(dir.join("published")).unwrap();
    let publish = |mixes: &[serde_json::Value]| {
        let file = serde_json::json!({"format": datagen_mix::MIXES_FORMAT, "mixes": mixes});
        std::fs::write(dir.join("published").join("mixes.json"), file.to_string()).unwrap();
    };

    // A solved preflop game (short stacks keep its flop trees small) and its heads-up flop leaves.
    let eq = Arc::new(EquityTable::load_or_build(dir.join("cache").join("preflop_eq169.bin").to_str().unwrap(), SAMPLES));
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "stack": 15.0, "posts": [0.0, 0.5, 1.0], "limp": true,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 4, "add_allin": false,
        "rake_pct": 5.0, "rake_cap": 3.0, "realization": "balanced",
    })).unwrap();
    let mut game = PreflopSolver::new(cfg, eq).unwrap();
    for _ in 0..3 {
        game.iterate();
    }
    game.save_game(dir.join("game.gtop").to_str().unwrap()).unwrap();
    let out = cli(&dir, &["datagen", "leaves", "game.gtop", "--out", "g01", "--leaves", "6", "--boards", "2"]);
    assert!(out.status.success(), "{}", text(&out));

    // One entry per leaf, whatever flops the export drew; the command prints the part a mix needs.
    let out = cli(&dir, &["datagen", "situations", "calls-1", "g01", "--out", "published"]);
    assert!(out.status.success(), "{}", text(&out));
    let part = answer(&out);
    let list_text = std::fs::read_to_string(dir.join("published").join("calls-1.jsonl")).unwrap();
    let list = datagen_mix::SituationList::parse(&list_text).unwrap();
    assert_eq!((list.name.as_str(), list.entries.len()), ("calls-1", 6));
    assert_eq!(part["sha256"], datagen_mix::sha256_hex(list_text.as_bytes()));
    assert!(list.entries.iter().all(|s| s.id.starts_with("g01:") && s.about.as_ref().unwrap()["line"].is_string()));

    // The pool publishes a mix this build has never seen: all of it from the list.
    let built_in: Vec<serde_json::Value> = serde_json::from_str::<serde_json::Value>(datagen_mix::BUILT_IN).unwrap()["mixes"]
        .as_array().unwrap().clone();
    let id = Book::built_in().open_ids()[0] + 1;
    let mut new_part = part.clone();
    new_part["share"] = 1.0.into();
    let mut published = built_in.clone();
    published.push(serde_json::json!({"id": id, "needs_generator": 5, "note": "Called pots from a solve", "parts": [new_part]}));
    publish(&published);

    let run = ["datagen", "run", "--contributor", "alice", "--jobs", "1", "--per-job", "2", "--max-vram", "1",
               "--max-iters", "30", "--target", "1"];
    let out = cli(&dir, &run);
    assert!(out.status.success(), "{}", text(&out));
    assert!(text(&out).contains(&format!("game mix {id}: Called pots from a solve (100% situations from the list calls-1)")), "{}", text(&out));
    let job = datagen::mix_job("alice", id, 0);
    let file = dir.join("datagen_out").join("alice").join(format!("job-{job}.jsonl"));
    let solved = rows(&file);
    assert_eq!((solved[0]["mix"].as_u64(), solved[0]["generator_version"].as_u64()), (Some(id as u64), Some(5)));
    assert_eq!(solved.len(), 4); // header, two examples, done
    for r in &solved[1..3] {
        let name = r["situation"].as_str().unwrap().strip_prefix("calls-1/").unwrap();
        let entry = list.entries.iter().find(|s| s.id == name).unwrap();
        assert_eq!(r["pot_bb"].as_f64(), Some(entry.pot_bb));
        assert_eq!(r["rake_pct"].as_f64(), Some(0.05));
    }

    // The validator's machine has its own folder and has not heard of the mix either: it reads the list
    // of mixes and the situation list itself, draws the job again and re-solves a sample.
    let check = |file: &Path, folder: &str| {
        Command::new(env!("CARGO_BIN_EXE_solve-cli")).current_dir(&dir).env("SOLVER_GPU", "0")
            .env("GTOPEN_MIX_URL", dir.join("published").join("mixes.json"))
            .env("GTOPEN_SITUATIONS_URL", dir.join("published"))
            .env("GTOPEN_MIX_DIR", dir.join(folder))
            .env("GTOPEN_MIX_EVERY_S", "0") // a validator reads the list again every few minutes; here, every time
            .args(["datagen", "verify", file.to_str().unwrap(), "--sample", "1"]).output().unwrap()
    };
    let out = check(&file, "validator");
    let v = answer(&out);
    assert!(out.status.success() && v["ok"] == true, "{}", text(&out));
    assert_eq!((v["mix"].as_u64(), v["examples"].as_u64(), v["resolved"].as_array().unwrap().len()), (Some(id as u64), Some(2), 1));
    assert!(dir.join("validator").join("situations").read_dir().unwrap().count() == 1);

    // An upload whose ranges are not the list's is turned away.
    let mut forged = solved.clone();
    let w = forged[2]["range"][0][0].as_f64().unwrap();
    forged[2]["range"][0][0] = (if w > 0.5 { 0.25 } else { 0.75 }).into();
    let forged_file = dir.join("forged.jsonl");
    write_rows(&forged_file, &forged);
    let out = check(&forged_file, "validator");
    assert_eq!(out.status.code(), Some(2), "{}", text(&out));
    assert!(answer(&out)["errors"][0].as_str().unwrap().contains("example 1: inputs differ"), "{}", text(&out));

    // A job that names a mix nobody published is turned away too.
    let mut invented = solved.clone();
    let other = ((id as u64 + 7) << datagen::MIX_SHIFT) | (job & ((1 << datagen::MIX_SHIFT) - 1));
    invented[0]["mix"] = (id + 7).into();
    for r in invented.iter_mut().take(3) {
        r["job"] = other.into();
    }
    let invented_file = dir.join("invented.jsonl");
    write_rows(&invented_file, &invented);
    let out = check(&invented_file, "validator");
    assert_eq!(out.status.code(), Some(2), "{}", text(&out));
    assert!(answer(&out)["errors"][0].as_str().unwrap().contains("is not a published mix"));

    // The mix is withdrawn: its jobs stop being accepted, and the generator goes back to the mix before
    // it without being restarted by hand (here: on its next start, with nothing changed on the machine).
    published.last_mut().unwrap()["withdrawn"] = true.into();
    publish(&published);
    let out = check(&file, "validator");
    assert_eq!(out.status.code(), Some(2), "{}", text(&out));
    assert!(answer(&out)["errors"][0].as_str().unwrap().contains("was withdrawn"));
    let out = cli(&dir, &run);
    assert!(out.status.success(), "{}", text(&out));
    assert!(text(&out).contains(&format!("game mix {}: ", id - 1)), "{}", text(&out));
    let earlier = dir.join("datagen_out").join("alice").join(format!("job-{}.jsonl", datagen::mix_job("alice", id - 1, 0)));
    let out = check(&earlier, "validator");
    assert!(out.status.success() && answer(&out)["ok"] == true, "{}", text(&out));

    // A machine that cannot read the published list and never saw the mix cannot tell: exit code 3
    // ("ask again later"), never a rejection of a good upload.
    std::fs::remove_file(dir.join("published").join("mixes.json")).unwrap();
    let out = check(&file, "offline");
    assert_eq!(out.status.code(), Some(3), "{}", text(&out));
    assert!(String::from_utf8_lossy(&out.stdout).lines().all(|l| !l.starts_with('{')));
    assert!(text(&out).contains("could not be read"));
    // ... while one that did see it still gives its answer (the mix was withdrawn when it last looked)
    let out = check(&file, "validator");
    assert_eq!(out.status.code(), Some(2), "{}", text(&out));

    // The mix after that needs code this build does not have: the generator says so and keeps solving.
    published.push(serde_json::json!({"id": id + 1, "needs_generator": datagen::GENERATOR_VERSION + 1,
                                      "note": "Something new", "parts": [{"kind": "not_invented_yet", "share": 1}]}));
    publish(&published);
    let out = cli(&dir, &run);
    assert!(out.status.success(), "{}", text(&out));
    let said = text(&out);
    assert!(said.contains(&format!("PLEASE UPDATE: the pool has moved to game mix {}", id + 1)), "{said}");
    assert!(said.contains(&format!("keeps solving mix {}", id - 1)) && said.contains("(1 this run)"), "{said}");

    std::fs::remove_dir_all(&dir).ok();
}
