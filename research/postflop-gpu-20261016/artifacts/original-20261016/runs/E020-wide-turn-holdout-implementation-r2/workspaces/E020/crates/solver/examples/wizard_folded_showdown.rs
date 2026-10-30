//! Physical eight-player deals and boards under frozen observed-action policies.
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
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let folder = std::path::Path::new(args.get(1).expect("research folder"));
    let dest = folder.join("folded-showdown-batches.json");
    assert!(!dest.exists(), "preserve completed evidence");
    let read = |name: &str| -> Value { serde_json::from_slice(&std::fs::read(folder.join(name)).unwrap()).unwrap() };
    let history = read("fold-history.json");
    let audit = read("premium-branches.json");
    let mut policies = [[1.;169];8];
    for a in history["actions"].as_array().unwrap() {
        let seat = a["actor"].as_u64().unwrap() as usize;
        for (i,v) in a["probabilities"].as_array().unwrap().iter().enumerate() { policies[seat][i] = v.as_f64().unwrap(); }
    }
    let reply = audit["nodes"].as_array().unwrap().iter().find(|n|n["path"] == json!([1,2,0,0,0,0,0,0,3])).unwrap();
    let mut call = [0.;169];
    for i in 0..169 { call[i] = reply["view"]["strategy"][169+i].as_f64().unwrap(); }
    let seats = [0,2,3,4,5,6,7];
    let available: Vec<u8> = (0..52).filter(|c|*c!=48 && *c!=49).collect();
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global().unwrap();
    let started = std::time::Instant::now();
    let batches: Vec<_> = (0..40).into_par_iter().map(|batch| {
        let mut rng = Rng(1909192600+batch);
        let mut sums = [[0.;5];2];
        for _ in 0..800_000 {
            let mut deck = [0u8;50]; deck.copy_from_slice(&available);
            for i in 0..19 { let j=i+rng.below((50-i) as u64);deck.swap(i,j); }
            let mut w = [1.;2];let mut lj=0;
            for (k,&seat) in seats.iter().enumerate() {
                let (a,b)=(deck[2*k],deck[2*k+1]);
                let c=class_index(a/4,b/4,a%4==b%4);
                if seat==2 { lj=c;w[0]*=policies[seat][c]; }
                w[1]*=policies[seat][c];
            }
            let hero=[48,49,deck[14],deck[15],deck[16],deck[17],deck[18]];
            let opp=[deck[2],deck[3],deck[14],deck[15],deck[16],deck[17],deck[18]];
            let (a,b)=(evaluate7(&hero),evaluate7(&opp));
            let win=if a>b {1.} else if a==b {0.5} else {0.};
            let v=(1.-call[lj])*27.5+call[lj]*(397.5*win-194.);
            for mode in 0..2 {
                sums[mode][0]+=w[mode];sums[mode][1]+=w[mode]*w[mode];
                sums[mode][2]+=w[mode]*call[lj];sums[mode][3]+=w[mode]*call[lj]*win;
                sums[mode][4]+=w[mode]*v;
            }
        }
        sums
    }).collect();
    let result=json!({"draws":32_000_000,"batch_draws":800_000,"batches":batches,
        "columns":["likelihood","likelihood_squared","call_mass","called_win_mass","jam_value_mass"],
        "modes":["two_live_hands","including_six_folds"],"hero":[48,49],"seeds":"1909192600 + batch index",
        "elapsed_seconds":started.elapsed().as_secs_f64(),
        "note":"Physical hole cards and board, fixed history/response policies. No equity cache, no policy adaptation."});
    std::fs::write(dest,serde_json::to_vec_pretty(&result).unwrap()).unwrap();
}
