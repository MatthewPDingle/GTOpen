use super::{StoredContinuationGpu,StoredWorkspace};
use crate::{gpu::SymmetricContinuationGpu, store::Store, Solver, Spot, SpotConfig, TreeConfig, StreetSizing, Algorithm, parse_sizes};
use std::sync::Arc;
fn data(s: &Store) -> &[f32] {
    let Store::F32(a) = s else {
        panic!("F32 required")
    };
    a.as_slice()
}
fn data_mut(s: &mut Store) -> &mut [f32] {
    let Store::F32(a) = s else {
        panic!("F32 required")
    };
    a.as_mut_slice()
}
fn weights(sp: &Spot, p: usize, t: u32) -> Vec<f32> {
    sp.hands[p]
        .iter()
        .map(|h| {
            let c = crate::preflop::equity::class_index(h.c1 / 4, h.c2 / 4, h.c1 % 4 == h.c2 % 4);
            0.02 + ((c * 7 + t as usize * 3 + p * 11) % 23) as f32 / 23.
        })
        .collect()
}
fn pair(sp: &Spot, mode: &str, t: u32) -> [Vec<f32>; 2] {
    let source = t.min(100);
    let mut result = std::array::from_fn(|p| {
        if mode == "abrupt_pair" {
            weights(sp, p, source)
        } else {
            let (a, b) = (weights(sp, p, 31), weights(sp, p, 47));
            let x = (source - 1) as f32 / 99.;
            a.iter()
                .zip(&b)
                .map(|(a, b)| a * (1. - x) + b * x)
                .collect()
        }
    });
    if mode == "abrupt_pair" && t <= 100 && t % 17 == 0 {
        result[(t / 17) as usize % 2].fill(0.);
    }
    result
}

fn mismatch(a: &Solver, b: &Solver) -> (usize, f64) {
    let mut count = 0;
    let mut max = 0f64;
    for (a, b) in a
        .regrets
        .iter()
        .chain(&a.strat)
        .zip(b.regrets.iter().chain(&b.strat))
    {
        assert_eq!(data(a).len(), data(b).len());
        for (a, b) in data(a).iter().zip(data(b)) {
            assert!(a.is_finite() && b.is_finite());
            count += usize::from(a.to_bits() != b.to_bits());
            max = max.max((*a as f64 - *b as f64).abs());
        }
    }
    (count, max)
}


#[test]
fn direct_gpu_storage_preserves_720_full_state_passes() {
    let root=std::path::PathBuf::from(std::env::var("GTO_SSD_STUDY_DIR").unwrap());
    let mut workspace=StoredWorkspace::default();
    let mut ram=u64::MAX;
    let mut entries=vec![];
    for board in ["KsQs2d","KsQs2s","KsQh2d"] {
        for (pot,stack) in [(39.5,80.),(93.5,155.)] {
            let z=StreetSizing{bet:parse_sizes("50").unwrap(),raise:vec![],donk:parse_sizes("50").unwrap()};
            let sp=Arc::new(Spot::new(SpotConfig{board:board.into(),range_oop:"AA,KK,AQs,KQo,88,76s".into(),
                range_ip:"AA,QQ,AKo,QJs,99".into(),tree:TreeConfig{starting_pot:pot,effective_stack:stack,
                rake_pct:0.04,rake_cap:6.,max_raises:0,oop:[z.clone(),z.clone(),z.clone()],
                ip:[z.clone(),z.clone(),z],..Default::default()}}).unwrap());
            let mut host=Solver::new(sp.clone());host.algo=Algorithm::CfrPlus;host.use_isomorphism=false;
            let reference=SymmetricContinuationGpu::new_explicit_reference(&host,u64::MAX).unwrap();
            let candidate=StoredContinuationGpu::new(&host,&mut workspace,&root,entries.len() as u64,&mut ram).unwrap();
            entries.push((sp,reference,candidate));
        }
    }
    let mut passes=0;
    for t in 1..=60 {for p in 0..2 {
        let mut order:Vec<_>=(0..entries.len()).collect();
        if (t+p as u32)%2==0 {order.reverse();}
        order.rotate_left((t as usize+p)%entries.len());
        for index in order {
            let (sp,reference,candidate)=&mut entries[index];
            let reaches=pair(sp,"abrupt_pair",t);
            let expected=reference.sweep(p,t,&reaches[p],&reaches[1-p]).unwrap();
            let actual=candidate.sweep(&mut workspace,p,t,&reaches[p],&reaches[1-p]).unwrap();
            assert!(expected.iter().zip(&actual).all(|(a,b)|a.to_bits()==b.to_bits()));
            let mut expected_host=Solver::new(sp.clone());expected_host.algo=Algorithm::CfrPlus;expected_host.use_isomorphism=false;
            reference.sync_to_cpu(&mut expected_host).unwrap();
            let restored=candidate.materialize().unwrap();
            assert_eq!(mismatch(&expected_host,&restored).0,0,"restored state mismatch {index}/{t}/{p}");
            // Inspect full shared DEVICE arenas after gather, including unused holes.
            let mut actual_host=Solver::new(sp.clone());
            let buffers=workspace.buffers.as_ref().unwrap();
            let stream=&candidate.gpu.gpu.stream;
            for q in 0..2 {
                let r=data_mut(&mut actual_host.regrets[q]);let n=r.len();
                stream.memcpy_dtoh(&buffers[q].slice(0..n),r).unwrap();
                let a=data_mut(&mut actual_host.strat[q]);let n=a.len();
                stream.memcpy_dtoh(&buffers[q+2].slice(0..n),a).unwrap();
            }
            stream.synchronize().unwrap();
            assert_eq!(mismatch(&expected_host,&actual_host).0,0,"device state mismatch {index}/{t}/{p}");
            passes+=1;
            println!("GPU_STORED_PASS {}",serde_json::json!({"entry":index,"iteration":t,"player":p,"passed":true}));
        }
    }}
    assert_eq!(passes,720);
    println!("GPU_STORED_SUMMARY {}",serde_json::json!({"passes":passes,"full_device_arrays_bitwise_equal":true,
        "restored_arrays_bitwise_equal":true,"values_bitwise_equal":true,"workspace_bytes":workspace.bytes()}));
}
