struct Node {player:u8,num_children:u8}
struct Tree {nodes:Vec<Node>}
struct Spot {tree:Tree}
struct Solver {spot:Spot}
fn main(){
 let nodes:Vec<Node>=(0u16..=255).flat_map(|p|(0u16..=255).map(move |a|Node{player:p as u8,num_children:a as u8})).collect();
 let solver=Solver{spot:Spot{tree:Tree{nodes}}};
 let node_attrs: Vec<u16> = solver.spot.tree.nodes.iter()
            .map(|node| ((node.player as u16) << 8) | node.num_children as u16)
            .collect();
 assert_eq!(node_attrs.len(),65536);
 for (index,&packed) in node_attrs.iter().enumerate(){
  let original=&solver.spot.tree.nodes[index];
  assert_eq!(packed as usize,index);
  assert_eq!((packed>>8) as u8,original.player);
  assert_eq!((packed&255) as u8,original.num_children);
 }
 println!("E070_HOST_PACK_EXHAUSTIVE_PASS cases=65536 bytes={}",node_attrs.len()*std::mem::size_of::<u16>());
}
