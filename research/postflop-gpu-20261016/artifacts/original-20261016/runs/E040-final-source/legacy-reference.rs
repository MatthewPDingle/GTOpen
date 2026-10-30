    fn legacy_sync(gpu: &mut GpuSolver, solver: &mut Solver) -> Result<(), String> {
        gpu.stream.synchronize().map_err(e)?;
        for p in 0..2 {
            let len = gpu.d_regrets[p].len();
            gpu.stream
                .memcpy_dtoh(&gpu.d_regrets[p], &mut gpu.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            gpu.stream.synchronize().map_err(e)?;
            gpu.arena_layout[p].write(solver, p, 0, &gpu.h_staging.as_slice()[..len]);
            gpu.stream
                .memcpy_dtoh(&gpu.d_strat[p], &mut gpu.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            gpu.stream.synchronize().map_err(e)?;
            gpu.arena_layout[p].write(solver, p, 1, &gpu.h_staging.as_slice()[..len]);
        }
        solver.iteration = gpu.iteration;
        if gpu.iso_active {
            // only representative branches hold fresh data; queries/saves
            // re-materialize siblings via Solver::ensure_symmetric
            solver.mark_sym_dirty();
        }
        Ok(())
    }
