//! Least-exploitable frequency locks: the quick fit and the full fit must hit
//! their targets, and the full fit must match the exact constrained optimum,
//! computed here independently as a linear program on a river spot where
//! OOP's whole strategy is the one fitted decision.

use solver::cards::card_mask;
use solver::evaluator::evaluate7;
use solver::query::PathStep;
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{LockMode, Solver, Spot, SpotConfig};
use std::sync::Arc;

fn sizing(bet: &str) -> StreetSizing {
    StreetSizing { bet: parse_sizes(bet).unwrap(), raise: vec![], donk: vec![] }
}

const POT: f64 = 100.0;
const BET: f64 = 100.0;

/// River: OOP checks (showdown) or jams pot; IP folds or calls.
fn river_spot() -> Arc<Spot> {
    Arc::new(
        Spot::new(SpotConfig {
            board: "Ks9h5d3c2s".to_string(),
            range_oop: "AA,KK,99,AK,KQ,KJs,K9s,QJ,JT,T8s,76s,A4s,64s".to_string(),
            range_ip: "AK,KQ,KJ,KT,QQ,JJ,TT,99,A9s,98s,55".to_string(),
            tree: TreeConfig {
                starting_pot: POT,
                effective_stack: BET,
                oop: [sizing(""), sizing(""), sizing("100")],
                ip: [sizing(""), sizing(""), sizing("")],
                ..Default::default()
            },
        })
        .unwrap(),
    )
}

fn solved(iters: u32) -> Solver {
    let mut s = Solver::new(river_spot());
    for _ in 0..iters {
        s.iterate();
    }
    s
}

const ROOT: &[PathStep] = &[];

/// OOP's bet probability per combo from the lock at the root.
fn root_bet(s: &Solver) -> Vec<f64> {
    let nh = s.spot.hands[0].len();
    let lock = &s.locks[&0];
    (0..nh).map(|i| lock[nh + i] as f64).collect()
}

/// Exact model of the river: for OOP's per-combo bet probabilities, OOP's
/// expected chips (relative to the river start) against IP's best response.
struct Model {
    wi: Vec<f64>,
    /// pair weight (blockers removed) and showdown sign, [i][j]
    w: Vec<Vec<f64>>,
    sd: Vec<Vec<f64>>,
}

impl Model {
    fn new(spot: &Spot) -> Model {
        let board = &spot.board;
        let strength = |c1: u8, c2: u8| {
            let mut cards = board.clone();
            cards.push(c1);
            cards.push(c2);
            evaluate7(&cards)
        };
        let (h0, h1) = (&spot.hands[0], &spot.hands[1]);
        let mut w = vec![vec![0.0; h1.len()]; h0.len()];
        let mut sd = vec![vec![0.0; h1.len()]; h0.len()];
        for (i, a) in h0.iter().enumerate() {
            let sa = strength(a.c1, a.c2);
            for (j, b) in h1.iter().enumerate() {
                if (card_mask(a.c1) | card_mask(a.c2)) & (card_mask(b.c1) | card_mask(b.c2)) != 0 {
                    continue;
                }
                w[i][j] = a.weight as f64 * b.weight as f64;
                let sb = strength(b.c1, b.c2);
                sd[i][j] = if sa > sb { 1.0 } else if sa < sb { -1.0 } else { 0.0 };
            }
        }
        // chips per (hand, hand) pair: normalize by the total pair weight
        let tot: f64 = w.iter().flatten().sum();
        for row in &mut w {
            for x in row.iter_mut() {
                *x /= tot;
            }
        }
        Model { wi: h0.iter().map(|h| h.weight as f64).collect(), w, sd }
    }

    fn value(&self, bet: &[f64]) -> f64 {
        let (n, m) = (self.w.len(), self.w[0].len());
        let mut v = 0.0;
        for i in 0..n {
            for j in 0..m {
                v += (1.0 - bet[i]) * self.w[i][j] * self.sd[i][j] * POT / 2.0;
            }
        }
        for j in 0..m {
            let fold: f64 = (0..n).map(|i| bet[i] * self.w[i][j] * POT / 2.0).sum();
            let call: f64 = (0..n).map(|i| bet[i] * self.w[i][j] * self.sd[i][j] * (POT / 2.0 + BET)).sum();
            v += fold.min(call);
        }
        v
    }

