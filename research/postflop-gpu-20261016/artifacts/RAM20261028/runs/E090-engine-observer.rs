impl GpuSolver {
    pub fn e090_force_sweep(&mut self, p:usize) {
        self.iteration=self.iteration.max(1);
        let disc=Discounts::for_iteration(self.algo,self.iteration);
        self.stream.memcpy_htod(&[disc.pos,disc.neg,disc.strat],&mut self.d_disc).unwrap();
        let seed=vec![f32::from_bits(0x4b123456);self.d_cfv.len()];
        self.stream.memcpy_htod(&seed,&mut self.d_cfv).unwrap();
        self.sweep(p,None).unwrap();self.stream.synchronize().unwrap();
    }
    pub fn e090_snapshot(&self,path:&std::path::Path,p:usize,poisoned:bool)->(Vec<Vec<u32>>,serde_json::Value) {
        self.stream.synchronize().unwrap();
        let old_width=self.nh_max as usize;
        let logical=self.nh[p]as usize;
        let stride=E090_STRIDE;
        let physical=self.stream.clone_dtoh(&self.d_cfv).unwrap();
        self.stream.synchronize().unwrap();
        assert_eq!(physical.len()%old_width,0);
        let rows=physical.len()/old_width;
        let mut values=Vec::with_capacity(rows*logical);
        let mut guards=0usize;
        for row in 0..rows {
            for i in 0..logical {
                let bits=physical[row*stride+i].to_bits();
                if poisoned {assert_ne!(bits,0x4b123456,"every logical word overwritten");}
                values.push(bits);
            }
        }
        if poisoned {
            for i in 0..physical.len() {
                let live=i/stride<rows && i%stride<logical;
                if !live {assert_eq!(physical[i].to_bits(),0x4b123456,"full physical CFV guard");guards+=1;}
            }
        }
        let mut out=std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(path).unwrap());
        use std::io::Write;out.write_all(b"E090-GPU-RAW1\0\0\0").unwrap();
        let mut image=Vec::new();
        macro_rules! field {
            ($name:expr,$data:expr) => {{
                let v=self.stream.clone_dtoh($data).unwrap();self.stream.synchronize().unwrap();
                let bits=crate::words(&v);crate::host_field(&mut out,$name,&bits);image.push(bits);
            }}
        }
        crate::host_field(&mut out,"iteration",&[self.iteration]);image.push(vec![self.iteration]);
        field!("regret0",&self.d_regrets[0]);field!("regret1",&self.d_regrets[1]);
        field!("strategy0",&self.d_strat[0]);field!("strategy1",&self.d_strat[1]);
        field!("reach0",&self.d_reach[0]);field!("reach1",&self.d_reach[1]);
        field!("discounts",&self.d_disc);field!("weights0",&self.d_weights[0]);field!("weights1",&self.d_weights[1]);
        field!("lock_offsets",&self.d_lock_off);field!("lock_sigma",&self.d_lock_sigma);
        crate::host_field(&mut out,"CFV_logical",&values);image.push(values);
        crate::host_field(&mut out,"CFV_physical",&crate::words(&physical));
        out.flush().unwrap();out.get_ref().sync_all().unwrap();
        let info=serde_json::json!({"p":p,"rows":rows,"logical_hands":logical,"original_width":old_width,"actual_stride":stride,"physical_words":physical.len(),"logical_words":rows*logical,"poisoned":poisoned,"full_physical_guard_words":guards,
            "wrapper_bytes":std::mem::size_of::<Self>(),"pinned_words":self.h_staging.len,
            "arena_words":[self.d_regrets[0].len(),self.d_regrets[1].len()],
            "reach_words":[self.d_reach[0].len(),self.d_reach[1].len()],
            "graphs_present":self.graphs.is_some(),"eval_graph_present":[self.eval_graphs[0].is_some(),self.eval_graphs[1].is_some()],
            "performance_measurement":false});
        (image,info)
    }
}
