from pathlib import Path
import difflib
import hashlib

out = Path(__file__).parent
src = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910\crates\solver\src\preflop\gpu.rs')
old = src.read_text(encoding='utf-8')
tests = (out / 'boundary_tests.rs').read_text(encoding='utf-8')
anchor = '    #[test]\n    fn coupled_terminal_matches_cpu_across_particle_batches() {'
assert old.count(anchor) == 1
new = old.replace(anchor, tests + '\n' + anchor)
patch = difflib.unified_diff(old.splitlines(True), new.splitlines(True),
    fromfile='a/crates/solver/src/preflop/gpu.rs', tofile='b/crates/solver/src/preflop/gpu.rs')
(out / 'boundary-tests.patch').write_bytes(''.join(patch).encode('utf-8'))
(out / 'boundary-tests-baseline-sha256.txt').write_text(hashlib.sha256(src.read_bytes()).hexdigest() + '\n', encoding='utf-8')
print('Actual GPU budget-boundary test proposal generated; no source edits.')
