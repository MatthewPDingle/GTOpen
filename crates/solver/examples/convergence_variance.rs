//! Offline control-variate screen. Synthetic range drift, not a solver speed claim.
use solver::preflop::{equity::{class_parts, class_prob, NUM_CLASSES}, multiway::{CoupledDeck, SAMPLES, QUAD_T, QUAD_W}};
use serde_json::{json, Value};
use std::time::Instant;

fn normalized(values: &[f64]) -> Vec<f32> {
    let mass: f64 = values.iter().sum();
    values.iter().map(|v|(v/mass) as f32).collect()
}

fn synthetic_range(seat: usize, changed: bool) -> Vec<f32> {
    let weights: Vec<f64> = (0..NUM_CLASSES).map(|h| {
        let (hi,lo,suited)=class_parts(h);
        let score=0.6*hi as f64+0.4*lo as f64+if hi==lo {4.0} else if suited {1.2} else {0.0};
        let cutoff=if changed {6.0+(seat%3) as f64} else {9.0+(seat%3) as f64};
        class_prob(h) as f64*(0.02+0.98/(1.0+(-(score-cutoff)).exp()))
    }).collect();
    normalized(&weights)
}

fn particle_values(deck: &CoupledDeck, opponents: &[Vec<f32>]) -> Vec<[f64; NUM_CLASSES]> {
    assert!(opponents.len()<=8);
    let mut result=vec![[0.0;NUM_CLASSES];SAMPLES];
    let mut cdf=[[0.0;NUM_CLASSES+1];8];
    for sample in 0..SAMPLES {
        let base=sample*NUM_CLASSES;
        for (q,range) in opponents.iter().enumerate() {
            assert_eq!(range.len(),NUM_CLASSES);
            for i in 0..NUM_CLASSES {cdf[q][i+1]=cdf[q][i]+range[deck.order[base+i] as usize] as f64;}
        }
        for h in 0..NUM_CLASSES {
            let lo=deck.lower[base+h] as usize;
            let hi=deck.upper[base+h] as usize;
            result[sample][h]=QUAD_T.iter().zip(QUAD_W).map(|(t,w)| {
                w*cdf[..opponents.len()].iter().map(|q|q[lo]+t*(q[hi]-q[lo])).product::<f64>()
            }).sum();
        }
    }
    result
}

fn all_offset_errors(current: &[[f64;NUM_CLASSES]], reference: &[[f64;NUM_CLASSES]], k: usize) -> Value {
    assert_eq!(current.len(),SAMPLES); assert_eq!(reference.len(),SAMPLES);
    assert!(k>0 && k<=SAMPLES);
    let mut ordinary_mse=0.0;
    let mut cv_mse=0.0;
    let mut max_bias=0.0f64;
    let mut minimum=f64::INFINITY;
    let mut maximum=f64::NEG_INFINITY;
    for h in 0..NUM_CLASSES {
        let full=current.iter().map(|v|v[h]).sum::<f64>()/SAMPLES as f64;
        let ref_full=reference.iter().map(|v|v[h]).sum::<f64>()/SAMPLES as f64;
        let mut current_sum=current[..k].iter().map(|v|v[h]).sum::<f64>();
        let mut difference_sum=(0..k).map(|s|current[s][h]-reference[s][h]).sum::<f64>();
        let mut ordinary_error=0.0;
        let mut cv_error=0.0;
        let mut bias=0.0;
        for offset in 0..SAMPLES {
            let ordinary=current_sum/k as f64;
            let cv=ref_full+difference_sum/k as f64;
            ordinary_error+=(ordinary-full).powi(2);
            cv_error+=(cv-full).powi(2);
            bias+=cv-full;
            minimum=minimum.min(cv); maximum=maximum.max(cv);
            let next=(offset+k)%SAMPLES;
            current_sum+=current[next][h]-current[offset][h];
            difference_sum+=(current[next][h]-reference[next][h])-(current[offset][h]-reference[offset][h]);
        }
        ordinary_mse+=class_prob(h) as f64*ordinary_error/SAMPLES as f64;
        cv_mse+=class_prob(h) as f64*cv_error/SAMPLES as f64;
        max_bias=max_bias.max((bias/SAMPLES as f64).abs());
    }
    json!({"samples":k,"ordinary_mean_squared_error":ordinary_mse,"control_variate_mean_squared_error":cv_mse,
        "cv_to_ordinary_mse_ratio":if ordinary_mse>0.0 {Some(cv_mse/ordinary_mse)} else {None},
        "maximum_absolute_bias_over_all_offsets":max_bias,"minimum_unclamped_estimate":minimum,"maximum_unclamped_estimate":maximum})
}

