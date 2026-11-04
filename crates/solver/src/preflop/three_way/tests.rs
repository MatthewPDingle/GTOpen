use super::*;

/// A coarse table, shared by the tests (a few seconds to build).
pub(crate) fn small() -> Arc<ThreeWayTable> {
    static T: OnceLock<Arc<ThreeWayTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(ThreeWayTable::build(48))).clone()
}

fn class(label: &str) -> usize {
    (0..N).find(|&c| super::super::equity::class_label(c) == label).unwrap()
}

#[test]
fn compatible_fractions_count_jointly_dealt_combos() {
    let t = small();
    let (aa, kk, qq, aks) = (class("AA"), class("KK"), class("QQ"), class("AKs"));
    assert_eq!(t.compatible(aa, aa, aa), 0.0);
    assert_eq!(t.compatible(aa, kk, qq), 1.0);
    // Each AA combo leaves exactly one disjoint AA combo; KK is unaffected.
    assert!((t.compatible(aa, aa, kk) - 1.0 / 6.0).abs() < 1e-6);
    // Three AKs need three different suits: 4 x 3 x 2 of 64.
    assert!((t.compatible(aks, aks, aks) - 24.0 / 64.0).abs() < 1e-6);
}

#[test]
fn shares_are_symmetric_and_split_each_pot_exactly() {
    let t = small();
    for [x, y, z] in triples().into_iter().step_by(997) {
        let w = t.compatible(x, y, z);
        assert_eq!(w, t.compatible(y, z, x));
        assert_eq!(w, t.compatible(z, y, x));
        if w == 0.0 { continue; }
        assert_eq!(t.share(x, y, z), t.share(x, z, y));
        let total = t.share(x, y, z) + t.share(y, x, z) + t.share(z, x, y);
        assert!((total - 1.0).abs() < 1e-5, "{x} {y} {z}: {total}");
    }
}

#[test]
fn point_masses_read_the_table_and_ranges_weight_by_compatibility() {
    let t = small();
    let (aa, kk, qq) = (class("AA"), class("KK"), class("QQ"));
    let point = |c: usize| { let mut d = vec![0f32; N]; d[c] = 1.0; d };
    let s = t.shares(&point(kk), &point(qq));
    assert!((s[aa] - t.share(aa, kk, qq) as f64).abs() < 1e-6);
    // Against {AA, KK} half and half, AA only ever meets the KK half
    // alongside another AA one time in six: the weights must say so.
    let mut mix = vec![0f32; N];
    mix[aa] = 0.5; mix[kk] = 0.5;
    let got = t.shares(&mix, &point(qq))[aa];
    let w_aa = t.compatible(aa, aa, qq) as f64;
    let want = (0.5 * w_aa * t.share(aa, aa, qq) as f64 + 0.5 * t.share(aa, kk, qq) as f64) / (0.5 * w_aa + 0.5);
    assert!((got - want).abs() < 1e-6);
    // Impossible deals get an even third.
    assert_eq!(t.shares(&point(aa), &point(aa))[aa], 1.0 / 3.0);
}

#[test]
fn simulated_shares_approach_known_equities() {
    // AA vs KK vs QQ all in preflop: about 66.5% / 17.4% / 16.1%.
    let combos = combos();
    let (aa, kk, qq) = (class("AA"), class("KK"), class("QQ"));
    let (s, w) = simulate([qq, kk, aa], &combos, 40_000);
    assert_eq!(w, 1.0);
    let total: f32 = s.iter().sum();
    assert!((total - 1.0).abs() < 1e-5);
    assert!((s[2] - 0.665).abs() < 0.012, "AA {}", s[2]);
    assert!(s[1] > s[0], "KK {} should beat QQ {}", s[1], s[0]);
}

#[test]
fn cache_round_trips() {
    let t = small();
    let path = std::env::temp_dir().join(format!("gtopen-3way-{}.bin", std::process::id()));
    let path = path.to_str().unwrap();
    t.save(path).unwrap();
    let back = ThreeWayTable::load(path, t.samples).unwrap();
    assert!(ThreeWayTable::load(path, t.samples + 1).is_none());
    std::fs::remove_file(path).ok();
    for [x, y, z] in triples().into_iter().step_by(1009) {
        assert_eq!(back.compatible(x, y, z), t.compatible(x, y, z));
        assert!((back.share(x, y, z) - t.share(x, y, z)).abs() < 1e-6);
    }
}

