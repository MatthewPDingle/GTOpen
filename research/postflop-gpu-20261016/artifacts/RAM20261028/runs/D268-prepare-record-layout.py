"""Freeze one CPU-only Rust padding capability check, not a solver candidate."""
import ast, re, shutil, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists()
H = ROOT / 'runs/D268-record-layout'
H.mkdir(exist_ok=False)
arena = h.REPO / 'crates/solver/src/gpu/arena.rs'
original = arena.read_text(encoding='utf-8')
definitions = {}
for name in ['ActiveBlock', 'InactiveBlock']:
    matches = re.findall(r'(?m)^struct ' + name + r' \{\n.*?^\}', original, flags=re.S)
    assert len(matches) == 1
    definitions[name] = matches[0]
source = '#![allow(dead_code)]\nuse std::mem::{size_of, align_of, offset_of};\n'
for name, definition in definitions.items():
    source += definition.replace('struct ' + name, 'struct Baseline' + name) + '\n'
    assert definition.count('    node: u32,') == 1
    changed = definition.replace('struct ' + name, 'struct Proposed' + name)
    changed = changed.replace('    node: u32,', '    node: u32,\n    device_node: u32,')
    source += changed + '\n'
source += 'fn main() {\n'
for name, fields in [('ActiveBlock', ['node', 'host', 'device', 'len']),
                     ('InactiveBlock', ['node', 'host', 'len', 'initial'])]:
    for arm in ['Baseline', 'Proposed']:
        ty = arm + name
        fs = fields + (['device_node'] if arm == 'Proposed' else [])
        source += 'println!("D268_LAYOUT|' + ty + '|{}|{}' + '|{}' * len(fs) + '", '
        source += ', '.join(['size_of::<' + ty + '>()', 'align_of::<' + ty + '>()']
                            + ['offset_of!(' + ty + ', ' + f + ')' for f in fs]) + ');\n'
source += '}\n'
with (H / 'layout.rs').open('x', encoding='utf-8', newline='\n') as f:
    f.write(source)
runner = ROOT / 'runs/D268-execute-record-layout.py'
ast.parse(runner.read_text(encoding='utf-8'))
protocol = {
    'id': 'D268', 'at': h.now(), 'status': 'FROZEN_PRE_RUST_RECORD_LAYOUT_ONLY',
    'source_sha256': h.sha(H / 'layout.rs'),
    'input_sha256': {str(p): h.sha(p) for p in [Path(__file__), runner, arena, ROOT / 'epoch/common.py',
                                               ROOT / 'runs/D267b-node-order-model/protocol.json',
                                               ROOT / 'runs/D267b-node-order-model/root-report.json']},
    'compile_command': ['rustc', '--edition=2021', '-O', str(H / 'layout.rs'), '-o', str(H / 'layout.exe')],
    'required_free_bytes': 66 * 1024**3,
    'prospective_gate': {
        'baseline_sizes': {'ActiveBlock': 32, 'InactiveBlock': 40},
        'allowed_proposed_size_growth_bytes': 0,
        'alignment': 8,
        'node_and_device_node_distinct_u32_in_bounds': True,
    },
    'scope': 'Verbatim accepted private record definitions and one proposed additional u32 device_node field; Rust native default layout on actual compiler. One standalone compiler and one CPU-only layout helper. No cargo, solver construction, CUDA API/context/kernel/solve, timing or production source changes. This proves record padding only, not complete GpuSolver/ArenaLayout type sizes, material cost, locks/all callers or candidate feasibility.',
    'failure_rule': 'Record growth or alignment/overlap failure declines this exact field form before any solver prototype. No alternate field placement or packing rescue.',
}
h.save(H / 'protocol.json', protocol)
dst = h.ar.DASHBOARD / 'evidence' / H.name / 'protocol.json'
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(H / 'protocol.json', dst)
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + H.name + '/protocol.json', timeout=20) as z:
    assert z.read() == (H / 'protocol.json').read_bytes()
print(h.sha(H / 'protocol.json'), flush=True)
