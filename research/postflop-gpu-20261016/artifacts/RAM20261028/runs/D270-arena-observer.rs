#[cfg(test)]
impl ArenaLayout {
    pub(super) fn d270_dump(&self,path:&std::path::Path) {
        use std::io::Write;
        let file=std::fs::OpenOptions::new().write(true).create_new(true).open(path).unwrap();
        let mut w=std::io::BufWriter::new(file);
        w.write_all(b"D270-ARENA-v1\0\0\0").unwrap();
        w.write_all(&[self.compact as u8]).unwrap();
        let scalar=[self.len,self.active.len(),self.active.capacity(),self.copies.len(),self.copies.capacity(),
            self.inactive.len(),self.inactive.capacity(),self.initial[0].len(),self.initial[0].capacity(),
            self.initial[1].len(),self.initial[1].capacity(),self.zeros.len(),self.zeros.capacity()];
        for v in scalar {w.write_all(&(v as u64).to_le_bytes()).unwrap();}
        for b in &self.active {
            w.write_all(&b.node.to_le_bytes()).unwrap();w.write_all(&b.device_node.to_le_bytes()).unwrap();
            for v in [b.host,b.device as u64,b.len as u64] {w.write_all(&v.to_le_bytes()).unwrap();}
        }
        for b in &self.copies {for v in [b.host,b.device as u64,b.len as u64] {w.write_all(&v.to_le_bytes()).unwrap();}}
        for b in &self.inactive {
            w.write_all(&b.node.to_le_bytes()).unwrap();w.write_all(&b.device_node.to_le_bytes()).unwrap();
            for v in [b.host,b.len as u64,b.initial[0] as u64,b.initial[1] as u64] {w.write_all(&v.to_le_bytes()).unwrap();}
        }
        for data in [&self.initial[0],&self.initial[1],&self.zeros] {for v in data {w.write_all(&v.to_bits().to_le_bytes()).unwrap();}}
        w.flush().unwrap();w.get_ref().sync_all().unwrap();
    }
}
