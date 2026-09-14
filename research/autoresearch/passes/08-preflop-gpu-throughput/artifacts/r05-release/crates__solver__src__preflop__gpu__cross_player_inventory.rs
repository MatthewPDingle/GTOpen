//! D04: read-only inventory of immutable average-policy CDFs across traversers.
use super::*;
use serde_json::json;
use std::collections::{HashMap, HashSet};
mod cohorts;

#[derive(Default)]
struct Interner { buckets: HashMap<u64, Vec<(Vec<u32>, u32)>>, next: u32 }
impl Interner {
    fn insert_hash(&mut self, bits: &[u32], hash: u64) -> u32 {
        let bucket = self.buckets.entry(hash).or_default();
        if let Some((_, id)) = bucket.iter().find(|(old, _)| old == bits) { return *id; }
        let id = self.next; self.next += 1;
        bucket.push((bits.to_vec(), id)); id
    }
    fn insert(&mut self, values: &[f32]) -> u32 {
        let bits: Vec<_> = values.iter().map(|x| x.to_bits()).collect();
        let hash = bits.iter().fold(0xcbf29ce484222325u64, |h, x| {
            x.to_le_bytes().iter().fold(h, |h, b| (h ^ *b as u64).wrapping_mul(0x100000001b3))
        });
        self.insert_hash(&bits, hash)
    }
}

// Enumerate every disjoint pairing; exactly one singleton for odd player counts.
fn pairings(players: &[usize]) -> Vec<Vec<Vec<usize>>> {
    if players.is_empty() { return vec![vec![]]; }
    let p = players[0]; let mut result = Vec::new();
    if players.len() % 2 == 1 {
        for mut tail in pairings(&players[1..]) {
            tail.insert(0, vec![p]); result.push(tail);
        }
    }
    for i in 1..players.len() {
        let rest: Vec<_> = players[1..].iter().copied().filter(|&q| q != players[i]).collect();
        for mut tail in pairings(&rest) {
            tail.insert(0, vec![p, players[i]]); result.push(tail);
        }
    }
    result
}
fn union_len(group: &[usize], sets: &[HashSet<u32>]) -> usize {
    let mut union = HashSet::new();
    for &p in group { union.extend(sets[p].iter().copied()); }
    union.len()
}

#[test]
fn cross_player_inventory_identity_and_pairing() {
    let mut ids = Interner::default();
    let a = [0u32, 0.25f32.to_bits(), 0.75f32.to_bits()];
    assert_eq!(ids.insert_hash(&a, 7), ids.insert_hash(&a, 7));
    let mut b = a; b[1] += 1;
    assert_ne!(ids.insert_hash(&a, 7), ids.insert_hash(&b, 7));
    b = a; b[0] = (-0.0f32).to_bits();
    assert_ne!(ids.insert_hash(&a, 7), ids.insert_hash(&b, 7));
    assert_eq!(ids.next, 3);
    assert_eq!(pairings(&[0, 1, 2, 3]).len(), 3);
    assert_eq!(pairings(&[0, 1, 2, 3, 4]).len(), 15);
    assert_eq!(pairings(&[0, 1, 2, 3, 4, 5, 6, 7]).len(), 105);
    for n in 1..=9 {
        let all: Vec<_> = (0..n).collect();
        let mut seen = HashSet::new();
        for groups in pairings(&all) {
            let mut flat: Vec<_> = groups.iter().flatten().copied().collect(); flat.sort();
            assert_eq!(flat, all);
            assert_eq!(groups.iter().filter(|x| x.len() == 1).count(), n % 2);
            assert!(groups.iter().all(|x| !x.is_empty() && x.len() <= 2));
            assert!(seen.insert(groups));
        }
    }
    let sets = vec![[1,2].into_iter().collect(), [2,3].into_iter().collect()];
    assert_eq!(union_len(&[0,1], &sets), 3);
}