    /// OOP's value against a fixed IP calling strategy.
    fn value_vs(&self, bet: &[f64], call: &[f64]) -> f64 {
        let (n, m) = (self.w.len(), self.w[0].len());
        let mut v = 0.0;
        for i in 0..n {
            for j in 0..m {
                let w = self.w[i][j];
                v += (1.0 - bet[i]) * w * self.sd[i][j] * POT / 2.0;
                v += bet[i] * w * ((1.0 - call[j]) * POT / 2.0 + call[j] * self.sd[i][j] * (POT / 2.0 + BET));
            }
        }
        v
    }

    fn freq(&self, bet: &[f64]) -> f64 {
        let r: f64 = self.wi.iter().sum();
        self.wi.iter().zip(bet).map(|(w, b)| w * b).sum::<f64>() / r
    }

    /// max value(bet) s.t. freq(bet) = t, as an LP (dense big-M simplex).
    fn optimum(&self, t: f64) -> f64 {
        let (n, m) = (self.w.len(), self.w[0].len());
        // x = [bet_0..n, z'_0..m]; z_j = z'_j - L
        let l = 4.0 * (POT / 2.0 + BET);
        let nv = n + m;
        let mut rows: Vec<(Vec<f64>, f64)> = Vec::new();
        for i in 0..n {
            let mut a = vec![0.0; nv];
            a[i] = 1.0;
            rows.push((a, 1.0));
        }
        for j in 0..m {
            let mut a = vec![0.0; nv];
            for i in 0..n {
                a[i] = -self.w[i][j] * POT / 2.0;
            }
            a[n + j] = 1.0;
            rows.push((a, l));
            let mut a = vec![0.0; nv];
            for i in 0..n {
                a[i] = -self.w[i][j] * self.sd[i][j] * (POT / 2.0 + BET);
            }
            a[n + j] = 1.0;
            rows.push((a, l));
        }
        // objective: sum_i (1-bet_i) C_i + sum_j (z'_j - L)
        let mut c = vec![0.0; nv];
        let mut c0 = -(m as f64) * l;
        for i in 0..n {
            let ci: f64 = (0..m).map(|j| self.w[i][j] * self.sd[i][j] * POT / 2.0).sum();
            c[i] = -ci;
            c0 += ci;
        }
        for j in 0..m {
            c[n + j] = 1.0;
        }
        let r: f64 = self.wi.iter().sum();
        let eq: Vec<f64> = (0..nv).map(|k| if k < n { self.wi[k] } else { 0.0 }).collect();
        c0 + simplex_max(&c, &rows, &eq, t * r)
    }
}

/// maximize c.x s.t. rows (a.x <= b, b >= 0), eq.x = beq, x >= 0.
/// Big-M with one artificial for the equality; Bland's rule.
fn simplex_max(c: &[f64], rows: &[(Vec<f64>, f64)], eq: &[f64], beq: f64) -> f64 {
    let nv = c.len();
    let nr = rows.len() + 1;
    let ncol = nv + nr; // structural + slacks (last slack column is the artificial)
    let big_m = 1e5;
    let mut t = vec![vec![0.0; ncol + 1]; nr + 1];
    for (k, (a, b)) in rows.iter().enumerate() {
        t[k][..nv].copy_from_slice(a);
        t[k][nv + k] = 1.0;
        t[k][ncol] = *b;
    }
    let ke = rows.len();
    t[ke][..nv].copy_from_slice(eq);
    t[ke][nv + ke] = 1.0; // artificial
    t[ke][ncol] = beq;
    let mut cost = vec![0.0; ncol];
    cost[..nv].copy_from_slice(c);
    cost[nv + ke] = -big_m;
    let mut basis: Vec<usize> = (0..nr).map(|k| nv + k).collect();
    // reduced costs row: z_j - c_j
    let obj = nr;
    for j in 0..ncol {
        let mut z = 0.0;
        for k in 0..nr {
            z += cost[basis[k]] * t[k][j];
        }
        t[obj][j] = z - cost[j];
    }
    let mut z = 0.0;
    for k in 0..nr {
        z += cost[basis[k]] * t[k][ncol];
    }
    t[obj][ncol] = z;
    for _ in 0..200_000 {
        let Some(e) = (0..ncol).find(|&j| t[obj][j] < -1e-9) else { break };
        let mut best: Option<(f64, usize)> = None;
        for k in 0..nr {
            if t[k][e] > 1e-10 {
                let ratio = t[k][ncol] / t[k][e];
                if best.map_or(true, |(r, bk)| ratio < r - 1e-12 || (ratio <= r + 1e-12 && basis[k] < basis[bk])) {
                    best = Some((ratio, k));
                }
            }
        }
        let (_, pr) = best.expect("LP unbounded");
        let pv = t[pr][e];
        for v in t[pr].iter_mut() {
            *v /= pv;
        }
        for k in 0..=nr {
            if k != pr {
                let f = t[k][e];
                if f != 0.0 {
                    for j in 0..=ncol {
                        t[k][j] -= f * t[pr][j];
                    }
                }
            }
        }
        basis[pr] = e;
    }
    assert!(basis.iter().all(|&b| b != nv + ke) || t[basis.iter().position(|&b| b == nv + ke).unwrap()][ncol].abs() < 1e-7,
        "LP infeasible");
    t[obj][ncol]
}

