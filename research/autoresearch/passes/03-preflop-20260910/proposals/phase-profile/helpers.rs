// Diagnostic-only eager phase timing. This field, code and every call site are
// compiled out of production binaries (including the frozen example harness).
#[cfg(test)]
struct PhaseEventTrace {
    events: Vec<cudarc::driver::CudaEvent>,
    marks: Vec<(&'static str, i32)>,
}

#[cfg(test)]
impl PreflopGpu {
    fn phase_mark(&mut self, phase: &'static str, seat: i32) -> Result<(), String> {
        if let Some(trace) = &mut self.phase_trace {
            let event = trace.events.get(trace.marks.len())
                .ok_or_else(|| "phase event pool exhausted".to_string())?;
            event.record(&self.stream).map_err(e)?;
            trace.marks.push((phase, seat));
        }
        Ok(())
    }

    fn phase_profile_begin(&mut self) -> Result<(), String> {
        self.stream.synchronize().map_err(e)?;
        assert!(self.phase_trace.is_none(), "nested phase profiling");
        // Host hooks are bypassed by graphs. Eager launch the same operations
        // with lazy kernels already warm; never change numerical state here.
        for graph in &mut self.learning_graphs { *graph = None; }
        self.eval_graph = None;
        self.warmed = false;
        self.eval_warmed = false;
        let batches = super::multiway::SAMPLES.div_ceil(self.mw_batch.max(1) as usize);
        let capacity = self.np as usize * (2 * batches + 16) + 8;
        let mut events = Vec::with_capacity(capacity);
        for _ in 0..capacity {
            events.push(self._ctx.new_event(Some(sys::CUevent_flags::CU_EVENT_DEFAULT)).map_err(e)?);
        }
        self.phase_trace = Some(PhaseEventTrace { events, marks: Vec::with_capacity(capacity) });
        Ok(())
    }

    fn phase_profile_end(&mut self) -> Result<serde_json::Value, String> {
        self.stream.synchronize().map_err(e)?;
        let trace = self.phase_trace.take().ok_or_else(|| "phase profiling not active".to_string())?;
        assert!(trace.marks.len() >= 2);
        assert_eq!(trace.marks.last().unwrap().0, "end");
        let mut phases = std::collections::BTreeMap::<(&str, i32), (f64, usize)>::new();
        for (i, &(phase, seat)) in trace.marks[..trace.marks.len()-1].iter().enumerate() {
            assert_ne!(phase, "end", "one operation per phase trace");
            let ms = trace.events[i].elapsed_ms(&trace.events[i+1]).map_err(e)? as f64;
            assert!(ms.is_finite() && ms >= 0.0);
            let row = phases.entry((phase, seat)).or_default();
            row.0 += ms; row.1 += 1;
        }
        let total = trace.events[0].elapsed_ms(&trace.events[trace.marks.len()-1]).map_err(e)?;
        let rows: Vec<_> = phases.iter().map(|((phase,seat),(ms,count))|
            serde_json::json!({"phase":phase,"seat":seat,"ms":ms,"intervals":count})).collect();
        Ok(serde_json::json!({"execution":"eager_cuda_events","gpu_ms":total,
            "interval_sum_ms":phases.values().map(|x|x.0).sum::<f64>(),"rows":rows}))
    }
}
