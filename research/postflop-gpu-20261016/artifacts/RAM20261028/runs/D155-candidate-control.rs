impl GpuSolver {
    pub fn d155_default_sync(&mut self, solver:&mut Solver, strategy:bool) {
        let bytes=(0..2).map(|p|(self.d_strat[p].len()+if strategy{0}else{self.d_regrets[p].len()})*4).sum::<usize>();
        assert!(bytes<packet_readback::MIN_SOURCE_BYTES);
        assert!(self.packet_functions.is_none());
        if strategy {self.sync_strategy(solver).unwrap();} else {self.sync_to_cpu(solver).unwrap();}
        assert!(self.packet_functions.is_none());
    }
    pub fn d155_forced_sync(&mut self, solver:&mut Solver, strategy:bool,
        before:&std::path::Path, after:&std::path::Path) -> serde_json::Value {
        use std::io::Write;
        self.stream.synchronize().unwrap();
        let expected=solver.storage==crate::store::Storage::Compressed
            && self.d_cfv.len()>=packet_readback::PACKET_WORDS && self.h_staging.len>=packet_readback::PACKET_WORDS;
        let was_loaded=self.packet_functions.is_some();
        let len=self.h_staging.len;
        assert!(len<=isize::MAX as usize/4);
        unsafe{self.h_staging.ptr.cast::<u8>().write_bytes(0x5a,len*4);}
        let mut f=std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(before).unwrap());
        for &v in self.h_staging.as_slice(){f.write_all(&v.to_bits().to_le_bytes()).unwrap();}f.flush().unwrap();f.get_ref().sync_all().unwrap();drop(f);
        let (gpu_before,_,_)=self.d155_snapshot(&before.with_extension("gpu.bin"),1);
        let handled=self.try_packet_sync(solver,strategy,0).unwrap();
        assert_eq!(handled,expected,"force actual compressed path when current capacities admit");
        if !handled {
            assert!(!self.packet_functions.is_some());
            if strategy {self.sync_strategy(solver).unwrap();} else {self.sync_to_cpu(solver).unwrap();}
        }
        self.stream.synchronize().unwrap();
        let (gpu_after,gpu_info,_)=self.d155_snapshot(&after.with_extension("gpu.bin"),1);
        assert_eq!(gpu_before[..gpu_before.len()-1],gpu_after[..gpu_after.len()-1],"all65 actual GPU arrays unchanged across readback");
        let mut f=std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(after).unwrap());
        for &v in self.h_staging.as_slice(){f.write_all(&v.to_bits().to_le_bytes()).unwrap();}f.flush().unwrap();f.get_ref().sync_all().unwrap();drop(f);
        let guard_words=if handled {let tail=&self.h_staging.as_slice()[packet_readback::PACKET_WORDS..];assert!(tail.iter().all(|v|v.to_bits()==0x5a5a5a5a));tail.len()} else {0};
        assert_eq!(self.packet_functions.is_some(),handled);
        serde_json::json!({"strategy_only":strategy,"forced_packed_path":handled,"expected_from_fixture_format_and_current_capacity":expected,
            "module_loaded_before":was_loaded,"module_loaded_after":self.packet_functions.is_some(),"pinned_words":len,
            "CFV_words":self.d_cfv.len(),"packet_prefix_words":packet_readback::PACKET_WORDS,"all_pinned_tail_guards_exact":true,"pinned_tail_guard_words":guard_words,
            "production_min_source_bytes":packet_readback::MIN_SOURCE_BYTES,"internal_control_min_source_bytes":0,
            "all65_arrays_before_after_exact":true,"GPU_info":gpu_info})
    }
}
