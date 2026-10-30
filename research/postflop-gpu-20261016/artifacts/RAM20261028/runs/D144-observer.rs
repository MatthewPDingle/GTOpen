impl GpuSolver {
    pub fn d144_sample(&self, path: &std::path::Path) {
        self.stream.synchronize().unwrap();
        let mut out = std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(path).unwrap());
        use std::io::Write;
        out.write_all(b"D144-REACH-v1\0\0\0").unwrap();
        crate::host_field(&mut out, "iteration", &[self.iteration]);
        crate::host_field(&mut out, "hands", &[self.nh[0] as u32, self.nh[1] as u32]);
        macro_rules! field {
            ($name:expr, $data:expr) => {{
                let values = self.stream.clone_dtoh($data).unwrap();
                self.stream.synchronize().unwrap();
                crate::host_field(&mut out, $name, &crate::words(&values));
            }}
        }
        field!("action_nodes", &self.d_action_nodes);
        field!("node_player", &self.d_node_player);
        field!("node_na", &self.d_node_na);
        field!("node_children_start", &self.d_node_children_start);
        field!("children", &self.d_children);
        field!("chance_children", &self.d_chance_children);
        field!("rsrc0", &self.d_rsrc[0]);
        field!("rsrc1", &self.d_rsrc[1]);
        field!("lock_off", &self.d_lock_off);
        field!("reach0", &self.d_reach[0]);
        field!("reach1", &self.d_reach[1]);
        out.flush().unwrap();
        out.get_ref().sync_all().unwrap();
    }
}
