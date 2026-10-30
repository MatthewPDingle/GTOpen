
// Identical test-only attachment for the pinned original and E038 arena.rs.
#[cfg(test)]
mod e038_upload_control {
    use super::*;
    use super::super::GpuSolver;
    use crate::game::{Spot, SpotConfig};
    use crate::store::Storage;
    use crate::tree::{parse_sizes, StreetSizing, TreeConfig};
    use serde_json::{json, Value};
    use std::io::{BufWriter, Write};
    use std::path::{Path, PathBuf};

    type ControlResult<T> = Result<T, String>;

    struct DrainOnDrop(GpuSolver);
    impl std::ops::Deref for DrainOnDrop {
        type Target = GpuSolver;
        fn deref(&self) -> &GpuSolver { &self.0 }
    }
    impl std::ops::DerefMut for DrainOnDrop {
        fn deref_mut(&mut self) -> &mut GpuSolver { &mut self.0 }
    }
    impl Drop for DrainOnDrop {
        fn drop(&mut self) {
            if let Err(error) = self.0.synchronize() {
                let _ = writeln!(std::io::stderr().lock(), "E038_CONTROL_CLEANUP_ERROR {error}");
            }
        }
    }

    fn u32_word(out: &mut Vec<u8>, value: u32) { out.extend(value.to_le_bytes()); }
    fn u64_word(out: &mut Vec<u8>, value: u64) { out.extend(value.to_le_bytes()); }

