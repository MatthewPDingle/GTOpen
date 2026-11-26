//! Three-player game mixes end to end through `solve-cli`: a generator solves a job of a published
//! three-player mix, the job passes the check the pool's validator runs, an interrupted job is carried on,
//! and a card that is too small for the mix keeps to the heads-up mix before it. See `solver::datagen3`.

use solver::datagen;
use solver::datagen3;
use solver::datagen_mix;
use std::path::Path;
use std::process::{Command, Output};

fn cli(dir: &Path, args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_solve-cli"))
        .current_dir(dir)
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

/// A random part with short stacks behind big pots, so the trees are small.
fn part() -> serde_json::Value {
    serde_json::json!({"kind": "random", "share": 1,
        "pot_types": [{"name": "4bet", "share": 1, "pot_bb": [60, 80]}],
        "tables": [{"share": 1, "pot_scale": [1, 1], "stack_bb": [34, 40]}],
        "rake": [{"share": 0.5, "pct": [0, 0], "cap_bb": [0, 0]}, {"share": 0.5, "pct": [0.05, 0.05], "cap_bb": [2, 4]}]})
}

#[test]
fn a_three_player_mix_is_solved_checked_and_carried_on() {
    let dir = std::env::temp_dir().join(format!("gtopen_three_{}", std::process::id()));
    std::fs::remove_dir_all(&dir).ok();
    std::fs::create_dir_all(dir.join("published")).unwrap();
    let publish = |mixes: &[serde_json::Value]| {
        let file = serde_json::json!({"format": datagen_mix::MIXES_FORMAT, "mixes": mixes});
        std::fs::write(dir.join("published").join("mixes.json"), file.to_string()).unwrap();
    };
    let heads_up = serde_json::json!({"id": 1, "needs_generator": 5, "note": "Heads-up", "parts": [part()]});
    let three = serde_json::json!({"id": 2, "needs_generator": datagen3::PLAYERS3_GENERATOR, "note": "Three players",
                                   "parts": [part()], "players": 3});
    publish(&[heads_up.clone(), three.clone()]);

    let run = ["datagen", "run", "--contributor", "alice", "--jobs", "1", "--per-job", "2", "--max-vram", "2",
               "--max-iters", "1", "--target", "1"];
    let out = cli(&dir, &run);
    assert!(out.status.success(), "{}", text(&out));
    assert!(text(&out).contains("game mix 2: Three players (three-player flops: 100% random ranges)"), "{}", text(&out));
    let job = datagen::mix_job("alice", 2, 0);
    let folder = dir.join("datagen_out").join("alice");
    let file = folder.join(format!("job3-{job}.jsonl"));
    let solved = rows(&file);
    assert_eq!(solved.len(), 4, "header, two examples, done");
    assert_eq!(solved[0]["format"], datagen3::FORMAT3);
    assert_eq!(solved[0]["menu"], datagen3::MENU3);
    assert_eq!((solved[0]["mix"].as_u64(), solved[0]["generator_version"].as_u64()), (Some(2), Some(datagen::GENERATOR_VERSION as u64)));
    for (i, r) in solved[1..3].iter().enumerate() {
        assert_eq!((r["type"].as_str(), r["index"].as_u64()), (Some("example"), Some(i as u64)));
        assert_eq!(r["range"].as_array().unwrap().len(), 3);
        assert_eq!(r["value"].as_array().unwrap().len(), 3);
        assert!(r["tree_bytes"].as_u64().unwrap() <= 2_000_000_000);
    }
    assert!(!folder.join(format!("job-{job}.jsonl")).exists(), "a three-player job has its own file name");

    // The validator's check: inputs and sizes drawn again, values plausible.
    let check = |f: &Path| cli(&dir, &["datagen", "verify", f.to_str().unwrap()]);
    let out = check(&file);
    assert!(out.status.success(), "{}", text(&out));
    let said = answer(&out);
    assert_eq!((said["ok"].as_bool(), said["players"].as_u64(), said["examples"].as_u64(), said["skipped"].as_u64()),
               (Some(true), Some(3), Some(2), Some(0)));

    // Made-up inputs or values are refused.
    let bad = dir.join("bad.jsonl");
    let mut changed = solved.clone();
    changed[1]["pot_bb"] = serde_json::json!(changed[1]["pot_bb"].as_f64().unwrap() + 1.0);
    write_rows(&bad, &changed);
    let out = check(&bad);
    assert_eq!(out.status.code(), Some(2), "{}", text(&out));
    assert!(answer(&out)["errors"][0].as_str().unwrap().contains("inputs differ"), "{}", text(&out));
    let mut changed = solved.clone();
    let k = changed[2]["value"][1].as_array().unwrap().iter().position(|v| !v.is_null()).unwrap();
    changed[2]["value"][1][k] = serde_json::json!(40.0);
    write_rows(&bad, &changed);
    let out = check(&bad);
    assert_eq!(out.status.code(), Some(2), "{}", text(&out));
    assert!(answer(&out)["errors"][0].as_str().unwrap().contains("value"), "{}", text(&out));

    // A machine that went down after the first example carries on from it: the same job, the first example kept.
    let part_file = folder.join(format!("job3-{job}.jsonl.part"));
    let mut cut = format!("{}\n{}\n", solved[0], solved[1]);
    cut.push_str(&solved[2].to_string()[..40]); // the line being written when it stopped
    std::fs::write(&part_file, cut).unwrap();
    std::fs::remove_file(&file).unwrap();
    let out = cli(&dir, &run);
    assert!(out.status.success(), "{}", text(&out));
    assert!(text(&out).contains("carrying on after 1 of 2 examples"), "{}", text(&out));
    let again = rows(&file);
    assert_eq!(again.len(), 4);
    assert_eq!(again[1], solved[1], "the kept example is written back as it was");
    assert_eq!(again[2]["value"], solved[2]["value"], "the same solve gives the same values");
    assert!(!part_file.exists());
    assert!(check(&file).status.success());

    // An example that was started twice without finishing is left out the third time, and the job still passes.
    std::fs::write(&part_file, format!("{}\n{}\n", solved[0], solved[1])).unwrap();
    std::fs::write(folder.join(format!("job3-{job}.jsonl.part.tries")), "1 2\n").unwrap();
    std::fs::remove_file(&file).unwrap();
    let out = cli(&dir, &run);
    assert!(out.status.success(), "{}", text(&out));
    assert!(text(&out).contains("left out: stopped twice before it finished"), "{}", text(&out));
    let short = rows(&file);
    assert_eq!((short[2]["type"].as_str(), short[2]["index"].as_u64()), (Some("skipped"), Some(1)));
    let out = check(&file);
    assert!(out.status.success(), "{}", text(&out));
    assert_eq!((answer(&out)["examples"].as_u64(), answer(&out)["skipped"].as_u64()), (Some(1), Some(1)));

    // A mix that asks for a bigger card than this one is passed over: the heads-up mix before it is solved.
    let mut big = three.clone();
    big["id"] = 3.into();
    big["min_card_gb"] = 6.into();
    let mut gone = three.clone();
    gone["withdrawn"] = true.into();
    publish(&[heads_up, gone, big]);
    let out = cli(&dir, &run);
    assert!(out.status.success(), "{}", text(&out));
    assert!(text(&out).contains("mix 3 needs a graphics card that holds 6 GB trees (this machine: 2 GB)"), "{}", text(&out));
    assert!(folder.join(format!("job-{}.jsonl", datagen::mix_job("alice", 1, 0))).exists(), "{}", text(&out));
    // ... and without --max-vram a machine with no GPU never takes a three-player mix
    let out = cli(&dir, &["datagen", "run", "--contributor", "bob", "--jobs", "1", "--per-job", "1", "--max-iters", "1", "--target", "1"]);
    assert!(out.status.success(), "{}", text(&out));
    assert!(text(&out).contains("(this machine: no GPU)"), "{}", text(&out));
    // a job of the withdrawn mix is no longer accepted
    let out = check(&file);
    assert_eq!(out.status.code(), Some(2), "{}", text(&out));
    std::fs::remove_dir_all(&dir).ok();
}
