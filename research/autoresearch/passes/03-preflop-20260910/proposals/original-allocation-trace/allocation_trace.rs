// Diagnostic only. No planning, array contents, model or arithmetic changes.
struct AllocationTrace {
    mode: u8, // 0 disabled, 1 totals, 2 snapshot after every allocation
    label: &'static str,
    baseline_used: Option<usize>,
    previous_used: Option<usize>,
    requested: usize,
    records: Vec<(&'static str, usize, usize)>,
}
impl AllocationTrace {
    fn new(label: &'static str) -> Result<Self, String> {
        let mode = match std::env::var("PREFLOP_GPU_ALLOCATION_TRACE") {
            Err(std::env::VarError::NotPresent) => 0,
            Ok(v) if v == "totals" => 1,
            Ok(v) if v == "each" => 2,
            value => return Err(format!("PREFLOP_GPU_ALLOCATION_TRACE must be absent, totals, or each: {value:?}")),
        };
        Ok(Self {mode,label,baseline_used:None,previous_used:None,requested:0,records:Vec::new()})
    }
    fn snapshot(&mut self, ctx: &Arc<CudaContext>, stage: &str) -> Result<(), String> {
        if self.mode == 0 { return Ok(()); }
        ctx.synchronize().map_err(e)?;
        let (free,total) = ctx.mem_get_info().map_err(e)?;
        let used = total.saturating_sub(free);
        let initial = *self.baseline_used.get_or_insert(used);
        let delta = used as i64 - initial as i64;
        println!("PREFLOP_ALLOCATION_TRACE {}", serde_json::json!({
            "phase":"memory","baseline":self.label,"mode":if self.mode==1 {"totals"} else {"each"},
            "stage":stage,"free_bytes":free,"total_bytes":total,"used_bytes":used,
            "delta_since_context_bytes":delta,
            "delta_previous_bytes":self.previous_used.map(|v|used as i64-v as i64),
            "requested_so_far_bytes":self.requested,
            "delta_minus_requested_bytes":delta-self.requested as i64,
            "scope":"device-global free/total; differences are not an attribution to allocator, residency or paging"
        }));
        self.previous_used=Some(used);
        Ok(())
    }
    fn buffer<T>(&mut self, ctx: &Arc<CudaContext>, name: &'static str, buffer: CudaSlice<T>) -> Result<CudaSlice<T>,String> {
        if self.mode == 0 { return Ok(buffer); }
        let bytes=buffer.num_bytes();
        self.requested=self.requested.checked_add(bytes).ok_or("diagnostic byte sum overflow")?;
        self.records.push((name,buffer.len(),bytes));
        if self.mode==2 { self.snapshot(ctx,name)?; }
        Ok(buffer)
    }
    fn finish(&mut self, ctx: &Arc<CudaContext>, need_mb: f64, actual: &[(&'static str,usize,usize)]) -> Result<(),String> {
        if self.mode == 0 { return Ok(()); }
        let final_requested=actual.iter().try_fold(0usize,|sum,(_,_,bytes)|sum.checked_add(*bytes))
            .ok_or("diagnostic final byte sum overflow")?;
        if final_requested!=self.requested || actual!=self.records.as_slice() {
            return Err("diagnostic allocation trace does not match final CudaSlice fields".into());
        }
        self.snapshot(ctx,"after_all_constructor_buffers")?;
        println!("PREFLOP_ALLOCATION_TRACE {}",serde_json::json!({
            "phase":"ledger","baseline":self.label,"allocation_count":actual.len(),
            "requested_bytes":final_requested,"planned_need_mb":need_mb,
            "requested_minus_planned_bytes":final_requested as f64-need_mb*1e6,
            "forced_requested_bytes":actual.iter().find(|(name,_,_)|*name=="d_forced").map(|(_,_,bytes)|*bytes),
            "fields":actual.iter().map(|(name,len,bytes)|serde_json::json!({"name":name,"elements":len,"bytes":bytes})).collect::<Vec<_>>(),
            "note":"CudaSlice.num_bytes counts requested payload only. Driver granularity/reservation and module/context resources are separate. Each-mode synchronizes between allocations and may perturb allocator behavior."
        }));
        Ok(())
    }
}
