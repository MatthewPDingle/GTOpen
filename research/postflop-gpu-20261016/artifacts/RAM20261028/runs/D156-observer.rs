impl GpuSolver {
    pub fn d156_snapshot(&self,path:&std::path::Path) -> serde_json::Value {
        use std::io::Write;
        self.stream.synchronize().unwrap();
        let cfv=self.stream.clone_dtoh(&self.d_cfv).unwrap();self.stream.synchronize().unwrap();
        let mut f=std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(path).unwrap());
        for v in cfv {f.write_all(&v.to_bits().to_le_bytes()).unwrap();}f.flush().unwrap();f.get_ref().sync_all().unwrap();
        serde_json::json!({"iteration":self.iteration,"hands":self.nh,"iso_active":self.iso_active,
            "CFV_words":self.d_cfv.len(),"pinned_words":self.h_staging.len,"regret_words":[self.d_regrets[0].len(),self.d_regrets[1].len()],
            "strategy_words":[self.d_strat[0].len(),self.d_strat[1].len()],"graphs_present":self.graphs.is_some(),"eval_graphs_present":[self.eval_graphs[0].is_some(),self.eval_graphs[1].is_some()],
            "packet_module_loaded":D156_MODULE_LOADED,"wrapper_bytes":std::mem::size_of::<Self>()})
    }
}
