//! Offline shared-board equity with pairwise collision corrections.
use rayon::prelude::*;
use serde_json::{json, Value};
use solver::evaluator::evaluate7;
use solver::preflop::equity::class_index;
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
fn corrected(m: [f64; 3], c: [f64; 3]) -> f64 {
    let mut z = m.iter().product::<f64>();
    for (k, (i, j)) in [(0, 1), (0, 2), (1, 2)].iter().enumerate() {
        if m[*i] * m[*j] <= 0. {
            return 0.;
        }
        z *= (1. - c[k] / (m[*i] * m[*j])).max(0.);
    }
    z
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
                .map(|h| node["reaches_all"][p][h].as_f64().unwrap())
                .collect()
        })
        .collect();
    let mut combos = vec![];
    let mut classes = vec![vec![]; 169];
    for a in 0..52u8 {
        for b in a + 1..52u8 {
            let h = class_index(a / 4, b / 4, a % 4 == b % 4);
            classes[h].push(combos.len());
            combos.push((a, b, h));
        }
    }
    let hands = [
        ("KQo", class_index(11, 10, false), 0.2079848333),
        ("AQo", class_index(12, 10, false), 0.2042160833),
        ("KQs", class_index(11, 10, true), 0.2408018333),
        ("76s", class_index(5, 4, true), 0.1999143333),
        ("AA", class_index(12, 12, false), 0.5882696667),
    ];
    let runs:Vec<_>=(0..8).into_par_iter().map(|seed|{let mut rng=Rng(90210+seed);let mut sums=[0.;5];let mut denoms=[0.;5];let mut out=vec![];
 for n in 1..=4096{let mut board=[0;5];let mut mask=0u64;for c in &mut board{loop{let x=(rng.next()%52)as u8;if mask&(1<<x)==0{*c=x;mask|=1<<x;break;}}}
 let mut ranks=vec![0;1326];for(k,&(a,b,_))in combos.iter().enumerate(){if mask&((1<<a)|(1<<b))==0{ranks[k]=evaluate7(&[a,b,board[0],board[1],board[2],board[3],board[4]]);}}
 for(i,(_,h,_))in hands.iter().enumerate(){for &hi in &classes[*h]{let(a,b,_)=combos[hi];if mask&((1<<a)|(1<<b))!=0{continue}let hm=mask|(1<<a)|(1<<b);let rank=ranks[hi];let mut mass=[[0.;3];3];let mut cards=[[[0.;52];3];3];let mut same=[[0.;3];3];
 for(k,&(x,y,c))in combos.iter().enumerate(){if hm&((1<<x)|(1<<y))!=0{continue}let cat=if ranks[k]<rank{0}else if ranks[k]==rank{1}else{2};for p in 0..3{mass[cat][p]+=weights[p][c];cards[cat][p][x as usize]+=weights[p][c];cards[cat][p][y as usize]+=weights[p][c];}for(j,(p,q))in[(0,1),(0,2),(1,2)].iter().enumerate(){same[cat][j]+=weights[*p][c]*weights[*q][c];}}
 let mut full=[0.;3];let mut fullc=[0.;3];let mut coefs=[[0.;3];3];for p in 0..3{full[p]=mass.iter().map(|m|m[p]).sum();}
 for(j,(p,q))in[(0,1),(0,2),(1,2)].iter().enumerate(){for c in 0..52{let cp:f64=(0..3).map(|k|cards[k][*p][c]).sum();let cq:f64=(0..3).map(|k|cards[k][*q][c]).sum();fullc[j]+=cp*cq;coefs[0][j]+=cards[0][*p][c]*cards[0][*q][c];coefs[1][j]+=cards[0][*p][c]*cards[1][*q][c]+cards[1][*p][c]*cards[0][*q][c];coefs[2][j]+=cards[1][*p][c]*cards[1][*q][c];}fullc[j]-=same.iter().map(|s|s[j]).sum::<f64>();coefs[0][j]-=same[0][j];coefs[2][j]-=same[1][j];}
 let denom=corrected(full,fullc);let mut num=0.;for(t,w)in[(0.069431844202974,0.173927422568727),(0.330009478207572,0.326072577431273),(0.669990521792428,0.326072577431273),(0.930568155797026,0.173927422568727)]{let mut m=[0.;3];let mut c=[0.;3];for p in 0..3{m[p]=mass[0][p]+t*mass[1][p];c[p]=coefs[0][p]+t*coefs[1][p]+t*t*coefs[2][p];}num+=w*corrected(m,c);}sums[i]+=num/classes[*h].len()as f64;denoms[i]+=denom/classes[*h].len()as f64;
 }}
 if[32,64,128,256,512,1024,2048,4096].contains(&n){out.push(json!({"seed":seed,"boards":n,"results":hands.iter().enumerate().map(|(i,(label,_,reference))|json!({"hand":label,"equity":sums[i]/denoms[i],"reference":reference,"error":sums[i]/denoms[i]-reference})).collect::<Vec<_>>()}));}
 }out}).flatten().collect();
    println!("{}",serde_json::to_string_pretty(&json!({"method":"Exact hero-card removal, all compatible combos per shared board, joint opportunity weighting, product of exact pairwise opponent collision-compatibility factors; 4-point Gauss quadrature for split ties. Residual higher-order collision correlations remain approximate.","runs":runs})).unwrap());
}
