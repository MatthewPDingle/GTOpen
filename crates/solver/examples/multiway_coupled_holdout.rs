//! Offline out-of-fixture tests for coherent deck-coupled class ranks.
use rayon::prelude::*;
use serde_json::json;
use solver::evaluator::evaluate7;
use solver::preflop::equity::{class_combos, class_index, class_parts};
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
fn share(rank: u32, ranks: &[u32], weights: &[Vec<f64>]) -> f64 {
    let mut poly = [0.; 9];
    poly[0] = 1.;
    for (p, w) in weights.iter().enumerate() {
        let (mut l, mut e) = (0., 0.);
        for h in 0..169 {
            if ranks[h] < rank {
                l += w[h]
            } else if ranks[h] == rank {
                e += w[h]
            }
        }
        for k in (0..=p + 1).rev() {
            poly[k] = poly[k] * l + if k > 0 { poly[k - 1] * e } else { 0. };
        }
    }
    poly.iter()
        .enumerate()
        .map(|(i, x)| x / (i + 1) as f64)
        .sum()
}
fn main() {
    let mut combos = vec![vec![]; 169];
    for a in 0..52u8 {
        for b in a + 1..52u8 {
            combos[class_index(a / 4, b / 4, a % 4 == b % 4)].push([a, b]);
        }
    }
    let mut cases = vec![];
    for n in [2, 5, 8] {
        cases.push((format!("uniform_{}way", n + 1), vec![vec![1.; 169]; n]));
    }
    let tight: Vec<_> = (0..169)
        .map(|h| {
            let (a, b, s) = class_parts(h);
            if (a == b && a >= 5) || (a >= 11 && b >= 10) || (s && a == 12 && b >= 8) {
                1.
            } else {
                0.
            }
        })
        .collect();
    cases.push(("tight_3way".into(), vec![tight.clone(); 2]));
    cases.push(("tight_4way".into(), vec![tight; 3]));
    let pairs: Vec<_> = (0..169)
        .map(|h| {
            let (a, b, _) = class_parts(h);
            if a == b && a <= 9 {
                1.
            } else {
                0.
            }
        })
        .collect();
    cases.push(("pairs_4way".into(), vec![pairs; 3]));
    let premium: Vec<_> = (0..169)
        .map(|h| {
            let (a, b, _) = class_parts(h);
            if (a == b && a >= 10) || (a == 12 && b == 11) {
                1.
            } else {
                0.
            }
        })
        .collect();
    cases.push(("premium_4way".into(), vec![premium; 3]));
    let hands = [
        ("KQo", [44u8, 41u8]),
        ("AQo", [48, 41]),
        ("KQs", [44, 40]),
        ("76s", [20, 16]),
        ("AA", [48, 49]),
        ("22", [0, 1]),
    ];
    let seeds = [90210u64, 711281, 711282, 711283, 711284];
    let particles: Vec<Vec<Vec<u32>>> = seeds
        .into_par_iter()
        .map(|seed| {
            let mut rng = Rng(seed);
            (0..4096)
                .map(|_| {
                    let mut deck: Vec<u8> = (0..52).collect();
                    for k in (1..52).rev() {
                        let j = rng.next() as usize % (k + 1);
                        deck.swap(k, j);
                    }
                    combos
                        .iter()
                        .map(|cc| {
                            let c = cc[rng.next() as usize % cc.len()];
                            let b: Vec<_> = deck
                                .iter()
                                .copied()
                                .filter(|&x| x != c[0] && x != c[1])
                                .take(5)
                                .collect();
                            evaluate7(&[c[0], c[1], b[0], b[1], b[2], b[3], b[4]])
                        })
                        .collect()
                })
                .collect()
        })
        .collect();
    let bytes = std::fs::read("cache/preflop_eq169.bin").unwrap();
    let table: Vec<f64> = bytes[4..]
        .chunks_exact(4)
        .map(|b| f32::from_le_bytes(b.try_into().unwrap()) as f64)
        .collect();
    let output:Vec<_>=cases.par_iter().enumerate().map(|(case_idx,(name,percombo))|{
 let weights:Vec<Vec<f64>>=percombo.iter().map(|w|{let total:f64=(0..169).map(|h|w[h]*class_combos(h)as f64).sum();(0..169).map(|h|w[h]*class_combos(h)as f64/total).collect()}).collect();
 let samplers:Vec<Vec<(f64,[u8;2])>>=percombo.iter().map(|w|{let mut sum=0.;let mut c=vec![];for h in 0..169{for &cards in &combos[h]{sum+=w[h];c.push((sum,cards));}}for(a,_)in &mut c{*a/=sum;}c}).collect();
 let mut results=vec![];
 for(label,hero)in hands {let h=class_index(hero[0]/4,hero[1]/4,hero[0]%4==hero[1]%4);let mut rng=Rng(620011+case_idx as u64*200+h as u64);let(mut sum,mut squares,mut accepted)=(0.,0.,0);let trials=100_000;while accepted<trials{let mut mask=(1u64<<hero[0])|(1u64<<hero[1]);let mut hs=vec![hero];let mut collision=false;for sampler in &samplers{let u=rng.unit();let cards=sampler[sampler.partition_point(|(w,_)|*w<=u).min(sampler.len()-1)].1;let bits=(1u64<<cards[0])|(1u64<<cards[1]);if bits&mask!=0{collision=true;break}mask|=bits;hs.push(cards);}if collision{continue}let mut board=[0;5];for c in &mut board{loop{let x=(rng.next()%52)as u8;if mask&(1<<x)==0{*c=x;mask|=1<<x;break}}}let ranks:Vec<_>=hs.iter().map(|c|evaluate7(&[c[0],c[1],board[0],board[1],board[2],board[3],board[4]])).collect();let best=*ranks.iter().max().unwrap();let winners=ranks.iter().filter(|&&r|r==best).count();let eq=if ranks[0]==best{1./winners as f64}else{0.};sum+=eq;squares+=eq*eq;accepted+=1;}
 let reference=sum/trials as f64;let modeled:Vec<_>=particles.iter().enumerate().map(|(seed,ps)|{let mut sum=0.;let mut out=vec![];for(n,ranks)in ps.iter().enumerate(){sum+=share(ranks[h],ranks,&weights);if[1024,4096].contains(&(n+1)){out.push(json!({"seed":seeds[seed],"particles":n+1,"equity":sum/(n+1)as f64,"error":sum/(n+1)as f64-reference}));}}out}).flatten().collect();let legacy=weights.iter().map(|w|(0..169).map(|j|table[h*169+j]*w[j]).sum::<f64>()).product::<f64>();results.push(json!({"hand":label,"reference":reference,"legacy_product":legacy,"legacy_error":legacy-reference,"mc_95_half_width":1.96*((squares/trials as f64-reference*reference)/trials as f64).sqrt(),"coupled":modeled}));}
 json!({"case":name,"opponents":weights.len(),"results":results})}).collect();
    println!("{}",serde_json::to_string_pretty(&json!({"mc_samples_per_hand":100000,"scope":"Out-of-fixture synthetic range tests. Independent class prior deck-coupled ranks versus compatible-card exact-deal Monte Carlo. No future betting or folded-card removal.","cases":output})).unwrap());
}