fn main() -> Result<(),String> {
    let path=std::env::args().nth(1).ok_or("OUTPUT.json")?;
    if std::path::Path::new(&path).exists() {return Err("output already exists".into());}
    let started=Instant::now();
    let deck=CoupledDeck::shared();
    let mut rows=Vec::new();
    for opponents in [2,3,5,7] {
        let reference: Vec<_>=(0..opponents).map(|p|synthetic_range(p,false)).collect();
        let changed: Vec<_>=(0..opponents).map(|p|synthetic_range(p,true)).collect();
        let reference_values=particle_values(&deck,&reference);
        for drift in [0.0,0.01,0.05,0.2,0.5,1.0] {
            let current: Vec<_>=reference.iter().zip(&changed).map(|(a,b)|normalized(
                &a.iter().zip(b).map(|(x,y)|(1.0-drift)*(*x as f64)+drift*(*y as f64)).collect::<Vec<_>>()
            )).collect();
            let values=particle_values(&deck,&current);
            let production=deck.equities(&current);
            let disagreement=(0..NUM_CLASSES).map(|h|
                (values.iter().map(|v|v[h]).sum::<f64>()/SAMPLES as f64-production[h]).abs()
            ).fold(0.0,f64::max);
            if disagreement>1e-12 {return Err("per-particle mean differs from production terminal mean".into());}
            let errors: Vec<_>=[16,32,64,128].into_iter().map(|k|all_offset_errors(&values,&reference_values,k)).collect();
            rows.push(json!({"opponents":opponents,"synthetic_mixture_drift":drift,
                "max_full_mean_difference":disagreement,"estimators":errors}));
        }
    }
    let output=json!({"scope":"Synthetic normalized range-drift variance screen; not historical data, GPU timing or solver convergence.",
        "estimator":"full_reference_mean + sampled(current_particle_value - reference_particle_value)",
        "offsets_evaluated":SAMPLES,"elapsed_seconds":started.elapsed().as_secs_f64(),"rows":rows});
    std::fs::write(path,serde_json::to_vec_pretty(&output).map_err(|e|e.to_string())?).map_err(|e|e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn identical_reference_eliminates_variance_without_bias() {
        let deck=CoupledDeck::shared();
        let values=particle_values(&deck,&[synthetic_range(0,false),synthetic_range(1,true)]);
        for k in [16,64,128] {
            let result=all_offset_errors(&values,&values,k);
            assert!(result["control_variate_mean_squared_error"].as_f64().unwrap()<1e-24);
            assert!(result["maximum_absolute_bias_over_all_offsets"].as_f64().unwrap()<1e-12);
        }
    }
    #[test]
    fn different_reference_remains_unbiased_over_uniform_offsets() {
        let deck=CoupledDeck::shared();
        let reference=particle_values(&deck,&[synthetic_range(0,false),synthetic_range(1,false)]);
        let current=particle_values(&deck,&[synthetic_range(0,true),synthetic_range(1,true)]);
        for k in [16,64,128] {
            let result=all_offset_errors(&current,&reference,k);
            assert!(result["maximum_absolute_bias_over_all_offsets"].as_f64().unwrap()<1e-12);
        }
    }
}
