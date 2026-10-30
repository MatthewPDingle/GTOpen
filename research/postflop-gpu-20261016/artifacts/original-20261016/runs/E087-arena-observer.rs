pub(super) fn e087_manual(
    solver: &mut Solver, stream: &Arc<CudaStream>,
    p: usize, force_full: bool, prechecked: bool, out: &std::path::Path, id: &str,
) -> serde_json::Value {
    let mut plan = GpuPlan::build(&solver.spot, solver.use_isomorphism);
    if force_full { super::plan::full_arena_adapter(&mut plan, &solver.spot); }
    let mut layout = ArenaLayout::new(solver, &plan, p);
    // CONTROL_CAPACITY
    let mut staging = super::PinnedBuf::new(stream.context(), capacity).unwrap();
    let mut rows=Vec::new();
    for which in 0..2 {
        let base=out.join(format!("{id}-w{which}"));
        crate::state_frame(solver,&base.with_extension("input.bin"));
        let store=if which==0{&solver.regrets[p]}else{&solver.strat[p]};
        let check=prechecked.then(||ZeroCheck::new(store));
        let expected=crate::expected_arena(solver,&plan,p,which);
        let device=layout.upload_prechecked(stream,solver,p,which,staging.as_mut_slice(),check.as_ref()).unwrap();
        stream.synchronize().unwrap();
        drop(check);
        crate::state_frame(solver,&base.with_extension("post-upload.bin"));
        crate::same_files(&base.with_extension("input.bin"),&base.with_extension("post-upload.bin"));
        crate::device_frame(stream,&device,&expected,&base.with_extension("device-before.bin"));
        crate::fill_store(solver,p,which,1);
        // CONTROL_DOWNLOAD_FIRST
        crate::state_frame(solver,&base.with_extension("download.bin"));
        crate::fill_store(solver,p,which,2);
        // CONTROL_DOWNLOAD_REPEAT
        crate::state_frame(solver,&base.with_extension("repeat.bin"));
        crate::same_files(&base.with_extension("download.bin"),&base.with_extension("repeat.bin"));
        crate::device_frame(stream,&device,&expected,&base.with_extension("device-after.bin"));
        crate::same_files(&base.with_extension("device-before.bin"),&base.with_extension("device-after.bin"));
        let expected_again=crate::expected_arena(solver,&plan,p,which);
        let second=layout.upload(stream,solver,p,which,staging.as_mut_slice()).unwrap();
        stream.synchronize().unwrap();
        crate::device_frame(stream,&second,&expected_again,&base.with_extension("reupload-device.bin"));
        crate::fill_store(solver,p,which,3);
        // CONTROL_DOWNLOAD_SECOND
        crate::state_frame(solver,&base.with_extension("reupload-download.bin"));
        rows.push(serde_json::json!({
            "which":which,"device_words":device.len(),"whole_GPU_before_after_exact":true,
            "whole_CPU_source_upload_unchanged":true,"repeat_CPU_output_exact":true,
            "warm_reupload_device_exact":true
        }));
    }
    let mut info=serde_json::json!({
        "id":id,"p":p,"force_full":force_full,"compact":layout.compact,
        "prechecked":prechecked,"capacity_words":capacity,"device_words":layout.len,
        "active_nodes":layout.active.len(),"copy_spans":layout.copies.len(),
        "inactive_nodes":layout.inactive.len(),"phases":rows,
        "GPU_compute_kernel_launches":0,"performance_measurement":false
    });
    // CONTROL_CLEANUP
    info["full_metadata_cleanup_exact"]=serde_json::json!(layout.compact||layout.active.capacity()==0);
    info
}

// CANDIDATE_DRAIN_OBSERVER