mod solver {
    use super::small;
    use crate::preflop::equity::{EquityTable, NUM_CLASSES};
    use crate::preflop::{PreflopConfig, PreflopSolver, KIND_POT_SHARE};
    use std::sync::Arc;

    fn table() -> Arc<EquityTable> {
        static T: std::sync::OnceLock<Arc<EquityTable>> = std::sync::OnceLock::new();
        T.get_or_init(|| Arc::new(EquityTable::build(200))).clone()
    }

    fn game(positions: &[&str]) -> PreflopSolver {
        let n = positions.len();
        let mut posts = vec![0.0; n];
        posts[n - 2] = 0.5;
        posts[n - 1] = 1.0;
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions": positions, "posts": posts, "stack": 10.0, "limp": true,
            "open_raises": [2.5], "raise_mults": [], "max_raises": 1, "add_allin": true,
            "rake_pct": 5.0, "rake_cap": 1.0, "realization": "raw"
        })).unwrap();
        PreflopSolver::new(cfg, table()).unwrap()
    }

    fn reaches(n: usize) -> Vec<Vec<f32>> {
        (0..n).map(|q| (0..NUM_CLASSES).map(|h| ((h * 7 + q * 13) % 11) as f32 / 40.0).collect()).collect()
    }

    #[test]
    fn three_seat_pots_use_the_table_and_bigger_pots_stay_coupled() {
        let mut s = game(&["CO", "BTN", "SB", "BB"]);
        let coupled = game(&["CO", "BTN", "SB", "BB"]);
        s.set_three_way_table(small()).unwrap();
        assert_eq!(s.multiway_equity_model(), super::MODEL);
        let r = reaches(4);
        let mut checked = [false; 2];
        for (t, nd) in s.nodes.iter().enumerate() {
            if nd.kind != KIND_POT_SHARE || nd.live.count_ones() < 3 || !nd.side_pots.is_empty() { continue; }
            for p in (0..4).filter(|&p| nd.live & (1 << p) != 0) {
                let mut got = vec![0f32; NUM_CLASSES];
                s.terminal_value(t, p, &r, &mut got);
                let mut want = vec![0f32; NUM_CLASSES];
                if nd.live.count_ones() == 3 {
                    let opp: Vec<Vec<f32>> = (0..4).filter(|&q| q != p && nd.live & (1 << q) != 0).map(|q| {
                        let m: f32 = r[q].iter().sum();
                        r[q].iter().map(|x| x / m).collect()
                    }).collect();
                    let shares = small().shares(&opp[0], &opp[1]);
                    let prob: f64 = (0..4).filter(|&q| q != p).map(|q| r[q].iter().sum::<f32>() as f64).product();
                    let pot = nd.pot - s.rake_of(nd.pot);
                    for h in 0..NUM_CLASSES { want[h] = (prob * (pot * shares[h] - nd.invested[p])) as f32; }
                    checked[0] = true;
                } else {
                    coupled.terminal_value(t, p, &r, &mut want);
                    checked[1] = true;
                }
                assert_eq!(got, want, "terminal {t} seat {p}");
            }
        }
        assert_eq!(checked, [true, true]);
    }

    #[test]
    fn the_model_is_recorded_and_fixed_once_solving() {
        let mut s = game(&["BTN", "SB", "BB"]);
        s.set_three_way_table(small()).unwrap();
        s.iterate();
        assert!(s.set_multiway_equity_model("coupled_deck_v1").is_err());
        let path = std::env::temp_dir().join(format!("gtopen-3way-save-{}.gtop", std::process::id()));
        s.save_game(path.to_str().unwrap()).unwrap();
        let bytes = std::fs::read(&path).unwrap();
        std::fs::remove_file(&path).ok();
        let header = String::from_utf8_lossy(&bytes[..bytes.len().min(4096)]).to_string();
        assert!(header.contains("\"multiway_equity_model\":\"three_way_table_v1\""));
    }
}
