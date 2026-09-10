//! Frozen-model independent checks. Never trains, solves, saves games or uses CUDA.
//! FROZEN.json CORPUS.json REPO AUDIT.log MC_ACCEPTED THREADS
#[path = "support/continuation_ensemble.rs"] mod continuation_ensemble;
use continuation_ensemble::Ensemble;
use rayon::prelude::*;
use serde_json::{json, Value};
use solver::{Range, combo_index};
use solver::evaluator::evaluate7;
use solver::preflop::equity::{class_combos, class_index, class_label, NUM_CLASSES};
use solver::preflop::multiway::CoupledDeck;
use std::{path::Path, time::Instant};

fn read(path: &Path) -> Value {
    let s = std::fs::read_to_string(path).unwrap();
    serde_json::from_str(&s[s.find('{').unwrap()..]).unwrap()
}
fn normalize(w: &[f64]) -> Vec<f32> {
    let total: f64 = w.iter().enumerate().map(|(h,x)|x*class_combos(h) as f64).sum();
    assert!(total > 0.0);
    w.iter().enumerate().map(|(h,x)|(x*class_combos(h) as f64/total) as f32).collect()
}
fn from_node(v: &Value) -> Vec<Vec<f32>> {
    let p = v["actor"].as_u64().unwrap() as usize;
    v["reaches_all"].as_array().unwrap().iter().enumerate()
        .filter(|(q,_)|*q != p && v["live"][*q].as_bool().unwrap())
        .map(|(_,v)|normalize(&v.as_array().unwrap().iter().map(|x|x.as_f64().unwrap()).collect::<Vec<_>>())).collect()
}
fn hand(label: &str) -> usize {(0..NUM_CLASSES).find(|&h|class_label(h)==label).unwrap()}
fn errors(v: &[f64]) -> Value {
    let mut e: Vec<f64> = v.iter().map(|x|x.abs()*100.0).collect();
    e.sort_by(f64::total_cmp);
    json!({"mean_absolute_pp":e.iter().sum::<f64>()/e.len() as f64,
        "max_absolute_pp":e[e.len()-1],"p95_absolute_pp":e[(e.len()*95/100).min(e.len()-1)]})
}
struct Rng(u64);
impl Rng {
    fn next(&mut self)->u64 {self.0=self.0.wrapping_add(0x9e3779b97f4a7c15);let mut z=self.0;
        z=(z^(z>>30)).wrapping_mul(0xbf58476d1ce4e5b9);z=(z^(z>>27)).wrapping_mul(0x94d049bb133111eb);z^(z>>31)}
    fn unit(&mut self)->f64 {(self.next()>>11) as f64/(1u64<<53) as f64}
    fn below(&mut self,n:u64)->usize {let threshold=n.wrapping_neg()%n;loop {let v=self.next();if v>=threshold{return (v%n) as usize;}}}
}
fn concrete_combos(label:&str)->Vec<[u8;2]> {
    let target=hand(label);let mut out=Vec::new();
    for a in 0..52u8 {for b in a+1..52u8 {if class_index(a/4,b/4,a%4==b%4)==target {out.push([a,b]);}}}out
}
fn range_data(text:&str)->(Vec<f32>,Vec<(f64,[u8;2])>) {
    let range=Range::parse(text).unwrap();let mut classes=vec![0.0;169];let mut sampler=Vec::new();let mut mass=0.0;
    for a in 0..52u8 {for b in a+1..52u8 {
        let w=range.weights[combo_index(a,b)] as f64;if w<=0.0 {continue;}
        mass+=w;sampler.push((mass,[a,b]));classes[class_index(a/4,b/4,a%4==b%4)]+=w;
    }}assert!(mass>0.0);
    for (cum,_) in &mut sampler {*cum/=mass;}
    (classes.into_iter().map(|x|(x/mass) as f32).collect(),sampler)
}
fn physical(hero:[u8;2],samplers:&[Vec<(f64,[u8;2])>],seed:u64,target:usize)->Value {
    let mut rng=Rng(seed);let (mut accepted,mut attempts)=(0usize,0usize);let(mut sum,mut sq)=(0.0,0.0);
    while accepted<target && attempts<10_000_000 {
        attempts+=1;let mut mask=(1u64<<hero[0])|(1u64<<hero[1]);let mut holes=vec![hero];let mut rejected=false;
        for sampler in samplers {
            let u=rng.unit();let cards=sampler[sampler.partition_point(|(w,_)|*w<=u).min(sampler.len()-1)].1;
            let bits=(1u64<<cards[0])|(1u64<<cards[1]);
            if mask&bits!=0 {rejected=true;break;}mask|=bits;holes.push(cards);
        }
        if rejected {continue;} // whole tuple starts fresh, never repair just one player's hand
        let mut board=[0u8;5];for c in &mut board {loop {let v=(rng.next()%52) as u8;if mask&(1u64<<v)==0 {*c=v;mask|=1u64<<v;break;}}}
        let ranks:Vec<_>=holes.iter().map(|c|evaluate7(&[c[0],c[1],board[0],board[1],board[2],board[3],board[4]])).collect();
        let best=*ranks.iter().max().unwrap();let ties=ranks.iter().filter(|&&r|r==best).count();
        let value=if ranks[0]==best {1.0/ties as f64}else{0.0};sum+=value;sq+=value*value;accepted+=1;
    }
    if accepted!=target {return json!({"status":"unsupported_attempt_limit","accepted":accepted,"attempts":attempts});}
    let mean=sum/accepted as f64;
    json!({"status":"complete","equity":mean,"accepted":accepted,"attempts":attempts,"seed":seed,
        "mc_95_half_width":1.96*((sq/accepted as f64-mean*mean).max(0.0)/accepted as f64).sqrt()})
}
fn physical_uniform_nine(hero:[u8;2],seed:u64,target:usize)->Value {
    let original:Vec<u8>=(0..52u8).filter(|c|!hero.contains(c)).collect();
    let mut rng=Rng(seed);let(mut sum,mut sq)=(0.0,0.0);
    for _ in 0..target {
        let mut deck=original.clone();
        for i in 0..21 {let j=i+rng.below((50-i) as u64);deck.swap(i,j);}
        let board=&deck[16..21];
        let rank=|a,b|evaluate7(&[a,b,board[0],board[1],board[2],board[3],board[4]]);
        let hero_rank=rank(hero[0],hero[1]);let mut best=hero_rank;let mut ties=1;
        for i in 0..8 {let r=rank(deck[2*i],deck[2*i+1]);if r>best {best=r;ties=1;}else if r==best {ties+=1;}}
        let value=if hero_rank==best {1.0/ties as f64}else{0.0};sum+=value;sq+=value*value;
    }
    let mean=sum/target as f64;
    json!({"status":"complete","equity":mean,"accepted":target,"attempts":target,"seed":seed,
        "sampler":"uniform_compatible_without_replacement_v1",
        "mc_95_half_width":1.96*((sq/target as f64-mean*mean).max(0.0)/target as f64).sqrt()})
}
fn main() {
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),6,"FROZEN CORPUS REPO AUDIT MC_ACCEPTED THREADS");
    let samples:usize=args[4].parse().unwrap();
    let threads:usize=args[5].parse().unwrap();assert!((1..=4).contains(&threads));
    rayon::ThreadPoolBuilder::new().num_threads(threads).build_global().unwrap();
    let frozen=read(Path::new(&args[0]));let corpus=read(Path::new(&args[1]));let audit=read(Path::new(&args[3]));
    let supplemental=corpus["supplement_id"]=="uniform-nine-aa-million-v1";
    if supplemental {
        assert_eq!(samples,1_000_000);assert_eq!(corpus["physical_samples_per_hand"].as_u64(),Some(1_000_000));
        let cases=corpus["new_terminal_holdout"].as_array().unwrap();assert_eq!(cases.len(),1);
        let c=&cases[0];assert_eq!(c["id"],"uniform-nine-aa-supplement");assert_eq!(c["hands"],json!(["AA"]));
        assert_eq!(c["mc_seed"].as_u64(),Some(2026091199));
        let opponents=c["opponents"].as_array().unwrap();assert_eq!(opponents.len(),8);
        for text in opponents {let r=Range::parse(text.as_str().unwrap()).unwrap();assert_eq!(r.weights.len(),1326);assert!(r.weights.iter().all(|&w|w==1.0));}
    }else{assert!(corpus["supplement_id"].is_null());assert!(samples==0||samples==100_000);}
    let id=frozen["candidate"]["id"].as_str().unwrap();
    let expected_count=match id {"coupled_subset_herding_v1_64"=>64,"coupled_subset_exchange_v2_32"=>32,_=>panic!("unregistered frozen candidate ID")};
    assert_eq!(frozen["candidate"]["particles"].as_u64(),Some(expected_count));
    let source=audit["models"].as_array().unwrap().iter().find(|m|m["id"]==id).unwrap();
    assert_eq!(source["indices"],frozen["candidate"]["indices"]);
    let model=Ensemble::new(source["indices"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap() as usize).collect()).unwrap();
    assert_eq!(model.indices.len(),expected_count as usize);
    assert_eq!(source["particles"].as_u64(),Some(expected_count));
    assert_eq!(source["weight"].as_f64(),Some(1.0/expected_count as f64));
    let started=Instant::now();let table=CoupledDeck::shared();let init_seconds=started.elapsed().as_secs_f64();
    let mut holdouts=Vec::new();
    for case in corpus["new_terminal_holdout"].as_array().unwrap() {
        let data:Vec<_>=case["opponents"].as_array().unwrap().iter().map(|t|range_data(t.as_str().unwrap())).collect();
        let weights:Vec<_>=data.iter().map(|(w,_)|w.clone()).collect();let samplers:Vec<_>=data.into_iter().map(|(_,s)|s).collect();
        let full=table.equities(&weights);let candidate=model.equities(&table,&weights);
        let rows:Vec<_>=case["hands"].as_array().unwrap().par_iter().enumerate().map(|(i,name)|{
            let name=name.as_str().unwrap();let h=hand(name);
            let seed=case["mc_seed"].as_u64().unwrap()+i as u64*10000;
            let mc=if samples==0 {json!({"status":"not_run"})}else if supplemental {physical_uniform_nine(concrete_combos(name)[0],seed,samples)}else{physical(concrete_combos(name)[0],&samplers,seed,samples)};
            json!({"hand":name,"candidate":candidate[h],"coupled_1024":full[h],"physical":mc,
                "candidate_minus_coupled_pp":100.0*(candidate[h]-full[h]),
                "candidate_minus_physical_pp":mc["equity"].as_f64().map(|eq|100.0*(candidate[h]-eq)),
                "coupled_minus_physical_pp":mc["equity"].as_f64().map(|eq|100.0*(full[h]-eq))})
        }).collect();
        holdouts.push(json!({"id":case["id"],"split":if supplemental{"registered_supplemental_reference"}else{"registered_independent_holdout"},"stress_only":case["stress_only"].as_bool().unwrap_or(false),
            "all169_errors_vs_coupled":errors(&(0..169).map(|h|candidate[h]-full[h]).collect::<Vec<_>>()),"hands":rows}));
    }
    if supplemental {
        println!("{}",serde_json::to_string_pretty(&json!({"schema":1,"supplement_id":corpus["supplement_id"],
            "frozen_candidate":frozen,"corpus":corpus,"physical_samples_per_hand":samples,"threads":threads,
            "holdouts":holdouts,"elapsed_total_seconds":started.elapsed().as_secs_f64(),
            "limitations":["Supplemental seen-case uncertainty check; not a replacement independent holdout.",
                "Uniform compatible deals only; no future betting or folded-card removal.","Candidate indices and quality thresholds are unchanged."]})).unwrap());
        return;
    }
    let repo=Path::new(&args[2]);let rebuilt=read(&repo.join("research/multiway-equity-audit/rebuilt-range-node.json"));
    let rebuilt_ref=read(&repo.join("research/multiway-equity-audit/rebuilt-range-audit.json"));let opponents=from_node(&rebuilt);
    let full=table.equities(&opponents);let mut rebuilt_rows=Vec::new();
    let bench_repeats=32;
    let t=Instant::now();for _ in 0..bench_repeats {std::hint::black_box(table.equities(std::hint::black_box(&opponents)));}
    let full_ms=t.elapsed().as_secs_f64()*1000.0/bench_repeats as f64;
    for m in audit["models"].as_array().unwrap() {
        let ensemble=Ensemble::new(m["indices"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap() as usize).collect()).unwrap();
        let values=ensemble.equities(&table,&opponents);let t=Instant::now();
        for _ in 0..bench_repeats {std::hint::black_box(ensemble.equities(&table,std::hint::black_box(&opponents)));}
        let candidate_ms=t.elapsed().as_secs_f64()*1000.0/bench_repeats as f64;
        let rows:Vec<_>=rebuilt_ref["results"].as_array().unwrap().iter().map(|r|{let h=hand(r["hand"].as_str().unwrap());let eq=r["compatible_deal_reference"].as_f64().unwrap();
            json!({"hand":r["hand"],"candidate":values[h],"coupled_1024":full[h],"physical_equity":eq,
                "candidate_minus_physical_pp":100.0*(values[h]-eq),"physical_95_half_width":r["reference_95_half_width"],
                "candidate_showdown_call_minus_fold_bb":7.6*values[h]-1.0,"physical_showdown_call_minus_fold_bb":7.6*eq-1.0})}).collect();
        rebuilt_rows.push(json!({"model":m["id"],"hands":rows,"cpu_terminal_ms":candidate_ms,"full_cpu_terminal_ms":full_ms,
            "terminal_speedup_only":full_ms/candidate_ms,"benchmark_repetitions":bench_repeats}));
    }
    println!("{}",serde_json::to_string_pretty(&json!({"schema":1,"frozen_candidate":frozen,"corpus_baseline":corpus["baseline"],
        "physical_samples_per_hand":samples,"threads":threads,"coupled_table_init_seconds":init_seconds,"holdouts":holdouts,
        "rebuilt_bb_regressions_all_models":rebuilt_rows,"elapsed_total_seconds":started.elapsed().as_secs_f64(),
        "limitations":["No training or selection uses these holdout outputs.","Physical references use compatible live hole cards and shared board; folded-card removal/future betting omitted.","Same fixed representative hero combo is valid only for these suit-symmetric class ranges.","Terminal timing is not whole-solver or end-to-end speedup; independent result does not certify policy quality."]})).unwrap());
}
