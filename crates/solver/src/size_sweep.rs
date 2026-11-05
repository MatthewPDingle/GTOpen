//! Size-sweep reports ("dynamic sizing"): which single size of ONE bet is
//! best on a board, found by solving one tree per candidate size.
//!
//! The decision swept is the first bet of one player on the spot's root
//! street (e.g. IP's flop c-bet after a check). Every other bet, raise and
//! later street keeps the report's normal menu. Each candidate is an
//! ordinary single-size solve; the size whose solve gives the choosing
//! player the highest root EV wins.
//!
//! Solver noise matters: EV gaps between neighbouring sizes are often a few
//! tenths of a percent of the pot, the same order as a report's convergence
//! target. So two sizes TIE when their EV gap is within the two solves'
//! combined exploitability, and a board reports the whole tie band
//! ("anything 33 to 75% is fine here") instead of forcing a winner.
//!
//! This module is the pure math (no solving): the golden-section refinement
//! between the best grid size's neighbours, the per-board verdict, and the
//! all-board summary (EV lost by always using one fixed size). The server's
//! report runner drives it with real solves.

use serde::{Deserialize, Serialize};

/// Default candidate sizes, % pot.
pub const DEFAULT_SIZES: [f64; 5] = [25.0, 33.0, 50.0, 75.0, 125.0];
/// Default convergence target for sweep solves, % pot (tighter than the
/// 0.35% report default, because size EV gaps are that small).
pub const DEFAULT_TARGET: f64 = 0.15;
/// Default number of golden-section refinement solves per board.
pub const DEFAULT_REFINE: usize = 3;
/// Refinement stops once the bracket's outer sizes are within this ratio
/// (e.g. 40% vs 45% pot): finer than that is below what the solves resolve.
pub const MIN_BRACKET_RATIO: f64 = 1.12;
/// Refined sizes are rounded to this step, % pot.
pub const SIZE_STEP: f64 = 0.5;

/// One solved candidate size on one board.
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct SizePoint {
    /// Bet size, % pot.
    pub size: f64,
    /// Root EV of the choosing player, % of the starting pot.
    pub ev_pct: f64,
    /// Exploitability of this solve, % of the starting pot.
    pub exploit_pct: f64,
    /// True for golden-section refinement points (not on the grid).
    #[serde(default)]
    pub refined: bool,
}

/// The per-board answer.
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Verdict {
    /// Highest-EV size over every evaluated point (grid + refined).
    pub best: f64,
    pub best_ev_pct: f64,
    /// Highest-EV GRID size (the one a fixed-menu player would pick).
    pub best_grid: f64,
    /// Every evaluated size whose EV is within the combined exploitability
    /// of the best one, ascending. Always contains `best`.
    pub ties: Vec<f64>,
    /// [smallest, largest] tied size.
    pub band: [f64; 2],
    /// The best grid size is the smallest or largest candidate, so the true
    /// optimum may lie outside the grid and refinement was skipped.
    pub edge: bool,
}

/// Sort ascending, drop non-finite / non-positive values and duplicates
/// (within 1e-6).
pub fn normalize_sizes(sizes: &[f64]) -> Vec<f64> {
    let mut v: Vec<f64> = sizes
        .iter()
        .copied()
        .filter(|s| s.is_finite() && *s > 0.0)
        .collect();
    v.sort_by(|a, b| a.partial_cmp(b).unwrap());
    v.dedup_by(|a, b| (*a - *b).abs() < 1e-6);
    v
}

/// The size token the tree builder parses ("33", "12.5").
pub fn size_token(size: f64) -> String {
    let r = (size * 1000.0).round() / 1000.0;
    if (r - r.round()).abs() < 1e-9 {
        format!("{}", r.round() as i64)
    } else {
        format!("{r}")
    }
}

/// A file-name-safe label for a size ("33", "12_5").
pub fn size_label(size: f64) -> String {
    size_token(size).replace('.', "_")
}

fn round_step(x: f64) -> f64 {
    (x / SIZE_STEP).round() * SIZE_STEP
}

