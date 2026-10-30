"""Preserve mixed newline bytes in one existing continuation source."""
import ast, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
old = ROOT / 'runs/E115-source'
assert not (old / 'manifest.json').exists()
assert set(p.name for p in (old / 'candidate').iterdir()) == {'arena.rs', 'mod.rs'}
source = (ROOT / 'runs/E115-make-source.py').read_text(encoding='utf-8')
source = source.replace("H = ROOT / 'runs/E115-source'", "H = ROOT / 'runs/E115-source-v2'")
source = source.replace("assert base.read_bytes() == originals[name].encode('utf-8')", "assert base.read_bytes().decode('utf-8').replace('\\r\\n', '\\n') == originals[name]")
old_write = """    with candidate.open('x', encoding='utf-8', newline='\\n') as f:
        f.write(text)"""
new_write = """    if name == 'continuation.rs':
        before = b'GpuSolver::new_with_budget(host,budget.checked_sub(metadata_bytes)'
        after = b'GpuSolver::new_original_layout(host,budget.checked_sub(metadata_bytes)'
        data = base.read_bytes()
        assert data.count(before) == 1
        data = data.replace(before, after)
        assert data.decode('utf-8').replace('\\r\\n', '\\n') == text
        with candidate.open('xb') as f:
            f.write(data)
    else:
        with candidate.open('x', encoding='utf-8', newline='\\n') as f:
            f.write(text)"""
assert source.count(old_write) == 1
source = source.replace(old_write, new_write)
ast.parse(source)
dest = ROOT / 'runs/E115-make-source-v2.py'
with dest.open('x', encoding='utf-8', newline='\n') as f:
    f.write(source)
h.save(old / 'generation-failure.json', {
    'at': h.now(), 'reason': 'Byte assertion discovered original continuation.rs uses mixed CRLF/LF. Generation stopped before manifest, compilation or activation. Initial partial output preserved.',
    'old_generator_sha256': h.sha(ROOT / 'runs/E115-make-source.py'),
    'repair_generator_sha256': h.sha(dest),
    'retained_partial_sha256': {str(p): h.sha(p) for p in old.rglob('*.rs')},
    'unchanged_solver_form_only_verbatim_original_newline_preservation': True,
    'source_activation_compilation_CUDA_solver_timing_runs': 0,
})
print(h.sha(dest), flush=True)
