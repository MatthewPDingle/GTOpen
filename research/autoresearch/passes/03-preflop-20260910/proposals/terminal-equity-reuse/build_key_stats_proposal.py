from pathlib import Path
import difflib
import hashlib
import json

out = Path(__file__).parent
source = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910\crates\solver\src\preflop\gpu.rs')
raw = source.read_bytes()
old = raw.decode('utf-8').replace('\r\n', '\n')
helper = (out / 'key-stats.rs').read_text(encoding='utf-8')
anchor = 'impl PreflopGpu {\n    pub fn new(s: &PreflopSolver, budget_mb: u64) -> Result<Self, String> {\n'
assert old.count(anchor) == 1
call_anchor = '        let use_multiway = !mw_terms.is_empty();\n'
assert old.count(call_anchor) == 1
call = '''        if use_multiway && std::env::var("PREFLOP_MW_KEY_STATS").as_deref() == Ok("1") {
            multiway_terminal_key_stats(s, &reach_src, &mw_terms);
        }
'''
new = old.replace(anchor, helper.rstrip() + '\n\n' + anchor)
new = new.replace(call_anchor, call_anchor + call)
patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
    fromfile='a/crates/solver/src/preflop/gpu.rs', tofile='b/crates/solver/src/preflop/gpu.rs'))
(out / 'key-stats.patch').write_text(patch, encoding='utf-8', newline='\n')
(out / 'key-stats-baseline.json').write_text(json.dumps({
    'source': str(source), 'sha256': hashlib.sha256(raw).hexdigest(),
    'scope': 'Host-only count instrumentation proposal; no source edits/builds/GPU execution.',
}, indent=2) + '\n', encoding='utf-8')
assert source.read_bytes() == raw, 'Active source changed while producing proposal; regenerate against its final version.'
print('Generated key-stats.patch; active source untouched.')