fn locked_value(s: &Solver, model: &Model) -> (f64, f64) {
    let bet = root_bet(s);
    (model.value(&bet), model.freq(&bet))
}

/// A fresh copy of the base solve (deterministic, so re-running it is exact).
fn rerun(iters: u32) -> Solver {
    solved(iters)
}

fn lock_with(iters: u32, mode: LockMode) -> Solver {
    let mut s = rerun(iters);
    s.lock_node(ROOT, mode, "test".into()).unwrap();
    s
}

fn avg_bet(s: &Solver) -> Vec<f64> {
    let nh = s.spot.hands[0].len();
    let node = &s.spot.tree.nodes[0];
    let sig = s.average_strategy(0, node);
    (0..nh).map(|i| sig[nh + i] as f64).collect()
}

/// IP's call probability per combo facing the bet, from the solve.
fn ip_call(s: &Solver) -> Vec<f64> {
    let idx = s.walk_path(&[PathStep::Action { index: 1 }]).unwrap().node_idx;
    let node = &s.spot.tree.nodes[idx as usize];
    let nh = s.spot.hands[1].len();
    let sig = s.average_strategy(idx, node);
    (0..nh).map(|j| sig[nh + j] as f64).collect()
}

const BASE: u32 = 400;

/// Run a full fit from the base solve and lock it.
fn full_fit(freqs: &[f32], iters: u32) -> Solver {
    let mut s = rerun(BASE);
    s.add_fit(ROOT, freqs, "fit".into()).unwrap();
    for _ in 0..iters {
        s.iterate();
    }
    s.materialize_fits().unwrap();
    s
}

#[test]
fn model_lp_reproduces_the_unconstrained_solve() {
    let base = rerun(BASE);
    let model = Model::new(&base.spot);
    let bet = avg_bet(&base);
    let (v, f) = (model.value(&bet), model.freq(&bet));
    let opt = model.optimum(f);
    assert!((opt - v).abs() < 0.01, "LP {opt} vs solved {v} at freq {f}");
}

#[test]
fn full_fit_matches_the_constrained_lp_and_beats_raking() {
    let model = Model::new(&rerun(0).spot);
    for &t in &[0.25f64, 0.75] {
        let freqs = vec![(1.0 - t) as f32, t as f32];
        let opt = model.optimum(t);
        let (rake, _) = locked_value(&lock_with(BASE, LockMode::Range { freqs: freqs.clone() }), &model);
        let (quick, _) = locked_value(&lock_with(BASE, LockMode::Fit { freqs: freqs.clone() }), &model);
        let s = full_fit(&freqs, 1500);
        let (full, ff) = locked_value(&s, &model);
        eprintln!("t={t}: lp={opt:.4} full={full:.4} quick={quick:.4} rake={rake:.4} (chips per pair, pot {POT})");
        assert!((ff - t).abs() < 1e-4, "fit locked at {ff}, target {t}");
        // within 0.02% of pot of the exact constrained optimum
        assert!(full > opt - 0.02 && full < opt + 0.005, "full fit {full} vs LP {opt}");
        // raking and the quick fit lose far more to a best response here
        assert!(full > rake + 1.0 && full > quick + 1.0, "full {full} quick {quick} rake {rake}");
    }
}

#[test]
fn quick_fit_loses_less_ev_than_raking_against_the_current_strategy() {
    let base = rerun(BASE);
    let model = Model::new(&base.spot);
    let call = ip_call(&base);
    for &t in &[0.25f64, 0.4, 0.7, 0.85] {
        let freqs = vec![(1.0 - t) as f32, t as f32];
        let rake = lock_with(BASE, LockMode::Range { freqs: freqs.clone() });
        let quick = lock_with(BASE, LockMode::Fit { freqs: freqs.clone() });
        let (vr, fr) = (model.value_vs(&root_bet(&rake), &call), model.freq(&root_bet(&rake)));
        let (vq, fq) = (model.value_vs(&root_bet(&quick), &call), model.freq(&root_bet(&quick)));
        eprintln!("t={t}: quick {vq:.4}@{fq:.4} rake {vr:.4}@{fr:.4}");
        assert!((fq - t).abs() < 1e-4 && (fr - t).abs() < 1e-4);
        assert!(vq >= vr - 1e-3, "quick {vq} below rake {vr} at {t}");
    }
}