#[test]
#[ignore = "D04 read-only inventory; frozen save and idle GPU required"]
fn cross_player_inventory_from_saved_state() {
    let input = std::env::var("PREFLOP_GPU_REUSE_INPUT").unwrap();
    let output = std::env::var("PREFLOP_GPU_REUSE_OUTPUT").unwrap();
    assert!(!std::path::Path::new(&output).exists());
    let eq_path = std::env::var("PREFLOP_GPU_REUSE_EQUITY").unwrap();
    let data = std::fs::read(&eq_path).unwrap();
    let samples = u32::from_le_bytes(data[..4].try_into().unwrap()); drop(data);
    let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(&eq_path, samples));
    let s = PreflopSolver::load_game(&input, eq).unwrap();
    assert_eq!(s.multiway_equity_model(), "coupled_deck_v1");
    let age = s.iteration; let before = s.arena_snapshot();
    let mut g = PreflopGpu::new(&s, 23000).unwrap();
    assert!(g.use_mw_normalized && g.use_mw_prepared && g.use_mw_compact != 0);
    assert_eq!(g.mw_batch, 32);
    let work = g.stream.clone_dtoh(&g.d_mw_work).unwrap();
    let blocks = g.stream.clone_dtoh(&g.d_mw_blocks).unwrap();
    // Exactly queue_evaluation's common down sweep. No learning-active gating.
    g.down(1, -1).unwrap();
    let mass = g.stream.clone_dtoh(&g.d_reach_mass).unwrap();
    let reach = g.stream.clone_dtoh(&g.d_reach).unwrap();
    let mut identities = Interner::default();
    let mut sources = HashMap::new(); let mut source_rechecks = 0usize;
    let mut static_sets = Vec::new(); let mut unique_sets = Vec::new(); let mut rows = Vec::new();
    for p in 0..g.np as usize {
        let (start, count) = g.mw_spans[p]; let gate = 0i32;
        if count > 0 { unsafe {
            g.stream.launch_builder(&g.f_multiway_normalize)
                .arg(&g.d_mw_work).arg(&start).arg(&g.d_mw_blocks)
                .arg(&g.d_reach).arg(&g.d_reach_mass).arg(&g.d_mw_active).arg(&gate)
                .arg(&g.use_mw_compact).arg(&mut g.d_mw_normalized)
                .launch(LaunchConfig { grid_dim: (count,1,1), block_dim: (192,1,1), shared_mem_bytes: 0 }).unwrap();
        }}
        let values = g.stream.clone_dtoh(&g.d_mw_normalized).unwrap();
        let mut slots = HashSet::new(); let mut unique = HashSet::new(); let mut positive = 0;
        for k in 0..count as usize {
            let slot = work[start as usize + k]; assert!(slots.insert(slot));
            let block = blocks[slot as usize];
            if mass[block as usize] <= 0.0 { continue; }
            let v = &values[k*NUM_CLASSES..(k+1)*NUM_CLASSES];
            assert!(v.iter().all(|x| x.is_finite() && *x >= 0.0));
            assert!(v.iter().any(|x| *x > 0.0));
            let id = identities.insert(v); unique.insert(id); positive += 1;
            if let Some(old) = sources.insert(block, id) { assert_eq!(old, id); source_rechecks += 1; }
        }
        rows.push(json!({"player":p,"static_slots":slots.len(),"positive_slots":positive,"unique_distributions":unique.len()}));
        static_sets.push(slots); unique_sets.push(unique);
    }
    let all: Vec<_> = (0..g.np as usize).collect();
    let baseline_rows: usize = unique_sets.iter().map(|s| s.len()).sum();
    let mut pairs = Vec::new();
    for p in 0..all.len() { for q in p+1..all.len() {
        let u = union_len(&[p,q], &unique_sets);
        pairs.push(json!({"players":[p,q],"unique_union":u,"shared_rows":unique_sets[p].len()+unique_sets[q].len()-u,
            "static_union":union_len(&[p,q], &static_sets)}));
    }}
    // Includes every plain device buffer; optional research buffers/graphs are absent.
    let buffer_bytes = device_buffer_bytes(&g);
    let base_bytes: usize = buffer_bytes.values().sum();
    let capacity = g.d_mw_normalized.len()/NUM_CLASSES;
    let old_classify = (capacity + (capacity*2).next_power_of_two())*4;
    let retained_bytes = base_bytes + old_classify;
    let mut plans = Vec::new();
    for groups in pairings(&all) {
        let union_rows: usize = groups.iter().map(|x| union_len(x, &unique_sets)).sum();
        let static_capacity = capacity.max(groups.iter().map(|x| union_len(x, &static_sets)).max().unwrap());
        let unique_capacity = groups.iter().map(|x| union_len(x, &unique_sets)).max().unwrap();
        let cdf_bytes = static_capacity * 32 * 170 * 4;
        let normalized_bytes = static_capacity * NUM_CLASSES * 4;
        let classification_bytes = (static_capacity + (static_capacity*2).next_power_of_two())*4;
        // Conservative separate maps for every pair, union worklists, extra probabilities,
        // and a complete second value arena. Existing maps/worklists remain for learning.
        let maps_bytes = groups.len()*g.mw_union_slots as usize*4;
        let work_bytes: usize = groups.iter().map(|x| union_len(x, &static_sets)*4).sum();
        let extra_value_bytes = g.d_val.len()*4;
        let extra_prob_bytes = g.d_mw_prob.len()*4;
        let total_bytes = base_bytes - g.d_mw_cdf.len()*4 - g.d_mw_normalized.len()*4
            + cdf_bytes + normalized_bytes + classification_bytes + maps_bytes + work_bytes + extra_value_bytes + extra_prob_bytes;
        let reserve_bytes = 256usize*1024*1024;
        plans.push(json!({"groups":groups,"cdf_rows":union_rows,"saved_fraction":1.0-union_rows as f64/baseline_rows as f64,
            "static_capacity":static_capacity,"observed_unique_capacity":unique_capacity,"cdf_bytes":cdf_bytes,
            "observed_unique_cdf_bytes":unique_capacity*32*170*4,"normalized_bytes":normalized_bytes,
            "classification_bytes":classification_bytes,"maps_bytes":maps_bytes,"work_bytes":work_bytes,
            "extra_value_bytes":extra_value_bytes,"extra_prob_bytes":extra_prob_bytes,"total_bytes":total_bytes,
            "reserve_bytes":reserve_bytes,"planned_initial_peak_bytes":total_bytes+reserve_bytes,
            "replace_existing_peak_bytes":total_bytes+reserve_bytes+g.d_mw_cdf.len()*4+g.d_mw_normalized.len()*4+old_classify,
            "fits_preplanned_23gb":total_bytes+reserve_bytes<=23_000_000_000usize}));
    }
    plans.sort_by_key(|p| (p["cdf_rows"].as_u64().unwrap(), p["total_bytes"].as_u64().unwrap(), p["groups"].to_string()));
    let natural: Vec<_> = all.chunks(2).map(|x|x.to_vec()).collect();
    let natural_plan = plans.iter().find(|p| p["groups"] == json!(natural)).unwrap().clone();
    let best = plans[0].clone();
    let admitted = plans.iter().find(|p| p["saved_fraction"].as_f64().unwrap()>=0.25 && p["fits_preplanned_23gb"]==true).cloned();
    let cohort_inventory = if std::env::var("PREFLOP_GPU_COHORT_INVENTORY").as_deref()==Ok("1") {
        Some(cohorts::inventory(&static_sets, &unique_sets, &buffer_bytes))
    } else { None };
    for (actual, expected) in [(g.stream.clone_dtoh(&g.d_regrets).unwrap(), &before.0),
        (g.stream.clone_dtoh(&g.d_strat).unwrap(), &before.1),
        (g.stream.clone_dtoh(&g.d_reach).unwrap(), &reach),
        (g.stream.clone_dtoh(&g.d_reach_mass).unwrap(), &mass)] {
        assert_eq!(actual.len(), expected.len());
        assert!(actual.iter().zip(expected).all(|(a,b)| a.to_bits()==b.to_bits()));
    }
    assert_eq!(age, s.iteration);
    let result = json!({"input":input,"players":s.n,"nodes":s.nodes.len(),"iteration":age,"batch":g.mw_batch,
        "rows":rows,"baseline_cdf_rows":baseline_rows,"all_player_union":identities.next,"pairs":pairs,
        "same_source_rechecks":source_rechecks,"source_identities":sources.len(),"all_static_union":union_len(&all,&static_sets),
        "buffer_bytes":buffer_bytes,"base_bytes":base_bytes,"retained_c01_bytes":retained_bytes,"best_pairing":best,
        "natural_pairing":natural_plan,"admitted_pairing":admitted,"all_pairings":plans,"cohorts":cohort_inventory,
        "arenas_unchanged":true,"average_reaches_unchanged":true,"read_only":true,
        "scope":"Inventory only, not speed. Memory plan requires constructor preallocation; replacing live buffers has a higher peak."});
    std::fs::write(output, serde_json::to_vec_pretty(&result).unwrap()).unwrap();
    println!("D04 {}", json!({"baseline_rows":baseline_rows,"best":best,"admitted":admitted.is_some()}));
}

pub(super) fn device_buffer_bytes(g:&PreflopGpu)->std::collections::BTreeMap<&'static str,usize>{ super::static_cdf::ordinary::ordinary_buffer_bytes(g) }
