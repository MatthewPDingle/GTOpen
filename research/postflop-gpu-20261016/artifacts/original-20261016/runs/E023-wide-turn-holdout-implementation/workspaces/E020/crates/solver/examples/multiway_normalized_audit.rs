//! Offline test of coherent normalized pairwise-product tuple payoffs.
use serde_json::{json, Value};
use solver::preflop::equity::{class_combos, class_index};
struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
        z ^ (z >> 31)
    }
    fn unit(&mut self) -> f64 {
        (self.next() >> 11) as f64 / (1u64 << 53) as f64
    }
}
fn main() {
    let node: Value = serde_json::from_str(
        &std::fs::read_to_string("research/multiway-equity-audit/node.json").unwrap(),
    )
    .unwrap();
    let actor = node["actor"].as_u64().unwrap() as usize;
    let weights: Vec<Vec<f64>> = node["live"]
        .as_array()
        .unwrap()
        .iter()
        .enumerate()
        .filter(|(p, l)| *p != actor && l.as_bool().unwrap())
        .map(|(p, _)| {
            (0..169)
                .map(|h| node["reaches_all"][p][h].as_f64().unwrap() * class_combos(h) as f64)
                .collect()
        })
        .collect();
    let cdfs: Vec<Vec<f64>> = weights
        .iter()
        .map(|w| {
            let total: f64 = w.iter().sum();
            let mut sum = 0.;
            w.iter()
                .map(|x| {
                    sum += x / total;
                    sum
                })
                .collect()
        })
        .collect();
    let bytes = std::fs::read("cache/preflop_eq169.bin").unwrap();
    let table: Vec<f64> = bytes[4..]
        .chunks_exact(4)
        .map(|b| f32::from_le_bytes(b.try_into().unwrap()) as f64)
        .collect();
    let hands = [
        ("KQo", class_index(11, 10, false), 0.2079848333),
        ("AQo", class_index(12, 10, false), 0.2042160833),
        ("KQs", class_index(11, 10, true), 0.2408018333),
        ("76s", class_index(5, 4, true), 0.1999143333),
        ("AA", class_index(12, 12, false), 0.5882696667),
    ];
    let mut out = vec![];
    for (label, hero, reference) in hands {
        let mut rng = Rng(72561 + hero as u64);
        let mut sums = [0.; 5];
        let mut legacy = 0.;
        let n = 1_000_000;
        for _ in 0..n {
            let mut hs = vec![hero];
            for cdf in &cdfs {
                let u = rng.unit();
                hs.push(cdf.partition_point(|&p| p <= u).min(168));
            }
            let mut p = vec![1.; hs.len()];
            for i in 0..hs.len() {
                for j in 0..hs.len() {
                    if i != j {
                        p[i] *= table[hs[i] * 169 + hs[j]];
                    }
                }
            }
            legacy += p[0];
            for (k, exponent) in [0.5, 0.75, 1., 1.25, 1.5].iter().enumerate() {
                let powered: Vec<f64> = p.iter().map(|v| v.powf(*exponent)).collect();
                sums[k] += powered[0] / powered.iter().sum::<f64>();
            }
        }
        out.push(json!({"hand":label,"reference":reference,"product":legacy/n as f64,"normalized":sums.iter().zip([0.5,0.75,1.,1.25,1.5]).map(|(s,e)|json!({"exponent":e,"equity":s/n as f64,"error":s/n as f64-reference})).collect::<Vec<_>>()}));
    }
    println!("{}",serde_json::to_string_pretty(&json!({"samples_per_hand":1000000,"method":"Independent class tuples from exact arriving class masses. For each tuple each player gets the product of pairwise equities normalized by the sum of all players products. Exponents are unvalidated sensitivity variants.","results":out})).unwrap());
}
