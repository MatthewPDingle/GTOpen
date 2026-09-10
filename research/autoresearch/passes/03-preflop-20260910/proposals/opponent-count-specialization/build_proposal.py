from pathlib import Path
import difflib
import hashlib
import json

out = Path(__file__).parent
source = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910\crates\solver\src\preflop\kernels.cu')
raw = source.read_bytes()
old = raw.decode('utf-8').replace('\r\n', '\n')
start = old.index('template<int Q>\n__device__ __forceinline__ float pf_multiway_sum(')
end = old.index('// Terminal values for traverser p.', start)
region = old[start:end]
assert 'const size_t* opponent_bases' in region, 'Requires accepted CDF base hoist.'
assert 'opponent_bases[nopponents++] = (size_t)cdf_slot * batch_capacity * (NC + 1);' in region
replacements = {
    'template<int Q>\n': 'template<int Q, int O>\n',
    'u32 h, int nopponents, const size_t* opponent_bases, const float* cdf,':
        'u32 h, const size_t* opponent_bases, const float* cdf,',
    '        for (int q = 0; q < nopponents; q++) {':
        '        #pragma unroll\n        for (int q = 0; q < O; q++) {',
}
new_region = region
for before, after in replacements.items():
    assert new_region.count(before) == 1, before
    new_region = new_region.replace(before, after)
dispatch_start = new_region.index('        float sum = nopponents <= 3\n')
dispatch_end = new_region.index('        float increment = ', dispatch_start)
original_dispatch = new_region[dispatch_start:dispatch_end]
assert original_dispatch.count('pf_multiway_sum<') == 4
args = 'h, opponent_bases, cdf, lower, upper, sample_start, sample_count'
lines = [
    '        // Live multiway terminals have exactly 2..8 opponents. The switch',
    '        // is block-uniform; each specialization preserves ascending q order.',
    '        float sum;',
    '        switch (nopponents) {',
]
for opponents in range(2, 8):
    quadrature = (opponents + 2) // 2
    lines.append(f'            case {opponents}: sum = pf_multiway_sum<{quadrature}, {opponents}>({args}); break;')
lines += [
    f'            default: sum = pf_multiway_sum<5, 8>({args}); break; // eight opponents',
    '        }',
]
new_region = new_region[:dispatch_start] + '\n'.join(lines) + '\n' + new_region[dispatch_end:]
new = old[:start] + new_region + old[end:]
assert new[:start] == old[:start] and new[start+len(new_region):] == old[end:]
patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
    fromfile='a/crates/solver/src/preflop/kernels.cu', tofile='b/crates/solver/src/preflop/kernels.cu'))
(out / 'implementation.patch').write_text(patch, encoding='utf-8', newline='\n')
(out / 'specialized-region.cu').write_text(new_region, encoding='utf-8', newline='\n')
(out / 'baseline.json').write_text(json.dumps({
    'source': str(source), 'sha256': hashlib.sha256(raw).hexdigest(),
    'required_base': 'Accepted terminal CDF base hoist from dea49d1',
    'scope': 'Proposal only: kernels template/opponent dispatch; no CDF or launch edits.',
}, indent=2)+'\n', encoding='utf-8')
assert source.read_bytes() == raw, 'Source changed while generating; regenerate.'
print('Generated exact opponent-count specialization proposal; active source untouched.')