fn argmax(points: &[SizePoint]) -> Option<usize> {
    let mut best: Option<usize> = None;
    for (i, p) in points.iter().enumerate() {
        if best.is_none_or(|b| p.ev_pct > points[b].ev_pct) {
            best = Some(i);
        }
    }
    best
}

/// Golden-section refinement around the best grid size.
///
/// `points` holds the solved grid (any order). If the best grid size has a
/// neighbour on both sides, the bracket [left, best, right] is narrowed with
/// up to `steps` extra solves, each probing the golden point (in log-size,
/// since bet sizes are compared multiplicatively) of the wider half. Probes
/// are rounded to `SIZE_STEP` and the search stops early when the bracket
/// is narrower than `MIN_BRACKET_RATIO` or a probe repeats a solved size.
/// Each new point is appended to `points` with `refined = true`.
///
/// Returns whether the best grid size was at an edge (no refinement).
pub fn refine<E>(
    points: &mut Vec<SizePoint>,
    steps: usize,
    mut eval: impl FnMut(f64) -> Result<SizePoint, E>,
) -> Result<bool, E> {
    let mut grid: Vec<SizePoint> = points.clone();
    grid.sort_by(|a, b| a.size.partial_cmp(&b.size).unwrap());
    let Some(bi) = argmax(&grid) else {
        return Ok(false);
    };
    if bi == 0 || bi + 1 == grid.len() {
        return Ok(grid.len() > 1);
    }
    // bracket: (size, ev) triples, a < b < c, f(b) >= f(a), f(c)
    let (mut a, mut b, mut c) = (grid[bi - 1].clone(), grid[bi].clone(), grid[bi + 1].clone());
    const R: f64 = 0.381_966_011_250_105; // 2 - golden ratio
    for _ in 0..steps {
        if c.size / a.size < MIN_BRACKET_RATIO {
            break;
        }
        let (la, lb, lc) = (a.size.ln(), b.size.ln(), c.size.ln());
        let right = lc - lb >= lb - la;
        let x = if right {
            lb + R * (lc - lb)
        } else {
            lb - R * (lb - la)
        };
        let size = round_step(x.exp());
        if points.iter().any(|p| (p.size - size).abs() < 1e-6) || size <= a.size || size >= c.size {
            break;
        }
        let mut p = eval(size)?;
        p.size = size;
        p.refined = true;
        points.push(p.clone());
        if p.ev_pct > b.ev_pct {
            if right {
                a = b;
            } else {
                c = b;
            }
            b = p;
        } else if right {
            c = p;
        } else {
            a = p;
        }
    }
    Ok(false)
}

/// The board's verdict over every evaluated point (grid points have
/// `refined = false`); `edge` is what `refine` returned.
pub fn verdict(points: &[SizePoint], edge: bool) -> Option<Verdict> {
    let bi = argmax(points)?;
    let best = &points[bi];
    let grid_pts: Vec<&SizePoint> = points.iter().filter(|p| !p.refined).collect();
    let best_grid = grid_pts
        .iter()
        .copied()
        .max_by(|a, b| a.ev_pct.partial_cmp(&b.ev_pct).unwrap())
        .unwrap_or(best);
    let mut ties: Vec<f64> = points
        .iter()
        .filter(|p| {
            best.ev_pct - p.ev_pct <= best.exploit_pct.max(0.0) + p.exploit_pct.max(0.0) + 1e-9
        })
        .map(|p| p.size)
        .collect();
    ties.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let band = [ties[0], *ties.last().unwrap()];
    Some(Verdict {
        best: best.size,
        best_ev_pct: best.ev_pct,
        best_grid: best_grid.size,
        ties,
        band,
        edge,
    })
}

/// One board of a sweep, as the summary reads it.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BoardSweep {
    pub board: String,
    pub weight: u32,
    pub points: Vec<SizePoint>,
    pub verdict: Verdict,
}

/// One fixed grid size across every board.
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct FixedSize {
    pub size: f64,
    /// Weighted mean EV lost by always using this size instead of each
    /// board's best evaluated size (grid + refined), % pot.
    pub ev_lost_pct: f64,
    /// Same, against each board's best GRID size.
    pub ev_lost_vs_grid_pct: f64,
    /// Weighted share of boards where this is the best grid size.
    pub best_share: f64,
    /// Weighted share of boards where this size is in the tie band.
    pub tie_share: f64,
}

