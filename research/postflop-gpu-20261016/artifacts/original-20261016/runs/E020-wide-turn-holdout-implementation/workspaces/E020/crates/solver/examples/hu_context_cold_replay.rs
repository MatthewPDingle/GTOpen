//! Research control: evict every candidate GPU object after each player sweep.
//! Uses existing immutable checkpoints; does not change storage or solver code.
use serde_json::json;
use solver::{Algorithm, Solver, Spot, SpotConfig, StreetSizing, TreeConfig, parse_sizes};
use solver::gpu::{StoredContinuationGpu, StoredWorkspace};
use solver::store::Store;
use std::{path::PathBuf, sync::Arc, time::Instant};

fn values(s: &Store) -> &[f32] {
    let Store::F32(v) = s else { panic!("F32 control required") };
    v.as_slice()
}

fn equal(a: &Solver, b: &Solver) {
    assert_eq!(a.iteration, b.iteration);
    for (a, b) in a.regrets.iter().chain(&a.strat).zip(b.regrets.iter().chain(&b.strat)) {
        let a = values(a); let b = values(b);
        assert_eq!(a.len(), b.len());
        assert!(a.iter().zip(b).all(|(x,y)| x.to_bits() == y.to_bits()), "state changed across eviction");
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let root = PathBuf::from(std::env::var("GTO_SSD_STUDY_DIR")?);
    assert!(root.is_dir() && std::fs::read_dir(&root)?.next().is_none(), "dedicated empty directory required");
    let began = Instant::now();
    let mut passes = 0;
    let mut bytes_written = 0u64;
    let mut reconstruction_seconds = 0.;
    let mut serialization_seconds = 0.;
    let mut max_workspace = 0;
    // Compact controls cover all flop suit textures and the BB candidate's pots.
    // They qualify exact state recovery, not wide-range strategic performance.
    for (case, (board, pot, stack)) in [
        ("AsKd7c", 4.5, 198.), ("KsQd9d", 12.5, 194.), ("9h8h7h", 36.5, 182.)
    ].into_iter().enumerate() {
        let sizing = StreetSizing { bet:parse_sizes("50")?, raise:vec![], donk:parse_sizes("50")? };
        let spot = Arc::new(Spot::new(SpotConfig {
            board:board.into(), range_oop:"AA,KK,AQs,KQo,88,76s".into(),
            range_ip:"AA,QQ,AKo,QJs,99".into(),
            tree:TreeConfig { starting_pot:pot, effective_stack:stack, rake_pct:0.05, rake_cap:2.,
                max_raises:0, oop:[sizing.clone(),sizing.clone(),sizing.clone()],
                ip:[sizing.clone(),sizing.clone(),sizing], ..Default::default() },
        })?);
        let mut host = Solver::new(spot.clone()); host.algo=Algorithm::CfrPlus; host.use_isomorphism=false;
        let mut reference_workspace = StoredWorkspace::default(); let mut unlimited = u64::MAX;
        let mut reference = StoredContinuationGpu::new(&host, &mut reference_workspace, &root, 999, &mut unlimited)?;
        let mut previous: Option<(PathBuf, u32, [u64;8])> = None;
        for t in 1..=8 { for p in 0..2 {
            let reaches: [Vec<f32>;2] = std::array::from_fn(|q|
                spot.hands[q].iter().map(|h| {
                    let c=solver::preflop::equity::class_index(h.c1/4,h.c2/4,h.c1%4==h.c2%4);
                    if t==3 && q==0 {0.} else {0.02+((c*7+t as usize*3+q*11)%23) as f32/23.}
                }).collect());
            let expected = reference.sweep(&mut reference_workspace, p, t, &reaches[p], &reaches[1-p])?;
            let started = Instant::now();
            let mut workspace = StoredWorkspace::default();
            let mut candidate = StoredContinuationGpu::new(&host, &mut workspace, &root, 0, &mut unlimited)?;
            if let Some((path, iteration, descriptor)) = &previous {
                candidate.checkpoint_import(path, 0, *iteration, *descriptor)?;
            }
            reconstruction_seconds += started.elapsed().as_secs_f64();
            let actual = candidate.sweep(&mut workspace, p, t, &reaches[p], &reaches[1-p])?;
            assert_eq!(expected.len(), actual.len());
            assert!(expected.iter().zip(&actual).all(|(x,y)|x.to_bits()==y.to_bits()), "CFV changed across eviction");
            equal(&reference.materialize()?, &candidate.materialize()?);
            let snapshot = root.join(format!("case-{case}-iteration-{t}-player-{p}"));
            assert!(bytes_written + candidate.storage_bytes + 72 < 16*1024*1024*1024, "control write budget");
            std::fs::create_dir(&snapshot)?;
            let started = Instant::now();
            let descriptor = candidate.checkpoint_export(&snapshot, 0, t)?;
            serialization_seconds += started.elapsed().as_secs_f64();
            bytes_written += candidate.storage_bytes+72;
            max_workspace = max_workspace.max(workspace.bytes());
            previous = Some((snapshot, t, descriptor));
            drop(candidate); drop(workspace);
            passes += 1;
            println!("COLD_PASS {}",json!({"case":case,"iteration":t,"player":p,"passed":true}));
        }}
    }
    assert_eq!(passes, 48);
    let result = json!({"passes":passes,"all_values_bitwise_equal":true,"all_state_arrays_bitwise_equal":true,
        "candidate_gpu_dropped_after_every_pass":true,"includes_zero_reach_and_reentry":true,
        "reconstruction_seconds":reconstruction_seconds,"serialization_seconds":serialization_seconds,
        "elapsed_seconds":began.elapsed().as_secs_f64(),"max_candidate_workspace_bytes":max_workspace,
        "bytes_written":bytes_written,"wide_range_fit_proven":false,
        "note":"Compact control; reference remains resident. Candidate recreated from fresh zeros and exact checkpoint before every subsequent sweep. No full-forest admission or throughput claim."});
    std::fs::write(root.join("result.json"),serde_json::to_vec_pretty(&result)?)?;
    println!("COLD_SUMMARY {result}");
    Ok(())
}
