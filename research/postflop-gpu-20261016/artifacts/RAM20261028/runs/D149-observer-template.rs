impl GpuSolver {
    pub fn d149_snapshot(&self, path: &std::path::Path, p: usize)
        -> (Vec<Vec<u32>>, serde_json::Value, Vec<u32>) {
        self.stream.synchronize().unwrap();
        let mut out = std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(path).unwrap());
        use std::io::Write;
        out.write_all(b"D149-GPU-RAW1\0\0\0").unwrap();
        let mut image = Vec::new();
        let algorithm = match self.algo { Algorithm::Dcfr => 0, Algorithm::CfrPlus => 1, Algorithm::PcfrPlus => 2 };
        for (name, values) in [("iteration", vec![self.iteration]), ("algorithm", vec![algorithm]), ("hands", vec![self.nh[0] as u32, self.nh[1] as u32])] {
            crate::host_field(&mut out, name, &values);
            image.push(values);
        }
        let mut physical = Vec::new();
        macro_rules! field {
            ($name:expr, $data:expr) => {{
                let values = self.stream.clone_dtoh($data).unwrap();
                self.stream.synchronize().unwrap();
                let bits = crate::words(&values);
                crate::host_field(&mut out, $name, &bits);
                if $name == "d_cfv" { physical = bits; } else { image.push(bits); }
            }}
        }
        // D149_ALL_DEVICE_FIELDS
        let stride = self.nh_max as usize;
        let nh = self.nh[p] as usize;
        assert!(stride > 0 && nh <= stride && physical.len() % stride == 0);
        let rows = physical.len() / stride;
        let mut logical = Vec::with_capacity(rows * nh);
        for row in 0..rows { logical.extend_from_slice(&physical[row * stride..row * stride + nh]); }
        crate::host_field(&mut out, "CFV_logical", &logical);
        image.push(logical);
        out.flush().unwrap();
        out.get_ref().sync_all().unwrap();
        let info = serde_json::json!({"logical_player": p, "rows": rows, "stride": stride,
            "logical_hands": nh, "physical_words": physical.len(), "device_fields": 66,
            "all_fields": 70, "graphs_present": self.graphs.is_some(),
            "eval_graphs_present": [self.eval_graphs[0].is_some(), self.eval_graphs[1].is_some()],
            "pinned_words": self.h_staging.len, "wrapper_bytes": std::mem::size_of::<Self>()});
        (image, info, physical)
    }

    pub fn d149_clobber(&mut self, before: &std::path::Path, after: &std::path::Path,
        p: usize, epoch: usize) -> serde_json::Value {
        let (old, old_info, old_cfv) = self.d149_snapshot(before, p);
        let pattern: [u32; 16] = [0x7fc01234, 0x7f801234, 0x7f800000, 0xff800000,
            0xdeadc0de, 0xffffffff, 0, 0x80000000, 1, 0x80000001, 0x3f800000,
            0xbf800000, 0x4b123456, 0x00800000, 0x7f7fffff, 0xff7fffff];
        let seed: Vec<u32> = (0..self.d_cfv.len()).map(|i| pattern[(i + epoch) % pattern.len()]).collect();
        let values: Vec<f32> = seed.iter().copied().map(f32::from_bits).collect();
        self.stream.memcpy_htod(&values, &mut self.d_cfv).unwrap();
        self.stream.synchronize().unwrap();
        let (new, new_info, actual) = self.d149_snapshot(after, p);
        assert_eq!(actual, seed, "all actual CFV words replaced");
        assert_eq!(old.len(), new.len());
        assert_eq!(old[..old.len() - 1], new[..new.len() - 1], "all65 other device arrays and host state unchanged");
        assert_eq!(old_info, new_info);
        let changed = old_cfv.iter().zip(&seed).filter(|(a, b)| a != b).count();
        assert!(changed > 0);
        serde_json::json!({"epoch": epoch, "pattern": pattern, "rotation": epoch % 16,
            "words": seed.len(), "changed_words": changed, "info": new_info,
            "all65other_actual_arrays_unchanged": true, "CFV_only_written": true})
    }
}
