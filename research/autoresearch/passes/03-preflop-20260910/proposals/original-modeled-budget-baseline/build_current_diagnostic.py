from pathlib import Path
import difflib
import hashlib
import json

out = Path(__file__).parent
source = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910\crates\solver\src\preflop\gpu.rs')
raw = source.read_bytes()
old = raw.decode('utf-8').replace('\r\n', '\n')
baseline = (out / 'gpu.rs').read_text(encoding='utf-8')
marker = '        if std::env::var("PREFLOP_GPU_LAYOUT_STATS").as_deref() == Ok("1") {\n'
assert marker not in old, 'Current diagnostic already present; do not duplicate it.'
start = baseline.index(marker)
end = baseline.index('        Ok(PreflopGpu {\n', start)
diag = baseline[start:end]
replacements = {
    '"baseline": "1b8fc3f_forced_budget_only"': '"baseline": "optimized_8e7e4b0"',
    '"cdf_slots": if use_multiway { mw_plan.blocks.len() } else { 0 }':
        '"cdf_slots": if use_multiway { compact.capacity } else { 0 }',
    '"compact_cdf": false, "normalized_cdf": false':
        '"compact_cdf": compact.enabled, "normalized_cdf": use_mw_normalized',
}
for a,b in replacements.items():
    assert diag.count(a) == 1, a
    diag = diag.replace(a,b)
anchor = '        Ok(PreflopGpu {\n'
assert old.count(anchor) == 1
new = old.replace(anchor, diag + anchor)
assert new.replace(diag, '', 1) == old
patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
    fromfile='a/crates/solver/src/preflop/gpu.rs', tofile='b/crates/solver/src/preflop/gpu.rs'))
(out / 'current-layout-diagnostic.patch').write_text(patch, encoding='utf-8', newline='\n')
(out / 'current-layout-diagnostic.rs').write_text(diag, encoding='utf-8', newline='\n')
(out / 'current-layout-baseline.json').write_text(json.dumps({
    'source': str(source), 'sha256': hashlib.sha256(raw).hexdigest(),
    'schema_matches': 'Original corrected gpu.rs PREFLOP_GPU_LAYOUT_STATS record, same exact field names.',
    'differences': 'baseline label, compact capacity versus union slots, actual compact/normalized flags',
    'scope': 'Host metadata log only; no accounting, kernels, layouts or source edits.',
}, indent=2)+'\n', encoding='utf-8')
assert source.read_bytes() == raw, 'Active source changed while generating; regenerate.'
print('Generated matching current layout diagnostic patch; active source untouched.')
