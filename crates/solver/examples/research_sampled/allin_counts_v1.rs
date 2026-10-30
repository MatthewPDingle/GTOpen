//! All-in metadata is simulation information, never an observation feature.
use serde::Deserialize;
use serde_json::{json, Value};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Counts {
    private_cards: [u8; 4],
    wins: u64,
    ties: u64,
    losses: u64,
    boards: u64,
}

pub fn equities(batch: &Value, deals: &[[u8; 9]]) -> Vec<f64> {
    assert_eq!(batch["terminal_estimator"], "conditional-preflop-allin-v1");
    let rows: Vec<Counts> = serde_json::from_value(batch["allin_counts"].clone()).unwrap();
    assert_eq!(rows.len(), deals.len());
    rows.iter().zip(deals).map(|(r, d)| {
        let mut seen = [false; 52];
        for &c in d { assert!(c < 52 && !seen[c as usize]); seen[c as usize] = true; }
        // Exact original card order binds each label to its sampled private pair.
        assert_eq!(r.private_cards, d[..4]);
        assert_eq!(r.boards, 1_712_304);
        assert!(r.wins <= r.boards && r.ties <= r.boards && r.losses <= r.boards);
        assert_eq!(r.wins + r.ties + r.losses, r.boards);
        (r.wins as f64 + 0.5 * r.ties as f64) / r.boards as f64
    }).collect()
}

/// Independent terminal cash-flow reference: winnings less chips invested.
/// No showdown after a postflop decision is changed.
pub fn cashflow_context(context: &Value, equity: f64) -> Value {
    assert!(equity.is_finite() && (0. ..=1.).contains(&equity));
    let mut c = context.clone();
    let rate = c["rake_fraction"].as_f64().unwrap();
    let cap = c["rake_cap"].as_f64().unwrap();
    assert!(rate.is_finite() && (0. ..=1.).contains(&rate));
    assert!(cap.is_finite() && cap >= 0.);
    for node in c["nodes"].as_array_mut().unwrap() {
        if node["leaf"]["type"] != "showdown" { continue; }
        assert_eq!(node["leaf"]["effective_stack"], 0.);
        let pot = node["pot"].as_f64().unwrap();
        assert!(pot.is_finite() && pot >= 0.);
        let gross = pot * rate;
        let rake = if cap > 0. { gross.min(cap) } else { gross };
        let shares = [equity, 1. - equity];
        let mut utilities = [0.; 2];
        for p in 0..2 {
            let invested = node["invested"][p].as_f64().unwrap();
            assert!(invested.is_finite() && invested >= 0.);
            utilities[p] = shares[p] * (pot - rake) - invested;
        }
        node["leaf"] = json!({"type":"fold", "utilities":utilities});
    }
    c
}