    // Complete raw compressed storage, including all non-action scale words.
    fn host_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E038HOST1".to_vec();
        u64_word(&mut out, s.iteration as u64);
        out.push(u8::from(s.use_isomorphism));
        for store in [&s.regrets[0], &s.regrets[1], &s.strat[0], &s.strat[1]] {
            match store {
                Store::I16 { q, scale } => {
                    u32_word(&mut out, 1);
                    u64_word(&mut out, q.len() as u64);
                    for value in q.as_slice() { out.extend(value.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for value in scale.as_slice() { u32_word(&mut out, value.to_bits()); }
                }
                Store::U16 { q, scale } => {
                    u32_word(&mut out, 2);
                    u64_word(&mut out, q.len() as u64);
                    for value in q.as_slice() { out.extend(value.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for value in scale.as_slice() { u32_word(&mut out, value.to_bits()); }
                }
                Store::F32(_) => panic!("control requires compressed stores"),
            }
        }
        out
    }

    fn query_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E038QUERY1".to_vec();
        let mut nonuniform = false;
        for (id, node) in s.spot.tree.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            let p = node.player as usize;
            let nh = s.spot.hands[p].len();
            let na = node.num_children as usize;
            let mut sigma = vec![f32::NAN; nh * na];
            s.solved_strategy_into(node, &mut sigma);
            u32_word(&mut out, id as u32);
            u32_word(&mut out, p as u32);
            u32_word(&mut out, nh as u32);
            u32_word(&mut out, na as u32);
            if na > 1 {
                nonuniform |= (0..nh).any(|i| sigma[i].to_bits() != sigma[nh + i].to_bits());
            }
            for value in sigma { u32_word(&mut out, value.to_bits()); }
        }
        assert!(nonuniform, "raw nonzero U16 quants must affect an actual CPU query");
        out
    }

    fn device_image(gpu: &GpuSolver) -> ControlResult<Vec<u8>> {
        gpu.synchronize()?;
        let mut out = b"E038GPU1".to_vec();
        for (index, data) in [&gpu.d_regrets[0], &gpu.d_regrets[1], &gpu.d_strat[0], &gpu.d_strat[1]].into_iter().enumerate() {
            let host = gpu.stream.clone_dtoh(data).map_err(e)?;
            if index >= 2 { assert!(host.iter().all(|value| value.to_bits() == 0)); }
            u64_word(&mut out, host.len() as u64);
            for value in host { u32_word(&mut out, value.to_bits()); }
        }
        Ok(out)
    }

    fn save_image(s: &Solver, path: &Path) -> ControlResult<Vec<u8>> {
        let name = path.to_str().ok_or("non-UTF8 output path")?;
        assert!(!path.exists() && !PathBuf::from(format!("{name}.tmp")).exists());
        s.save(name)?;
        std::fs::read(path).map_err(e)
    }

    fn retain(dir: &Path, name: &str, bytes: &[u8], files: &mut Vec<Value>) -> ControlResult<()> {
        let file = std::fs::OpenOptions::new().write(true).create_new(true)
            .open(dir.join(name)).map_err(e)?;
        let mut out = BufWriter::new(file);
        out.write_all(bytes).map_err(e)?;
        out.flush().map_err(e)?;
        out.get_ref().sync_all().map_err(e)?;
        files.push(json!({"file":name,"bytes":bytes.len()}));
        Ok(())
    }

    fn run_layout(dir: &Path, iso: bool, expected_fast_path: bool) -> ControlResult<Value> {
        let sizing = || StreetSizing { bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![] };
        let spot = Arc::new(Spot::new_with_limit(SpotConfig {
            board: "KsQs2dJd".into(),
            range_oop: "AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
            range_ip: "AA,QQ,TT,77,AQs,KQs,AQo".into(),
            tree: TreeConfig { starting_pot:10.0, effective_stack:20.0,
                oop:[sizing(),sizing(),sizing()], ip:[sizing(),sizing(),sizing()],
                ..Default::default() },
        }, Some(20_000))?);
        // Keep this proof small; do not silently substitute another fixture.
        assert!(spot.tree.data_size.iter().sum::<u64>() <= 250_000);
        let mut s = Solver::with_storage(spot.clone(), Storage::Compressed);
        s.use_isomorphism = iso;
        let plan = GpuPlan::build(&spot, iso);
        for p in 0..2 {
            if let Store::U16 { q, scale } = &mut s.strat[p] {
                for (i, word) in q.as_mut_slice().iter_mut().enumerate() {
                    *word = ((i as u64 * 73 + p as u64 * 997) % 65535 + 1) as u16;
                }
                assert!(scale.as_slice().iter().all(|value| value.to_bits() == 0));
            }
        }
        // Distinct finite regret blocks make materialization/restoration observable.
        // These are seeded host inputs, not a synthetic solver iteration.
        for (id, node) in spot.tree.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            let p = node.player as usize;
            if let Store::I16 { q, scale } = &mut s.regrets[p] {
                let value = (id + 1) as i16 * if id % 2 == 0 { 1 } else { -1 };
                let start = node.data_offset as usize;
                let len = node.num_children as usize * spot.hands[p].len();
                q.as_mut_slice()[start..start + len].fill(value);
                scale.as_mut_slice()[id] = 1.0;
            }
        }
        let layouts = [ArenaLayout::new(&s, &plan, 0), ArenaLayout::new(&s, &plan, 1)];
        for p in 0..2 {
            assert_eq!(layouts[p].compact, iso);
            assert_eq!(layouts[p].can_upload_zeros(&s.strat[p], 1), expected_fast_path);
            if iso {
                assert!(!layouts[p].inactive.is_empty());
                assert!(plan.arena_elements[p] < spot.tree.data_size[p] as usize);
            } else {
                assert!(layouts[p].inactive.is_empty());
                assert_eq!(plan.arena_elements[p], spot.tree.data_size[p] as usize);
            }
        }
        let mut files = Vec::new();
        let initial = host_image(&s);
        let query_before = query_image(&s);
        retain(dir, "pre_upload.host.bin", &initial, &mut files)?;
        retain(dir, "pre_upload.query.bin", &query_before, &mut files)?;
        let save_before = save_image(&s, &dir.join("pre_upload.save"))?;
        files.push(json!({"file":"pre_upload.save","bytes":save_before.len()}));
        assert_eq!(host_image(&s), initial, "query/save must not rewrite seeded host input");

        let budget = plan.staging_bytes()
            + (plan.arena_elements[0] + plan.arena_elements[1]) as u64 * 8
            + 512 * 1024 * 1024;
        let mut gpu = DrainOnDrop(GpuSolver::new_with_budget(&s, budget)?);
        let owner = gpu._ctx.clone();
        for p in 0..2 {
            assert_eq!(gpu.arena_layout[p].compact, iso);
            assert_eq!(gpu.d_strat[p].len(), plan.arena_elements[p]);
            assert_eq!(gpu.d_regrets[p].len(), plan.arena_elements[p]);
            assert_eq!(gpu.arena_layout[p].inactive.len(), layouts[p].inactive.len());
            assert!(gpu.arena_layout[p].initial[1].is_empty());
            assert!(gpu.arena_layout[p].inactive.iter().all(|block| block.initial[1] == usize::MAX));
            if iso { assert!(!gpu.arena_layout[p].initial[0].is_empty()); }
        }
        assert_eq!(host_image(&s), initial, "constructor/upload changed raw host stores");
        let query_after = query_image(&s);
        let save_after = save_image(&s, &dir.join("post_upload.save"))?;
        assert_eq!(query_after, query_before);
        assert_eq!(save_after, save_before);
        assert_eq!(host_image(&s), initial, "post-upload query/save changed raw stores");
        files.push(json!({"file":"post_upload.save","bytes":save_after.len()}));
        retain(dir, "post_upload.query.bin", &query_after, &mut files)?;
        retain(dir, "post_upload.host.bin", &host_image(&s), &mut files)?;
        let gpu_initial = device_image(&gpu)?;
        retain(dir, "post_upload.gpu.bin", &gpu_initial, &mut files)?;

        gpu.sync_to_cpu(&mut s)?;
        let first_readback = host_image(&s);
        retain(dir, "first_readback.host.bin", &first_readback, &mut files)?;
        let device = device_image(&gpu)?;
        assert_eq!(device, gpu_initial);
        retain(dir, "first_readback.gpu.bin", &device, &mut files)?;
        s.ensure_symmetric();
        let materialized = host_image(&s);
        if iso { assert_ne!(materialized, first_readback, "inactive materialization witness"); }
        retain(dir, "materialized.host.bin", &materialized, &mut files)?;
        let device = device_image(&gpu)?;
        assert_eq!(device, gpu_initial);
        retain(dir, "materialized.gpu.bin", &device, &mut files)?;
        gpu.sync_to_cpu(&mut s)?;
        let repeated = host_image(&s);
        assert_eq!(repeated, first_readback, "readback must restore inactive initial state");
        retain(dir, "repeat_readback.host.bin", &repeated, &mut files)?;
        let device = device_image(&gpu)?;
        assert_eq!(device, gpu_initial);
        retain(dir, "repeat_readback.gpu.bin", &device, &mut files)?;

        gpu.synchronize()?;
        drop(gpu);
        owner.check_err().map_err(e)?;
        let bytes: u64 = files.iter().map(|f| f["bytes"].as_u64().unwrap()).sum();
        assert!(bytes <= 32 * 1024 * 1024, "per-layout output bound");
        Ok(json!({"layout":if iso {"compact"} else {"full"},
            "nodes":spot.tree.nodes.len(),"nh":plan.nh,"host_elements":spot.tree.data_size,
            "device_elements":plan.arena_elements,
            "inactive_blocks":[layouts[0].inactive.len(),layouts[1].inactive.len()],
            "u16_zero_fast_path":expected_fast_path,"host_query_save_preserved":true,
            "device_unchanged_after_readbacks":true,"repeat_restores_first_readback":true,
            "materialization_changed_host":materialized != first_readback,
            "cleanup_complete":true,"files":files,"output_bytes":bytes}))
    }

