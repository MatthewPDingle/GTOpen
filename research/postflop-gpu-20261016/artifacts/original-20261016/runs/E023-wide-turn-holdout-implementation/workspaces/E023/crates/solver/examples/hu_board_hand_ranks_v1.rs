//! Native hand strengths for a fixed river; no solve, ranges or GPU allocation.
use serde_json::json;
fn main() -> Result<(),Box<dyn std::error::Error>> {
    let board: Vec<u8> = std::env::args().skip(1).map(|x|x.parse().unwrap()).collect();
    assert_eq!(board.len(),5);
    let mut mask=0u64;
    for &c in &board { assert!(c<52 && mask&(1u64<<c)==0); mask|=1u64<<c; }
    let mut rows=Vec::new();
    for a in 0u8..52 { for b in a+1..52 {
        if mask & ((1u64<<a)|(1u64<<b)) != 0 { continue; }
        let cards=[a,b,board[0],board[1],board[2],board[3],board[4]];
        rows.push(json!({"hand":[a,b],"rank":solver::evaluator::evaluate7(&cards)}));
    }}
    assert_eq!(rows.len(),1081);
    println!("{}",json!({"format":1,"board":board,"larger_rank_is_stronger":true,"rows":rows}));
    Ok(())
}
