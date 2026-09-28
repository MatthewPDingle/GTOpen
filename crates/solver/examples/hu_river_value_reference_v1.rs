//! Research-only terminal-value checks and visible river equity enumeration.
//! No learned policy, hidden opponent input, GPU, or production state.
#![allow(dead_code)]
#[path = "research_sampled/state.rs"] mod state;
#[path = "research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path = "research_sampled/observation_v1.rs"] mod observation_v1;
use poker_reference_v1::{Game, Table, Walk};
use observation_v1::Observation;
use rayon::prelude::*;
use serde_json::{json, Value};
use solver::tree::{Action, KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN};
use state::State;
use std::{collections::BTreeMap, io::Read};

type Identity = (usize, usize, usize, Vec<u8>);

fn visit(g: &Game, branch: usize, s: State, history: &mut Vec<u8>, rows: &mut Vec<Value>) {
    assert!(history.len() <= 19);
    if s.kind == KIND_CHANCE {
        history.push(5); visit(g, branch, s.deal(), history, rows); history.pop(); return;
    }
    if s.kind != KIND_ACTION { return; }
    let cfg = &g.configs[branch];
    let actions = s.actions(cfg);
    if s.street == 2 && matches!(actions[0], Action::Fold) {
        assert!(matches!(actions[1], Action::Call(_)));
        let me = s.player as usize;
        let folded = s.act(cfg, actions[0]);
        let called = s.act(cfg, actions[1]);
        assert_eq!(folded.kind, KIND_TERM_FOLD);
        assert_eq!(folded.player, s.player);
        assert_eq!(called.kind, KIND_TERM_SHOWDOWN);
        assert!((called.put[0] - called.put[1]).abs() < 1e-9);
        let pot = s.put.iter().sum::<f64>();
        let cost = called.put[me] - s.put[me];
        assert!(cost > 0.);
        let gross = cfg.rake_pct * (pot + cost);
        let rake = if cfg.rake_cap > 0. { gross.min(cfg.rake_cap) } else { gross };
        let expected = [-cost, (pot + cost - rake) / 2. - cost, pot - rake];
        let fold = folded.payouts(cfg)[1];
        let call = called.payouts(cfg);
        let actual = [call[1] - fold, call[2] - fold, call[0] - fold];
        for i in 0..3 { assert!((actual[i] - expected[i]).abs() < 1e-9); }
        rows.push(json!({"public_id":branch,"actor":me,"phase":3,"history":history,
            "legal_actions":actions.len(),"fold_index":0,"call_index":1,
            "pot":pot,"amount_to_call":cost,"rake":rake,
            "rake_fraction":cfg.rake_pct,"rake_cap":cfg.rake_cap,
            "endpoints_loss_tie_win":actual,"call_ends_showdown":true}));
    }
    for (i, action) in actions.into_iter().enumerate() {
        history.push(i as u8 + 1); visit(g, branch, s.act(cfg, action), history, rows); history.pop();
    }
}

fn catalog(g: &Game) -> Vec<Value> {
    let mut rows = vec![];
    for b in 0..g.kinds.len() {
        if g.kinds[b] == 2 { visit(g, b, State::root(&g.configs[b]), &mut vec![], &mut rows); }
    }
    assert!(!rows.is_empty()); rows
}

fn identity(v: &Value) -> Identity {
    (v["public_id"].as_u64().unwrap() as usize, v["actor"].as_u64().unwrap() as usize,
     3, v["history"].as_array().unwrap().iter().map(|x| x.as_u64().unwrap() as u8).collect())
}

