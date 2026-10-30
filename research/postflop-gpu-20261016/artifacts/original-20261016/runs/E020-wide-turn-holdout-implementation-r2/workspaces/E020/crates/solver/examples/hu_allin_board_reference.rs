//! Bounded research control: exact future-board equity for fixed private cards.
//! No solver, policies, game mutation, GPU allocation or training is involved.
use serde::{Deserialize, Serialize};
use std::{collections::HashSet, fs, time::Instant};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    format: u32,
    cases: Vec<Case>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Case {
    private_cards: [u8; 4],
    sampled_boards: Vec<[u8; 5]>,
}

#[derive(Serialize)]
struct ResultRow {
    private_cards: [u8; 4],
    exact_boards: u64,
    wins: u64,
    ties: u64,
    losses: u64,
    equity: f64,
    exact_seconds: f64,
    sampled_scores: Vec<u8>, // Twice BB's share: 0=loss, 1=tie, 2=win.
    sample_seconds: f64,
}

fn score(hole: &[u8; 4], board: &[u8; 5]) -> u8 {
    let mut a = [0u8; 7];
    let mut b = [0u8; 7];
    a[..2].copy_from_slice(&hole[..2]);
    b[..2].copy_from_slice(&hole[2..]);
    a[2..].copy_from_slice(board);
    b[2..].copy_from_slice(board);
    let x = solver::evaluator::evaluate7(&a);
    let y = solver::evaluator::evaluate7(&b);
    if x > y { 2 } else if x == y { 1 } else { 0 }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    assert_eq!(args.len(), 2);
    assert!(!std::path::Path::new(&args[1]).exists());
    let input: Input = serde_json::from_slice(&fs::read(&args[0])?)?;
    assert_eq!(input.format, 1);
    assert!(!input.cases.is_empty() && input.cases.len() <= 20);
    let mut results = Vec::new();
    for case in input.cases {
        let hole = case.private_cards;
        assert!(hole.iter().all(|&c| c < 52));
        assert_eq!(hole.iter().collect::<HashSet<_>>().len(), 4);
        assert!(!case.sampled_boards.is_empty() && case.sampled_boards.len() <= 32768);
        let deck: Vec<_> = (0u8..52).filter(|c| !hole.contains(c)).collect();
        assert_eq!(deck.len(), 48);
        let started = Instant::now();
        let mut counts = [0u64; 3];
        // Each unordered five-card board appears exactly once. Preflop all-in
        // payoffs are independent of the order in which its five cards arrive.
        for a in 0..44 {
            for b in a+1..45 {
                for c in b+1..46 {
                    for d in c+1..47 {
                        for e in d+1..48 {
                            let board = [deck[a], deck[b], deck[c], deck[d], deck[e]];
                            counts[score(&hole, &board) as usize] += 1;
                        }
                    }
                }
            }
        }
        let exact_seconds = started.elapsed().as_secs_f64();
        let exact_boards: u64 = counts.iter().sum();
        assert_eq!(exact_boards, 1_712_304);
        let started = Instant::now();
        let mut sampled_scores = Vec::new();
        for board in &case.sampled_boards {
            assert!(board.iter().all(|c| deck.contains(c)));
            assert_eq!(board.iter().collect::<HashSet<_>>().len(), 5);
            sampled_scores.push(score(&hole, board));
        }
        results.push(ResultRow {
            private_cards: hole,
            exact_boards,
            wins: counts[2], ties: counts[1], losses: counts[0],
            equity: (counts[2] as f64 + 0.5 * counts[1] as f64) / exact_boards as f64,
            exact_seconds,
            sampled_scores,
            sample_seconds: started.elapsed().as_secs_f64(),
        });
    }
    fs::write(&args[1], serde_json::to_vec(&results)?)?;
    Ok(())
}
