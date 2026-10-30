//! Save/load of three-player solves: a magic line, a JSON header line, then
//! each player's regrets and strategy sums as raw little-endian f32 (always
//! full precision, whatever the in-RAM storage).

use super::game::{MwSpot, MwSpotConfig};
use super::solver::MwSolver;
use super::tree::{KIND_ACTION, NP};
use crate::cfr::Algorithm;
use crate::store::Storage;
use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader, BufWriter, Read, Write};
use std::sync::Arc;

const MAGIC: &str = "GTOMW1";

#[derive(Serialize, Deserialize)]
pub struct MwSaveHeader {
    pub config: MwSpotConfig,
    pub iteration: u32,
    #[serde(default)]
    pub algo: Option<String>,
    #[serde(default)]
    pub exploit_pct_pot: Option<f64>,
}

fn algo_name(a: Algorithm) -> &'static str {
    match a {
        Algorithm::Dcfr => "dcfr",
        Algorithm::CfrPlus => "cfr+",
        Algorithm::PcfrPlus => "pcfr+",
    }
}

/// Writes `s` (call `ensure_symmetric` first when it uses isomorphism).
pub fn save(s: &MwSolver, exploit_pct_pot: Option<f64>, w: impl Write) -> Result<(), String> {
    let mut w = BufWriter::new(w);
    let hdr = MwSaveHeader {
        config: s.spot.config.clone(),
        iteration: s.iteration,
        algo: Some(algo_name(s.algo).into()),
        exploit_pct_pot,
    };
    let io = |e: std::io::Error| e.to_string();
    writeln!(w, "{MAGIC}").map_err(io)?;
    writeln!(w, "{}", serde_json::to_string(&hdr).map_err(|e| e.to_string())?).map_err(io)?;
    let spot = &*s.spot;
    let mut buf = Vec::new();
    for p in 0..NP {
        let nh = spot.hands[p].len();
        for store in [&s.regrets[p], &s.strat[p]] {
            for (i, n) in spot.tree.nodes.iter().enumerate() {
                if n.kind != KIND_ACTION || n.player as usize != p {
                    continue;
                }
                let k = n.num_children as usize * nh;
                buf.resize(k, 0f32);
                unsafe { store.read_f32(i as u32, n.data_offset, k, &mut buf) };
                for v in &buf {
                    w.write_all(&v.to_le_bytes()).map_err(io)?;
                }
            }
        }
    }
    w.flush().map_err(io)
}

/// Reads just the header (cheap; for listings and pre-load checks).
pub fn peek(r: impl Read) -> Result<MwSaveHeader, String> {
    let mut r = BufReader::new(r);
    let mut line = String::new();
    r.read_line(&mut line).map_err(|e| e.to_string())?;
    if line.trim_end() != MAGIC {
        return Err("not a three-player save".into());
    }
    line.clear();
    r.read_line(&mut line).map_err(|e| e.to_string())?;
    serde_json::from_str(&line).map_err(|e| format!("bad save header: {e}"))
}

pub fn load(r: impl Read, storage: Storage) -> Result<(MwSolver, MwSaveHeader), String> {
    let mut r = BufReader::new(r);
    let mut line = String::new();
    r.read_line(&mut line).map_err(|e| e.to_string())?;
    if line.trim_end() != MAGIC {
        return Err("not a three-player save".into());
    }
    line.clear();
    r.read_line(&mut line).map_err(|e| e.to_string())?;
    let hdr: MwSaveHeader = serde_json::from_str(&line).map_err(|e| format!("bad save header: {e}"))?;
    let spot = Arc::new(MwSpot::new(hdr.config.clone())?);
    let mut s = MwSolver::new(spot.clone(), storage);
    s.iteration = hdr.iteration;
    if let Some(a) = &hdr.algo {
        s.algo = Algorithm::parse(a)?;
    }
    let mut bytes = Vec::new();
    let mut buf = Vec::new();
    for p in 0..NP {
        let nh = spot.hands[p].len();
        for which in 0..2 {
            for (i, n) in spot.tree.nodes.iter().enumerate() {
                if n.kind != KIND_ACTION || n.player as usize != p {
                    continue;
                }
                let k = n.num_children as usize * nh;
                bytes.resize(k * 4, 0u8);
                r.read_exact(&mut bytes).map_err(|e| format!("truncated save: {e}"))?;
                buf.clear();
                buf.extend(bytes.chunks_exact(4).map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]])));
                let store = if which == 0 { &s.regrets[p] } else { &s.strat[p] };
                unsafe { store.write_f32(i as u32, n.data_offset, k, &buf) };
            }
        }
    }
    // The file holds every branch, so no symmetrization is pending.
    Ok((s, hdr))
}
