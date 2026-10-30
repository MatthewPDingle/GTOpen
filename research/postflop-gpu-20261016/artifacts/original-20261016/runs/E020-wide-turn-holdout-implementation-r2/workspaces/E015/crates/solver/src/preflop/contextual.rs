//! Versioned experimental re-raise predictions. Training is offline; inference
//! uses the frozen artifact embedded here, never a mutable file or network model.
use super::{BucketPolicy, PreflopConfig};
use serde::{Deserialize, Serialize};
use std::sync::OnceLock;

pub const MODEL_ID: &str = "ignition-nl10-reraise-v1";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Entry { Cold, Called, Raised }

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ContextualInput {
    pub entry: Entry,
    /// Raises already made: 2 means facing a 3-bet; 3+ means a 4-bet or later.
    pub raises: u8,
    /// Pot before this decision, including the opponent's bet, in bb.
    pub pot: f64,
    /// Actor's previous live investment (excluding ante), in bb.
    pub invested: f64,
    /// Total live amount currently faced, in bb (not the incremental call).
    pub to_call: f64,
}

#[derive(Debug, Clone, Serialize)]
pub struct ContextualPrediction {
    pub version: String,
    pub policy: Option<BucketPolicy>,
    pub nominal_price: Option<f64>,
    pub note: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct ContextualStatus {
    pub version: String,
    pub active: bool,
    pub context: ContextualInput,
    pub nominal_price: Option<f64>,
    pub note: String,
}

#[derive(Deserialize)]
struct Baseline { players: usize, role: i32, probabilities: Vec<[f64; 3]> }
#[derive(Deserialize)]
struct Artifact {
    features: Vec<String>,
    weights: Vec<[f64; 2]>,
    baseline: std::collections::BTreeMap<String, Vec<Baseline>>,
}

// Entry type × intercept/price/depth × hand × call/raise. Keep all arithmetic
// in f64 and round only the final normalized probabilities to the policy's f32.
type HandTerms = [[[[f64; 2]; 169]; 3]; 3];
struct CompiledBaseline { players: usize, role: i32, logits: Vec<[f64;3]> }
struct CompiledArtifact {
    weights: Vec<[f64;2]>,
    baseline: std::collections::BTreeMap<String, Vec<CompiledBaseline>>,
    hand_terms: HandTerms,
}

#[derive(Debug, Serialize)]
pub struct ContextualModelMemory {
    pub baseline_numeric_bytes: usize,
    pub compiled_numeric_bytes: usize,
    pub added_hand_term_bytes: usize,
}

pub fn validate_version(version: &str) -> Result<(), String> {
    if version == MODEL_ID { Ok(()) }
    else { Err(format!("unknown contextual re-raise model: {version}")) }
}

fn feature_names() -> Vec<String> {
    let entries = ["cold", "called", "raised"];
    let mut names = Vec::new();
    for prefix in ["entry", "depth", "price", "price2", "commit", "stack"] {
        for entry in entries { names.push(format!("{prefix}/{entry}")); }
    }
    for role in -2..=4 { names.push(format!("seat/{role}")); }
    names.push("players".into());
    for entry in entries {
        for tag in ["hand", "hand_price", "hand_depth"] {
            for hand in ["high", "low", "pair", "suited", "pair_rank", "suited_low"] {
                names.push(format!("{entry}/{tag}/{hand}"));
            }
        }
    }
    names
}

fn read_artifact() -> Artifact {
        let model: Artifact = serde_json::from_str(include_str!(
            "../../../../cache/contextual/ignition-nl10-reraise-v1.json"
        )).expect("checked-in contextual artifact must parse");
        assert_eq!(model.features, feature_names(), "contextual feature order changed");
        assert_eq!(model.weights.len(), 80);
        assert!(model.weights.iter().flatten().all(|v| v.is_finite()));
        for key in ["cold_reraise", "reraise"] {
            let rows = &model.baseline[key];
            assert!(!rows.is_empty());
            for row in rows {
                assert_eq!(row.probabilities.len(), 169);
                assert!((3..=6).contains(&row.players));
                assert!((-2..=4).contains(&row.role));
                for p in &row.probabilities {
                    assert!(p.iter().all(|v| v.is_finite() && *v >= 0.0));
                    assert!((p.iter().sum::<f64>() - 1.0).abs() < 1e-9);
                }
            }
        }
        model
}

fn hand_features(h: usize) -> [f64;6] {
    let row=h/13;let col=h%13;
    let hi=row.max(col) as f64/12.0-0.5;
    let lo=row.min(col) as f64/12.0-0.5;
    let pair=f64::from(row==col);let suited=f64::from(row>col);
    [hi,lo,pair,suited,pair*hi,suited*lo]
}

fn artifact() -> &'static CompiledArtifact {
    static MODEL:OnceLock<CompiledArtifact>=OnceLock::new();
    MODEL.get_or_init(|| {
        let raw=read_artifact();
        let mut hand_terms=[[[[0.0;2];169];3];3];
        for (entry,terms) in hand_terms.iter_mut().enumerate() {
            for (modifier,hands) in terms.iter_mut().enumerate() {
                for (h,term) in hands.iter_mut().enumerate() {
                    for (k,value) in hand_features(h).into_iter().enumerate() {
                        let w=raw.weights[26+entry*18+modifier*6+k];
                        term[0]+=value*w[0];term[1]+=value*w[1];
                    }
                }
            }
        }
        let baseline=raw.baseline.into_iter().map(|(key,rows)| {
            let rows=rows.into_iter().map(|row|CompiledBaseline {players:row.players,role:row.role,
                logits:row.probabilities.into_iter().map(|p|p.map(|v|v.max(1e-12).ln())).collect()}).collect();
            (key,rows)
        }).collect();
        CompiledArtifact {weights:raw.weights,baseline,hand_terms}
    })
}

