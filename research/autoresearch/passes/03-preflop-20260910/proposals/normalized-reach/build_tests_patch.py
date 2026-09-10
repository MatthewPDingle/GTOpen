from pathlib import Path
import difflib
import hashlib

out = Path(__file__).parent
src = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910\crates\solver\src\preflop\gpu.rs')
old = src.read_text(encoding='utf-8')
tests = (out / 'tests.rs').read_text(encoding='utf-8')
anchor = '    fn legacy_solver(cfg: PreflopConfig, eq: Arc<crate::preflop::equity::EquityTable>) -> Result<PreflopSolver, String> {'
assert old.count(anchor) == 1
new = old.replace(anchor, tests + '\n' + anchor)
patch = difflib.unified_diff(old.splitlines(True), new.splitlines(True),
    fromfile='a/crates/solver/src/preflop/gpu.rs', tofile='b/crates/solver/src/preflop/gpu.rs')
(out / 'tests.patch').write_bytes(''.join(patch).encode('utf-8'))
(out / 'tests-baseline-sha256.txt').write_text(hashlib.sha256(src.read_bytes()).hexdigest() + '\n', encoding='utf-8')
print('Normalized-reach test-only patch generated; no source edits.')
