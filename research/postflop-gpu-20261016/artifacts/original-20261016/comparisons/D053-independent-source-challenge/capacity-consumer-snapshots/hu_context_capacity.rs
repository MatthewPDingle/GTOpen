//! CPU-only payload planning for a qualified HU context. Never allocates CUDA.
//! CONTEXT MANIFEST OUTPUT; use a small texture probe before planning a panel.
use serde_json::{json, Value};
use solver::{Spot, SpotConfig, TreeConfig, StreetSizing, parse_sizes};
use solver::gpu::stored_capacity_plan;
use solver::preflop::equity::class_label;
use std::{fs::OpenOptions, io::Write};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    assert_eq!(args.len(), 3, "CONTEXT MANIFEST OUTPUT");
    assert!(!std::path::Path::new(&args[2]).exists(), "preserve evidence");
    let read = |p: &str| -> Value { serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap() };
    let d = read(&args[0]); let m = read(&args[1]);
    assert_eq!(d["schema"], "hu-context-v1");
    assert_eq!(d["postflop_order"], json!([0, 1]));
    let ranges: Vec<String> = (0..2).map(|p| {
        let weights: Vec<f64> = (0..169).map(|c|
            d["incoming_class_mass"][p][c].as_f64().unwrap() /
            if c/13 == c%13 { 6. } else if c/13 > c%13 { 4. } else { 12. }).collect();
        assert!(weights.iter().all(|w| w.is_finite() && *w >= 0.));
        let max = weights.iter().copied().fold(0., f64::max);
        assert!(max > 0.);
        (0..169).filter(|&c| weights[c]/max >= 1e-5).map(class_label).collect::<Vec<_>>().join(",")
    }).collect();
    let menu = m["bet_menu"].as_str().unwrap();
    let sizing = StreetSizing { bet:parse_sizes(menu)?, raise:parse_sizes("100")?, donk:parse_sizes(menu)? };
    let mut rows = vec![];
    let mut workspace = [0u64; 11];
    let mut metadata = 0u64; let mut host = 0u64; let mut state = 0u64;
    let mut peak = 0u64;
    for b in m["boards"].as_array().unwrap() {
        let board = b["board"].as_str().unwrap();
        for (i, n) in d["nodes"].as_array().unwrap().iter().enumerate() {
            if n["leaf"]["type"] != "postflop" { continue; }
            let pot = n["leaf"]["starting_pot"].as_f64().unwrap();
            let stack = n["leaf"]["effective_stack"].as_f64().unwrap();
            assert!(stack > 0.);
            let spot = Spot::new_with_limit(SpotConfig {
                board:board.into(), range_oop:ranges[0].clone(), range_ip:ranges[1].clone(),
                tree:TreeConfig { starting_pot:pot, effective_stack:stack,
                    rake_pct:d["rake_fraction"].as_f64().unwrap(), rake_cap:d["rake_cap"].as_f64().unwrap(),
                    max_raises:1, oop:[sizing.clone(),sizing.clone(),sizing.clone()],
                    ip:[sizing.clone(),sizing.clone(),sizing.clone()], ..Default::default() },
            }, Some(2_000_000))?;
            let mut row = stored_capacity_plan(&spot);
            metadata += row["retained_gpu_payload_bytes"].as_u64().unwrap();
            host += row["host_retained_payload_bytes"].as_u64().unwrap();
            state += row["canonical_state_bytes"].as_u64().unwrap();
            let components = row["workspace_components_bytes"].as_array().unwrap();
            assert_eq!(components.len(), workspace.len());
            peak = peak.max(metadata + workspace.iter().sum::<u64>() + components.iter().map(|v| v.as_u64().unwrap()).sum::<u64>());
            for (w, v) in workspace.iter_mut().zip(components) { *w = (*w).max(v.as_u64().unwrap()); }
            row["board"] = json!(board); row["preflop_leaf"] = json!(i);
            row["pot"] = json!(pot); row["effective_stack"] = json!(stack);
            println!("planned {board} leaf={i} pot={pot}: canonical={} retained_device={}",
                row["canonical_state_bytes"], row["retained_gpu_payload_bytes"]);
            rows.push(row);
        }
    }
    assert!(!rows.is_empty());
    let output = json!({"context":args[0],"manifest":m,"rows":rows,
        "totals":{"canonical_state_bytes":state,"host_retained_payload_bytes":host,
            "ram_payload_total_bytes":host+state,"retained_gpu_payload_bytes":metadata,
            "shared_gpu_workspace_bytes":workspace.iter().sum::<u64>(),
            "steady_gpu_payload_bytes":metadata+workspace.iter().sum::<u64>(),
            "constructor_gpu_payload_upper_bytes":peak},
        "device_allocated":false,"strategies_evaluated":false,
        "note":"CPU-only payload estimate. Includes all postflop leaves with full incoming support. Excludes allocator, driver, temporary CPU plans and evaluation scratch. Not an admission decision; preserve RAM/VRAM reserves."});
    OpenOptions::new().write(true).create_new(true).open(&args[2])?
        .write_all(&serde_json::to_vec_pretty(&output)?)?;
    Ok(())
}
