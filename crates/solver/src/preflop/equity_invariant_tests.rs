//! Same-class all-in payoffs must share the pot equally, including when an
//! old Monte-Carlo cache supplies the pairwise table.
use super::*;

#[test]
fn same_class_all_in_terminals_are_zero_sum_for_raw_and_static() {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
    let bytes = std::fs::read(path).unwrap();
    let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
    let eq = Arc::new(equity::EquityTable::load_or_build(path, samples));
    for realization in ["raw", "static"] {
        for card_removal in [false, true] {
            let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
                "positions": ["SB", "BB"], "posts": [0.5, 1.0], "stack": 5.0,
                "open_raises": [], "raise_mults": [], "max_raises": 1,
                "add_allin": true, "limp": false, "realization": realization,
                "rake_pct": 0.0, "card_removal": card_removal
            }))
            .unwrap();
            let solver = PreflopSolver::new(cfg, eq.clone()).unwrap();
            let node = solver
                .nodes
                .iter()
                .position(|nd| {
                    nd.kind == KIND_POT_SHARE && nd.live == 3 && nd.invested == [5.0, 5.0]
                })
                .expect("called all-in");
            for h in 0..NUM_CLASSES {
                let mut reaches = vec![vec![0.0; NUM_CLASSES]; 2];
                reaches[0][h] = 1.0;
                reaches[1][h] = 1.0;
                let mut payoffs = [0.0; 2];
                for (p, payoff) in payoffs.iter_mut().enumerate() {
                    let mut out = [0.0; NUM_CLASSES];
                    solver.terminal_value(node, p, &reaches, &mut out);
                    *payoff = out[h];
                    assert_eq!(
                        out[h], 0.0,
                        "{realization}, removal={card_removal}, seat={p}, class={h}"
                    );
                }
                assert_eq!(payoffs[0] + payoffs[1], 0.0);
            }
        }
    }
}