#[test]
fn fit_converges_fast_and_its_readout_tracks_the_target() {
    let mut s = rerun(BASE);
    s.add_fit(ROOT, &[0.75, 0.25], "fit".into()).unwrap();
    for _ in 0..100 {
        s.iterate();
    }
    let v = s.fits_view();
    assert_eq!(v.len(), 1);
    assert!(v[0].max_error < 0.01, "after 100 iterations: {:?}", v[0]);
    for _ in 0..300 {
        s.iterate();
    }
    // best responses treat the fitted node as its future lock, so the usual
    // readout converges on the constrained game
    let x = s.exploitability() / POT * 100.0;
    assert!(x < 0.05, "exploitability {x}% pot");
    assert!(s.fit_max_error() < FIT_TOL);
}

const FIT_TOL: f64 = solver::fit::FIT_TOLERANCE;

#[test]
fn materialized_fit_is_one_undoable_lock_edit() {
    let mut s = rerun(BASE);
    s.add_fit(ROOT, &[0.75, 0.25], "fit".into()).unwrap();
    for _ in 0..200 {
        s.iterate();
    }
    let labels = s
        .record_lock_edit(|s| {
            let l = s.materialize_fits()?;
            Ok((l, "Fit".to_string()))
        })
        .unwrap();
    assert_eq!(labels, vec!["fit".to_string()]);
    assert!(!s.has_fits() && s.locks.contains_key(&0));
    assert_eq!(s.lock_history().undo, vec!["Fit".to_string()]);
    s.undo_lock_edit().unwrap();
    assert!(!s.locks.contains_key(&0));
}

#[test]
fn unlocking_or_hard_locking_drops_a_running_fit() {
    let mut s = rerun(50);
    s.add_fit(ROOT, &[0.5, 0.5], "fit".into()).unwrap();
    assert!(s.unlock_node(ROOT).unwrap());
    assert!(!s.has_fits());
    s.add_fit(ROOT, &[0.5, 0.5], "fit".into()).unwrap();
    s.lock_node(ROOT, LockMode::Freeze, "x".into()).unwrap();
    assert!(!s.has_fits());
}

/// Turn spot with suit isomorphism and compressed arenas: a fit on a river
/// decision below a chance node still lands on target.
#[test]
fn fit_below_a_chance_node_with_isomorphism() {
    for storage in [solver::Storage::F32, solver::Storage::Compressed] {
        let spot = Arc::new(
            Spot::new(SpotConfig {
                board: "Kh9d5c2h".to_string(),
                range_oop: "AA,KK,99,AK,KQ,QJs,JTs,T8s,76s,A5s".to_string(),
                range_ip: "AK,KQ,KJ,QQ,JJ,TT,A9s,98s,55".to_string(),
                tree: TreeConfig {
                    starting_pot: POT,
                    effective_stack: 200.0,
                    oop: [sizing(""), sizing("75"), sizing("75")],
                    ip: [sizing(""), sizing("75"), sizing("75")],
                    ..Default::default()
                },
            })
            .unwrap(),
        );
        let mut s = Solver::with_storage(spot, storage);
        for _ in 0..150 {
            s.iterate();
        }
        // turn: OOP checks, IP checks; river 3s; OOP to act
        let path = vec![
            PathStep::Action { index: 0 },
            PathStep::Action { index: 0 },
            PathStep::Card { card: "3s".into() },
        ];
        let walk = s.walk_path(&path).unwrap();
        assert_eq!(s.spot.tree.nodes[walk.node_idx as usize].player, 0);
        s.add_fit(&path, &[0.4, 0.6], "river fit".into()).unwrap();
        for _ in 0..400 {
            s.iterate();
        }
        assert!(s.exploitability() / POT * 100.0 < 0.05);
        let v = s.fits_view();
        assert!(v[0].max_error < 0.01, "{storage:?}: {:?}", v[0]);
        s.materialize_fits().unwrap();
        s.ensure_symmetric();
        let view = s.node_view(&path).unwrap();
        let hands = &view.players[0].hands;
        let (mut tot, mut bet) = (0f64, 0f64);
        for h in hands {
            if let Some(st) = &h.strategy {
                tot += h.reach as f64;
                bet += h.reach as f64 * st[1] as f64;
            }
        }
        assert!((bet / tot - 0.6).abs() < 1e-3, "{storage:?}: locked bet {}", bet / tot);
    }
}
