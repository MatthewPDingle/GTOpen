//! Which leaf nets the Preflop Lab can use: the shipped nets (v4, the one a
//! new game uses, v3, v2 and v1, the first), every net the leaf-net harness
//! (tools/leafnet) kept and every ensemble it built (`harness.py ensemble`:
//! one file whose output is the mean of several kept nets).
//!
//! The harness writes each run to `WORK/runs/SNAPSHOT/RUN/leaf_net.bin` and
//! never changes it afterwards, so "SNAPSHOT/RUN" names a net for good and a
//! save can refer to it. WORK is `$LEAFNET_WORK`, else the first of
//! `leafnet_work/` in the repo (the harness's default), `../leafnet-work`
//! (its README's layout) or `../GTOpen-research/leafnet-work` that has a
//! `runs` folder.
use super::leafnet::LeafNet;
use serde_json::{json, Value};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

/// The first shipped net, and what `leaf_net: None` means: games saved
/// before a second net shipped carry no name and keep this one.
pub const SHIPPED: &str = "v1";

/// The net a new Preflop Lab game uses.
pub const DEFAULT_NET: &str = "v4";

/// A net that ships in cache/.
pub struct ShippedNet {
    pub name: &'static str,
    pub file: &'static str,
    pub desc: &'static str,
    /// When it was trained and on how many examples, where the file's
    /// header does not say.
    pub trained: Option<&'static str>,
    pub examples: Option<u64>,
}

/// The shipped nets, newest first.
///
/// v4 (2026-11-24) is the mean of three 2x1218 nets of the "near zero"
/// layout (one more input per class and player that marks a hand the range
/// does not hold), trained on the pool with game mixes 2 and 3 and on exact
/// solves that also give a value to the hands just outside each range, so
/// those hands are no longer priced too low (harness run snap-v5/ens3-fix,
/// byte for byte).
/// v3 (2026-11-17) is the mean of three 2x1334 nets trained on the pool
/// with generator v3's and v4's examples (rake up to 10% with caps, larger
/// pots, and from v4 straddles and stacks to 400 bb) and on exact solves of
/// GTOpen's own preflop ranges, live 7 to 9 handed games among them (harness
/// run snap-v4-live/ens3-live-quick, byte for byte). v2 (2026-11-12) is the
/// same shape trained on generator v2's examples only, without rake or with
/// 5% capped at 3 bb (snap-73k-real2/ens3-real2).
/// v1 (2026-11-09) is the first net, trained on the pool's random ranges
/// only.
pub const SHIPPED_NETS: [ShippedNet; 4] = [
    ShippedNet {
        name: DEFAULT_NET,
        file: "leaf_net_v4.bin",
        desc: "shipped with GTOpen: mean of three nets that also learned the value of hands just outside each range, trained on the pool and on exact solves of solved preflop ranges",
        trained: Some("2026-11-24"),
        examples: Some(283_938),
    },
    ShippedNet {
        name: "v3",
        file: "leaf_net_v3.bin",
        desc: "shipped with GTOpen: mean of three nets, trained on the pool with higher rake, larger pots, straddles and deep stacks, and on exact solves of solved preflop ranges",
        trained: Some("2026-11-17"),
        examples: Some(159_809),
    },
    ShippedNet {
        name: "v2",
        file: "leaf_net_v2.bin",
        desc: "shipped with GTOpen: mean of three nets, trained on the pool and on exact solves of solved preflop ranges",
        trained: Some("2026-11-12"),
        examples: Some(66_325),
    },
    ShippedNet { name: SHIPPED, file: "leaf_net_v1.bin", desc: "shipped with GTOpen: the first net", trained: None, examples: None },
];

/// The shipped net of that name.
pub fn shipped(name: &str) -> Option<&'static ShippedNet> {
    SHIPPED_NETS.iter().find(|n| n.name == name)
}

/// Where a shipped net's file is, if this build has it.
pub fn shipped_path(net: &ShippedNet) -> Option<PathBuf> {
    // the server runs from the repo root; tests run from crates/solver
    ["cache", "../../cache"].iter().map(|dir| Path::new(dir).join(net.file)).find(|p| p.is_file())
}