/// All-board summary of a sweep.
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Summary {
    pub boards: usize,
    pub fixed: Vec<FixedSize>,
    /// Weighted mean EV gained by the refined best over the best grid
    /// size, % pot (how much the golden-section search bought).
    pub refine_gain_pct: f64,
    /// Weighted share of boards where every grid size ties.
    pub all_tie_share: f64,
}

pub fn summarize(grid: &[f64], boards: &[BoardSweep]) -> Summary {
    let mut wsum = 0f64;
    let mut fixed: Vec<FixedSize> = grid
        .iter()
        .map(|&size| FixedSize {
            size,
            ev_lost_pct: 0.0,
            ev_lost_vs_grid_pct: 0.0,
            best_share: 0.0,
            tie_share: 0.0,
        })
        .collect();
    let (mut gain, mut all_tie) = (0f64, 0f64);
    let mut n = 0usize;
    for b in boards {
        let w = b.weight as f64;
        let grid_best = b
            .points
            .iter()
            .filter(|p| !p.refined)
            .map(|p| p.ev_pct)
            .fold(f64::NEG_INFINITY, f64::max);
        if !grid_best.is_finite() {
            continue;
        }
        n += 1;
        wsum += w;
        gain += w * (b.verdict.best_ev_pct - grid_best).max(0.0);
        let mut ties_all = true;
        for f in fixed.iter_mut() {
            let Some(p) = b
                .points
                .iter()
                .find(|p| !p.refined && (p.size - f.size).abs() < 1e-6)
            else {
                ties_all = false;
                continue;
            };
            f.ev_lost_pct += w * (b.verdict.best_ev_pct - p.ev_pct).max(0.0);
            f.ev_lost_vs_grid_pct += w * (grid_best - p.ev_pct).max(0.0);
            if (b.verdict.best_grid - f.size).abs() < 1e-6 {
                f.best_share += w;
            }
            if b.verdict.ties.iter().any(|t| (t - f.size).abs() < 1e-6) {
                f.tie_share += w;
            } else {
                ties_all = false;
            }
        }
        if ties_all {
            all_tie += w;
        }
    }
    if wsum > 0.0 {
        for f in fixed.iter_mut() {
            f.ev_lost_pct /= wsum;
            f.ev_lost_vs_grid_pct /= wsum;
            f.best_share /= wsum;
            f.tie_share /= wsum;
        }
        gain /= wsum;
        all_tie /= wsum;
    }
    Summary {
        boards: n,
        fixed,
        refine_gain_pct: gain,
        all_tie_share: all_tie,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn pt(size: f64, ev: f64) -> SizePoint {
        SizePoint {
            size,
            ev_pct: ev,
            exploit_pct: 0.0,
            refined: false,
        }
    }

    /// Smooth single-peaked EV curve in log-size with its peak at `peak`.
    fn curve(peak: f64) -> impl Fn(f64) -> SizePoint {
        move |s: f64| SizePoint {
            size: s,
            ev_pct: 50.0 - 4.0 * (s.ln() - peak.ln()).powi(2),
            exploit_pct: 0.0,
            refined: false,
        }
    }

    #[test]
    fn tokens_and_labels() {
        assert_eq!(size_token(33.0), "33");
        assert_eq!(size_token(12.5), "12.5");
        assert_eq!(size_label(12.5), "12_5");
        assert_eq!(
            normalize_sizes(&[75.0, 25.0, f64::NAN, -1.0, 25.0, 33.0]),
            vec![25.0, 33.0, 75.0]
        );
    }

    #[test]
    fn refinement_closes_in_on_an_interior_peak() {
        let f = curve(42.0);
        let mut points: Vec<SizePoint> = DEFAULT_SIZES.iter().map(|&s| f(s)).collect();
        let mut calls = 0;
        let edge = refine(&mut points, 6, |s| -> Result<SizePoint, ()> {
            calls += 1;
            Ok(f(s))
        })
        .unwrap();
        assert!(!edge);
        assert!(calls >= 2 && calls <= 6, "{calls} probes");
        let v = verdict(&points, edge).unwrap();
        assert_eq!(v.best_grid, 50.0);
        assert!((v.best - 42.0).abs() <= 3.0, "refined best {}", v.best);
        assert!(v.best_ev_pct >= f(50.0).ev_pct);
        assert!(points
            .iter()
            .filter(|p| p.refined)
            .all(|p| p.size > 33.0 && p.size < 75.0));
    }

    #[test]
    fn refinement_respects_the_step_budget() {
        let f = curve(60.0);
        let mut points: Vec<SizePoint> = DEFAULT_SIZES.iter().map(|&s| f(s)).collect();
        refine(&mut points, 1, |s| -> Result<SizePoint, ()> { Ok(f(s)) }).unwrap();
        assert_eq!(points.iter().filter(|p| p.refined).count(), 1);
        let mut points: Vec<SizePoint> = DEFAULT_SIZES.iter().map(|&s| f(s)).collect();
        refine(&mut points, 0, |s| -> Result<SizePoint, ()> { Ok(f(s)) }).unwrap();
        assert_eq!(points.len(), DEFAULT_SIZES.len());
    }

    #[test]
    fn an_edge_optimum_skips_refinement_and_is_flagged() {
        // polarized river: EV rises with size, best is the largest candidate
        let mut points: Vec<SizePoint> = DEFAULT_SIZES.iter().map(|&s| pt(s, s / 10.0)).collect();
        let edge = refine(&mut points, 3, |_| -> Result<SizePoint, ()> {
            panic!("no probe at an edge")
        })
        .unwrap();
        assert!(edge);
        let v = verdict(&points, edge).unwrap();
        assert_eq!(v.best, 125.0);
        assert!(v.edge);
    }

    #[test]
    fn ties_use_combined_exploitability() {
        let mut points = vec![
            pt(25.0, 10.0),
            pt(33.0, 10.25),
            pt(50.0, 10.4),
            pt(75.0, 10.1),
            pt(125.0, 9.0),
        ];
        for p in points.iter_mut() {
            p.exploit_pct = 0.15;
        }
        let v = verdict(&points, false).unwrap();
        assert_eq!(v.best, 50.0);
        // 33 (gap 0.15) and 75 (gap 0.3) are within 0.15 + 0.15; 25 (0.4) is not
        assert_eq!(v.ties, vec![33.0, 50.0, 75.0]);
        assert_eq!(v.band, [33.0, 75.0]);
    }

    #[test]
    fn summary_weights_boards_and_measures_fixed_size_losses() {
        let grid = [33.0, 75.0];
        let b1 = BoardSweep {
            board: "AhKs2d".into(),
            weight: 3,
            points: vec![pt(33.0, 10.0), pt(75.0, 12.0)],
            verdict: verdict(&[pt(33.0, 10.0), pt(75.0, 12.0)], true).unwrap(),
        };
        let pts2 = vec![
            pt(33.0, 20.0),
            pt(75.0, 19.0),
            SizePoint {
                refined: true,
                ..pt(45.0, 20.5)
            },
        ];
        let b2 = BoardSweep {
            board: "7c6c5d".into(),
            weight: 1,
            verdict: verdict(&pts2, false).unwrap(),
            points: pts2,
        };
        let s = summarize(&grid, &[b1, b2]);
        assert_eq!(s.boards, 2);
        // always-33: loses 2.0 on b1 (w3) and 0.5 on b2 (w1) -> 6.5/4
        assert!((s.fixed[0].ev_lost_pct - 6.5 / 4.0).abs() < 1e-9);
        assert!((s.fixed[0].ev_lost_vs_grid_pct - 6.0 / 4.0).abs() < 1e-9);
        // always-75: 0 on b1, 1.5 on b2 -> 1.5/4
        assert!((s.fixed[1].ev_lost_pct - 1.5 / 4.0).abs() < 1e-9);
        assert!((s.fixed[1].best_share - 0.75).abs() < 1e-9);
        assert!((s.fixed[0].best_share - 0.25).abs() < 1e-9);
        assert!((s.refine_gain_pct - 0.5 / 4.0).abs() < 1e-9);
    }
}
