#[allow(dead_code)]
#[derive(Clone, Copy)]
enum Algorithm { Dcfr, CfrPlus, PcfrPlus }
struct Discounts { pos:f32, neg:f32, strat:f32 }
impl Discounts {
    pub fn for_iteration(algo: Algorithm, t: u32) -> Discounts {
        let t = t as f64;
        match algo {
            Algorithm::Dcfr => {
                let ta = t.powf(1.5);
                Discounts {
                    pos: (ta / (ta + 1.0)) as f32,
                    neg: 0.5,
                    strat: (t / (t + 1.0)).powi(2) as f32,
                }
            }
            // RM+ flooring: multiplying a negative cumulative regret by 0
            // before adding the new delta equals max(R + r, 0) over time.
            Algorithm::CfrPlus | Algorithm::PcfrPlus => Discounts {
                pos: 1.0,
                neg: 0.0,
                strat: (t / (t + 1.0)).powi(2) as f32,
            },
        }
    }
}
