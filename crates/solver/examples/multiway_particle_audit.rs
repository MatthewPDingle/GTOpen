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
    let rows:Vec<_>=(0..32usize).into_par_iter().map(|run|{
        let mode=run/8;let seed=run%8;let mut rng=Rng(90210+seed as u64);let mut sums=[0.0;5];let mut denoms=[0.0;5];let mut out=vec![];
        for n in 1..=4096 {
            let mut board=[0u8;5];let mut mask=0u64;
            for c in &mut board {loop{let x=(rng.next()%52) as u8;if mask&(1<<x)==0 {*c=x;mask|=1<<x;break;}}}
            let mut ranks=vec![vec![];169];
            let mut adjusted=weights.clone();
            for h in 0..169 {
                let valid:Vec<_>=combos[h].iter().filter(|c|mask&((1<<c[0])|(1<<c[1]))==0).collect();
                for p in 0..3 {adjusted[p][h]*=valid.len() as f64/combos[h].len() as f64;}
                if valid.is_empty(){continue}
                if mode<2 {let count=if mode==0 {1} else {4};for _ in 0..count {let c=valid[rng.next() as usize%valid.len()];ranks[h].push(evaluate7(&[c[0],c[1],board[0],board[1],board[2],board[3],board[4]]));}}
                else {for c in valid {ranks[h].push(evaluate7(&[c[0],c[1],board[0],board[1],board[2],board[3],board[4]]));}}
            }
            if mode==3 {
                for (i,(_,h,_)) in hands.iter().enumerate() {
                    let hero_valid:Vec<_>=combos[*h].iter().filter(|c|mask&((1<<c[0])|(1<<c[1]))==0).collect();
                    for (hi,hero) in hero_valid.iter().enumerate() {
                        let hm=(1u64<<hero[0])|(1u64<<hero[1]);let mut hr=vec![vec![];169]; let mut hw=weights.clone();
                        for c in 0..169 {
                            let valid:Vec<_>=combos[c].iter().filter(|a|mask&((1<<a[0])|(1<<a[1]))==0).collect();
                            for (ci,hole) in valid.iter().enumerate() {if hm&((1<<hole[0])|(1<<hole[1]))==0 {hr[c].push(ranks[c][ci]);}}
                            for p in 0..3 {hw[p][c]*=hr[c].len() as f64/combos[c].len() as f64;}
                        }
                        let importance=(0..3).map(|p|hw[p].iter().sum::<f64>()/weights[p].iter().sum::<f64>()).product::<f64>()/combos[*h].len() as f64;
                        denoms[i]+=importance;sums[i]+=importance*share(ranks[*h][hi],&hr,&hw);
                    }
                }
            } else {
            let board_mass:f64=(0..3).map(|p|adjusted[p].iter().sum::<f64>()/weights[p].iter().sum::<f64>()).product(); for (i,(_,h,_)) in hands.iter().enumerate(){if !ranks[*h].is_empty(){let valid=combos[*h].iter().filter(|c|mask&((1<<c[0])|(1<<c[1]))==0).count(); let importance=board_mass*valid as f64/combos[*h].len() as f64; denoms[i]+=importance; sums[i]+=importance*ranks[*h].iter().map(|&r|share(r,&ranks,&adjusted)).sum::<f64>()/ranks[*h].len() as f64;}}
            }            if [32,64,128,256,512,1024,2048,4096].contains(&n){out.push(json!({"mode":(["one_combo","four_combos","all_combos","hero_excluded"][mode]),"seed":seed,"boards":n,"results":hands.iter().enumerate().map(|(i,(label,_,reference))|json!({"hand":label,"equity":sums[i]/denoms[i],"reference":reference,"error":sums[i]/denoms[i]-reference})).collect::<Vec<_>>()}));}
        }out
    }).flatten().collect();
    println!("{}",serde_json::to_string_pretty(&json!({"scope":"Board-conditional categorical independent opponent draws; board card removal weighted, cross-hole-card collisions omitted. Same class rank samples shared by hero and opponents.","runs":rows})).unwrap());
}