fn repo_roots() -> Vec<PathBuf> {
    // the server runs from the repo root; tests run from crates/solver
    [".", "../.."].iter().map(PathBuf::from).filter(|r| r.join("cache").is_dir()).collect()
}

/// The harness's work folder, if there is one.
pub fn work_dir() -> Option<PathBuf> {
    if let Some(p) = std::env::var_os("LEAFNET_WORK").filter(|p| !p.is_empty()) {
        return Some(PathBuf::from(p));
    }
    for root in repo_roots() {
        for rel in ["leafnet_work", "../leafnet-work", "../GTOpen-research/leafnet-work"] {
            let p = root.join(rel);
            if p.join("runs").is_dir() {
                return Some(p);
            }
        }
    }
    None
}

fn valid_part(s: &str) -> bool {
    !s.is_empty() && !s.starts_with('.') && s.chars().all(|c| c.is_ascii_alphanumeric() || "._-".contains(c))
}

/// The file behind a research net name "SNAPSHOT/RUN".
pub fn research_net_path(name: &str) -> Result<PathBuf, String> {
    let parts: Vec<&str> = name.split('/').collect();
    if parts.len() != 2 || !parts.iter().all(|p| valid_part(p)) {
        let names: Vec<&str> = SHIPPED_NETS.iter().map(|n| n.name).collect();
        return Err(format!("leaf net \"{name}\" is not a shipped net ({}) or SNAPSHOT/RUN", names.join(", ")));
    }
    let work = work_dir().ok_or_else(|| {
        format!("leaf net \"{name}\" comes from the leaf-net harness, but its work folder was not found (set LEAFNET_WORK)")
    })?;
    let p = work.join("runs").join(parts[0]).join(parts[1]).join("leaf_net.bin");
    if !p.is_file() {
        return Err(format!("leaf net \"{name}\" not found at {}", p.display()));
    }
    Ok(p)
}

/// Only the JSON header of a net file (cheap: no weights).
fn read_header(path: &Path) -> Option<Value> {
    use std::io::Read;
    let mut f = std::fs::File::open(path).ok()?;
    let mut head = [0u8; 12];
    f.read_exact(&mut head).ok()?;
    if &head[..8] != b"GTOLEAF1" {
        return None;
    }
    let n = u32::from_le_bytes(head[8..12].try_into().ok()?) as usize;
    if n > 1 << 20 {
        return None;
    }
    let mut buf = vec![0u8; n];
    f.read_exact(&mut buf).ok()?;
    serde_json::from_slice(&buf).ok()
}

/// results.tsv as rows of column -> value.
pub fn read_results(work: &Path) -> Vec<HashMap<String, String>> {
    let Ok(text) = std::fs::read_to_string(work.join("results.tsv")) else { return Vec::new() };
    let mut lines = text.lines();
    let Some(head) = lines.next() else { return Vec::new() };
    let cols: Vec<&str> = head.split('\t').collect();
    lines
        .filter(|l| !l.trim().is_empty())
        .map(|l| cols.iter().zip(l.split('\t')).map(|(c, v)| (c.to_string(), v.to_string())).collect())
        .collect()
}

fn read_json(path: &Path) -> Option<Value> {
    serde_json::from_str(&std::fs::read_to_string(path).ok()?).ok()
}

fn num(v: Option<&String>) -> Value {
    v.and_then(|s| s.parse::<f64>().ok()).map_or(Value::Null, |x| json!(x))
}

