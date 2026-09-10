from pathlib import Path
import difflib
import hashlib
import json

root = Path(r'T:\Dev\GTOpen')
out = Path(__file__).parent
src = root / 'crates/solver/src/preflop/multiway.rs'
old = src.read_text(encoding='utf-8')
new = old

def replace(text, before, after):
    assert text.count(before) == 1, (before[:80], text.count(before))
    return text.replace(before, after)

new = replace(new, 'pub struct CoupledDeck {', '''// Q-point Gauss-Legendre integrates through polynomial degree 2Q-1.
// These are the same two-/three-/four-point constants used by the GPU,
// retained as f64 here; zero or one opponent needs only the midpoint rule.
const QUAD_T1: [f64; 1] = [0.5];
const QUAD_W1: [f64; 1] = [1.0];
const QUAD_T2: [f64; 2] = [0.211324865405187, 0.788675134594813];
const QUAD_W2: [f64; 2] = [0.5, 0.5];
const QUAD_T3: [f64; 3] = [0.112701665379258, 0.5, 0.887298334620742];
const QUAD_W3: [f64; 3] = [0.277777777777778, 0.444444444444444, 0.277777777777778];
const QUAD_T4: [f64; 4] = [0.069431844202974, 0.330009478207572, 0.669990521792428, 0.930568155797026];
const QUAD_W4: [f64; 4] = [0.173927422568727, 0.326072577431273, 0.326072577431273, 0.173927422568727];

pub struct CoupledDeck {''')
new = replace(new, '''    /// Integrating product(less + t*equal) splits any tied pot exactly. Five
    /// Gauss points integrate degree <=8 (up to nine seats), without sampling ties.
    pub fn equities(&self, opponents: &[Vec<f32>]) -> [f64; NUM_CLASSES] {
        assert!(opponents.len() <= 8);
        let mut sums''', '''    /// Integrating product(less + t*equal) splits any tied pot exactly.
    /// Use the smallest Gauss rule exact for the number of opponents. This
    /// preserves the latent game and f64 arithmetic, not bitwise rounding.
    pub fn equities(&self, opponents: &[Vec<f32>]) -> [f64; NUM_CLASSES] {
        assert!(opponents.len() <= 8);
        match opponents.len() {
            0..=1 => self.equities_with_rule(opponents, QUAD_T1, QUAD_W1),
            2..=3 => self.equities_with_rule(opponents, QUAD_T2, QUAD_W2),
            4..=5 => self.equities_with_rule(opponents, QUAD_T3, QUAD_W3),
            6..=7 => self.equities_with_rule(opponents, QUAD_T4, QUAD_W4),
            _ => self.equities_with_rule(opponents, QUAD_T, QUAD_W),
        }
    }

    fn equities_with_rule<const Q: usize>(
        &self, opponents: &[Vec<f32>], points: [f64; Q], weights: [f64; Q],
    ) -> [f64; NUM_CLASSES] {
        let mut sums''')
new = replace(new, '                let mut values = [1.0; 5];', '                let mut values = [1.0; Q];')
new = replace(new, '''                    for k in 0..5 {
                        values[k] *= less + QUAD_T[k] * equal;''', '''                    for k in 0..Q {
                        values[k] *= less + points[k] * equal;''')
new = replace(new, '                sums[h] += values.iter().zip(QUAD_W).map(|(v, w)| v * w).sum::<f64>();',
    '                sums[h] += values.iter().zip(weights).map(|(v, w)| v * w).sum::<f64>();')

prefix = '    /// All hero classes against normalized independent opponent class weights.'
start = old.index(prefix)
end = old.index('\n}\n\n#[cfg(test)]', start)
original_method = old[start:end]
reference = original_method.replace('    pub fn equities(', '    fn old_five_point_equities(')
# Make the reference a test-only inherent method containing the exact old body,
# so the comparisons do not accidentally share the new quadrature helper.
reference_impl = '\n    impl CoupledDeck {\n' + '\n'.join('    ' + line for line in reference.splitlines()) + '\n    }\n'
tests = (out / 'tests.rs').read_text(encoding='utf-8')
anchor = '    #[test]\n    fn coupled_payoffs_flow_through_cfr_and_charge_rake_once() {'
with_tests = replace(new, anchor, reference_impl + '\n' + tests + '\n' + anchor)
def patch(a, b):
    return ''.join(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
        fromfile='a/crates/solver/src/preflop/multiway.rs',
        tofile='b/crates/solver/src/preflop/multiway.rs'))
(out / 'cpu-quadrature.patch').write_bytes(patch(old, new).encode('utf-8'))
(out / 'tests.patch').write_bytes(patch(new, with_tests).encode('utf-8'))
(out / 'combined.patch').write_bytes(patch(old, with_tests).encode('utf-8'))
(out / 'multiway.rs').write_bytes(with_tests.replace('\n', '\r\n').encode('utf-8'))
(out / 'baseline-sha256.json').write_text(json.dumps({'multiway.rs': hashlib.sha256(src.read_bytes()).hexdigest()}, indent=2), encoding='utf-8')
print('CPU quadrature proposal generated; no production sources changed.')
