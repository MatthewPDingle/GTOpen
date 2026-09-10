from pathlib import Path
import difflib
import hashlib
import json

out = Path(__file__).parent
repo = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
gpu_path = 'crates/solver/src/preflop/gpu.rs'
kernel_path = 'crates/solver/src/preflop/kernels.cu'
gpu_raw = (repo / gpu_path).read_bytes()
kernel_raw = (repo / kernel_path).read_bytes()
gpu = gpu_raw.decode('utf-8').replace('\r\n','\n')
kernel = kernel_raw.decode('utf-8').replace('\r\n','\n')
assert 'template<int Q, int O>' in kernel, 'Requires opponent-count specialization.'
anchor = '.launch(LaunchConfig { block_dim: (192, 1, 1), ..Self::cfg(self.mw_nterms) }).map_err(e)?;'
assert gpu.count(anchor) == 1
def write_patch(old, new, source, name):
    patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
        fromfile=f'a/{source}', tofile=f'b/{source}'))
    (out / name).write_text(patch, encoding='utf-8', newline='\n')
for width in [96,128,160,256,384,512]:
    new = gpu.replace(anchor, anchor.replace('(192, 1, 1)', f'({width}, 1, 1)'))
    write_patch(gpu,new,gpu_path,f'terminal-{width}.patch')
start = kernel.index('extern "C" __global__ void pf_multiway_terminal(')
end = kernel.index('\n{',start)
signature = kernel[start:end]
before = 'const u32* __restrict__ val_slot, float* val)'
after = 'const u32* __restrict__ val_slot, float* __restrict__ val)'
assert signature.count(before) == 1
new_kernel = kernel[:start] + signature.replace(before,after) + kernel[end:]
write_patch(kernel,new_kernel,kernel_path,'restrict-terminal-output.patch')
test_path = 'crates/solver/tests/coupled_terminal_resources.rs'
test = (out / 'coupled_terminal_resources.rs').read_text(encoding='utf-8')
write_patch('',test,test_path,'resource-test.patch')
(out / 'sweep.json').write_text(json.dumps({
    'control_threads':192,
    'first_stage_threads':[192,128,160,256,192],
    'second_stage_optional_threads':[96],
    'low_priority_negative_controls':[384,512],
    'restrictions':'One width per candidate; no math, CDF, cache, particle or kernel edits for geometry trials.',
    'restrict_candidate':'Separate from geometry until both independently validated; then compare at retained geometry.',
    'required':'Exact all-O terminal bits and fixture arena/gap/EV parity; same memory plan; repeated wall timings.',
},indent=2)+'\n',encoding='utf-8')
(out / 'baseline.json').write_text(json.dumps({
    'gpu_source':str(repo / gpu_path),'gpu_sha256':hashlib.sha256(gpu_raw).hexdigest(),
    'kernel_source':str(repo / kernel_path),'kernel_sha256':hashlib.sha256(kernel_raw).hexdigest(),
    'scope':'Proposal generation only; no active writes, compile or hardware jobs.',
},indent=2)+'\n',encoding='utf-8')
assert (repo / gpu_path).read_bytes() == gpu_raw and (repo / kernel_path).read_bytes() == kernel_raw
print('Generated independent terminal geometry/restrict/resource proposals; active files untouched.')