/// Numeric resident payload; excludes map/vector headers and allocator overhead.
pub fn model_memory() -> ContextualModelMemory {
    let m=artifact();
    let baseline=m.weights.len()*std::mem::size_of::<[f64;2]>()
        +m.baseline.values().flatten().map(|r|r.logits.len()*std::mem::size_of::<[f64;3]>()).sum::<usize>();
    ContextualModelMemory {baseline_numeric_bytes:baseline,
        compiled_numeric_bytes:baseline+std::mem::size_of::<HandTerms>(),
        added_hand_term_bytes:std::mem::size_of::<HandTerms>()}
}

// Independent dense oracle for tests/benchmarks. The application does not call
// this function or load this separate copy of the original probabilities.
fn reference_artifact() -> &'static Artifact {
    static REFERENCE:OnceLock<Artifact>=OnceLock::new();
    REFERENCE.get_or_init(read_artifact)
}

/// Source support is deliberately narrower than the generic preflop solver.
/// Unsupported games retain the caller's existing static policy.
pub fn is_supported(cfg: &PreflopConfig) -> bool {
    let n = cfg.positions.len();
    (3..=6).contains(&n) && cfg.posts.len() == n && cfg.ante.abs() <= 1e-9
        && cfg.posts[..n-2].iter().all(|p|p.abs() <= 1e-9)
        && (cfg.posts[n-2]-0.5).abs() <= 1e-9 && (cfg.posts[n-1]-1.0).abs() <= 1e-9
}

pub fn support_note(cfg: &PreflopConfig) -> Option<String> {
    let n = cfg.positions.len();
    let mut why = Vec::new();
    if !(3..=6).contains(&n) { why.push("source tables have 3–6 players"); }
    if cfg.ante.abs() > 1e-9 { why.push("source games have no ante"); }
    if cfg.posts.len() != n || n < 2 || cfg.posts[..n-2].iter().any(|p| p.abs() > 1e-9)
        || (cfg.posts[n-2] - 0.5).abs() > 1e-9 || (cfg.posts[n-1] - 1.0).abs() > 1e-9 {
        why.push("source blinds are 0.5/1 bb with no straddle");
    }
    if why.is_empty() { None } else {
        Some(format!("Contextual re-raise model inactive: {}; using the saved non-contextual policy.", why.join("; ")))
    }
}

pub fn predict(version: &str, cfg: &PreflopConfig, seat: usize, input: &ContextualInput)
    -> Result<ContextualPrediction, String>
{
    predict_impl(version,cfg,seat,input,false)
}

/// Frozen dense implementation for numerical/performance regression tools.
/// This is never selected by the application or stored profiles.
#[doc(hidden)]
pub fn predict_dense_reference(version: &str, cfg: &PreflopConfig, seat: usize, input: &ContextualInput)
    -> Result<ContextualPrediction, String>
{
    predict_impl(version,cfg,seat,input,true)
}

