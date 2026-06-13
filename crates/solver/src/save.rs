//! Save/load of solved spots: a JSON header line followed by raw f32 arenas.
//!
//! The on-disk format is always full-precision f32 regardless of the in-RAM
//! storage mode, so files written by compressed and uncompressed solvers are
//! interchangeable (and older saves keep loading).

use crate::cfr::Solver;
use crate::game::{Spot, SpotConfig};
use crate::store::{Storage, Store};
use crate::tree::KIND_ACTION;
use serde::{Deserialize, Serialize};
use std::io::{BufReader, BufWriter, Read, Write};
use std::sync::Arc;

const MAGIC: &[u8] = b"GTOSOLVE2\n";

#[derive(Serialize, Deserialize)]
struct Header {
    config: SpotConfig,
    iteration: u32,
}

impl Solver {
    /// Decode one whole arena (player `p`'s action-node blocks) to f32.
    pub(crate) fn arena_to_f32(&self, store: &Store, p: usize) -> Vec<f32> {
        let len = self.spot.tree.data_size[p] as usize;
        let nh = self.spot.hands[p].len();
        let mut buf = vec![0f32; len];
        for (idx, node) in self.spot.tree.nodes.iter().enumerate() {
            if node.kind == KIND_ACTION && node.player as usize == p {
                let n = node.num_children as usize * nh;
                let off = node.data_offset as usize;
                unsafe {
                    store.read_f32(idx as u32, node.data_offset, n, &mut buf[off..off + n]);
                }
            }
        }
        buf
    }

    pub fn save(&self, path: &str) -> Result<(), String> {
        let file = std::fs::File::create(path).map_err(|e| e.to_string())?;
        let mut w = BufWriter::new(file);
        w.write_all(MAGIC).map_err(|e| e.to_string())?;
        let header = Header {
            config: self.spot.config.clone(),
            iteration: self.iteration,
        };
        let hjson = serde_json::to_string(&header).map_err(|e| e.to_string())?;
        w.write_all(hjson.as_bytes()).map_err(|e| e.to_string())?;
        w.write_all(b"\n").map_err(|e| e.to_string())?;
        for (store, p) in [
            (&self.regrets[0], 0usize),
            (&self.regrets[1], 1),
            (&self.strat[0], 0),
            (&self.strat[1], 1),
        ] {
            let write_slice = |w: &mut BufWriter<std::fs::File>, slice: &[f32]| {
                w.write_all(&(slice.len() as u64).to_le_bytes())
                    .map_err(|e| e.to_string())?;
                // f32 slice as raw little-endian bytes
                let bytes: &[u8] = unsafe {
                    std::slice::from_raw_parts(slice.as_ptr() as *const u8, slice.len() * 4)
                };
                w.write_all(bytes).map_err(|e| e.to_string())
            };
            match store {
                Store::F32(b) => write_slice(&mut w, b.as_slice())?,
                _ => write_slice(&mut w, &self.arena_to_f32(store, p))?,
            }
        }
        w.flush().map_err(|e| e.to_string())?;
        Ok(())
    }

    pub fn load(path: &str) -> Result<Solver, String> {
        Solver::load_with_storage(path, Storage::F32)
    }

    pub fn load_with_storage(path: &str, storage: Storage) -> Result<Solver, String> {
        let file = std::fs::File::open(path).map_err(|e| e.to_string())?;
        let mut r = BufReader::new(file);
        let mut magic = [0u8; 10];
        r.read_exact(&mut magic).map_err(|e| e.to_string())?;
        if magic != MAGIC {
            return Err("not a solver save file".to_string());
        }
        let mut header_line = Vec::new();
        loop {
            let mut b = [0u8; 1];
            r.read_exact(&mut b).map_err(|e| e.to_string())?;
            if b[0] == b'\n' {
                break;
            }
            header_line.push(b[0]);
        }
        let header: Header =
            serde_json::from_slice(&header_line).map_err(|e| format!("bad header: {e}"))?;
        let spot = Spot::new(header.config)?;
        let mut solver = Solver::with_storage(Arc::new(spot), storage);
        solver.iteration = header.iteration;
        for arena in [0usize, 1, 2, 3] {
            let p = arena % 2;
            let mut len_bytes = [0u8; 8];
            r.read_exact(&mut len_bytes).map_err(|e| e.to_string())?;
            let len = u64::from_le_bytes(len_bytes) as usize;
            let expected = solver.spot.tree.data_size[p] as usize;
            if len != expected {
                return Err(format!(
                    "arena size mismatch: file {len}, expected {expected} (tree config changed?)"
                ));
            }
            let mut buf = vec![0f32; len];
            {
                let bytes: &mut [u8] = unsafe {
                    std::slice::from_raw_parts_mut(buf.as_mut_ptr() as *mut u8, len * 4)
                };
                r.read_exact(bytes).map_err(|e| e.to_string())?;
            }
            let store = match arena {
                0 | 1 => &solver.regrets[p],
                _ => &solver.strat[p],
            };
            match store {
                Store::F32(b) => unsafe { b.slice(0, len) }.copy_from_slice(&buf),
                _ => {
                    let nh = solver.spot.hands[p].len();
                    for (idx, node) in solver.spot.tree.nodes.iter().enumerate() {
                        if node.kind == KIND_ACTION && node.player as usize == p {
                            let n = node.num_children as usize * nh;
                            let off = node.data_offset as usize;
                            unsafe {
                                store.write_f32(
                                    idx as u32,
                                    node.data_offset,
                                    n,
                                    &buf[off..off + n],
                                );
                            }
                        }
                    }
                }
            }
        }
        Ok(solver)
    }
}
