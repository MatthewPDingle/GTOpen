impl GpuSolver {
    pub fn d157_resources(&self,stage:&str) -> serde_json::Value {
        self.stream.synchronize().unwrap();
        let (free,total)=self._ctx.mem_get_info().unwrap();
        let stack=self._ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
        let heap=self._ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_MALLOC_HEAP_SIZE).unwrap();
        serde_json::json!({"kind":"GPU_snapshot","stage":stage,"iteration":self.iteration,
            "explicit_device_payload_bytes":D157_DEVICE_BYTES,"pinned_bytes":self.h_staging.len*4,
            "wrapper_bytes":std::mem::size_of::<Self>(),"packet_module_loaded":D157_MODULE_LOADED,
            "graphs_present":self.graphs.is_some(),"eval_graphs_present":[self.eval_graphs[0].is_some(),self.eval_graphs[1].is_some()],
            "current_CFV_words":self.d_cfv.len(),"current_regret_words":[self.d_regrets[0].len(),self.d_regrets[1].len()],
            "current_strategy_words":[self.d_strat[0].len(),self.d_strat[1].len()],"context_stack_limit":stack,"context_heap_limit":heap,
            "driver_free_bytes":free,"driver_total_bytes":total,"driver_accounting_scope":"current driver context/device query,not a private instantaneous peak"})
    }
}
