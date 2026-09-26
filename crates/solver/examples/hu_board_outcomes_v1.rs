//! Research-only showdown scores for supplied physical deals. No game mutation.
use serde::Deserialize;
use serde_json::json;
use std::{collections::HashSet, fs, path::Path};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    format: u32,
    deals: Vec<[u8; 9]>,
}

fn valid(deal: &[u8; 9]) -> bool {
    deal.iter().all(|c| *c < 52) && deal.iter().collect::<HashSet<_>>().len() == 9
}

fn score(deal: &[u8; 9]) -> u8 {
    assert!(valid(deal), "Nine distinct cards in 0..51 required");
    let ranks: [u32; 2] = std::array::from_fn(|player| {
        let mut cards = [0u8; 7];
        cards[..2].copy_from_slice(&deal[player * 2..player * 2 + 2]);
        cards[2..].copy_from_slice(&deal[4..]);
        solver::evaluator::evaluate7(&cards)
    });
    match ranks[0].cmp(&ranks[1]) {
        std::cmp::Ordering::Less => 0,
        std::cmp::Ordering::Equal => 1,
        std::cmp::Ordering::Greater => 2,
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    assert_eq!(args.len(), 2);
    assert!(!Path::new(&args[1]).exists());
    let input_source = fs::read_to_string(&args[0])?;
    let input: Input = serde_json::from_str(&input_source)?;
    assert_eq!(input.format, 1);
    assert!(!input.deals.is_empty() && input.deals.len() <= 65_536);
    assert!(input.deals.iter().all(valid));
    let scores: Vec<u8> = input.deals.iter().map(score).collect();
    fs::write(&args[1], serde_json::to_vec(&json!({
        "format": 1, "input_source": input_source,
        "twice_bb_share": scores,
        "scope": "Showdown only on supplied cards; no strategy or expected-value estimate"
    }))?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pocket_aces_beat_kings_and_swap_complements() {
        let deal = [48, 49, 44, 45, 0, 5, 22, 31, 40];
        assert_eq!(score(&deal), 2);
        assert_eq!(score(&[44, 45, 48, 49, 0, 5, 22, 31, 40]), 0);
    }

    #[test]
    fn board_royal_is_tied() {
        assert_eq!(score(&[0, 5, 10, 15, 32, 36, 40, 44, 48]), 1);
    }

    #[test]
    fn wheel_beats_an_ordinary_pair() {
        assert_eq!(score(&[48, 1, 44, 45, 6, 11, 12, 29, 38]), 2);
    }

    #[test]
    fn invalid_cards_are_refused() {
        assert!(!valid(&[0, 1, 2, 3, 4, 5, 6, 7, 7]));
        assert!(!valid(&[0, 1, 2, 3, 4, 5, 6, 7, 52]));
    }
}
