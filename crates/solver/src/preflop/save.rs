//! Save/load of preflop games: a JSON header line (config, iteration, seat
//! models, point locks) followed by the raw f32 regret and strategy-sum
//! arenas. The equity table is NOT stored — it is deterministic and
//! disk-cached separately; the tree is rebuilt from the config on load and
//! must produce identical arena sizes (the builder is deterministic).

use super::equity::{EquityTable, NUM_CLASSES};
use super::{PreflopConfig, PreflopSolver, SeatProfile, KIND_ACTION};
use serde::{Deserialize, Serialize};
use std::io::{BufReader, BufWriter, Read, Write};
use std::sync::Arc;

const MAGIC: &[u8] = b"GTOPREFLOP1\n";

#[derive(Serialize, Deserialize)]
struct Header {
    config: PreflopConfig,
    iteration: u32,
    seat_frozen: Vec<bool>,
    seat_profiles: Vec<Option<SeatProfile>>,
    point_locks: Vec<(u32, Vec<f32>)>,
    /// Hero-mode state (defaulted so pre-2026-07-16 saves keep loading).
    #[serde(default)]
    hero: Option<usize>,
    #[serde(default)]
    pre_hero_frozen: Option<Vec<bool>>,
}

fn write_slice(w: &mut BufWriter<std::fs::File>, slice: &[f32]) -> Result<(), String> {
    w.write_all(&(slice.len() as u64).to_le_bytes())
        .map_err(|e| e.to_string())?;
    // f32 slice as raw little-endian bytes (same convention as postflop saves)
    let bytes: &[u8] =
        unsafe { std::slice::from_raw_parts(slice.as_ptr() as *const u8, slice.len() * 4) };
    w.write_all(bytes).map_err(|e| e.to_string())
}

fn read_slice(r: &mut BufReader<std::fs::File>, into: &mut [f32]) -> Result<(), String> {
    let mut lenb = [0u8; 8];
    r.read_exact(&mut lenb).map_err(|e| e.to_string())?;
    let len = u64::from_le_bytes(lenb) as usize;
    if len != into.len() {
        return Err(format!(
            "arena size mismatch: file has {len} entries, rebuilt tree needs {}",
            into.len()
        ));
    }
    let bytes: &mut [u8] =
        unsafe { std::slice::from_raw_parts_mut(into.as_mut_ptr() as *mut u8, len * 4) };
    r.read_exact(bytes).map_err(|e| e.to_string())
}

/// Validate a header's session state against the rebuilt tree BEFORE any of
/// it is installed (the preflop mirror of postflop's `validate_locks`,
/// save.rs). Every consumer of `point_locks` assumes the exact shape — the
/// traversal `copy_from_slice`s a forced sigma into an
/// `actions.len() x NUM_CLASSES` buffer and `average_strategy` returns it
/// as one — so a malformed entry that reached a live solver would panic at
/// the first query or solve step, under the server's session mutex.
fn validate_header(s: &PreflopSolver, header: &Header) -> Result<(), String> {
    if header.seat_frozen.len() != s.n || header.seat_profiles.len() != s.n {
        return Err("save is inconsistent (seat count mismatch)".to_string());
    }
    if let Some(h) = header.hero {
        if h >= s.n {
            return Err(format!(
                "save is inconsistent (hero seat {h}, but the game has {} seats)",
                s.n
            ));
        }
    }
    if let Some(f) = &header.pre_hero_frozen {
        if f.len() != s.n {
            return Err(format!(
                "save is inconsistent (pre-hero frozen flags have {} entries for {} seats)",
                f.len(),
                s.n
            ));
        }
    }
    for (idx, sigma) in &header.point_locks {
        let node = s.nodes.get(*idx as usize).ok_or_else(|| {
            format!(
                "point lock at node {idx}: index out of range (tree has {} nodes)",
                s.nodes.len()
            )
        })?;
        if node.kind != KIND_ACTION {
            return Err(format!("point lock at node {idx}: not an action node"));
        }
        let na = node.actions.len();
        if sigma.len() != na * NUM_CLASSES {
            return Err(format!(
                "point lock at node {idx}: sigma has {} entries, expected {na} actions x {NUM_CLASSES} classes = {}",
                sigma.len(),
                na * NUM_CLASSES
            ));
        }
        if let Some(v) = sigma.iter().find(|v| !v.is_finite() || **v < 0.0) {
            return Err(format!(
                "point lock at node {idx}: invalid frequency {v} (must be finite and >= 0)"
            ));
        }
    }
    Ok(())
}

