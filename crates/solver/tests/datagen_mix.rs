//! Game mixes end to end through `solve-cli`: a solved game's leaves become a situation list, a published
//! mix names it, a generator that was built before that mix existed solves it, and the job passes the same
//! check the pool's validator runs. See `solver::datagen_mix`.

use std::{
    path::Path,
    process::{Command, Output},
    sync::Arc,
};

use solver::{
    datagen,
    datagen_mix::{self, Book},
    preflop::{equity::EquityTable, PreflopConfig, PreflopSolver},
};

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
    format!(
        "{}{}",
        String::from_utf8_lossy(&out.stdout),
        String::from_utf8_lossy(&out.stderr)
    )
}

/// The last JSON line a command printed.
fn answer(out: &Output) -> serde_json::Value {
    let stdout = String::from_utf8_lossy(&out.stdout);
    let line = stdout
        .lines()
        .rev()
        .find(|l| l.starts_with('{'))
        .unwrap_or_else(|| panic!("no JSON in: {}", text(out)));
    serde_json::from_str(line).unwrap()
}

fn rows(path: &Path) -> Vec<serde_json::Value> {
    std::fs::read_to_string(path)
        .unwrap()
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect()
}

fn write_rows(path: &Path, rows: &[serde_json::Value]) {
    std::fs::write(
        path,
        rows.iter().map(|r| format!("{r}\n")).collect::<String>(),
    )
    .unwrap();
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
    let eq = Arc::new(EquityTable::load_or_build(
        dir.join("cache")
            .join("preflop_eq169.bin")
            .to_str()
            .unwrap(),
        SAMPLES,
    ));
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "stack": 15.0, "posts": [0.0, 0.5, 1.0], "limp": true,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 4, "add_allin": false,
        "rake_pct": 5.0, "rake_cap": 3.0, "realization": "balanced",
    }))
    .unwrap();
    let mut game = PreflopSolver::new(cfg, eq).unwrap();
    for _ in 0..3 {
        game.iterate();
    }
    game.save_game(dir.join("game.gtop").to_str().unwrap())
        .unwrap();
    let out = cli(
        &dir,
        &[
            "datagen",
            "leaves",
            "game.gtop",
            "--out",
            "g01",
            "--leaves",
            "6",
            "--boards",
            "2",
        ],
    );
    assert!(out.status.success(), "{}", text(&out));

    // One entry per leaf, whatever flops the export drew; the command prints the part a mix needs.
    let out = cli(
        &dir,
        &[
            "datagen",
            "situations",
            "calls-1",
            "g01",
            "--out",
            "published",
        ],
    );
    assert!(out.status.success(), "{}", text(&out));
    let part = answer(&out);
    let list_text = std::fs::read_to_string(dir.join("published").join("calls-1.jsonl")).unwrap();
    let list = datagen_mix::SituationList::parse(&list_text).unwrap();
    assert_eq!((list.name.as_str(), list.entries.len()), ("calls-1", 6));
    assert_eq!(
        part["sha256"],
        datagen_mix::sha256_hex(list_text.as_bytes())
    );
    assert!(list
        .entries
        .iter()
        .all(|s| s.id.starts_with("g01:") && s.about.as_ref().unwrap()["line"].is_string()));

    // The pool publishes a mix this build has never seen: all of it from the list.
    let built_in: Vec<serde_json::Value> =
        serde_json::from_str::<serde_json::Value>(datagen_mix::BUILT_IN).unwrap()["mixes"]
            .as_array()
            .unwrap()
            .clone();
    let id = Book::built_in().open_ids()[0] + 1;
    let mut new_part = part.clone();
    new_part["share"] = 1.0.into();
    let mut published = built_in.clone();
    published.push(serde_json::json!({"id": id, "needs_generator": 5, "note": "Called pots from a solve", "parts": [new_part]}));
    publish(&published);

    let run = [
        "datagen",
        "run",
        "--contributor",
        "alice",
        "--jobs",
        "1",
        "--per-job",
        "2",
        "--max-vram",
        "1",
        "--max-iters",
        "30",
        "--target",
        "1",
    ];
    let out = cli(&dir, &run);
    assert!(out.status.success(), "{}", text(&out));
    assert!(
        text(&out).contains(&format!(
            "game mix {id}: Called pots from a solve (100% situations from the list calls-1)"
        )),
        "{}",
        text(&out)
    );
    let job = datagen::mix_job("alice", id, 0);
    let file = dir
        .join("datagen_out")
        .join("alice")
        .join(format!("job-{job}.jsonl"));
    let solved = rows(&file);
    assert_eq!(
        (
            solved[0]["mix"].as_u64(),
            solved[0]["generator_version"].as_u64()
        ),
        (Some(id as u64), Some(datagen::GENERATOR_VERSION as u64))
    );
    assert_eq!(solved.len(), 4); // header, two examples, done
    for r in &solved[1..3] {
        let name = r["situation"]
            .as_str()
            .unwrap()
            .strip_prefix("calls-1/")
            .unwrap();
        let entry = list.entries.iter().find(|s| s.id == name).unwrap();
        assert_eq!(r["pot_bb"].as_f64(), Some(entry.pot_bb));
        assert_eq!(r["rake_pct"].as_f64(), Some(0.05));
    }

    // The validator's machine has its own folder and has not heard of the mix either: it reads the list
    // of mixes and the situation list itself, draws the job again and re-solves a sample.
    let check = |file: &Path, folder: &str| {
        Command::new(env!("CARGO_BIN_EXE_solve-cli"))
            .current_dir(&dir)
            .env("SOLVER_GPU", "0")
            .env("GTOPEN_MIX_URL", dir.join("published").join("mixes.json"))
            .env("GTOPEN_SITUATIONS_URL", dir.join("published"))
            .env("GTOPEN_MIX_DIR", dir.join(folder))
            .env("GTOPEN_MIX_EVERY_S", "0") // a validator reads the list again every few minutes; here, every time
            .args(["datagen", "verify", file.to_str().unwrap(), "--sample", "1"])
            .output()
            .unwrap()
    };
    let out = check(&file, "validator");
    let v = answer(&out);
    assert!(out.status.success() && v["ok"] == true, "{}", text(&out));
    assert_eq!(
        (
            v["mix"].as_u64(),
            v["examples"].as_u64(),
            v["resolved"].as_array().unwrap().len()
        ),
        (Some(id as u64), Some(2), 1)
    );
    assert!(
        dir.join("validator")
            .join("situations")
            .read_dir()
            .unwrap()
            .count()
            == 1
    );

    // An upload whose ranges are not the list's is turned away.
    let mut forged = solved.clone();
    let w = forged[2]["range"][0][0].as_f64().unwrap();
    forged[2]["range"][0][0] = (if w > 0.5 { 0.25 } else { 0.75 }).into();
    let forged_file = dir.join("forged.jsonl");
    write_rows(&forged_file, &forged);
    let out = check(&forged_file, "validator");
    assert_eq!(out.status.code(), Some(2), "{}", text(&out));
    assert!(
        answer(&out)["errors"][0]
            .as_str()
            .unwrap()
            .contains("example 1: inputs differ"),
        "{}",
        text(&out)
    );

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
    assert!(answer(&out)["errors"][0]
        .as_str()
        .unwrap()
        .contains("is not a published mix"));

    // The mix is withdrawn: its jobs stop being accepted, and the generator goes back to the mix before
    // it without being restarted by hand (here: on its next start, with nothing changed on the machine).
    published.last_mut().unwrap()["withdrawn"] = true.into();
    publish(&published);
    let out = check(&file, "validator");
    assert_eq!(out.status.code(), Some(2), "{}", text(&out));
    assert!(answer(&out)["errors"][0]
        .as_str()
        .unwrap()
        .contains("was withdrawn"));
    // (the newest earlier mix whose situation lists this test publishes, and that this small card may draw:
    // one of random ranges only, for any card)
    let fallback = Book::built_in()
        .mixes
        .values()
        .rev()
        .find(|m| m.lists().is_empty() && !m.withdrawn && m.min_card_gb == 0.0)
        .unwrap()
        .id;
    let out = cli(&dir, &run);
    assert!(out.status.success(), "{}", text(&out));
    assert!(
        text(&out).contains(&format!("game mix {fallback}: ")),
        "{}",
        text(&out)
    );
    let earlier = dir.join("datagen_out").join("alice").join(format!(
        "job-{}.jsonl",
        datagen::mix_job("alice", fallback, 0)
    ));
    let out = check(&earlier, "validator");
    assert!(
        out.status.success() && answer(&out)["ok"] == true,
        "{}",
        text(&out)
    );

    // A machine that cannot read the published list and never saw the mix cannot tell: exit code 3
    // ("ask again later"), never a rejection of a good upload.
    std::fs::remove_file(dir.join("published").join("mixes.json")).unwrap();
    let out = check(&file, "offline");
    assert_eq!(out.status.code(), Some(3), "{}", text(&out));
    assert!(String::from_utf8_lossy(&out.stdout)
        .lines()
        .all(|l| !l.starts_with('{')));
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
    assert!(
        said.contains(&format!(
            "PLEASE UPDATE: the pool has moved to game mix {}",
            id + 1
        )),
        "{said}"
    );
    assert!(
        said.contains(&format!("keeps solving mix {fallback}")) && said.contains("(1 this run)"),
        "{said}"
    );

    std::fs::remove_dir_all(&dir).ok();
}

