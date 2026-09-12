//! Offline convergence experiments. Never enabled by the production app.
use super::multiway::{CoupledDeck, SAMPLES};
use std::sync::Arc;

pub struct Experiment {
    pub(crate) samples: u32,
    pub(crate) deck: Arc<CoupledDeck>,
    schedule: String,
    horizon: u32,
    rng: u64,
    pub(crate) offset: usize,
}

impl Experiment {
    pub fn new(schedule: &str, samples: u32, horizon: u32, seed: u64) -> Result<Self, String> {
        if !["dcfr", "hs15", "hs30", "gamma15"].contains(&schedule) || horizon == 0
            || ![32, 64, 128, 256, 512, 1024].contains(&samples) {
            return Err("invalid registered convergence experiment".into());
        }
        Ok(Self { samples, deck: CoupledDeck::shared(), schedule: schedule.into(), horizon, rng: seed, offset: 0 })
    }

    pub(crate) fn next_offset(&mut self) -> usize {
        self.rng = self.rng.wrapping_add(0x9e3779b97f4a7c15);
        let mut z = self.rng;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
        // Uniform 10-bit cyclic offset. Every particle has inclusion chance K/1024.
        self.offset = ((z ^ (z >> 31)) as usize) & (SAMPLES - 1);
        self.offset
    }

    pub(crate) fn factors(&self, iteration: u32) -> (f32, f32, f32) {
        let t = iteration as f64;
        if self.schedule == "dcfr" {
            return ((t.powf(1.5)/(t.powf(1.5)+1.0)) as f32, 0.5, (t/(t+1.0)).powi(2) as f32);
        }
        // HS paper equation 4, fixed registered horizon, clamped beyond it.
        // Apply at the engine's existing end-of-iteration discount location.
        let fraction = (t / self.horizon as f64).min(1.0);
        let (alpha, beta, gamma) = match self.schedule.as_str() {
            "hs15" => (1.0+3.0*fraction, -1.0-2.0*fraction, 15.0-5.0*fraction),
            "hs30" => (1.0+3.0*fraction, -1.0-2.0*fraction, 30.0-5.0*fraction),
            _ => (1.5, 0.0, 15.0),
        };
        ((t.powf(alpha)/(t.powf(alpha)+1.0)) as f32,
         (t.powf(beta)/(t.powf(beta)+1.0)) as f32, (t/(t+1.0)).powf(gamma) as f32)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn cyclic_sampling_covers_every_particle_equally() {
        for k in [32,64,128,256,512] {
            let mut counts = [0; SAMPLES];
            for offset in 0..SAMPLES { for i in 0..k { counts[(offset+i)%SAMPLES] += 1; } }
            assert!(counts.iter().all(|&n| n == k));
        }
    }
    #[test]
    fn schedules_remain_finite_and_bounded() {
        for name in ["dcfr","hs15","hs30","gamma15"] {
            let r = Experiment::new(name,1024,1000,42).unwrap();
            for t in [1,2,10,100,1000,5000] {
                let (a,b,c) = r.factors(t);
                assert!([a,b,c].iter().all(|x| x.is_finite() && *x >= 0.0 && *x <= 1.0));
            }
        }
    }
}
