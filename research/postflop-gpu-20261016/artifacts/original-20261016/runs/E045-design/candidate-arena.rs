//! Exact host mapping for GPU arenas containing only visited action nodes.
use super::{e, plan::GpuPlan, write_arena};
use crate::{cfr::Solver, store::Store, tree::KIND_ACTION};
use cudarc::driver::{CudaSlice, CudaStream};
use std::sync::Arc;
use rayon::prelude::*;

struct ActiveBlock {
    node: u32,
    host: u64,
    device: usize,
    len: usize,
}

struct CopySpan { host: u64, device: usize, len: usize }

struct InactiveBlock {
    node: u32,
    host: u64,
    len: usize,
    // usize::MAX represents a block of positive-zero bits. Signed zero and
    // every other initial bit pattern have an explicit snapshot.
    initial: [usize; 2],
}

pub(super) struct ArenaLayout {
    compact: bool,
    len: usize,
    active: Vec<ActiveBlock>,
    copies: Vec<CopySpan>,
    inactive: Vec<InactiveBlock>,
    initial: [Vec<f32>; 2],
    zeros: Vec<f32>,
}

// Integer OR is exact across chunk/reduction order. Keep small inputs serial.
const ZERO_PROOF_CHUNK_WORDS: usize = 1 << 20;
fn zero_proof_i16_bits(q: &[i16]) -> u16 {
    if q.len() < 2 * ZERO_PROOF_CHUNK_WORDS {
        q.iter().fold(0u16, |bits, &v| bits | v as u16)
    } else {
        q.par_chunks(ZERO_PROOF_CHUNK_WORDS)
            .map(|chunk| chunk.iter().fold(0u16, |bits, &v| bits | v as u16))
            .reduce(|| 0, |a, b| a | b)
    }
}
fn zero_proof_u16_bits(q: &[u16]) -> u16 {
    if q.len() < 2 * ZERO_PROOF_CHUNK_WORDS {
        q.iter().fold(0u16, |bits, &v| bits | v)
    } else {
        q.par_chunks(ZERO_PROOF_CHUNK_WORDS)
            .map(|chunk| chunk.iter().fold(0u16, |bits, &v| bits | v))
            .reduce(|| 0, |a, b| a | b)
    }
}

impl ArenaLayout {
    pub(super) fn new(solver: &Solver, plan: &GpuPlan, p: usize) -> Self {
        let len = plan.arena_elements[p];
        let compact = len != solver.spot.tree.data_size[p] as usize
            || solver.spot.tree.nodes.iter().enumerate().any(|(i, n)|
                n.kind == KIND_ACTION && n.player as usize == p
                    && plan.node_data_off[i] != n.data_offset);
        let mut layout = Self {
            compact, len, active: Vec::new(), copies: Vec::new(), inactive: Vec::new(),
            initial: [Vec::new(), Vec::new()], zeros: Vec::new(),
        };
        if compact {
            let nh = solver.spot.hands[p].len();
            let mut max_inactive = 0;
            for (i, node) in solver.spot.tree.nodes.iter().enumerate() {
                if node.kind != KIND_ACTION || node.player as usize != p { continue; }
                let count = node.num_children as usize * nh;
                let off = plan.node_data_off[i];
                if off == u64::MAX {
                    max_inactive = max_inactive.max(count);
                    layout.inactive.push(InactiveBlock {
                        node: i as u32, host: node.data_offset, len: count,
                        initial: [usize::MAX; 2],
                    });
                } else {
                    layout.active.push(ActiveBlock {
                        node: i as u32, host: node.data_offset, device: off as usize, len: count,
                    });
                }
            }
            layout.zeros.resize(max_inactive, 0.0);
            for block in &layout.active {
                if let Some(last) = layout.copies.last_mut() {
                    if last.host + last.len as u64 == block.host
                        && last.device + last.len == block.device {
                        last.len += block.len;
                        continue;
                    }
                }
                layout.copies.push(CopySpan { host: block.host, device: block.device, len: block.len });
            }
        }
        layout
    }

