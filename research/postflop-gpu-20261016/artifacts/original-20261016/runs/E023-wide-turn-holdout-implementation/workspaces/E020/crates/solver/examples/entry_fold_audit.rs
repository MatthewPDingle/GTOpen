//! Physical entry-conditioned dead-card audit. Does not change production models.
use rayon::prelude::*;
use serde_json::{json, Value};
use solver::{evaluator::evaluate7, preflop::equity::class_index};

struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
        z ^ (z >> 31)
    }
    fn below(&mut self, n: u64) -> usize {
        let limit = u64::MAX - u64::MAX % n;
        loop { let v = self.next(); if v < limit { return (v % n) as usize; } }
    }
    fn unit(&mut self) -> f64 { (self.next() >> 11) as f64 / 9007199254740992. }
}
fn cls(c: [u8; 2]) -> usize { class_index(c[0]/4, c[1]/4, c[0]%4 == c[1]%4) }
struct Sampler { cards: Vec<[u8;2]>, cdf: Vec<f64> }
impl Sampler {
    fn new(policy: &[f64;169]) -> Self {
        let mut cards=Vec::new(); let mut cdf=Vec::new(); let mut sum=0.;
        for a in 0..52 { for b in a+1..52 {
            let w=policy[cls([a,b])];
            if w>0. { sum+=w; cards.push([a,b]); cdf.push(sum); }
        }}
        assert!(sum>0.);
        for x in &mut cdf { *x/=sum; }
        *cdf.last_mut().unwrap()=1.;
        Self {cards,cdf}
    }
    fn draw(&self,rng:&mut Rng)->[u8;2] {
        let u=rng.unit(); self.cards[self.cdf.partition_point(|&v|v<=u)]
    }
}
fn main() {
    let args:Vec<_>=std::env::args().skip(1).collect();
    assert_eq!(args.len(),3,"HISTORY CONFIG OUTPUT");
    assert!(!std::path::Path::new(&args[2]).exists(),"preserve evidence");
    let read=|p:&str|->Value {serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap()};
    let history=read(&args[0]); let config=read(&args[1]);
    let mut policies=[[1.;169];8]; let mut seen=[false;8];
    for a in history["actions"].as_array().unwrap() {
        let seat=a["actor"].as_u64().unwrap() as usize;
        assert!(!seen[seat]); seen[seat]=true;
        assert_eq!(a["probabilities"].as_array().unwrap().len(),169);
        for (i,x) in a["probabilities"].as_array().unwrap().iter().enumerate() {
            policies[seat][i]=x.as_f64().unwrap();
            assert!(policies[seat][i].is_finite() && (0. ..=1.).contains(&policies[seat][i]));
        }
        if seat!=1 && seat!=2 { assert_eq!(a["label"],"Fold"); }
    }
    assert!(seen.iter().all(|x|*x));
    let samplers=[Sampler::new(&policies[1]),Sampler::new(&policies[2])];
    let n_batch=config["batches"].as_u64().unwrap() as usize;
    let root_draws=config["root_draws_per_batch"].as_u64().unwrap();
    let probe_draws=config["probe_draws_per_batch"].as_u64().unwrap();
    let probes=config["probes"].as_array().unwrap();
    let seed=config["seed"].as_u64().unwrap();
    rayon::ThreadPoolBuilder::new().num_threads(2).build_global().unwrap();
    let started=std::time::Instant::now();
    let batches:Vec<_>=(0..(1+probes.len())*n_batch).into_par_iter().map(|job| {
        let kind=job/n_batch; let batch=job%n_batch;
        let mut rng=Rng(seed+kind as u64*1000+batch as u64);
        let fixed=if kind==0 {None} else {
            let c=probes[kind-1]["cards"].as_array().unwrap();
            Some([c[0].as_u64().unwrap() as u8,c[1].as_u64().unwrap() as u8])
        };
        let draws=if kind==0 {root_draws} else {probe_draws};
        let mut sums=[[0.;3];2];
        let mut classes=vec![vec![vec![0.;169];2];2];
        // 13 high ranks, five paired/suit strata, one all-distinct check.
        let mut boards=vec![vec![0.;18];2];
        for _ in 0..draws {
            let (hero,opp)=loop {
                let h=fixed.unwrap_or_else(||samplers[0].draw(&mut rng));
                let o=samplers[1].draw(&mut rng);
                if !h.contains(&o[0]) && !h.contains(&o[1]) {break(h,o)}
            };
            let mut deck=[0u8;48]; let mut n=0;
            for c in 0..52 {if !hero.contains(&c) && !opp.contains(&c) {deck[n]=c;n+=1;}}
            assert_eq!(n,48);
            for i in 0..17 {let j=i+rng.below((48-i) as u64);deck.swap(i,j);}
            let mut weight=1.;
            for (i,seat) in [0,3,4,5,6,7].iter().enumerate() {
                weight*=policies[*seat][cls([deck[i*2],deck[i*2+1]])];
            }
            let board=&deck[12..17];
            let win=if kind>0 {
                let a=evaluate7(&[hero[0],hero[1],board[0],board[1],board[2],board[3],board[4]]);
                let b=evaluate7(&[opp[0],opp[1],board[0],board[1],board[2],board[3],board[4]]);
                if a>b {1.} else if a==b {0.5} else {0.}
            } else {0.};
            let ranks=[board[0]/4,board[1]/4,board[2]/4];
            let suits=[board[0]%4,board[1]%4,board[2]%4];
            let paired=ranks[0]==ranks[1]||ranks[0]==ranks[2]||ranks[1]==ranks[2];
            let ns=if suits[0]==suits[1]&&suits[1]==suits[2] {1} else if suits[0]!=suits[1]&&suits[0]!=suits[2]&&suits[1]!=suits[2] {3} else {2};
            let texture=if paired {ns-2} else {ns+1};
            for (mode,w) in [1.,weight].into_iter().enumerate() {
                sums[mode][0]+=w; sums[mode][1]+=w*w; sums[mode][2]+=w*win;
                if kind==0 {
                    classes[mode][0][cls(hero)]+=w; classes[mode][1][cls(opp)]+=w;
                    boards[mode][*ranks.iter().max().unwrap() as usize]+=w;
                    boards[mode][13+texture]+=w;
                }
            }
        }
        json!({"kind":kind,"batch":batch,"draws":draws,"sums":sums,
            "class_mass":if kind==0 {json!(classes)} else {Value::Null},
            "board_mass":if kind==0 {json!(boards)} else {Value::Null}})
    }).collect();
    let result=json!({"config":config,"batches":batches,"elapsed_seconds":started.elapsed().as_secs_f64(),
        "modes":["entry_only","entry_and_six_folds"],"columns":["weight","weight_squared","win_mass"],
        "note":"Shared physical deals; conditional independent entry proposal with collision rejection. Fold likelihood is applied to six mutually disjoint private hands; boards drawn from their remaining deck. Equity is versus the entering LJ range, not its later jam response."});
    std::fs::write(&args[2],serde_json::to_vec_pretty(&result).unwrap()).unwrap();
    eprintln!("entry-fold audit done in {:.1}s",started.elapsed().as_secs_f64());
}
