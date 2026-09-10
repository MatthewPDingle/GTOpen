from pathlib import Path
import difflib

out = Path(__file__).parent
gpu = (out / 'gpu.rs').read_text(encoding='utf-8')
tests = (out / 'tests.rs').read_text(encoding='utf-8')
anchor = '    fn legacy_solver(cfg: PreflopConfig, eq: Arc<crate::preflop::equity::EquityTable>) -> Result<PreflopSolver, String> {'
assert gpu.count(anchor) == 1
changed = gpu.replace(anchor, tests + '\n' + anchor)
patch = difflib.unified_diff(gpu.splitlines(True), changed.splitlines(True),
    fromfile='a/crates/solver/src/preflop/gpu.rs',
    tofile='b/crates/solver/src/preflop/gpu.rs')
(out / 'tests.patch').write_bytes(''.join(patch).encode('utf-8'))
print('Tests-only patch generated against active-slots proposal; no production files changed.')
