//! Failure-atomicity of Solver::save.
//!
//! The saver used to File::create (truncate) the destination before writing,
//! so disk-full or a kill mid-write destroyed the previous valid save — the
//! only copy of a possibly multi-hour solve. It now stages into `{path}.tmp`
//! and renames over the destination; a failed write must leave the previous
//! file byte-identical.

use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{Solver, Spot, SpotConfig};
use std::sync::Arc;

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing {
        bet: parse_sizes(bet).unwrap(),
        raise: parse_sizes(raise).unwrap(),
        donk: vec![],
    }
}

/// Tiny river-only clairvoyance spot: cheap to build and solve.
fn tiny_config() -> SpotConfig {
    SpotConfig {
        board: "QcJc9c3d2d".to_string(),
        range_oop: "AcKc,8h7h".to_string(),
        range_ip: "QdQh".to_string(),
        tree: TreeConfig {
            starting_pot: 100.0,
            effective_stack: 100.0,
            oop: [sizing("", ""), sizing("", ""), sizing("100", "")],
            ip: [sizing("", ""), sizing("", ""), sizing("", "")],
            ..Default::default()
        },
    }
}

#[test]
fn failed_save_leaves_previous_save_intact() {
    let spot = Spot::new(tiny_config()).unwrap();
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..20 {
        solver.iterate();
    }
    let dir = std::env::temp_dir().join("gto_atomic_save_test");
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join("spot.gto");
    let path = path.to_str().unwrap().to_string();
    let tmp = format!("{path}.tmp");

    solver.save(&path).unwrap();
    assert!(
        !std::path::Path::new(&tmp).exists(),
        "staging file must not survive a successful save"
    );
    let before = std::fs::read(&path).unwrap();

    // a directory at the staging path makes its File::create fail — the
    // same failure point as a full disk
    std::fs::create_dir(&tmp).unwrap();
    for _ in 0..10 {
        solver.iterate();
    }
    assert!(solver.save(&path).is_err(), "blocked staging path must fail the save");
    assert_eq!(
        before,
        std::fs::read(&path).unwrap(),
        "failed save must leave the previous save byte-identical"
    );
    std::fs::remove_dir(&tmp).unwrap();

    // the next save recovers, replaces the old file and loads
    solver.save(&path).unwrap();
    assert!(!std::path::Path::new(&tmp).exists());
    let loaded = Solver::load(&path).unwrap();
    assert_eq!(loaded.iteration, solver.iteration);
    std::fs::remove_dir_all(&dir).ok();
}
