// Source-only proposal: append inside preflop/gpu.rs's existing tests module.
// Copy reference-writers.cu alongside kernels.cu for this test only. Those two
// names are frozen baseline writers, compiled in the same module as candidate.
#[test]
fn inclusive_cdf_preserves_all_logical_prefix_bits() {
    let ctx = CudaContext::new(0).unwrap();
    let stream = ctx.default_stream();
    let source = format!("{}\n{}", include_str!("kernels.cu"), include_str!("reference-writers.cu"));
    let (major, minor) = ctx.compute_capability().unwrap();
    let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let ptx = cudarc::nvrtc::compile_ptx_with_opts(source, cudarc::nvrtc::CompileOptions {
        // Match production options exactly; do not introduce fast math.
        arch: Some(arch), ..Default::default()
    }).unwrap();
    let module = ctx.load_module(ptx).unwrap();
    let work = [3u32, 1, 2, 0];
    let blocks = [2u32, 0, 3, 1];
    let mass = [1.3f32, 0.7, 0.0, 2.1];
    let active = [1u32, 1, 0, 1];
    let reach: Vec<f32> = (0..4*NUM_CLASSES).map(|i| ((i*19 % 97)+1) as f32 / 197.0).collect();
    let order: Vec<u32> = (0..40).flat_map(|p| (0..NUM_CLASSES).map(move |i| ((i+p*11)%NUM_CLASSES) as u32)).collect();
    let d_work = stream.clone_htod(&work).unwrap();
    let d_blocks = stream.clone_htod(&blocks).unwrap();
    let d_mass = stream.clone_htod(&mass).unwrap();
    let d_active = stream.clone_htod(&active).unwrap();
    let d_order = stream.clone_htod(&order).unwrap();
    for direct in [false, true] {
        let name = if direct { "pf_multiway_cdf_direct" } else { "pf_multiway_cdf" };
        let old = module.load_function(&format!("{name}_reference")).unwrap();
        let new = module.load_function(name).unwrap();
        for compact in [0i32, 1] {
            let mut input = reach.clone();
            if !direct {
                for (wi, &slot) in work.iter().enumerate() {
                    let block = blocks[slot as usize] as usize;
                    let dst = if compact == 1 { wi } else { slot as usize };
                    for h in 0..NUM_CLASSES {
                        input[dst*NUM_CLASSES+h] = reach[block*NUM_CLASSES+h]/mass[block];
                    }
                }
            }
            let d_input = stream.clone_htod(&input).unwrap();
            for gate in [0i32, 1] {
                for batch in [1u32, 7, 23, 31, 32] {
                    let start = 0u32;
                    let sample_start = 3u32;
                    // One extra unwritten particle row verifies capacity padding.
                    let capacity = batch+1;
                    let poison = vec![f32::NAN; 4*capacity as usize*(NUM_CLASSES+1)];
                    let mut before = stream.clone_htod(&poison).unwrap();
                    let mut after = stream.clone_htod(&poison).unwrap();
                    for (function, output) in [(&old, &mut before), (&new, &mut after)] {
                        unsafe { stream.launch_builder(function)
                            .arg(&d_work).arg(&start).arg(&d_blocks).arg(&d_order)
                            .arg(&d_input).arg(&d_mass).arg(&d_active).arg(&gate).arg(&compact)
                            .arg(output).arg(&sample_start).arg(&batch).arg(&capacity)
                            .launch(LaunchConfig { grid_dim: (4,batch.div_ceil(4),1), block_dim: (128,1,1), shared_mem_bytes: 0 }).unwrap(); }
                    }
                    let before = stream.clone_dtoh(&before).unwrap();
                    let after = stream.clone_dtoh(&after).unwrap();
                    for (wi, &slot) in work.iter().enumerate() {
                        let output_slot = if compact == 1 { wi } else { slot as usize };
                        for local in 0..capacity as usize {
                            let base = (output_slot*capacity as usize+local)*(NUM_CLASSES+1);
                            let written = local < batch as usize && mass[blocks[slot as usize] as usize] > 0.0
                                && (gate == 0 || active[slot as usize] != 0);
                            if written {
                                assert_eq!(before[base].to_bits(), 0f32.to_bits());
                                for k in 1..=NUM_CLASSES {
                                    assert_eq!(before[base+k].to_bits(), after[base+k-1].to_bits(),
                                        "direct={direct} compact={compact} gate={gate} batch={batch} slot={slot} local={local} k={k}");
                                }
                                assert!(after[base+NUM_CLASSES].is_nan(), "unused row padding was written");
                            } else {
                                assert!(before[base..base+NUM_CLASSES+1].iter().all(|v| v.is_nan()));
                                assert!(after[base..base+NUM_CLASSES+1].iter().all(|v| v.is_nan()));
                            }
                        }
                    }
                }
            }
        }
    }
}
