//! CPU-only research audit. Does not modify games, checkpoints, or model defaults.
//! Usage: preflop_ensemble_audit <repository containing historical audit JSONs>
#[path = "support/continuation_ensemble.rs"]
mod continuation_ensemble;
use continuation_ensemble::{exchange_refinement, representative_indices, Ensemble};
use serde_json::{json, Value};
use solver::preflop::equity::{class_combos, class_label, class_parts, NUM_CLASSES};
use solver::preflop::multiway::{CoupledDeck, SAMPLES};
use std::path::Path;

struct Rng(u64);
impl Rng {
    fn unit(&mut self) -> f64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
        ((z ^ (z >> 31)) >> 11) as f64 / (1u64 << 53) as f64
    }
}

fn normalized(per_combo: Vec<f64>) -> Vec<f32> {
    let mass: f64 = per_combo
        .iter()
        .enumerate()
        .map(|(h, v)| v * class_combos(h) as f64)
        .sum();
    assert!(mass > 0.0);
    per_combo
        .iter()
        .enumerate()
        .map(|(h, v)| (v * class_combos(h) as f64 / mass) as f32)
        .collect()
}

/// Synthetic training distribution, not history or a poker optimality claim.
/// Smooth strength thresholds, pairs, suits, gaps and independent seat mixtures.
fn synthetic_contexts(seed: u64, repeats: usize) -> Vec<Vec<Vec<f32>>> {
    let mut rng = Rng(seed);
    let mut out = Vec::new();
    for opponents in 1..=8 {
        for _ in 0..repeats {
            out.push(
                (0..opponents)
                    .map(|_| {
                        let threshold = 0.2 + 0.8 * rng.unit();
                        let temperature = 0.035 + 0.2 * rng.unit();
                        let pair_bonus = 0.1 + 0.6 * rng.unit();
                        let suit_bonus = 0.04 + 0.2 * rng.unit();
                        let gap_penalty = 0.02 + 0.18 * rng.unit();
                        let floor = if rng.unit() < 0.5 {
                            0.0
                        } else {
                            0.05 + 0.15 * rng.unit()
                        };
                        normalized(
                            (0..NUM_CLASSES)
                                .map(|h| {
                                    let (a, b, suited) = class_parts(h);
                                    let score = (a as f64 * 0.65 + b as f64 * 0.35) / 12.0
                                        + if a == b { pair_bonus } else { 0.0 }
                                        + if suited { suit_bonus } else { 0.0 }
                                        - gap_penalty * (a - b) as f64 / 12.0;
                                    floor
                                        + (1.0 - floor)
                                            / (1.0 + ((threshold - score) / temperature).exp())
                                })
                                .collect(),
                        )
                    })
                    .collect(),
            );
        }
    }
    out
}

fn errors(actual: &[f64; NUM_CLASSES], reference: &[f64; NUM_CLASSES]) -> Value {
    let mut abs: Vec<_> = (0..NUM_CLASSES)
        .map(|h| (actual[h] - reference[h]).abs())
        .collect();
    abs.sort_by(f64::total_cmp);
    let worst = (0..NUM_CLASSES)
        .max_by(|&a, &b| {
            (actual[a] - reference[a])
                .abs()
                .total_cmp(&(actual[b] - reference[b]).abs())
        })
        .unwrap();
    let weighted_mse: f64 = (0..NUM_CLASSES)
        .map(|h| (actual[h] - reference[h]).powi(2) * class_combos(h) as f64 / 1326.0)
        .sum();
    json!({"mean_absolute_pp":abs.iter().sum::<f64>() / NUM_CLASSES as f64 * 100.0,
        "p95_absolute_pp":abs[(NUM_CLASSES * 95 / 100).min(NUM_CLASSES - 1)] * 100.0,
        "max_absolute_pp":abs[NUM_CLASSES - 1] * 100.0,
        "combo_weighted_rmse_pp":weighted_mse.sqrt() * 100.0,
        "worst_hand":class_label(worst), "worst_signed_pp":(actual[worst] - reference[worst]) * 100.0})
}

fn historical_context(name: &str) -> Vec<Vec<f32>> {
    let (count, family) = match name {
        "uniform_3way" => (2, "uniform"),
        "uniform_6way" => (5, "uniform"),
        "uniform_9way" => (8, "uniform"),
        "tight_3way" => (2, "tight"),
        "tight_4way" => (3, "tight"),
        "pairs_4way" => (3, "pairs"),
        "premium_4way" => (3, "premium"),
        _ => panic!("unknown historical case {name}"),
    };
    let d = normalized(
        (0..NUM_CLASSES)
            .map(|h| {
                let (a, b, suited) = class_parts(h);
                let included = match family {
                    "uniform" => true,
                    "tight" => {
                        (a == b && a >= 5) || (a >= 11 && b >= 10) || (suited && a == 12 && b >= 8)
                    }
                    "pairs" => a == b && a <= 9,
                    "premium" => (a == b && a >= 10) || (a == 12 && b == 11),
                    _ => unreachable!(),
                };
                if included {
                    1.0
                } else {
                    0.0
                }
            })
            .collect(),
    );
    vec![d; count]
}

fn hand_index(label: &str) -> usize {
    (0..NUM_CLASSES).find(|&h| class_label(h) == label).unwrap()
}

fn physical_rows(
    actual: &[f64; NUM_CLASSES],
    full: &[f64; NUM_CLASSES],
    rows: &[Value],
) -> Vec<Value> {
    rows.iter()
        .map(|row| {
            let hand = row["hand"].as_str().unwrap();
            let h = hand_index(hand);
            let physical = row["reference"].as_f64().unwrap();
            json!({"hand":hand,"candidate":actual[h],"coupled_1024":full[h],
            "physical_mc":physical,"candidate_minus_coupled_pp":(actual[h]-full[h])*100.0,
            "candidate_minus_physical_pp":(actual[h]-physical)*100.0,
            "coupled_minus_physical_pp":(full[h]-physical)*100.0,
            "physical_mc_95_half_width":row.get("mc_95_half_width")})
        })
        .collect()
}

