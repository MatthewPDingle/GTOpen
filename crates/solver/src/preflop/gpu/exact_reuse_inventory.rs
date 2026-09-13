//! Read-only, opt-in inventory. No production dispatch or caching.
use super::*;
use std::collections::{HashMap, HashSet};
use serde_json::json;

fn bits_hash(v: &[f32]) -> u64 {
    v.iter().fold(0xcbf29ce484222325, |h, x| {
        x.to_bits().to_le_bytes().iter().fold(h, |h, b| (h ^ *b as u64).wrapping_mul(0x100000001b3))
    })
}

// Hash only locates candidates. Every proposed reuse requires full equality.
fn intern<'a>(v: &'a [f32], hash: u64, groups: &mut HashMap<u64, Vec<(&'a [f32], u32)>>,
    next: &mut u32) -> u32 {
    let bucket = groups.entry(hash).or_default();
    if let Some((_, id)) = bucket.iter().find(|(old, _)| old.len() == v.len()
        && old.iter().zip(v).all(|(a,b)| a.to_bits() == b.to_bits())) { return *id; }
    let id = *next; *next += 1; bucket.push((v, id)); id
}

#[test]
fn exact_reuse_classifier_preserves_bits_order_and_multiplicity() {
    let a = vec![0.0f32, 0.25, 0.75];
    let b = a.clone();
    let mut c = a.clone(); c[1] = f32::from_bits(c[1].to_bits()+1);
    let mut d = a.clone(); d[0] = -0.0;
    let mut groups = HashMap::new(); let mut next = 0;
    // Force all values into one hash bucket to prove collision safety.
    let ai=intern(&a,7,&mut groups,&mut next);
    assert_eq!(intern(&b,7,&mut groups,&mut next),ai);
    let ci=intern(&c,7,&mut groups,&mut next);
    let di=intern(&d,7,&mut groups,&mut next);
    assert_eq!(next,3); assert_ne!(ci,ai); assert_ne!(di,ai);
    let mut keys=HashSet::new();
    assert!(keys.insert(vec![ai,ci])); assert!(!keys.insert(vec![ai,ci]));
    assert!(keys.insert(vec![ci,ai])); assert!(keys.insert(vec![ai,ci,ci]));
    assert_eq!(bits_hash(&a),bits_hash(&b));
}

