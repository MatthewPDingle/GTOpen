pub(super) const PINNED_WORD_LIMIT: usize = 64 * 1024 * 1024 / 4;

#[derive(Clone, Copy, Debug)]
struct TransferGroup { first: usize, end: usize, device: usize, len: usize }

// VALIDATED_NEXT_GROUP

fn finish_bounded_copy(
    stream: &Arc<CudaStream>,
    copy: Result<(), cudarc::driver::DriverError>,
) -> Result<(), String> {
    // Always retire a possibly submitted copy before staging reuse or an
    // error return. Preserve the original copy error when both calls fail.
    let ready = stream.synchronize().map_err(e);
    copy.map_err(e)?;
    ready
}

impl ArenaLayout {
    pub(super) fn prepare_bounded(
        &mut self, solver: &Solver, p: usize, limit: usize,
    ) -> Result<usize, String> {
        if self.len <= limit { return Ok(self.len); }
        if !self.compact {
            self.active.clear();
            let nh = solver.spot.hands[p].len();
            for (i, node) in solver.spot.tree.nodes.iter().enumerate() {
                if node.kind != KIND_ACTION || node.player as usize != p { continue; }
                self.active.push(ActiveBlock {
                    node: i as u32, host: node.data_offset,
                    device: node.data_offset as usize,
                    len: node.num_children as usize * nh,
                });
            }
        }
        self.check_bounded(usize::MAX)?;
        let largest = self.active.iter().map(|b| b.len).max().unwrap_or(0);
        Ok(self.len.min(limit).max(largest))
    }

    pub(super) fn discard_bounded(&mut self) {
        if !self.compact { self.active = Vec::new(); }
    }

    fn check_bounded(&self, capacity: usize) -> Result<(), String> {
        let mut cursor = 0usize;
        for block in &self.active {
            if block.device != cursor { return Err("bounded arena has a gap or overlap".into()); }
            if block.len > capacity { return Err("bounded staging cannot hold a node".into()); }
            cursor = cursor.checked_add(block.len).ok_or("bounded arena length overflow")?;
        }
        if cursor != self.len { return Err("bounded arena has incomplete coverage".into()); }
        Ok(())
    }

    fn copy_spans_in(&self, start: usize, end: usize) -> &[CopySpan] {
        if start == end { return &self.copies[..0]; }
        let first = self.copies.partition_point(|s| s.device + s.len <= start);
        let last = self.copies.partition_point(|s| s.device < end);
        &self.copies[first..last]
    }

    fn read_bounded_group(&self, store: &Store, group: TransferGroup, data: &mut [f32]) {
        if let Store::F32(buf) = store {
            if !self.compact {
                data[..group.len].copy_from_slice(
                    &buf.as_slice()[group.device..group.device + group.len]);
            } else {
                for span in self.copy_spans_in(group.device, group.device + group.len) {
                    let first = span.device.max(group.device);
                    let last = (span.device + span.len).min(group.device + group.len);
                    let host = span.host as usize + first - span.device;
                    data[first - group.device..last - group.device]
                        .copy_from_slice(&buf.as_slice()[host..host + last - first]);
                }
            }
        } else {
            for block in &self.active[group.first..group.end] {
                let off = block.device - group.device;
                unsafe {
                    store.read_f32(block.node, block.host, block.len,
                        &mut data[off..off + block.len]);
                }
            }
        }
    }

    fn write_bounded_group(&self, store: &Store, group: TransferGroup, data: &[f32]) {
        if let Store::F32(buf) = store {
            if !self.compact {
                unsafe { buf.slice(group.device as u64, group.len) }
                    .copy_from_slice(&data[..group.len]);
            } else {
                self.copy_spans_in(group.device, group.device + group.len)
                    .par_iter().for_each(|span| {
                        let first = span.device.max(group.device);
                        let last = (span.device + span.len).min(group.device + group.len);
                        let host = span.host + (first - span.device) as u64;
                        unsafe { buf.slice(host, last - first) }
                            .copy_from_slice(&data[first - group.device..last - group.device]);
                    });
            }
        } else {
            self.active[group.first..group.end].par_iter().for_each(|block| {
                let off = block.device - group.device;
                unsafe {
                    store.write_f32(block.node, block.host, block.len,
                        &data[off..off + block.len]);
                }
            });
        }
    }

    fn capture_bounded_inactive(&mut self, store: &Store, which: usize) {
        if !self.compact { return; }
        // ORIGINAL_INACTIVE_CAPTURE
    }

