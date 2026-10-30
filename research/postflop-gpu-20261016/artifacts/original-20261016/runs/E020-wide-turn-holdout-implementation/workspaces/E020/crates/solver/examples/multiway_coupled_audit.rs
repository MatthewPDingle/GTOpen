//! Offline audit of board-correlated categorical equity. Never accesses the server.
use rayon::prelude::*;
use serde_json::{json, Value};
use solver::evaluator::evaluate7;
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
}
fn share(rank: u32, ranks: &[Vec<u32>], weights: &[Vec<f64>]) -> f64 {
    let mut poly = [0.0; 4];
    poly[0] = 1.0;
    for (p, w) in weights.iter().enumerate() {
        let (mut less, mut equal, mut total) = (0.0, 0.0, 0.0);
        for h in 0..169 {
            if ranks[h].is_empty() {
                continue;
            }
            total += w[h];
            let one = w[h] / ranks[h].len() as f64;
            for &r in &ranks[h] {
                if r < rank {
                    less += one
                } else if r == rank {
                    equal += one
                }
            }
        }
        for k in (0..=p + 1).rev() {
            poly[k] = (poly[k] * less + if k > 0 { poly[k - 1] * equal } else { 0.0 }) / total;
        }
    }
    poly.iter()
        .enumerate()
        .map(|(i, x)| x / (i + 1) as f64)
        .sum()
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
    assert_eq!(weights.len(), 3);
    let mut combos = vec![vec![]; 169];
    for a in 0..52u8 {
        for b in a + 1..52u8 {
            combos[class_index(a / 4, b / 4, a % 4 == b % 4)].push([a, b]);
        }
    }
    let hands = [
        ("KQo", class_index(11, 10, false), 0.2079848333),
        ("AQo", class_index(12, 10, false), 0.2042160833),
        ("KQs", class_index(11, 10, true), 0.2408018333),
        ("76s", class_index(5, 4, true), 0.1999143333),
        ("AA", class_index(12, 12, false), 0.5882696667),
    ];
    // Nested prefixes quantify sensitivity to board particle count and random seed.
    let rows:Vec<_>=(0..16usize).into_par_iter().map(|run|{
        let mode=run/8;let seed=run%8;let mut rng=Rng(90210+seed as u64);let mut sums=[0.0;5];let mut denoms=[0.0;5];let mut out=vec![];
        for n in 1..=4096 {
            let mut deck:Vec<u8>=(0..52).collect();for k in (1..52).rev(){let j=rng.next() as usize%(k+1);deck.swap(k,j);}
            let mut ranks=vec![vec![];169];
            for h in 0..169 {let count=if mode==0 {1} else {4};for _ in 0..count {let c=combos[h][rng.next()as usize%combos[h].len()];let board:Vec<_>=deck.iter().copied().filter(|&x|x!=c[0]&&x!=c[1]).take(5).collect();ranks[h].push(evaluate7(&[c[0],c[1],board[0],board[1],board[2],board[3],board[4]]));}}
            for(i,(_,h,_))in hands.iter().enumerate(){denoms[i]+=1.;sums[i]+=ranks[*h].iter().map(|&r|share(r,&ranks,&weights)).sum::<f64>()/ranks[*h].len()as f64;}            if [32,64,128,256,512,1024,2048,4096].contains(&n){out.push(json!({"mode":(["one_combo","four_combos","all_combos","hero_excluded"][mode]),"seed":seed,"boards":n,"results":hands.iter().enumerate().map(|(i,(label,_,reference))|json!({"hand":label,"equity":sums[i]/denoms[i],"reference":reference,"error":sums[i]/denoms[i]-reference})).collect::<Vec<_>>()}));}
        }out
    }).flatten().collect();
    println!("{}",serde_json::to_string_pretty(&json!({"scope":"Common random deck; each class gets uniformly sampled hole combo and first5deckcards excluding own holes. Different classes can see different boards. One/four ranks perclass, coherent fixed latent ordering with independent class chance and no mass reweighting.","runs":rows})).unwrap());
}
