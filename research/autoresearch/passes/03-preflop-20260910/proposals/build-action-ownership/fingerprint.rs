// Copy into the benchmark example; invoke AFTER stopping the build/load timer.
// No tree-sized serialization or extra arena copies.
fn topology_and_action_storage(s: &solver::preflop::PreflopSolver) -> serde_json::Value {
    struct Digest(u64);
    impl Digest {
        fn bytes(&mut self, bytes: &[u8]) {
            for b in bytes {
                self.0 = (self.0 ^ u64::from(*b)).wrapping_mul(0x100000001b3);
            }
        }
        fn number(&mut self, value: u64) {
            self.bytes(&value.to_le_bytes());
        }
        fn text(&mut self, value: &str) {
            self.number(value.len() as u64);
            self.bytes(value.as_bytes());
        }
    }
    let mut hash = Digest(0xcbf29ce484222325);
    let mut action_nodes = 0usize;
    let mut edges = 0usize;
    let mut vec_bytes = 0usize;
    let mut string_len = 0usize;
    let mut string_capacity = 0usize;
    hash.number(s.nodes.len() as u64);
    for (i, node) in s.nodes.iter().enumerate() {
        for value in [
            node.kind as u64,
            node.actor as u64,
            node.child_start as u64,
            node.live as u64,
            node.winner as u64,
            node.data_off as u64,
            node.aggressor as u64,
            node.bucket as u64,
            node.raises as u64,
            node.raised as u64,
            node.pot.to_bits(),
        ] {
            hash.number(value);
        }
        hash.number(node.invested.len() as u64);
        for value in &node.invested {
            hash.number(value.to_bits());
        }
        hash.number(node.r.len() as u64);
        for value in &node.r {
            hash.number(value.to_bits() as u64);
        }
        hash.number(node.posf.len() as u64);
        for value in &node.posf {
            hash.number(value.to_bits() as u64);
        }
        hash.number(node.actions.len() as u64);
        if !node.actions.is_empty() {
            action_nodes += 1;
        }
        vec_bytes += node.actions.capacity() * std::mem::size_of::<solver::preflop::PAction>();
        for (a, action) in node.actions.iter().enumerate() {
            hash.text(&action.kind);
            hash.number(action.to.to_bits());
            hash.text(&action.label);
            hash.number(s.child(i, a) as u64);
            string_len += action.kind.len() + action.label.len();
            string_capacity += action.kind.capacity() + action.label.capacity();
            edges += 1;
        }
    }
    assert_eq!(
        edges + 1,
        s.nodes.len(),
        "native tree must have one incoming edge per non-root node"
    );
    serde_json::json!({"topology_hash":format!("{:016x}",hash.0),"nodes":s.nodes.len(),
        "action_nodes":action_nodes,"edges":edges,"action_vec_capacity_bytes":vec_bytes,
        "action_string_len_bytes":string_len,"action_string_capacity_bytes":string_capacity,
        "action_retained_bytes":vec_bytes+string_capacity})
}