fn main() {
    let refine = std::env::args().any(|arg| arg == "--refine32");
    let root = std::env::args()
        .nth(1)
        .expect("repository root containing historical audit data");
    let audit = Path::new(&root).join("research/multiway-equity-audit");
    let old: Value =
        serde_json::from_slice(&std::fs::read(audit.join("coupled-holdout.json")).unwrap())
            .unwrap();
    let original: Value =
        serde_json::from_slice(&std::fs::read(audit.join("coupled-audit.json")).unwrap()).unwrap();
    let node: Value =
        serde_json::from_slice(&std::fs::read(audit.join("node.json")).unwrap()).unwrap();
    let train = synthetic_contexts(0x435046545241494e, 4);
    let development = synthetic_contexts(0x4350464445563031, 2);
    let table = CoupledDeck::shared();
    eprintln!(
        "Selecting fixed equal-weight representatives from {} training contexts...",
        train.len()
    );
    let chosen = representative_indices(&table, &train, 64);
    let mut models = Vec::new();
    for count in [16, 32, 64] {
        models.push((
            format!("coupled_subset_stratified_v1_{count}"),
            Ensemble::stratified(count),
        ));
        models.push((
            format!("coupled_subset_herding_v1_{count}"),
            Ensemble::new(chosen[..count].to_vec()).unwrap(),
        ));
    }
    let refinement = if refine {
        eprintln!("Training-only coordinate exchange:32 particles, maximum8 sweeps...");
        let (indices, trace) = exchange_refinement(&table, &train, &chosen[..32], 8);
        models.push((
            "coupled_subset_exchange_v2_32".into(),
            Ensemble::new(indices).unwrap(),
        ));
        json!({"algorithm":"coordinate exchange without replacement","max_sweeps":8,
            "training_only":true,"uniform_weights":true,"initial_model":"coupled_subset_herding_v1_32","trace":trace})
    } else {
        Value::Null
    };
    let mut context_rows = Vec::new();
    for (split, contexts) in [
        ("training", &train),
        ("development_seed_holdout", &development),
    ] {
        for (i, opponents) in contexts.iter().enumerate() {
            let full = table.equities(opponents);
            let rows: Vec<_> = models.iter().map(|(id, m)| json!({"model":id,"errors_vs_coupled_1024":errors(&m.equities(&table, opponents), &full)})).collect();
            context_rows
                .push(json!({"split":split,"context":i,"opponents":opponents.len(),"models":rows}));
        }
    }
    let mut stress_rows = Vec::new();
    for case in old["cases"].as_array().unwrap() {
        let name = case["case"].as_str().unwrap();
        let opponents = historical_context(name);
        let full = table.equities(&opponents);
        let rows: Vec<_> = models.iter().map(|(id, m)| {
            let eq = m.equities(&table, &opponents);
            json!({"model":id,"errors_vs_coupled_1024":errors(&eq,&full),"physical_comparisons":physical_rows(&eq,&full,case["results"].as_array().unwrap())})
        }).collect();
        stress_rows.push(json!({"case":name,"split":"previously_seen_regression","models":rows}));
    }
    let hero = node["actor"].as_u64().unwrap() as usize;
    let opponents: Vec<_> = node["reaches_all"]
        .as_array()
        .unwrap()
        .iter()
        .enumerate()
        .filter(|(p, _)| *p != hero && node["live"][*p].as_bool().unwrap())
        .map(|(_, w)| {
            normalized(
                w.as_array()
                    .unwrap()
                    .iter()
                    .map(|v| v.as_f64().unwrap())
                    .collect(),
            )
        })
        .collect();
    let full = table.equities(&opponents);
    let bb_rows: Vec<_> = models.iter().map(|(id, m)| {
        let eq = m.equities(&table, &opponents);
        json!({"model":id,"errors_vs_coupled_1024":errors(&eq,&full),"physical_comparisons":physical_rows(&eq,&full,original["runs"][0]["results"].as_array().unwrap())})
    }).collect();
    println!("{}", serde_json::to_string_pretty(&json!({
        "schema":"preflop_ensemble_audit_v1", "source_model":"coupled_deck_v1", "source_particles":SAMPLES,
        "candidate_status":"research approximation; not enabled in games", "train_seed":"435046545241494e", "development_seed":"4350464445563031",
        "training_contexts":train.len(), "development_contexts":development.len(),
        "refinement":refinement,
        "objective":"Greedy uniform-mean fit to1024 particle conditional equity, all169 hands weighted by combinatorial mass; no physical labels or blind holdout distributions used.",
        "limitations":["Physical MC compares different compatible-card chance model;1024 source is not ground truth.","Development holdout is only a new seed from the same synthetic generator. Independent registered holdouts are evaluated separately.","Equity error and particle reduction are not solver decision quality or end-to-end speedup.","Common fixed particle subset across all seats/terminals required for pot conservation; no own-reach pruning."],
        "models":models.iter().map(|(id,m)|json!({"id":id,"indices":m.indices,"particles":m.indices.len(),"weight":1.0/m.indices.len() as f64})).collect::<Vec<_>>(),
        "contexts":context_rows,"historical_stress":stress_rows,
        "original_bb_regression":{"case":"original_BB_vs_minraise_two_callers","split":"previously_seen_regression","models":bb_rows}
    })).unwrap());
}