#[test]
#[ignore = "opt-in read-only GPU exact-reuse inventory; requires frozen save and idle GPU"]
fn exact_reuse_inventory_from_saved_state() {
    let input=std::env::var("PREFLOP_GPU_REUSE_INPUT").expect("frozen native input");
    let output=std::env::var("PREFLOP_GPU_REUSE_OUTPUT").expect("new JSON output");
    assert!(!std::path::Path::new(&output).exists());
    let eq_path=std::env::var("PREFLOP_GPU_REUSE_EQUITY").expect("existing equity cache");
    let data=std::fs::read(&eq_path).unwrap();
    let samples=u32::from_le_bytes(data[..4].try_into().unwrap()); drop(data);
    let eq=Arc::new(crate::preflop::equity::EquityTable::load_or_build(&eq_path,samples));
    let s=PreflopSolver::load_game(&input,eq).unwrap();
    assert_eq!(s.multiway_equity_model(),"coupled_deck_v1");
    let age=s.iteration; let before=s.arena_snapshot();
    let mut g=PreflopGpu::new(&s,23000).unwrap();
    assert!(g.use_mw_normalized && g.use_mw_prepared && g.use_mw_compact!=0);
    assert!(g.d_mw_normalized.len()*4<=1024*1024*1024);
    let work=g.stream.clone_dtoh(&g.d_mw_work).unwrap();
    let slots=g.stream.clone_dtoh(&g.d_mw_slots).unwrap();
    let terms=g.stream.clone_dtoh(&g.d_mw_terms).unwrap();
    let sources=g.stream.clone_dtoh(&g.d_reach_src).unwrap();
    let live=g.stream.clone_dtoh(&g.d_live).unwrap();
    let mut rows=Vec::new();
    for mode in [0,1] {
        // No up/discount/iterate call is made: same immutable learning state.
        g.down(mode,0).unwrap();
        for p in 0..g.np {
            let (start,count)=g.mw_spans[p as usize];
            let slot_count=g.d_mw_active.len() as u32; let gate=1i32;
            unsafe {
                g.stream.launch_builder(&g.f_multiway_clear_active)
                    .arg(&mut g.d_mw_active).arg(&slot_count)
                    .launch(LaunchConfig{grid_dim:(slot_count.div_ceil(256),1,1),block_dim:(256,1,1),shared_mem_bytes:0}).unwrap();
                g.stream.launch_builder(&g.f_multiway_prepare)
                    .arg(&g.d_mw_terms).arg(&g.mw_nterms).arg(&p).arg(&g.np)
                    .arg(&g.d_live).arg(&g.d_reach_src).arg(&g.d_reach_mass)
                    .arg(&g.d_mw_slots).arg(&mut g.d_mw_active).arg(&mut g.d_mw_prob).arg(&gate)
                    .launch(LaunchConfig{grid_dim:(g.mw_nterms.div_ceil(256),1,1),block_dim:(256,1,1),shared_mem_bytes:0}).unwrap();
                if count>0 {
                    g.stream.launch_builder(&g.f_multiway_normalize)
                        .arg(&g.d_mw_work).arg(&start).arg(&g.d_mw_blocks)
                        .arg(&g.d_reach).arg(&g.d_reach_mass).arg(&g.d_mw_active).arg(&gate)
                        .arg(&g.use_mw_compact).arg(&mut g.d_mw_normalized)
                        .launch(LaunchConfig{grid_dim:(count,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).unwrap();
                }
            }
            let active=g.stream.clone_dtoh(&g.d_mw_active).unwrap();
            let prob=g.stream.clone_dtoh(&g.d_mw_prob).unwrap();
            let values=g.stream.clone_dtoh(&g.d_mw_normalized).unwrap();
            let mut groups=HashMap::new(); let mut unique=0u32; let mut active_count=0;
            let mut representatives=vec![u32::MAX;slots.len()];
            for k in 0..count as usize {
                let slot=work[start as usize+k] as usize;
                if active[slot]==0 {continue;}
                let v=&values[k*NUM_CLASSES..(k+1)*NUM_CLASSES];
                assert!(v.iter().all(|x|x.is_finite() && *x>=0.0));
                representatives[slot]=intern(v,bits_hash(v),&mut groups,&mut unique); active_count+=1;
            }
            let mut keys=HashSet::new(); let mut positive=0usize; let mut weighted=0usize;
            let mut unique_weighted=0usize;
            for (ti,&nd) in terms.iter().enumerate() {
                if prob[ti]<=0.0 {continue;}
                assert!((live[nd as usize]>>p)&1!=0);
                let mut key=Vec::new();
                for q in 0..g.np {
                    if q==p || (live[nd as usize]>>q)&1==0 {continue;}
                    let block=sources[nd as usize*s.n+q as usize] as usize;
                    let slot=slots[block] as usize; let id=representatives[slot];
                    assert_ne!(id,u32::MAX);key.push(id);
                }
                assert!(key.len()>=2); positive+=1;weighted+=key.len();
                let n=key.len(); if keys.insert(key) {unique_weighted+=n;}
            }
            let row=json!({"mode":mode,"player":p,"work_slots":count,"active_slots":active_count,
                "unique_distributions":unique,"positive_terminals":positive,"unique_equity_keys":keys.len(),
                "weighted_terminals":weighted,"unique_weighted_terminals":unique_weighted});
            println!("EXACT_REUSE {}",row); rows.push(row);
        }
    }
    let actual=g.stream.clone_dtoh(&g.d_regrets).unwrap();
    assert!(actual.iter().zip(&before.0).all(|(a,b)|a.to_bits()==b.to_bits()));
    assert_eq!(actual.len(),before.0.len());drop(actual);
    let actual=g.stream.clone_dtoh(&g.d_strat).unwrap();
    assert!(actual.iter().zip(&before.1).all(|(a,b)|a.to_bits()==b.to_bits()));
    assert_eq!(actual.len(),before.1.len());assert_eq!(s.iteration,age);
    let result=json!({"input":input,"nodes":s.nodes.len(),"players":s.n,"iteration":age,
        "cdf_bytes":g.d_mw_cdf.len()*4,"normalized_bytes":g.d_mw_normalized.len()*4,"batch":g.mw_batch,
        "arenas_unchanged":true,"read_only":true,"rows":rows,"scope":"Exact work inventory; no speed measurement"});
    std::fs::write(output,serde_json::to_vec_pretty(&result).unwrap()).unwrap();
}