/// A mix with a card rule (generator v6): a big card passes over most small trees, every example records the
/// size of its tree, the check draws both again, and a v5 upload of a mix without rules still passes.
#[test]
fn a_card_rule_reaches_the_generator_and_the_check() {
    let dir = std::env::temp_dir().join(format!("gtopen_mix_rules_{}", std::process::id()));
    std::fs::remove_dir_all(&dir).ok();
    std::fs::create_dir_all(dir.join("published")).unwrap();
    // short 4-bet pots only: tiny trees that solve in moments on the CPU, of a few different sizes
    let random = serde_json::json!({"kind": "random", "share": 1.0,
        "pot_types": [{"name": "4bet", "share": 1.0, "pot_bb": [38, 55]}],
        "tables": [{"share": 1.0, "pot_scale": [1, 1], "stack_bb": [30, 80]}],
        "rake": [{"share": 1.0, "pct": [0, 0], "cap_bb": [0, 0]}]});
    let built_in: Vec<serde_json::Value> =
        serde_json::from_str::<serde_json::Value>(datagen_mix::BUILT_IN).unwrap()["mixes"]
            .as_array()
            .unwrap()
            .clone();
    let id = Book::built_in().open_ids()[0] + 1;
    let rule = serde_json::json!({"cap_from_gb": 2, "under_gb": 0.56, "keep": 0.2});
    let mut published = built_in.clone();
    published.push(serde_json::json!({"id": id, "needs_generator": 6, "note": "Short 4-bet pots", "parts": [random.clone()],
                                      "card_rules": [rule]}));
    published.push(
        serde_json::json!({"id": id + 1, "needs_generator": 5, "note": "Short 4-bet pots, no rule",
                                      "parts": [random]}),
    );
    let publish = |mixes: &[serde_json::Value]| {
        let file = serde_json::json!({"format": datagen_mix::MIXES_FORMAT, "mixes": mixes});
        std::fs::write(dir.join("published").join("mixes.json"), file.to_string()).unwrap();
    };
    let run = |cap: &str| {
        let out = cli(
            &dir,
            &[
                "datagen",
                "run",
                "--contributor",
                "alice",
                "--jobs",
                "1",
                "--per-job",
                "6",
                "--max-vram",
                cap,
                "--max-iters",
                "20",
                "--target",
                "1",
            ],
        );
        assert!(out.status.success(), "{}", text(&out));
        text(&out)
    };
    let check = |file: &Path| {
        let out = Command::new(env!("CARGO_BIN_EXE_solve-cli"))
            .current_dir(&dir)
            .env("SOLVER_GPU", "0")
            .env("GTOPEN_MIX_URL", dir.join("published").join("mixes.json"))
            .env("GTOPEN_MIX_DIR", dir.join("validator"))
            .env("GTOPEN_MIX_EVERY_S", "0")
            .args(["datagen", "verify", file.to_str().unwrap(), "--sample", "1"])
            .output()
            .unwrap();
        (out.status.code(), answer(&out))
    };

    // the mix with the rule is the newest while the one after it is withdrawn
    published.last_mut().unwrap()["withdrawn"] = true.into();
    publish(&published);
    let said = run("4");
    assert!(
        said.contains(&format!(
            "game mix {id}: this card keeps about 1 in 5 of the games under 0.56 GB"
        )),
        "{said}"
    );
    let job = datagen::mix_job("alice", id, 0);
    let file = dir
        .join("datagen_out")
        .join("alice")
        .join(format!("job-{job}.jsonl"));
    let solved = rows(&file);
    assert_eq!(
        solved[0]["generator_version"].as_u64(),
        Some(datagen::GENERATOR_VERSION as u64)
    );
    let mut book = Book::default();
    book.add_text(&std::fs::read_to_string(dir.join("published").join("mixes.json")).unwrap())
        .unwrap();
    for (i, r) in solved[1..7].iter().enumerate() {
        let (ex, bytes) = book.sized_inputs(id, job, i as u32, Some(4.0)).unwrap();
        assert_eq!(r["tree_bytes"].as_u64(), Some(bytes));
        assert_eq!(r["attempt"].as_u64().unwrap_or(0), ex.attempt as u64);
    }
    let (code, v) = check(&file);
    assert!(code == Some(0) && v["ok"] == true, "{v}");

    // tree-sizes reads the recorded sizes
    let out = cli(&dir, &["datagen", "tree-sizes", file.to_str().unwrap()]);
    assert!(out.status.success(), "{}", text(&out));
    let sizes: Vec<serde_json::Value> = String::from_utf8_lossy(&out.stdout)
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    assert_eq!(sizes.len(), 6);
    assert_eq!(
        sizes[2],
        serde_json::json!({"job": job, "index": 2, "tree_bytes": solved[3]["tree_bytes"]})
    );

    // a size that is not the tree's is turned away, and so is one left out
    let mut forged = solved.clone();
    forged[1]["tree_bytes"] = (forged[1]["tree_bytes"].as_u64().unwrap() / 2).into();
    let forged_file = dir.join("forged.jsonl");
    write_rows(&forged_file, &forged);
    let (code, v) = check(&forged_file);
    assert_eq!(code, Some(2), "{v}");
    assert!(
        v["errors"][0]
            .as_str()
            .unwrap()
            .contains("example 0: tree_bytes"),
        "{v}"
    );
    forged[1].as_object_mut().unwrap().remove("tree_bytes");
    write_rows(&forged_file, &forged);
    assert_eq!(check(&forged_file).0, Some(2));

    // a job of a mix without rules, as generator v5 wrote it (no sizes), still passes; tree-sizes builds its trees
    published
        .last_mut()
        .unwrap()
        .as_object_mut()
        .unwrap()
        .remove("withdrawn");
    publish(&published);
    run("4");
    let plain = dir.join("datagen_out").join("alice").join(format!(
        "job-{}.jsonl",
        datagen::mix_job("alice", id + 1, 0)
    ));
    let mut v5 = rows(&plain);
    v5[0]["generator_version"] = 5.into();
    for r in v5[1..7].iter_mut() {
        r.as_object_mut().unwrap().remove("tree_bytes");
    }
    let v5_file = dir.join("v5.jsonl");
    write_rows(&v5_file, &v5);
    let (code, v) = check(&v5_file);
    assert!(code == Some(0) && v["ok"] == true, "{v}");
    let out = cli(&dir, &["datagen", "tree-sizes", v5_file.to_str().unwrap()]);
    let first: serde_json::Value =
        serde_json::from_str(String::from_utf8_lossy(&out.stdout).lines().next().unwrap()).unwrap();
    assert_eq!(first["tree_bytes"], rows(&plain)[1]["tree_bytes"]);

    std::fs::remove_dir_all(&dir).ok();
}
