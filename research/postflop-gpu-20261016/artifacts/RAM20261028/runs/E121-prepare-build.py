"""Fresh integrated builds after both entire direct terminal matrices pass."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h

base = h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists()
assert not (ROOT / 'epoch-sequence.lock').exists()
F = ROOT / 'comparisons/D298-hand-word-fold/report.json'
G = ROOT / 'comparisons/E121-kernel-control-root-check/report.json'
fold = h.read(F)
show = h.read(G)
assert fold['status'] == 'pass_scoped_encoded_input_full_raw_equivalence'
assert fold['cases'] == 380 and fold['kernel_launches'] == 760
assert show['status'] == 'pass_scoped_encoded_hand_word_full_raw_equivalence'
assert show['inventory']['comparison_pairs'] == 13300 and show['kernel_launches'] == 26600
assert h.read(ROOT / 'runs/E121-direct-owner/complete.json')['all_owned_children_terminal']
assert h.read(ROOT / 'runs/E121-direct-execution/complete.json')['all_owned_children_terminal']
S = ROOT / 'runs/E121-source'
manifest = h.read(S / 'manifest.json')
owned = manifest['owned']
assert set(owned) == {'crates/solver/src/gpu/kernels.cu', 'crates/solver/src/gpu/mod.rs'}
H = ROOT / 'runs/E121-build-plan'
H.mkdir(exist_ok=False)
parent = ROOT / 'runs/E114-build.py'
code = parent.read_text().replace('E114', 'E121').replace('e114', 'e121')
code = code.replace("b'float acc0 = 0.f, acc1 = 0.f;' in data", "b'hand_word >> 12' in data")
code = code.replace('fixed paired chance CUDA body', 'fixed private terminal hand-word Rust/CUDA form')
ast.parse(code)
script = ROOT / 'runs/E121-build.py'
assert not script.exists()
script.write_bytes(code.encode())
phases = [
    {'id': 'feature', 'features': 'preflop-research', 'expected_features': ['gpu', 'preflop-research'],
     'integration': False, 'outputs': {'solver': 'E121-feature-solver'}, 'target': str(ROOT / 'build-e121-final-feature')},
    {'id': 'primary', 'features': 'gpu', 'expected_features': ['gpu'], 'integration': True,
     'outputs': {'solver': 'E121-solver', 'postflop_autoresearch': 'E121-postflop_autoresearch'},
     'target': str(ROOT / 'build-e121-final-primary')}
]
for phase in phases:
    assert not Path(phase['target']).exists()
files = [Path(__file__), parent, script, S / 'manifest.json', F, G,
         ROOT / 'runs/E121-direct-owner/complete.json', ROOT / 'runs/E121-direct-execution/complete.json',
         ROOT / 'runs/E121-resource/protocol.json', ROOT / 'runs/E121-resource/report.json',
         ROOT / 'runs/E121-resource/host-encode-report.json', ROOT / 'runs/D296-hand-word-PTX/report.json',
         ROOT / 'runs/D297-hand-word-native/report.json', ROOT / 'epoch/common.py',
         ROOT / 'epoch/accepted-source.json', ROOT / 'epoch/protected-main.json',
         ROOT / 'epoch/preexisting-target-artifacts.json']
files += [Path(row[key]) for row in owned.values() for key in ['base', 'candidate']]
h.save(H / 'protocol.json', {
    'id': 'E121-final-build', 'at': h.now(), 'status': 'FROZEN_PRE_ORDINARY_CARGO_COMPILERS',
    'owned': owned, 'accepted_source_sha256': base,
    'candidate_owned_sha256': {name: row['candidate_sha256'] for name, row in owned.items()},
    'tracked_owned_paths': list(owned), 'new_owned_paths': [], 'phases': phases,
    'required_free_bytes': 80 * 1024**3, 'input_sha256': {str(path): h.sha(path) for path in files},
    'scope': 'Two fresh offline/locked integrated feature/primary Cargo builds. One frozen Rust/CUDA hand-word form. Complete original+boundary fold380pairs/760launches andshow13300pairs/26600launches exact; everyphysicalencodedword independentlydecoded, allotherinputs/wholeoutputs/guards checked. Restore accepted2sourcesaftereachcompiler. Source/publicplan/arithmetic unchanged beyondfixedprivateencoding. Showregister38to39warning/hosttemporary/packing/drop/JIT costs real. Ordinary86units theninitialfixed3pair1%strictfixture;fullrawengine/canonical/broad/material/fresh16/holdout/currentRAMcumulative/actualapp stillmandatorybeforeadoption. No source/encoding/sentinel/mask/width/helper/flags/quality/sample rescue after genuinefailure.'
})
h.custody()
print(h.sha(H / 'protocol.json'), flush=True)