    fn can_upload_zeros(&self, store: &Store, which: usize) -> bool {
        // Both inputs must prove positive-zero decoded bits: a negative q
        // with +0 scale, or a zero q with -0 scale, can decode to -0.0.
        // Check scales first so a warm arena can reject this path cheaply.
        let zero = match store {
            Store::I16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && zero_proof_i16_bits(q.as_slice()) == 0
            }
            Store::U16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && zero_proof_u16_bits(q.as_slice()) == 0
            }
            Store::F32(_) => false,
        };
        // Keep previously captured inactive state on the existing path if a
        // layout is reused. Fresh layouts already have the zero sentinels.
        zero && self.initial[which].is_empty()
            && self.inactive.iter().all(|block| block.initial[which] == usize::MAX)
    }

    pub(super) fn upload(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize, which: usize,
        staging: &mut [f32],
    ) -> Result<CudaSlice<f32>, String> {
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        if self.can_upload_zeros(store, which) {
            // Fresh compressed arenas need neither f32 host decoding nor a
            // host-to-device copy. Inactive positive-zero sentinels stay intact.
            let device = stream.alloc_zeros::<f32>(self.len).map_err(e)?;
            stream.synchronize().map_err(e)?;
            return Ok(device);
        }
        if !self.compact {
            if let Store::F32(b) = store {
                return stream.clone_htod(b.as_slice()).map_err(e);
            }
            // Decode directly into the reusable pinned allocation. A full
            // temporary f32 image would duplicate this buffer for each upload.
            let data = &mut staging[..self.len];
            let nh = solver.spot.hands[p].len();
            for (i, node) in solver.spot.tree.nodes.iter().enumerate() {
                if node.kind == KIND_ACTION && node.player as usize == p {
                    let len = node.num_children as usize * nh;
                    let off = node.data_offset as usize;
                    unsafe { store.read_f32(i as u32, node.data_offset, len, &mut data[off..off + len]); }
                }
            }
            let device = stream.clone_htod(&data[..]).map_err(e)?;
            stream.synchronize().map_err(e)?;
            return Ok(device);
        }
        let packed = &mut staging[..self.len];
        if let Store::F32(buf) = store {
            for span in &self.copies {
                let host = span.host as usize;
                packed[span.device..span.device + span.len]
                    .copy_from_slice(&buf.as_slice()[host..host + span.len]);
            }
        } else {
            for block in &self.active {
                unsafe {
                    store.read_f32(block.node, block.host, block.len,
                        &mut packed[block.device..block.device + block.len]);
                }
            }
        }
        let mut scratch = vec![0.0; self.zeros.len()];
        for block in &mut self.inactive {
            let values = if let Store::F32(buf) = store {
                let host = block.host as usize;
                &buf.as_slice()[host..host + block.len]
            } else {
                let values = &mut scratch[..block.len];
                unsafe { store.read_f32(block.node, block.host, block.len, values); }
                &values[..]
            };
            // A bitwise OR reduction can vectorize the cold zero-block scan;
            // comparison by bits still preserves -0.0 and non-finite payloads.
            if values.iter().fold(0u32, |bits, v| bits | v.to_bits()) != 0 {
                block.initial[which] = self.initial[which].len();
                self.initial[which].extend_from_slice(values);
            }
        }
        // These snapshots are immutable for the engine's lifetime. CPU
        // queries can materialize suit siblings between downloads; a later
        // sync must restore exactly what the former full GPU arena held.
        self.initial[which].shrink_to_fit();
        let device = stream.clone_htod(&packed[..]).map_err(e)?;
        // The same pinned allocation stages the next upload and all downloads.
        stream.synchronize().map_err(e)?;
        Ok(device)
    }

    pub(super) fn write(&self, solver: &Solver, p: usize, which: usize, data: &[f32]) {
        if !self.compact {
            write_arena(solver, which != 0, p, data);
            return;
        }
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        if let Store::F32(buf) = store {
            // Host spans are disjoint, just like parallel CPU CFR arenas.
            self.copies.par_iter().for_each(|span| {
                unsafe { buf.slice(span.host, span.len) }
                    .copy_from_slice(&data[span.device..span.device + span.len]);
            });
            self.inactive.par_iter().for_each(|block| {
                let dst = unsafe { buf.slice(block.host, block.len) };
                let start = block.initial[which];
                if start == usize::MAX { dst.fill(0.0); }
                else { dst.copy_from_slice(&self.initial[which][start..start + block.len]); }
            });
            return;
        }
        self.active.par_iter().for_each(|block| {
            unsafe {
                store.write_f32(block.node, block.host, block.len,
                    &data[block.device..block.device + block.len]);
            }
        });
        self.inactive.par_iter().for_each(|block| {
            let start = block.initial[which];
            let values = if start == usize::MAX { &self.zeros[..block.len] }
                else { &self.initial[which][start..start + block.len] };
            unsafe { store.write_f32(block.node, block.host, block.len, values); }
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn layout(compact: bool) -> ArenaLayout {
        ArenaLayout {
            compact, len: 4, active: Vec::new(), copies: Vec::new(),
            inactive: if compact {
                vec![InactiveBlock { node: 1, host: 2, len: 2, initial: [usize::MAX; 2] }]
            } else { Vec::new() },
            initial: [Vec::new(), Vec::new()], zeros: vec![0.0; 2],
        }
    }

    #[test]
    fn zero_upload_accepts_only_positive_zero_compressed_sources() {
        for compact in [false, true] {
            let layout = layout(compact);
            for store in [Store::i16(4, 2), Store::u16(4, 2)] {
                for which in 0..2 {
                    assert!(layout.can_upload_zeros(&store, which));
                }
                let mut decoded = [f32::NAN; 4];
                unsafe { store.read_f32(0, 0, decoded.len(), &mut decoded); }
                assert!(decoded.iter().all(|v| v.to_bits() == 0));
                assert!(layout.inactive.iter().all(|block| block.initial == [usize::MAX; 2]));
                assert!(layout.initial.iter().all(Vec::is_empty));
            }
            assert!(!layout.can_upload_zeros(&Store::f32(4), 0));
        }
    }

    #[test]
    fn zero_upload_rejects_nonzero_quantized_values_with_zero_scale() {
        let layout = layout(true);
        let mut signed = Store::i16(4, 2);
        for value in [1, -1, i16::MIN, i16::MAX] {
            if let Store::I16 { q, .. } = &mut signed {
                q.as_mut_slice()[3] = value;
            }
            assert!(!layout.can_upload_zeros(&signed, 0));
        }
        let mut unsigned = Store::u16(4, 2);
        for value in [1, u16::MAX] {
            if let Store::U16 { q, .. } = &mut unsigned {
                q.as_mut_slice()[3] = value;
            }
            assert!(!layout.can_upload_zeros(&unsigned, 1));
        }
    }

    #[test]
    fn zero_upload_rejects_signed_zero_nonzero_and_nonfinite_scales() {
        let layout = layout(true);
        let values = [
            -0.0, 1.0, -1.0, f32::from_bits(1), -f32::from_bits(1),
            f32::INFINITY, f32::NEG_INFINITY, f32::from_bits(0x7fc0_0123),
        ];
        for mut store in [Store::i16(4, 2), Store::u16(4, 2)] {
            for value in values {
                match &mut store {
                    Store::I16 { scale, .. } | Store::U16 { scale, .. } => {
                        scale.as_mut_slice()[1] = value;
                    }
                    Store::F32(_) => unreachable!(),
                }
                assert!(!layout.can_upload_zeros(&store, 0), "scale bits {:08x}", value.to_bits());
            }
        }
    }

    #[test]
    fn zero_upload_preserves_existing_inactive_snapshot_metadata() {
        let mut layout = layout(true);
        let store = Store::i16(4, 2);
        layout.initial[0].push(-0.0);
        assert!(!layout.can_upload_zeros(&store, 0));
        layout.inactive[0].initial[0] = 0;
        assert!(!layout.can_upload_zeros(&store, 0));
        assert!(layout.can_upload_zeros(&store, 1));
        assert_eq!(layout.initial[0][0].to_bits(), (-0.0f32).to_bits());
        assert_eq!(layout.inactive[0].initial, [0, usize::MAX]);
        layout.initial[0].clear();
        assert!(!layout.can_upload_zeros(&store, 0));
    }
}

#[cfg(test)]
mod e045_zero_proof_control {
    use super::*;
    impl ArenaLayout {
    fn e045_original_can_upload_zeros(&self, store: &Store, which: usize) -> bool {
        // Both inputs must prove positive-zero decoded bits: a negative q
        // with +0 scale, or a zero q with -0 scale, can decode to -0.0.
        // Check scales first so a warm arena can reject this path cheaply.
        let zero = match store {
            Store::I16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0
            }
            Store::U16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0
            }
            Store::F32(_) => false,
        };
        // Keep previously captured inactive state on the existing path if a
        // layout is reused. Fresh layouts already have the zero sentinels.
        zero && self.initial[which].is_empty()
            && self.inactive.iter().all(|block| block.initial[which] == usize::MAX)
    }


    }
    #[test]
    fn parallel_integer_or_matches_serial_original() {
        let c=ZERO_PROOF_CHUNK_WORDS;
        let lengths=[0,1,7,127,128,129,c-1,c,c+1,2*c-1,2*c,2*c+1,3*c+17];
        let mut checks=0usize;
        for threads in [1,2,16] {
            let pool=rayon::ThreadPoolBuilder::new().num_threads(threads).build().unwrap();
            pool.install(|| {
                for n in lengths {
                    let mut u=vec![0u16;n];let mut i=vec![0i16;n];
                    let mut check=|u:&[u16],i:&[i16]| {
                        let ub=u.to_vec();let ib=i.to_vec();
                        assert_eq!(zero_proof_u16_bits(u),u.iter().fold(0u16,|a,&v|a|v));
                        assert_eq!(zero_proof_i16_bits(i),i.iter().fold(0u16,|a,&v|a|v as u16));
                        assert_eq!(u,ub);assert_eq!(i,ib);checks+=2;
                    };
                    check(&u,&i);
                    let mut positions=vec![0,n.saturating_sub(1),c-1,c,2*c-1,2*c];
                    positions.retain(|&p|p<n);positions.sort_unstable();positions.dedup();
                    for p in positions {for bit in 0..16 {
                        u[p]=1u16<<bit;i[p]=u[p] as i16;check(&u,&i);u[p]=0;i[p]=0;
                    }}
                    for p in 0..n {
                        u[p]=(p as u32).wrapping_mul(73).wrapping_add(997) as u16;i[p]=u[p] as i16;
                    }
                    check(&u,&i);
                }
            });
        }
        assert_eq!(checks,3516);
        println!("E045_INTEGER_OR_CONTROL {}",serde_json::json!({"checks":checks,"threads":[1,2,16],"lengths":lengths,"inputs_unchanged":true,"raw_integer_or_exact":true}));
    }
    fn layout(compact:bool)->ArenaLayout {
        ArenaLayout {compact,len:4,active:Vec::new(),copies:Vec::new(),initial:[Vec::new(),Vec::new()],zeros:vec![0.;2],
            inactive:if compact {vec![InactiveBlock{node:1,host:2,len:2,initial:[usize::MAX;2]}]}else{Vec::new()}}
    }
    #[test]
    fn full_zero_predicate_matches_accepted_original() {
        let c=ZERO_PROOF_CHUNK_WORDS;let mut checks=0usize;
        for n in [0,1,c-1,c,c+1,2*c-1,2*c,2*c+1,3*c+17] {
            for compact in [false,true] {for which in 0..2 {for kind in 0..2 {for state in 0..8 {
                let mut a=layout(compact);let mut store=if kind==0{Store::i16(n,2)}else{Store::u16(n,2)};
                match &mut store {
                    Store::I16{q,scale}=>{if state==1&&n>0{q.as_mut_slice()[n-1]=i16::MIN;}if (2..=4).contains(&state){scale.as_mut_slice()[1]=f32::from_bits([0x80000000,0x7fc00123,0x3f800000][state-2]);}},
                    Store::U16{q,scale}=>{if state==1&&n>0{q.as_mut_slice()[n-1]=u16::MAX;}if (2..=4).contains(&state){scale.as_mut_slice()[1]=f32::from_bits([0x80000000,0x7fc00123,0x3f800000][state-2]);}},
                    _=>unreachable!(),
                }
                if state==5{a.initial[which].push(-0.0);}
                if state==6&&compact{a.inactive[0].initial[which]=0;}
                if state==7{a.initial[1-which].push(f32::from_bits(0x7fc00123));}
                let snapshot=match &store {Store::I16{q,scale}=>(q.as_slice().iter().map(|&x|x as u16).collect::<Vec<_>>(),scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>()),Store::U16{q,scale}=>(q.as_slice().to_vec(),scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>()),_=>unreachable!()};
                assert_eq!(a.can_upload_zeros(&store,which),a.e045_original_can_upload_zeros(&store,which),"n={n} compact={compact} which={which} kind={kind} state={state}");
                let after=match &store {Store::I16{q,scale}=>(q.as_slice().iter().map(|&x|x as u16).collect::<Vec<_>>(),scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>()),Store::U16{q,scale}=>(q.as_slice().to_vec(),scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>()),_=>unreachable!()};
                assert_eq!(snapshot,after);checks+=1;
            }}}}
        }
        assert_eq!(checks,576);
        println!("E045_FULL_PREDICATE_CONTROL {}",serde_json::json!({"cases":checks,"inputs_unchanged":true,"accepted_original_exact":true}));
    }
}
