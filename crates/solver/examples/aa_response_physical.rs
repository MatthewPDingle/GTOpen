//! Physical TT/AKo response check, with paired AA call-frequency sensitivity.
use rayon::prelude::*;
use serde_json::{json, Value};
use solver::{evaluator::evaluate7, preflop::equity::class_index};

struct Rng(u64);
impl Rng {
    fn next(&mut self)->u64 {
        self.0=self.0.wrapping_add(0x9e3779b97f4a7c15);let mut z=self.0;
        z=(z^(z>>30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z=(z^(z>>27)).wrapping_mul(0x94d049bb133111eb);z^(z>>31)
    }
    fn below(&mut self,n:u64)->usize {
        let limit=u64::MAX-u64::MAX%n;
        loop {let v=self.next();if v<limit {return (v%n) as usize;}}
    }
}

fn main() {
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3,"HISTORY POLICY OUTPUT");
    assert!(!std::path::Path::new(&args[2]).exists(),"preserve evidence");
    let read=|p:&str|->Value {serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap()};
    let history=read(&args[0]);let fitted=read(&args[1]);
    let record=fitted["records"].as_array().unwrap().last().unwrap();assert_eq!(record["iteration"],50000);
    let mut policies=[[1.;169];8];
    for action in history["actions"].as_array().unwrap() {
        let seat=action["actor"].as_u64().unwrap() as usize;
        for (i,v) in action["probabilities"].as_array().unwrap().iter().enumerate(){policies[seat][i]=v.as_f64().unwrap();}
    }
    for i in 0..169 {
        let jam=if i==168 {1.} else {record["policy"]["0"][3][i].as_f64().unwrap()};
        policies[1][i]*=jam;
    }
    let probes=[("TT",[32u8,33]),("AKo",[48,45])];let seats=[0,1,3,4,5,6,7];
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global().unwrap();
    let started=std::time::Instant::now();
    let batches:Vec<_>=(0..80usize).into_par_iter().map(|job| {
        let h=job/40;let batch=job%40;let cards=probes[h].1;
        let mut rng=Rng(9026191900+h as u64*1000+batch as u64);
        let available:Vec<u8>=(0..52).filter(|c|!cards.contains(c)).collect();
        let mut sums=[[[0.;3];2];2];
        for _ in 0..800_000 {
            let mut deck=[0u8;50];deck.copy_from_slice(&available);
            for i in 0..19 {let j=i+rng.below((50-i) as u64);deck.swap(i,j);}
            let mut weights=[1.;2];let mut aa=false;
            for (k,&seat) in seats.iter().enumerate() {
                let (a,b)=(deck[2*k],deck[2*k+1]);let cls=class_index(a/4,b/4,a%4==b%4);
                if seat==1 {weights[0]*=policies[seat][cls];aa=cls==168;}
                weights[1]*=policies[seat][cls];
            }
            let hero=[cards[0],cards[1],deck[14],deck[15],deck[16],deck[17],deck[18]];
            let opp=[deck[2],deck[3],deck[14],deck[15],deck[16],deck[17],deck[18]];
            let (a,b)=(evaluate7(&hero),evaluate7(&opp));let win=if a>b {1.} else if a==b {0.5} else {0.};
            for mode in 0..2 {
                let v=&mut sums[mode][aa as usize];v[0]+=weights[mode];v[1]+=weights[mode]*weights[mode];v[2]+=weights[mode]*win;
            }
        }
        json!({"hand":probes[h].0,"hero":cards,"batch":batch,"sums":sums})
    }).collect();
    let result=json!({"draws_per_hand":32_000_000,"batch_draws":800_000,"batches":batches,
        "modes":["two_live_hands","including_six_folds"],"components":["non_AA","AA"],
        "columns":["likelihood","likelihood_squared","win_mass"],
        "elapsed_seconds":started.elapsed().as_secs_f64(),
        "note":"Physical eight-player deals and boards. Current compatible jam range; earlier history fixed. No equity cache or production access."});
    std::fs::write(&args[2],serde_json::to_vec_pretty(&result).unwrap()).unwrap();
}
