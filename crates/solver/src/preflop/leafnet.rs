//! Learned heads-up flop leaf values (the pooled value-net, feature #14).
//!
//! A small MLP trained on exact flop solves (`tools/datagen/gonogo.py`)
//! predicts, for a heads-up flop leaf, how far each class's solved value is
//! from the balanced realization model's value. The file format and the
//! feature layout are defined in `tools/datagen/leafnet_io.py`; this module
//! reads the same file and computes the same features, so a net trained in
//! numpy gives the same numbers here.
use super::equity::NUM_CLASSES;
use std::path::Path;

const MAGIC: &[u8; 8] = b"GTOLEAF1";
/// Pot types in the one-hot order the net was trained with.
pub const POT_TYPES: [&str; 4] = ["limped", "srp", "3bet", "4bet"];
const META: usize = 10;

struct Layer {
    rows: usize,
    cols: usize,
    /// Row-major, input-major: `w[i * cols + j]` links input i to output j.
    w: Vec<f32>,
    b: Vec<f32>,
}

/// A loaded leaf-value net.
pub struct LeafNet {
    pub header: serde_json::Value,
    mu: Vec<f32>,
    sd: Vec<f32>,
    layers: Vec<Layer>,
}

/// One heads-up flop leaf, out of position first.
pub struct LeafSpot<'a> {
    /// Per-class range weights (any scale; normalized so the largest is 1).
    pub range: [&'a [f32]; 2],
    /// The balanced model's per-class values, as a fraction of the pot.
    pub balanced: [&'a [f32]; 2],
    pub pot_bb: f64,
    /// Effective stack behind at the flop.
    pub stack_bb: f64,
    /// Rake as a fraction (0.05 = 5%) and its cap in bb (0 = none).
    pub rake_frac: f64,
    pub rake_cap_bb: f64,
    /// Index into [`POT_TYPES`].
    pub pot_type: usize,
}

/// Pot type of a flop reached after `raises` preflop raises.
pub fn pot_type_for_raises(raises: u8) -> usize {
    (raises as usize).min(3)
}

impl LeafNet {
    pub fn from_bytes(bytes: &[u8]) -> Result<Self, String> {
        if bytes.len() < 12 || &bytes[..8] != MAGIC {
            return Err("not a GTOpen leaf net file".into());
        }
        let hlen = u32::from_le_bytes(bytes[8..12].try_into().unwrap()) as usize;
        let body = 12 + hlen;
        if bytes.len() < body {
            return Err("leaf net header is truncated".into());
        }
        let header: serde_json::Value =
            serde_json::from_slice(&bytes[12..body]).map_err(|e| format!("leaf net header: {e}"))?;
        let sizes: Vec<usize> = header["sizes"].as_array().ok_or("leaf net header has no sizes")?
            .iter().map(|v| v.as_u64().map(|x| x as usize)).collect::<Option<_>>()
            .ok_or("leaf net sizes must be integers")?;
        if sizes.len() < 2 || sizes[0] != 4 * NUM_CLASSES + META || *sizes.last().unwrap() != 2 * NUM_CLASSES {
            return Err(format!("leaf net sizes {sizes:?} do not match the feature layout"));
        }
        let data = &bytes[body..];
        if data.len() % 4 != 0 {
            return Err("leaf net data is not whole f32 values".into());
        }
        let vals: Vec<f32> = data.chunks_exact(4).map(|c| f32::from_le_bytes(c.try_into().unwrap())).collect();
        let mut pos = 0usize;
        let mut take = |n: usize| -> Result<Vec<f32>, String> {
            let out = vals.get(pos..pos + n).ok_or("leaf net data is truncated")?.to_vec();
            pos += n;
            Ok(out)
        };
        let mu = take(sizes[0])?;
        let sd = take(sizes[0])?;
        let mut layers = Vec::new();
        for win in sizes.windows(2) {
            let (rows, cols) = (win[0], win[1]);
            layers.push(Layer { rows, cols, w: take(rows * cols)?, b: take(cols)? });
        }
        if pos != vals.len() {
            return Err(format!("leaf net has {} unexpected trailing values", vals.len() - pos));
        }
        if sd.iter().any(|&s| !(s > 0.0)) || vals.iter().any(|v| !v.is_finite()) {
            return Err("leaf net has invalid numbers".into());
        }
        Ok(LeafNet { header, mu, sd, layers })
    }

    pub fn load(path: impl AsRef<Path>) -> Result<Self, String> {
        let p = path.as_ref();
        let bytes = std::fs::read(p).map_err(|e| format!("{}: {e}", p.display()))?;
        Self::from_bytes(&bytes).map_err(|e| format!("{}: {e}", p.display()))
    }

    /// `LEAF_NET`, else the shipped net under cache/.
    pub fn load_default() -> Result<Self, String> {
        if let Ok(p) = std::env::var("LEAF_NET") {
            return Self::load(p);
        }
        Self::load("cache/leaf_net_v1.bin").or_else(|_| Self::load("../../cache/leaf_net_v1.bin"))
    }

    /// The input vector, exactly as tools/datagen/gonogo.py builds it.
    pub fn features(spot: &LeafSpot) -> Vec<f32> {
        let mut x = Vec::with_capacity(4 * NUM_CLASSES + META);
        for r in spot.range {
            let max = r.iter().cloned().fold(0f32, f32::max);
            let scale = if max > 0.0 { 1.0 / max } else { 0.0 };
            x.extend(r.iter().map(|w| w * scale));
        }
        for b in spot.balanced {
            x.extend_from_slice(b);
        }
        let (pot, stack) = (spot.pot_bb, spot.stack_bb);
        let meta = [
            pot.ln(), stack.ln(), (stack / pot).ln(), 10.0 * spot.rake_frac,
            spot.rake_cap_bb / pot, if spot.rake_frac > 0.0 { 1.0 } else { 0.0 },
        ];
        x.extend(meta.iter().map(|&v| v as f32));
        for t in 0..POT_TYPES.len() {
            x.push(if t == spot.pot_type { 1.0 } else { 0.0 });
        }
        x
    }

    /// Raw net output for one input vector: solved minus balanced, oop then ip.
    pub fn residual(&self, x: &[f32]) -> Vec<f32> {
        let mut h: Vec<f32> = x.iter().zip(&self.mu).zip(&self.sd).map(|((v, m), s)| (v - m) / s).collect();
        for (k, layer) in self.layers.iter().enumerate() {
            let mut out = layer.b.clone();
            for i in 0..layer.rows {
                let xi = h[i];
                if xi == 0.0 {
                    continue;
                }
                let row = &layer.w[i * layer.cols..(i + 1) * layer.cols];
                for (o, w) in out.iter_mut().zip(row) {
                    *o += xi * w;
                }
            }
            if k + 1 < self.layers.len() {
                for o in &mut out {
                    *o = o.max(0.0);
                }
            }
            h = out;
        }
        h
    }

    /// `residual` for many inputs at once (`xs` holds them back to back).
    /// Each weight row is read once per batch instead of once per input,
    /// which is several times faster for the thousands of leaves of a big
    /// preflop tree. Same numbers as calling `residual` on each input.
    pub fn residual_batch(&self, xs: &[f32]) -> Vec<f32> {
        let inputs = self.mu.len();
        let n = xs.len() / inputs;
        let mut h: Vec<f32> = xs.chunks_exact(inputs)
            .flat_map(|x| x.iter().zip(&self.mu).zip(&self.sd).map(|((v, m), s)| (v - m) / s))
            .collect();
        for (k, layer) in self.layers.iter().enumerate() {
            let mut out: Vec<f32> = (0..n).flat_map(|_| layer.b.iter().cloned()).collect();
            for i in 0..layer.rows {
                let row = &layer.w[i * layer.cols..(i + 1) * layer.cols];
                for s in 0..n {
                    let xi = h[s * layer.rows + i];
                    if xi == 0.0 {
                        continue;
                    }
                    for (o, w) in out[s * layer.cols..(s + 1) * layer.cols].iter_mut().zip(row) {
                        *o += xi * w;
                    }
                }
            }
            if k + 1 < self.layers.len() {
                for o in &mut out {
                    *o = o.max(0.0);
                }
            }
            h = out;
        }
        h
    }

    /// Predicted per-class values (fraction of the pot), out of position first.
    pub fn values(&self, spot: &LeafSpot) -> [Vec<f32>; 2] {
        let r = self.residual(&Self::features(spot));
        let mut out = [spot.balanced[0].to_vec(), spot.balanced[1].to_vec()];
        for p in 0..2 {
            for k in 0..NUM_CLASSES {
                out[p][k] += r[p * NUM_CLASSES + k];
            }
        }
        out
    }
}

/// A net whose output ignores its input: `bias[k]` for output k (oop 169
/// then ip 169). For tests of the solver's use of the net.
#[cfg(test)]
pub(crate) fn constant_net(bias: &[f32]) -> LeafNet {
    let inputs = 4 * NUM_CLASSES + META;
    assert_eq!(bias.len(), 2 * NUM_CLASSES);
    LeafNet {
        header: serde_json::json!({"sizes": [inputs, 1, 2 * NUM_CLASSES]}),
        mu: vec![0.0; inputs],
        sd: vec![1.0; inputs],
        layers: vec![
            Layer { rows: inputs, cols: 1, w: vec![0.0; inputs], b: vec![0.0] },
            Layer { rows: 1, cols: 2 * NUM_CLASSES, w: vec![0.0; 2 * NUM_CLASSES], b: bias.to_vec() },
        ],
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tiny_net(seed: u32) -> Vec<u8> {
        // 686 -> 3 -> 338 with deterministic weights
        let sizes = [4 * NUM_CLASSES + META, 3, 2 * NUM_CLASSES];
        let header = serde_json::json!({"format": "gtopen-leaf-net", "version": 1, "sizes": sizes});
        let blob = serde_json::to_vec(&header).unwrap();
        let mut bytes = MAGIC.to_vec();
        bytes.extend((blob.len() as u32).to_le_bytes());
        bytes.extend(&blob);
        let mut k = seed;
        let mut next = || {
            k = k.wrapping_mul(1664525).wrapping_add(1013904223);
            ((k >> 8) as f32 / (1u32 << 24) as f32 - 0.5) * 0.2
        };
        let mut vals: Vec<f32> = Vec::new();
        vals.extend((0..sizes[0]).map(|_| 0.1));
        vals.extend((0..sizes[0]).map(|_| 2.0));
        for w in sizes.windows(2) {
            vals.extend((0..w[0] * w[1]).map(|_| next()));
            vals.extend((0..w[1]).map(|_| next()));
        }
        for v in vals {
            bytes.extend(v.to_le_bytes());
        }
        bytes
    }

    #[test]
    fn loads_and_runs_a_net() {
        let net = LeafNet::from_bytes(&tiny_net(7)).unwrap();
        let r = vec![0.5f32; NUM_CLASSES];
        let b = vec![0.4f32; NUM_CLASSES];
        let spot = LeafSpot { range: [&r, &r], balanced: [&b, &b], pot_bb: 6.0, stack_bb: 97.0,
                              rake_frac: 0.05, rake_cap_bb: 3.0, pot_type: 1 };
        let x = LeafNet::features(&spot);
        assert_eq!(x.len(), 4 * NUM_CLASSES + META);
        assert_eq!(x[0], 1.0, "ranges are scaled so the largest weight is 1");
        assert_eq!(&x[x.len() - 4..], &[0.0, 1.0, 0.0, 0.0]);
        let v = net.values(&spot);
        assert!(v.iter().flatten().all(|x| x.is_finite()));
        // residual is the difference from balanced
        let res = net.residual(&x);
        assert!((v[1][5] - (0.4 + res[NUM_CLASSES + 5])).abs() < 1e-6);
        // a batch gives exactly the per-input numbers
        let b2 = vec![0.1f32; NUM_CLASSES];
        let other = LeafSpot { balanced: [&b2, &b], pot_bb: 20.0, pot_type: 2, ..spot };
        let mut xs = x.clone();
        xs.extend(LeafNet::features(&other));
        let batch = net.residual_batch(&xs);
        assert_eq!(&batch[..2 * NUM_CLASSES], &res[..]);
        assert_eq!(&batch[2 * NUM_CLASSES..], &net.residual(&LeafNet::features(&other))[..]);
    }

    #[test]
    fn rejects_bad_files() {
        assert!(LeafNet::from_bytes(b"nope").is_err());
        let mut bytes = tiny_net(1);
        bytes.truncate(bytes.len() - 4);
        assert!(LeafNet::from_bytes(&bytes).is_err());
    }
}
