impl GpuSolver {
    pub fn d166_snapshot(&self,path:&std::path::Path)->serde_json::Value {
        use std::io::Write;
        self.stream.synchronize().unwrap();
        let mut out=std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(path).unwrap());
        out.write_all(b"D166-GPU-RAW1\0\0\0").unwrap();
        let algorithm=match self.algo{Algorithm::Dcfr=>0,Algorithm::CfrPlus=>1,Algorithm::PcfrPlus=>2};
        crate::host_field(&mut out,"iteration",&[self.iteration]);
        crate::host_field(&mut out,"algorithm",&[algorithm]);
        crate::host_field(&mut out,"hands",&[self.nh[0] as u32,self.nh[1] as u32]);
        let mut fields=Vec::new();
        macro_rules! field{($name:expr,$data:expr)=>{{fields.push(crate::d166_field(&self.stream,$name,$data,&mut out));}}}
        // D166_ALL_DEVICE_FIELDS
        assert_eq!(fields.len(),66);
        out.flush().unwrap();out.get_ref().sync_all().unwrap();
        serde_json::json!({"iteration":self.iteration,"algorithm":algorithm,"hands":self.nh,"nh_max":self.nh_max,"iso_active":self.iso_active,
          "CFV_words":self.d_cfv.len(),"pinned_words":self.h_staging.len,"regret_words":[self.d_regrets[0].len(),self.d_regrets[1].len()],
          "strategy_words":[self.d_strat[0].len(),self.d_strat[1].len()],"graphs_present":self.graphs.is_some(),"eval_graphs_present":[self.eval_graphs[0].is_some(),self.eval_graphs[1].is_some()],
          "wrapper_bytes":std::mem::size_of::<Self>(),"device_fields":fields,"host_fields":3})
    }
}