fn control(context: &Value) -> Value {
    let base = Game::new(context);
    let templates = catalog(&base);
    // Known outcomes: aces beat kings on 2c 5d 8h Ts Qc; royal-flush board ties.
    let deals = [([48,49,44,45,0,13,26,35,40], 0),
                 ([44,45,48,49,0,13,26,35,40], 1),
                 ([1,6,9,14,32,36,40,44,48], -1)];
    let mut checked = 0usize;
    let mut maximum = 0f64;
    let mut covered_outcomes = [0usize; 3];
    let mut variants = Vec::new();
    for (rate, cap) in [(0.,0.),(0.05,2.),(0.10,0.),(0.10,0.1)] {
        let mut changed = context.clone();
        changed["rake_fraction"] = json!(rate); changed["rake_cap"] = json!(cap);
        let mut game = Game::new(&changed);
        // A common branch offset must cancel even when the seats differ.
        for (i, offset) in game.offsets.iter_mut().enumerate() { *offset += (i as f64 - 8.) * 3.25; }
        let rows = catalog(&game);
        let table: BTreeMap<Identity, &Value> = rows.iter().map(|r| (identity(r),r)).collect();
        assert_eq!(table.len(), rows.len());
        let mut variant_rows = 0usize;
        for (deal, expected_winner) in deals {
            let strategy = Table::new();
            for updater in 0..2 {
                for seed in 0..16 {
                    let mut walk = Walk::new(&game, &strategy, &deal, updater, seed);
                    assert_eq!(walk.winner, expected_winner);
                    walk.pre(0);
                    for r in &walk.records {
                        if r.tag <= 0 { continue; }
                        let o = Observation::decode(r.key);
                        if o.phase != 3 { continue; }
                        if let Some(row) = table.get(&(o.public_id,o.actor,o.phase,o.history.clone())) {
                            assert_eq!(r.tag as u64,row["legal_actions"].as_u64().unwrap());
                            let outcome = if expected_winner < 0 {1} else if expected_winner as usize == updater {2} else {0};
                            let expected = row["endpoints_loss_tie_win"][outcome].as_f64().unwrap();
                            let error = (r.values[1] - r.values[0] - expected).abs();
                            maximum = maximum.max(error); assert!(error < 1e-9);
                            checked += 1; variant_rows += 1; covered_outcomes[outcome] += 1;
                        }
                    }
                }
            }
        }
        assert!(variant_rows > 0);
        variants.push(json!({"rake_fraction":rate,"rake_cap":cap,"walk_records_checked":variant_rows,
            "terminal_templates":rows.len()}));
    }
    assert!(covered_outcomes.iter().all(|x| *x > 0));
    json!({"passed":true,"templates":templates,"terminal_templates":templates.len(),
        "known_deal_walk_records":checked,"maximum_record_error_bb":maximum,
        "covered_loss_tie_win":covered_outcomes,"rake_variants":variants,
        "branch_offset_cancellation":true,"known_winner_checks":true,
        "no_training":true,"no_gpu":true})
}

fn counts(cards: &[u8; 7]) -> [u32; 3] {
    let mut mask = 0u64;
    for &c in cards { assert!(c < 52 && mask & (1u64 << c) == 0); mask |= 1u64 << c; }
    let own = solver::evaluator::evaluate7(cards);
    let mut out = [0;3]; // actor wins, ties, loses
    for a in 0u8..52 { for b in a+1..52 {
        if mask & ((1u64 << a) | (1u64 << b)) != 0 { continue; }
        let rank = solver::evaluator::evaluate7(&[a,b,cards[2],cards[3],cards[4],cards[5],cards[6]]);
        out[if own > rank {0} else if own == rank {1} else {2}] += 1;
    }}
    assert_eq!(out.iter().sum::<u32>(),990); out
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 2 { return Err("Expected control CONTEXT or equities THREADS".into()); }
    match args[0].as_str() {
        "control" => {
            let context: Value = serde_json::from_slice(&std::fs::read(&args[1])?)?;
            println!("{}",control(&context));
        },
        "equities" => {
            let threads: usize = args[1].parse()?;
            if !(1..=16).contains(&threads) { return Err("Threads must be in 1..=16".into()); }
            let mut text = String::new(); std::io::stdin().take(10_000_001).read_to_string(&mut text)?;
            if text.len() > 10_000_000 { return Err("Input budget exceeded".into()); }
            let rows: Vec<[u8;7]> = serde_json::from_str(&text)?;
            if rows.is_empty() || rows.len() > 100_000 { return Err("Invalid row count".into()); }
            for cards in &rows {
                let mut mask = 0u64;
                for &c in cards {
                    if c >= 52 || mask & (1u64 << c) != 0 { return Err("Overlapping or invalid visible cards".into()); }
                    mask |= 1u64 << c;
                }
            }
            let pool = rayon::ThreadPoolBuilder::new().num_threads(threads).build()?;
            let began = std::time::Instant::now();
            let result: Vec<_> = pool.install(|| rows.par_iter().map(counts).collect());
            println!("{}",json!({"counts_win_tie_loss":result,"opponent_pairs_per_row":990,
                "threads":threads,"seconds":began.elapsed().as_secs_f64()}));
        },
        _ => return Err("Unknown mode".into()),
    }
    Ok(())
}