fn predict_impl(version: &str, cfg: &PreflopConfig, seat: usize, input: &ContextualInput, dense: bool)
    -> Result<ContextualPrediction, String>
{
    validate_version(version)?;
    super::validate(cfg)?;
    if seat >= cfg.positions.len() { return Err("contextual seat out of range".into()); }
    if input.raises < 2 || input.raises > 32 { return Err("contextual preview needs 2–32 prior raises".into()); }
    if ![input.pot, input.invested, input.to_call].iter().all(|v| v.is_finite())
        || input.invested < 0.0 || input.invested >= cfg.stack
        || input.to_call <= input.invested || input.pot <= 0.0
        || input.pot + 1e-8 < input.invested + input.to_call {
        return Err("contextual amounts must describe a positive call with pot >= investment + faced total".into());
    }
    let post = cfg.posts[seat];
    if input.invested + 1e-8 < post || match input.entry {
        Entry::Cold => (input.invested-post).abs() > 1e-8,
        Entry::Called | Entry::Raised => input.invested <= post+1e-8,
    } {
        return Err("cold entry must have only its blind invested; called/raised entry needs voluntary investment".into());
    }
    let remaining = cfg.stack - input.invested;
    let call = (input.to_call - input.invested).min(remaining);
    if !(input.pot+call).is_finite() { return Err("contextual pot plus call is too large".into()); }
    let price = call / (input.pot + call);
    if let Some(note) = support_note(cfg) {
        return Ok(ContextualPrediction { version: version.into(), policy: None, nominal_price: Some(price), note });
    }
    let n = cfg.positions.len();
    let role = if seat == n-1 { -2 } else if seat == n-2 { -1 } else { (n-3-seat) as i32 };
    let key = if input.entry == Entry::Cold { "cold_reraise" } else { "reraise" };
    let entry = match input.entry { Entry::Cold => 0, Entry::Called => 1, Entry::Raised => 2 };
    let depth = f64::from(input.raises >= 3);
    let price_z = (price - 0.3) / 0.15;
    let mut x = [0.0; 80];
    for (i, value) in [1.0, depth, price_z, price_z*price_z, input.invested / cfg.stack,
        (remaining.ln_1p() - 101.0f64.ln()) / 2.0].into_iter().enumerate() {
        x[i*3+entry] = value;
    }
    x[18+(role+2) as usize] = 1.0;
    x[25] = (n as f64 - 6.0) / 3.0;
    let mut policy = BucketPolicy { call: vec![0.0;169], raise: vec![0.0;169], jam: vec![0.0;169], raise_size: "max".into(), raise_multiples: Vec::new(), raise_sizes: Vec::new() };
    if dense {
        let model=reference_artifact();let rows=&model.baseline[key];
        let matching:Vec<&Baseline>=rows.iter().filter(|r|r.role==role).collect();
        let matching=if matching.is_empty() {
            let same_kind:Vec<_>=rows.iter().filter(|r|(r.role>=0)==(role>=0)).collect();
            if same_kind.is_empty(){rows.iter().collect()}else{same_kind}
        }else{matching};
        let baseline=matching.into_iter().min_by_key(|r|((r.role-role).abs(),r.players.abs_diff(n),std::cmp::Reverse(r.players))).unwrap();
        for h in 0..169 {
            let hand=hand_features(h);
            for (m,modifier) in [1.0,price_z,depth].into_iter().enumerate() {
                for k in 0..6 {x[26+entry*18+m*6+k]=hand[k]*modifier;}
            }
            let mut logits=baseline.probabilities[h].map(|p|p.max(1e-12).ln());
            for (f,w) in x.iter().zip(&model.weights) {logits[1]+=f*w[0];logits[2]+=f*w[1];}
            store_probabilities(&mut policy,h,logits);
        }
    } else {
        let model=artifact();let rows=&model.baseline[key];
        // Same nearest-observed selection without temporary candidate lists.
        let exact=rows.iter().any(|r|r.role==role);
        let same_kind=rows.iter().any(|r|(r.role>=0)==(role>=0));
        let baseline=rows.iter().filter(|r| if exact {r.role==role} else if same_kind {(r.role>=0)==(role>=0)} else {true})
            .min_by_key(|r|((r.role-role).abs(),r.players.abs_diff(n),std::cmp::Reverse(r.players))).unwrap();
        let mut context=[0.0;2];
        for (f,w) in x[..26].iter().zip(&model.weights) {context[0]+=f*w[0];context[1]+=f*w[1];}
        let terms=&model.hand_terms[entry];
        for h in 0..169 {
            let mut logits=baseline.logits[h];
            for a in 0..2 {logits[a+1]+=context[a]+terms[0][h][a]+price_z*terms[1][h][a]+depth*terms[2][h][a];}
            store_probabilities(&mut policy,h,logits);
        }
    }
    let note = format!("Experimental contextual re-raise prediction: {:?}, facing {}. Nominal call price {:.1}%; investment {:.2} bb; remaining {:.2} bb. Conditional on this history, with sparse hands pooled. Retrospective validation only; prices are not adjusted for side pots.",
        input.entry, if depth == 0.0 { "3-bet" } else { "4-bet+" }, price*100.0, input.invested, remaining);
    Ok(ContextualPrediction { version: version.into(), policy: Some(policy), nominal_price: Some(price), note })
}

#[inline]
fn store_probabilities(policy:&mut BucketPolicy,h:usize,logits:[f64;3]) {
    let max=logits.iter().copied().fold(f64::NEG_INFINITY,f64::max);
    let probabilities=logits.map(|l|(l-max).exp());let sum=probabilities.iter().sum::<f64>();
    policy.call[h]=(probabilities[1]/sum) as f32;policy.raise[h]=(probabilities[2]/sum) as f32;
}

