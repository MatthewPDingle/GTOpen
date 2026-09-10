        if std::env::var("PREFLOP_GPU_LAYOUT_STATS").as_deref() == Ok("1") {
            println!("preflop gpu layout: {}", serde_json::json!({
                "baseline": "optimized_8e7e4b0",
                "model": s.multiway_equity_model(), "nodes": n, "seats": np,
                "budget_mb": budget_mb, "planned_need_mb": need,
                "forced_nodes": n_forced, "frozen_nodes": n_frozen,
                "forced_elements": forced.len(), "forced_bytes": forced_storage_bytes(forced.len())?,
                "multiway_enabled": use_multiway, "multiway_batch": mw_batch,
                "multiway_particles": super::multiway::SAMPLES,
                "cdf_slots": if use_multiway { compact.capacity } else { 0 },
                "cdf_allocated_bytes": mw_cache_len * std::mem::size_of::<f32>(),
                "compact_cdf": compact.enabled, "normalized_cdf": use_mw_normalized,
                "hu_equity_cache_enabled": use_eq_cache,
                "hu_equity_cache_slots": if use_eq_cache { eq_plan.blocks.len() } else { 0 },
                "hu_equity_cache_allocated_bytes": eq_cache_len * std::mem::size_of::<f32>(),
            }));
        }