impl PreflopSolver {
    pub fn save_game(&self, path: &str) -> Result<(), String> {
        // Stage into `{path}.tmp`, then rename over the destination (the
        // idiom the server's report writer uses): creating the destination
        // directly truncates the previous valid save BEFORE the new bytes
        // exist, so disk-full or a kill mid-write destroyed the only copy.
        let tmp = format!("{path}.tmp");
        let res = self
            .write_game(&tmp)
            .and_then(|()| std::fs::rename(&tmp, path).map_err(|e| e.to_string()));
        if res.is_err() {
            std::fs::remove_file(&tmp).ok();
        }
        res
    }

    fn write_game(&self, path: &str) -> Result<(), String> {
        let file = std::fs::File::create(path).map_err(|e| e.to_string())?;
        let mut w = BufWriter::new(file);
        w.write_all(MAGIC).map_err(|e| e.to_string())?;
        let header = Header {
            config: self.cfg.clone(),
            iteration: self.iteration,
            seat_frozen: self.seat_frozen.clone(),
            seat_profiles: self.seat_profiles.clone(),
            point_locks: self.point_locks.iter().map(|(k, v)| (*k, v.clone())).collect(),
            hero: self.hero,
            pre_hero_frozen: self.pre_hero_frozen.clone(),
        };
        let hjson = serde_json::to_string(&header).map_err(|e| e.to_string())?;
        w.write_all(hjson.as_bytes()).map_err(|e| e.to_string())?;
        w.write_all(b"\n").map_err(|e| e.to_string())?;
        // SAFETY: callers hold exclusive access (the server serializes solver
        // use through a mutex); no traversal mutates the arenas while we read
        unsafe {
            write_slice(&mut w, self.regrets.slice())?;
            write_slice(&mut w, self.strat_sum.slice())?;
        }
        w.flush().map_err(|e| e.to_string())?;
        // the data must be durable before the rename unlinks the old save
        w.get_ref().sync_all().map_err(|e| e.to_string())
    }

    pub fn load_game(path: &str, eq: Arc<EquityTable>) -> Result<PreflopSolver, String> {
        let file = std::fs::File::open(path).map_err(|e| e.to_string())?;
        let mut r = BufReader::new(file);
        let mut magic = [0u8; 12];
        r.read_exact(&mut magic).map_err(|e| e.to_string())?;
        if magic != MAGIC {
            return Err("not a preflop game save".to_string());
        }
        let mut line = Vec::new();
        loop {
            let mut b = [0u8; 1];
            r.read_exact(&mut b).map_err(|e| e.to_string())?;
            if b[0] == b'\n' {
                break;
            }
            line.push(b[0]);
        }
        let header: Header = serde_json::from_slice(&line).map_err(|e| e.to_string())?;
        let mut s = PreflopSolver::new(header.config.clone(), eq)?;
        // Refuse malformed session state here, while nothing depends on it:
        // installed unchecked it would panic at the first query instead.
        validate_header(&s, &header)?;
        // SAFETY: `s` is exclusively ours; nothing else touches its arenas
        unsafe {
            read_slice(&mut r, s.regrets.slice_mut())?;
            read_slice(&mut r, s.strat_sum.slice_mut())?;
        }
        s.iteration = header.iteration;
        s.seat_frozen = header.seat_frozen;
        s.seat_profiles = header.seat_profiles;
        s.point_locks = header.point_locks.into_iter().collect();
        s.hero = header.hero;
        s.pre_hero_frozen = header.pre_hero_frozen;
        Ok(s)
    }
}
