impl ArenaLayout {
    pub(super) fn packet_blocks(&self, solver:&Solver, p:usize) -> Option<Vec<super::packet_readback::Block>> {
        use super::packet_readback::Block;
        if self.compact {
            Some(self.active.iter().map(|b|Block{node:b.node as usize,host:b.host,source:b.device,len:b.len}).collect())
        } else {
            let nh=solver.spot.hands[p].len();let mut out=Vec::new();
            for (node,n) in solver.spot.tree.nodes.iter().enumerate() {
                if n.kind==KIND_ACTION && n.player as usize==p {
                    out.push(Block{node,host:n.data_offset,source:usize::try_from(n.data_offset).ok()?,len:(n.num_children as usize).checked_mul(nh)?});
                }
            }
            Some(out)
        }
    }

    pub(super) fn packet_restore_inactive(&self, solver:&Solver, p:usize, which:usize) {
        let store=if which==0 {&solver.regrets[p]} else {&solver.strat[p]};
        self.inactive.par_iter().for_each(|block| {
            let start = block.initial[which];
            let values = if start == usize::MAX { &self.zeros[..block.len] }
                else { &self.initial[which][start..start + block.len] };
            unsafe { store.write_f32(block.node, block.host, block.len, values); }
        });
    }
}
