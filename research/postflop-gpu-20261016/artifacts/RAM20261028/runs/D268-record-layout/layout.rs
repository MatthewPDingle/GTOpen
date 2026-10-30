#![allow(dead_code)]
use std::mem::{size_of, align_of, offset_of};
struct BaselineActiveBlock {
    node: u32,
    host: u64,
    device: usize,
    len: usize,
}
struct ProposedActiveBlock {
    node: u32,
    device_node: u32,
    host: u64,
    device: usize,
    len: usize,
}
struct BaselineInactiveBlock {
    node: u32,
    host: u64,
    len: usize,
    // usize::MAX represents a block of positive-zero bits. Signed zero and
    // every other initial bit pattern have an explicit snapshot.
    initial: [usize; 2],
}
struct ProposedInactiveBlock {
    node: u32,
    device_node: u32,
    host: u64,
    len: usize,
    // usize::MAX represents a block of positive-zero bits. Signed zero and
    // every other initial bit pattern have an explicit snapshot.
    initial: [usize; 2],
}
fn main() {
println!("D268_LAYOUT|BaselineActiveBlock|{}|{}|{}|{}|{}|{}", size_of::<BaselineActiveBlock>(), align_of::<BaselineActiveBlock>(), offset_of!(BaselineActiveBlock, node), offset_of!(BaselineActiveBlock, host), offset_of!(BaselineActiveBlock, device), offset_of!(BaselineActiveBlock, len));
println!("D268_LAYOUT|ProposedActiveBlock|{}|{}|{}|{}|{}|{}|{}", size_of::<ProposedActiveBlock>(), align_of::<ProposedActiveBlock>(), offset_of!(ProposedActiveBlock, node), offset_of!(ProposedActiveBlock, host), offset_of!(ProposedActiveBlock, device), offset_of!(ProposedActiveBlock, len), offset_of!(ProposedActiveBlock, device_node));
println!("D268_LAYOUT|BaselineInactiveBlock|{}|{}|{}|{}|{}|{}", size_of::<BaselineInactiveBlock>(), align_of::<BaselineInactiveBlock>(), offset_of!(BaselineInactiveBlock, node), offset_of!(BaselineInactiveBlock, host), offset_of!(BaselineInactiveBlock, len), offset_of!(BaselineInactiveBlock, initial));
println!("D268_LAYOUT|ProposedInactiveBlock|{}|{}|{}|{}|{}|{}|{}", size_of::<ProposedInactiveBlock>(), align_of::<ProposedInactiveBlock>(), offset_of!(ProposedInactiveBlock, node), offset_of!(ProposedInactiveBlock, host), offset_of!(ProposedInactiveBlock, len), offset_of!(ProposedInactiveBlock, initial), offset_of!(ProposedInactiveBlock, device_node));
}
