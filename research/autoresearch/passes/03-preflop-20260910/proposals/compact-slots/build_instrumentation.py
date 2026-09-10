from pathlib import Path
import difflib
import hashlib

out = Path(__file__).parent
src = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910\crates\solver\src\preflop\gpu.rs')
old = src.read_text(encoding='utf-8')
anchor = '        Self { slots, blocks, work, spans }'
assert old.count(anchor) == 1
replacement = '''        let plan = Self { slots, blocks, work, spans };
        // Opt-in planning-only instrumentation: no CUDA allocation/launch,
        // strategy mutation, or altered cache layout. Also works via the CPU
        // caller of vram_estimate_mb before GPU construction.
        if multiway && std::env::var_os("PREFLOP_MW_SLOT_STATS").is_some() {
            let counts: Vec<usize> = plan.spans[..s.n].iter().map(|&(_, count)| count as usize).collect();
            let union = plan.blocks.len();
            let max_seat = counts.iter().copied().max().unwrap_or(0);
            let layouts: Vec<_> = [1usize, 7, 32].into_iter().map(|batch| {
                let per_slot = (NUM_CLASSES + 1) * batch * 4;
                let normalization = NUM_CLASSES * 4;
                // Both remapping approaches retain the existing union maps,
                // work spans and active flags; only these additions/savings differ.
                let static_map = s.n * union * 4;
                let dynamic_map = union * 4;
                let saved_direct = (union - max_seat) * per_slot;
                let saved_normalized = (union - max_seat) * (per_slot + normalization);
                serde_json::json!({
                    "batch": batch,
                    "current_cdf_bytes": union * per_slot,
                    "compact_cdf_bytes": max_seat * per_slot,
                    "current_normalized_bytes": union * normalization,
                    "compact_normalized_bytes": max_seat * normalization,
                    "static_map_bytes": static_map,
                    "dynamic_map_bytes": dynamic_map,
                    "net_saved_static_direct_bytes": saved_direct as i128 - static_map as i128,
                    "net_saved_static_normalized_bytes": saved_normalized as i128 - static_map as i128,
                    "net_saved_dynamic_direct_bytes": saved_direct as i128 - dynamic_map as i128,
                    "net_saved_dynamic_normalized_bytes": saved_normalized as i128 - dynamic_map as i128,
                })
            }).collect();
            println!("preflop mw slot stats: {}", serde_json::json!({
                "positions": &s.cfg.positions,
                "union_slots": union,
                "per_traverser_slots": counts,
                "max_traverser_slots": max_seat,
                "max_union_ratio": if union == 0 { 0.0 } else { max_seat as f64 / union as f64 },
                "layouts": layouts,
            }));
        }
        plan'''
new = old.replace(anchor, replacement)
patch = difflib.unified_diff(old.splitlines(True), new.splitlines(True),
    fromfile='a/crates/solver/src/preflop/gpu.rs', tofile='b/crates/solver/src/preflop/gpu.rs')
(out / 'instrumentation.patch').write_bytes(''.join(patch).encode('utf-8'))
(out / 'gpu-instrumented.rs').write_bytes(new.replace('\n', '\r\n').encode('utf-8'))
(out / 'baseline-sha256.txt').write_text(hashlib.sha256(src.read_bytes()).hexdigest() + '\n', encoding='utf-8')
print('Opt-in slot-count instrumentation proposal generated; no source edits.')