    fn restore_bounded_inactive(&self, store: &Store, which: usize) {
        if !self.compact { return; }
        if let Store::F32(buf) = store {
            // ORIGINAL_F32_RESTORE
            return;
        }
        // ORIGINAL_COMPRESSED_RESTORE
    }

    fn upload_bounded(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize,
        which: usize, staging: &mut [f32],
    ) -> Result<CudaSlice<f32>, String> {
        self.check_bounded(staging.len())?;
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        self.capture_bounded_inactive(store, which);
        // Coverage is validated before allocation. Every device word is
        // written and drained before this array can reach a solver kernel.
        let mut device = unsafe { stream.alloc::<f32>(self.len) }.map_err(e)?;
        let mut first = 0;
        while let Some(group) = next_transfer_group(&self.active, first, staging.len())? {
            self.read_bounded_group(store, group, staging);
            let copy = stream.memcpy_htod(&staging[..group.len],
                &mut device.slice_mut(group.device..group.device + group.len));
            finish_bounded_copy(stream, copy)?;
            first = group.end;
        }
        Ok(device)
    }

    pub(super) fn download(
        &self, stream: &Arc<CudaStream>, solver: &Solver, p: usize,
        which: usize, device: &CudaSlice<f32>, staging: &mut [f32],
    ) -> Result<(), String> {
        let len = device.len();
        if len <= staging.len() {
            let copy = stream.memcpy_dtoh(device, &mut staging[..len]);
            finish_bounded_copy(stream, copy)?;
            self.write(solver, p, which, &staging[..len]);
            return Ok(());
        }
        if len != self.len { return Err("bounded device arena length mismatch".into()); }
        self.check_bounded(staging.len())?;
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        let mut first = 0;
        while let Some(group) = next_transfer_group(&self.active, first, staging.len())? {
            let copy = stream.memcpy_dtoh(
                &device.slice(group.device..group.device + group.len),
                &mut staging[..group.len]);
            finish_bounded_copy(stream, copy)?;
            self.write_bounded_group(store, group, &staging[..group.len]);
            first = group.end;
        }
        self.restore_bounded_inactive(store, which);
        Ok(())
    }
}

#[cfg(test)]
mod bounded_tests {
    use super::*;
    #[test]
    fn transfer_groups_keep_whole_nodes_and_reject_invalid_spans() {
        let mut device = 0;
        let blocks: Vec<_> = [0,1,3,0,5,2].into_iter().enumerate().map(|(node,len)| {
            let b=ActiveBlock{node:node as u32,host:device as u64,device,len};
            device+=len;b
        }).collect();
        let mut got=Vec::new();let mut first=0;
        while let Some(g)=next_transfer_group(&blocks,first,5).unwrap() {
            got.push((g.first,g.end,g.device,g.len));first=g.end;
        }
        assert_eq!(got,vec![(0,4,0,4),(4,5,4,5),(5,6,9,2)]);
        assert!(next_transfer_group(&blocks,4,4).is_err());
        let bad=[ActiveBlock{node:0,host:0,device:0,len:1},
            ActiveBlock{node:1,host:1,device:2,len:1}];
        assert!(next_transfer_group(&bad,0,5).is_err());
        assert!(next_transfer_group(&[],0,0).unwrap().is_none());
    }
    #[test]
    fn compact_copy_spans_cover_exact_window_intersections() {
        let l=ArenaLayout{
            compact:true,len:12,active:Vec::new(),inactive:Vec::new(),
            initial:[Vec::new(),Vec::new()],zeros:Vec::new(),
            copies:vec![CopySpan{host:3,device:0,len:5},
                CopySpan{host:20,device:5,len:3},CopySpan{host:30,device:8,len:4}],
        };
        let ranges=[(0,4),(4,9),(9,12)];
        let mut seen=Vec::new();
        for (first,last) in ranges {
            for s in l.copy_spans_in(first,last) {
                for d in s.device.max(first)..(s.device+s.len).min(last) {
                    seen.push((d,s.host+(d-s.device)as u64));
                }
            }
        }
        let expected:Vec<_>=(0..12).map(|d|(d,if d<5{3+d as u64}
            else if d<8{20+(d-5)as u64}else{30+(d-8)as u64})).collect();
        assert_eq!(seen,expected);
        assert!(l.copy_spans_in(5,5).is_empty());
    }
}