#[cfg(test)]
mod tests {
    use super::*;
    fn cfg() -> PreflopConfig {
        serde_json::from_value(serde_json::json!({"positions":["UTG","HJ","CO","BTN","SB","BB"],"stack":100.0,"posts":[0,0,0,0,0.5,1],"open_raises":[2.5],"raise_mults":[3.0],"limp":true})).unwrap()
    }
    #[test]
    fn compiled_inference_matches_dense_across_contexts() {
        let mut seed=0xC011CA11u64;
        let mut uniform=|| {seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1);(seed>>11) as f64/(1u64<<53) as f64};
        let mut maximum=0.0f32;
        for trial in 0..2048 {
            let n=3+trial%4;let seat=(trial/4)%n;
            let mut c=cfg();c.positions=(0..n).map(|i|format!("P{i}")).collect();
            c.posts=vec![0.0;n];c.posts[n-2]=0.5;c.posts[n-1]=1.0;
            c.stack=20.0+uniform()*280.0;
            let entry=[Entry::Cold,Entry::Called,Entry::Raised][(trial/24)%3];
            let post=c.posts[seat];
            let invested=if entry==Entry::Cold {post}else{post+0.01+uniform()*(c.stack-post-0.02)};
            let faced=invested+(c.stack-invested)*(0.001+uniform()*0.999);
            let input=ContextualInput {entry,raises:2+(trial%4) as u8,invested,to_call:faced,
                pot:invested+faced+uniform()*c.stack};
            let dense=predict_dense_reference(MODEL_ID,&c,seat,&input).unwrap();
            let compiled=predict(MODEL_ID,&c,seat,&input).unwrap();
            assert_eq!(compiled.note,dense.note);assert_eq!(compiled.nominal_price,dense.nominal_price);
            let dense=dense.policy.unwrap();let compiled=compiled.policy.unwrap();
            for (a,b) in compiled.call.iter().chain(&compiled.raise).zip(dense.call.iter().chain(&dense.raise)) {
                maximum=maximum.max((a-b).abs());
                assert!((a-b).abs()<=1e-7,"context {trial}: {a} != {b}");
            }
            assert_eq!(compiled.jam,dense.jam);
        }
        eprintln!("2048 complete-range compiled/dense comparisons; maximum f32 error {maximum}");
    }
    #[test]
    fn contextual_frozen_python_examples_match() {
        let examples: serde_json::Value = serde_json::from_str(include_str!("../../../../research/ignition-reraise/examples.json")).unwrap();
        let examples = examples.as_array().unwrap(); assert_eq!(examples.len(), 18);
        for e in examples {
            let h = match e["hand"].as_str().unwrap() { "AA" => 168, "QQ" => 140, "AKs" => 167, "72o" => 5, "32o" => 1, "J4o" => 35, _ => unreachable!() };
            let price = e["price"].as_f64().unwrap(); let call = 25.0;
            let p = predict(MODEL_ID, &cfg(), 1, &ContextualInput { entry: Entry::Raised, raises: 2, invested: 2.5, to_call: 27.5, pot: call/price-call }).unwrap().policy.unwrap();
            assert!((p.call[h] as f64-e["candidate_call"].as_f64().unwrap()).abs()<1e-6, "{e}");
            assert!((p.raise[h] as f64-e["candidate_raise"].as_f64().unwrap()).abs()<1e-6, "{e}");
            assert!((0..169).all(|i| p.call[i].is_finite() && p.raise[i].is_finite() && p.call[i]+p.raise[i]<=1.000001));
        }
    }
    #[test]
    fn contextual_support_and_invalid_input_are_explicit() {
        let mut cfg = cfg();
        let input = ContextualInput { entry: Entry::Cold, raises: 2, pot: 12.5, invested: 0.0, to_call: 7.5 };
        cfg.posts[4] = 1.0;
        assert!(predict(MODEL_ID,&cfg,0,&input).unwrap().policy.is_none());
        cfg.posts[4] = 0.5; cfg.ante = 0.1;
        assert!(predict(MODEL_ID,&cfg,0,&input).unwrap().note.contains("no ante"));
        assert!(predict("unknown",&cfg,0,&input).is_err());
        assert!(predict(MODEL_ID,&cfg,99,&input).is_err());
        cfg.posts.clear(); assert!(predict(MODEL_ID,&cfg,0,&input).is_err());
    }
    #[test]
    fn contextual_short_stack_caps_nominal_call_cost() {
        let input = ContextualInput { entry: Entry::Raised, raises: 3, pot: 220.0, invested: 90.0, to_call: 120.0 };
        let p = predict(MODEL_ID,&cfg(),0,&input).unwrap();
        assert!((p.nominal_price.unwrap()-10.0/230.0).abs()<1e-12);
    }
}