/// Every net the Preflop Lab can use, newest research nets first, the
/// shipped nets last (v4, v3, v2, then v1). `default` marks the net a new game uses.
pub fn list() -> Value {
    let mut nets = Vec::new();
    let work = work_dir();
    if let Some(work) = &work {
        let rows = read_results(work);
        let by_run: HashMap<(&str, &str), &HashMap<String, String>> = rows
            .iter()
            .filter_map(|r| Some(((r.get("snapshot")?.as_str(), r.get("run")?.as_str()), r)))
            .collect();
        let mut snaps: Vec<_> = std::fs::read_dir(work.join("runs"))
            .map(|d| d.flatten().filter(|e| e.path().is_dir()).collect())
            .unwrap_or_default();
        snaps.sort_by_key(|e| e.file_name());
        for snap in snaps {
            let snap_name = snap.file_name().to_string_lossy().to_string();
            let Some(state) = read_json(&snap.path().join("state.json")) else { continue };
            let best = state.get("best").and_then(Value::as_str).unwrap_or("");
            let mut kept: Vec<String> = state
                .get("history")
                .and_then(Value::as_array)
                .map(|h| h.iter().filter_map(|v| v.as_str().map(String::from)).collect())
                .unwrap_or_default();
            if !best.is_empty() && !kept.iter().any(|k| k == best) {
                kept.insert(0, best.to_string()); // the seed-0 noise run that set the first bar
            }
            // ensembles the harness built from kept runs
            let ensembles: Vec<String> = state
                .get("ensembles")
                .and_then(Value::as_array)
                .map(|e| e.iter().filter_map(|v| v.as_str().map(String::from)).collect())
                .unwrap_or_default();
            for e in ensembles {
                if !kept.contains(&e) {
                    kept.push(e);
                }
            }
            let manifest = read_json(&work.join("snapshots").join(&snap_name).join("manifest.json"));
            let train_examples = manifest.as_ref().and_then(|m| m.pointer("/examples_by_split/train").cloned());
            for run in kept {
                if !valid_part(&run) {
                    continue;
                }
                let path = snap.path().join(&run).join("leaf_net.bin");
                let Some(header) = read_header(&path) else { continue };
                let row = by_run.get(&(snap_name.as_str(), run.as_str()));
                let cfg = read_json(&snap.path().join(&run).join("config.json"));
                // an ensemble: how many nets it averages, and whether the best run is one of them
                let members = header.get("ensemble").and_then(Value::as_array).map(Vec::len);
                let averages_best = members.is_some() && !best.is_empty()
                    && header.get("members").and_then(Value::as_array)
                        .map_or(false, |m| m.iter().any(|v| v.as_str() == Some(best)));
                nets.push(json!({
                    "id": format!("{snap_name}/{run}"),
                    "kind": "research",
                    "snapshot": snap_name,
                    "run": run,
                    "best": run == best,
                    "members": members,
                    "averages_best": averages_best,
                    "time": row.and_then(|r| r.get("time")),
                    "desc": row.and_then(|r| r.get("desc")).cloned()
                        .or_else(|| cfg.as_ref().and_then(|c| c.get("desc")?.as_str().map(String::from))),
                    "val_class": num(row.and_then(|r| r.get("val_class"))),
                    "val_range": num(row.and_then(|r| r.get("val_range"))),
                    "leaf_class": row.and_then(|r| r.get("leaf_class")),
                    "macs": num(row.and_then(|r| r.get("macs"))),
                    "sizes": header.get("sizes"),
                    "train_examples": train_examples,
                }));
            }
        }
        nets.sort_by(|a, b| {
            let t = |v: &Value| v.get("time").and_then(Value::as_str).unwrap_or("").to_string();
            t(b).cmp(&t(a))
        });
    }
    for net in &SHIPPED_NETS {
        // v1 answers to LEAF_NET too, so it is read the way a solve loads it
        let header = if net.name == SHIPPED {
            LeafNet::load_default().ok().map(|n| n.header)
        } else {
            shipped_path(net).and_then(|p| read_header(&p))
        };
        let field = |key: &str| header.as_ref().and_then(|h| h.get(key)).cloned();
        nets.push(json!({
            "id": net.name,
            "kind": "shipped",
            "default": net.name == DEFAULT_NET,
            "time": field("trained").or_else(|| net.trained.map(|t| json!(t))),
            "desc": net.desc,
            "train_examples": field("dataset_examples").or_else(|| net.examples.map(|n| json!(n))),
            "members": field("ensemble").as_ref().and_then(Value::as_array).map(Vec::len),
            "sizes": field("sizes"),
            "available": header.is_some(),
        }));
    }
    json!({ "work": work.map(|w| w.display().to_string()), "default": DEFAULT_NET, "nets": nets })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::equity::EquityTable;
    use std::sync::Arc;

    #[test]
    fn names_must_be_two_plain_parts() {
        for bad in ["", "v5", "a/b/c", "../x", "snap/..", "snap/.hidden", "snap/run x", "snap\\run", "/abs"] {
            assert!(research_net_path(bad).is_err(), "{bad} accepted");
        }
        assert!(valid_part("snap-73k-2026-11-10") && valid_part("20261110-031200-s0"));
    }

    #[test]
    fn a_new_game_uses_v4_and_an_unnamed_net_stays_v1() {
        assert_eq!((DEFAULT_NET, SHIPPED), ("v4", "v1"), "a save without a net name was solved with v1");
        assert_eq!(SHIPPED_NETS[0].name, DEFAULT_NET, "newest first");
        for net in &SHIPPED_NETS {
            assert!(valid_part(net.name) && shipped(net.name).is_some());
            assert!(research_net_path(net.name).is_err(), "{} is not a harness run", net.name);
            // every shipped net is in the repo: a default that cannot load would fail every new game
            let path = shipped_path(net).unwrap_or_else(|| panic!("cache/{} is missing", net.file));
            let loaded = LeafNet::load_named(Some(net.name)).unwrap();
            assert_eq!(read_header(&path).as_ref(), Some(&loaded.header));
        }
        assert!(shipped("v5").is_none());
        // the shipped nets are different files: v4, v3 and v2 average three nets each, v1 is one
        let [v4, v3, v2] = [DEFAULT_NET, "v3", "v2"].map(|name| LeafNet::load_named(Some(name)).unwrap());
        assert_eq!((v4.members(), v3.members(), v2.members()), (3, 3, 3));
        assert_ne!(v4.header, v3.header, "a game saved with v3 keeps v3");
        assert_ne!(v3.header, v2.header, "a game saved with v2 keeps v2");
        if std::env::var_os("LEAF_NET").is_none() {
            let (unnamed, v1) = (LeafNet::load_named(None).unwrap(), LeafNet::load_named(Some(SHIPPED)).unwrap());
            assert_eq!(v1.members(), 1);
            assert_eq!(unnamed.header, v1.header, "no name means v1");
        }
    }

    #[test]
    fn lists_kept_runs_from_a_work_folder() {
        let work = std::env::temp_dir().join(format!("leafnet_catalog_{}", std::process::id()));
        let snap = work.join("runs").join("snap-1k");
        for run in ["r1", "r2", "r3"] {
            std::fs::create_dir_all(snap.join(run)).unwrap();
            let net = crate::preflop::leafnet::constant_net(&vec![0.0; 2 * crate::preflop::equity::NUM_CLASSES]);
            std::fs::write(snap.join(run).join("leaf_net.bin"), net.to_bytes()).unwrap();
        }
        // an ensemble of r2 and r3, as `harness.py ensemble` writes it
        let mut ens = LeafNet::ensemble(
            [0.1f32, 0.3].iter().map(|&b| crate::preflop::leafnet::constant_net(&vec![b; 2 * crate::preflop::equity::NUM_CLASSES])).collect(),
        );
        ens.header["members"] = json!(["r2", "r3"]);
        std::fs::create_dir_all(snap.join("ens2-r3")).unwrap();
        std::fs::write(snap.join("ens2-r3").join("leaf_net.bin"), ens.to_bytes()).unwrap();
        std::fs::write(snap.join("state.json"), r#"{"best": "r3", "history": ["r1", "r3"], "ensembles": ["ens2-r3"]}"#).unwrap();
        std::fs::create_dir_all(work.join("snapshots").join("snap-1k")).unwrap();
        std::fs::write(work.join("snapshots/snap-1k/manifest.json"), r#"{"examples_by_split": {"train": 800}}"#).unwrap();
        std::fs::write(
            work.join("results.tsv"),
            "time\tsnapshot\trun\tdesc\tval_class\tverdict\n\
             2026-11-10T01:00:00\tsnap-1k\tr1\tfirst\t0.15\tkeep\n\
             2026-11-10T02:00:00\tsnap-1k\tr2\tworse\t0.16\tdiscard\n\
             2026-11-10T03:00:00\tsnap-1k\tr3\twider\t0.14\tkeep\n\
             2026-11-10T04:00:00\tsnap-1k\tens2-r3\tensemble: mean of 2 nets (r2, r3)\t0.139\tensemble\n",
        )
        .unwrap();
        // LEAFNET_WORK is process-wide: this is the only test that sets it
        std::env::set_var("LEAFNET_WORK", &work);
        let out = list();
        let ids: Vec<&str> = out["nets"].as_array().unwrap().iter().map(|n| n["id"].as_str().unwrap()).collect();
        assert_eq!(ids, ["snap-1k/ens2-r3", "snap-1k/r3", "snap-1k/r1", "v4", "v3", "v2", "v1"]);
        assert_eq!(out["default"], "v4");
        let n = out["nets"].as_array().unwrap().len();
        let defaults: Vec<&Value> = (n - 4..n).map(|i| &out["nets"][i]["default"]).collect();
        assert_eq!(defaults, [&json!(true), &json!(false), &json!(false), &json!(false)]);
        assert_eq!(out["nets"][0]["members"], 2);
        assert_eq!(out["nets"][0]["averages_best"], true);
        assert_eq!(out["nets"][0]["best"], false);
        assert_eq!(out["nets"][0]["val_class"], 0.139);
        assert_eq!(out["nets"][1]["best"], true);
        assert_eq!(out["nets"][1]["members"], Value::Null);
        assert_eq!(out["nets"][1]["desc"], "wider");
        assert_eq!(out["nets"][1]["val_class"], 0.14);
        assert_eq!(out["nets"][1]["train_examples"], 800);
        // the solver loads an ensemble by name like any other net, and prices with the members' mean
        let ens = LeafNet::load_named(Some("snap-1k/ens2-r3")).unwrap();
        assert_eq!(ens.members(), 2);
        let x = vec![0f32; 4 * crate::preflop::equity::NUM_CLASSES + 10];
        assert!(ens.residual(&x).iter().all(|v| (v - 0.2).abs() < 1e-6));
        assert!(LeafNet::load_named(Some("snap-1k/r1")).is_ok());
        assert!(LeafNet::load_named(Some("snap-1k/missing")).is_err());

        // a game solved with a research net is reloaded with that net
        let cfg: crate::preflop::PreflopConfig = serde_json::from_value(json!({
            "positions": ["SB", "BB"], "stack": 30.0, "posts": [0.5, 1.0], "limp": true, "open_raises": [2.5],
            "raise_mults": [3.0], "max_raises": 3, "rake_pct": 5.0, "rake_cap": 2.0,
            "realization": "leafnet", "leaf_net": "snap-1k/r1",
        }))
        .unwrap();
        let eq = Arc::new(EquityTable::build(300));
        let mut s = crate::preflop::PreflopSolver::new(cfg, eq.clone()).unwrap();
        for _ in 0..60 {
            s.iterate();
        }
        let path = work.join("game.bin");
        s.save_game(path.to_str().unwrap()).unwrap();
        let loaded = crate::preflop::PreflopSolver::load_game(path.to_str().unwrap(), eq.clone()).unwrap();
        assert_eq!(loaded.cfg.leaf_net.as_deref(), Some("snap-1k/r1"));
        assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
        std::fs::remove_dir_all(work.join("runs/snap-1k/r1")).unwrap();
        let err = crate::preflop::PreflopSolver::load_game(path.to_str().unwrap(), eq).err().unwrap();
        assert!(err.contains("snap-1k/r1"), "{err}");
        std::env::remove_var("LEAFNET_WORK");
        let _ = std::fs::remove_dir_all(&work);
    }
}