    #[test]
    #[ignore = "root-only original/candidate upload control; requires CUDA and fresh output directory"]
    fn exact_u16_zero_upload_lifecycle() -> ControlResult<()> {
        let dir = PathBuf::from(std::env::var_os("E038_CONTROL_DIR").ok_or("E038_CONTROL_DIR missing")?);
        let expected_fast_path = match std::env::var("E038_CONTROL_EXPECT_FAST_PATH").as_deref() {
            Ok("0") => false, Ok("1") => true, _ => return Err("expected fast path must be0 or1".into()),
        };
        std::fs::create_dir(&dir).map_err(e)?;
        let mut cases = Vec::new();
        for (label, iso) in [("full", false), ("compact", true)] {
            let path = dir.join(label);
            std::fs::create_dir(&path).map_err(e)?;
            let result = run_layout(&path, iso, expected_fast_path)?;
            println!("E038_UPLOAD_CONTROL {}", json!({"stage":"layout_complete","result":result}));
            cases.push(result);
        }
        let summary = json!({"id":"E038-control","stage":"complete","layouts":cases,
            "solve_iterations":0,"performance_measurement":false,"candidate_accepted":false});
        retain(&dir, "evidence.json", &serde_json::to_vec_pretty(&summary).map_err(e)?, &mut Vec::new())?;
        println!("E038_UPLOAD_CONTROL {summary}");
        Ok(())
    }
}
