//! Which leaf nets the Preflop Lab can use: the shipped v1, every net the
//! leaf-net harness (tools/leafnet) kept and every ensemble it built
//! (`harness.py ensemble`: one file whose output is the mean of several
//! kept nets).
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

/// The name of the shipped net (also what `leaf_net: None` means).
pub const SHIPPED: &str = "v1";

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
        return Err(format!("leaf net \"{name}\" is not \"{SHIPPED}\" or SNAPSHOT/RUN"));
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
/// shipped net last.
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
    let shipped = LeafNet::load_default().ok().map(|n| n.header);
    nets.push(json!({
        "id": SHIPPED,
        "kind": "shipped",
        "time": shipped.as_ref().and_then(|h| h.get("trained")),
        "desc": "shipped with GTOpen",
        "train_examples": shipped.as_ref().and_then(|h| h.get("dataset_examples")),
        "sizes": shipped.as_ref().and_then(|h| h.get("sizes")),
        "available": shipped.is_some(),
    }));
    json!({ "work": work.map(|w| w.display().to_string()), "nets": nets })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::equity::EquityTable;
    use std::sync::Arc;

    #[test]
    fn names_must_be_two_plain_parts() {
        for bad in ["", "v2", "a/b/c", "../x", "snap/..", "snap/.hidden", "snap/run x", "snap\\run", "/abs"] {
            assert!(research_net_path(bad).is_err(), "{bad} accepted");
        }
        assert!(valid_part("snap-73k-2026-11-10") && valid_part("20261110-031200-s0"));
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
        assert_eq!(ids, ["snap-1k/ens2-r3", "snap-1k/r3", "snap-1k/r1", "v1"]);
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
