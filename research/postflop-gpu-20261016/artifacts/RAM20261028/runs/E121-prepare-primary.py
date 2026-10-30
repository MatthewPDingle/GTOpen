"""Freeze the first full-solve timing screen after complete direct controls."""
import ast
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h

h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists()
assert not (ROOT / 'epoch-sequence.lock').exists()
build_plan = ROOT / 'runs/E121-build-plan/protocol.json'
build = h.read(build_plan)
build_complete = ROOT / 'runs/E121-final-build/complete.json'
complete = h.read(build_complete)
assert complete['all_compilers_terminal'] and complete['native_executions'] == 0
for path, digest in complete['evidence_sha256'].items():
    h.pin(path, digest)
F = ROOT / 'comparisons/D298-hand-word-fold/report.json'
G = ROOT / 'comparisons/E121-kernel-control-root-check/report.json'
fold = h.read(F)
show = h.read(G)
assert fold['status'] == 'pass_scoped_encoded_input_full_raw_equivalence'
assert fold['cases'] == 380 and fold['kernel_launches'] == 760
assert fold['every_physical_input_checked_against_declared_encoding']
assert show['status'] == 'pass_scoped_encoded_hand_word_full_raw_equivalence'
assert show['inventory']['comparison_pairs'] == 13300 and show['kernel_launches'] == 26600
assert show['all21_input_buffers_fully_checked'] and show['encoded_same_all_words_checked_and_decoded']
assert h.read(ROOT / 'runs/E121-direct-owner/complete.json')['all_owned_children_terminal']
H = ROOT / 'runs/E121-primary-plan'
H.mkdir(exist_ok=False)
scripts = {}
for name in ['primary-native', 'primary-assess', 'primary-root-check', 'run-primary']:
    path = ROOT / 'runs' / ('E121-' + name + '.py')
    assert not path.exists()
    code = (ROOT / 'runs' / ('E114-' + name + '.py')).read_text().replace('E114', 'E121')
    ast.parse(code)
    path.write_bytes(code.encode())
    scripts[name] = path
sequence = [{'id': 'V121-unit', 'binary': 'E121-solver', 'unit': True}]
sequence += [{'id': ident, 'binary': 'E080-postflop_autoresearch' if ident.startswith('B') else 'E121-postflop_autoresearch', 'unit': False}
             for ident in ['B372', 'E121R1', 'E121R2', 'B373', 'B374', 'E121R3']]
for row in sequence:
    assert not (ROOT / 'runs' / row['id']).exists()
files = [Path(__file__), build_plan, build_complete, ROOT / 'runs/E121-build.py',
         ROOT / 'epoch/runner.py', ROOT / 'epoch/common.py', ROOT / 'epoch/exact-anchor.json',
         ROOT / 'epoch/accepted-source.json', ROOT / 'epoch/protected-main.json', ROOT / 'epoch/preexisting-target-artifacts.json',
         F, G, ROOT / 'comparisons/RAM20261028-baseline/report.json', ROOT / 'runs/E121-source/manifest.json',
         ROOT / 'runs/E121-resource/protocol.json', ROOT / 'runs/E121-resource/report.json',
         ROOT / 'runs/E121-resource/host-encode-report.json', ROOT / 'runs/D296-hand-word-PTX/report.json',
         ROOT / 'runs/D297-hand-word-native/report.json', ROOT / 'runs/E121-direct-owner/complete.json',
         ROOT / 'runs/E121-direct-execution/complete.json',
         h.REPO / 'research/postflop-gpu-20261016/qualification-policy-20261017.md'] + list(scripts.values())
for stem in ['E121-feature-solver', 'E121-solver', 'E121-postflop_autoresearch', 'E080-postflop_autoresearch']:
    exe = ROOT / 'binaries' / (stem + '.exe')
    mp = exe.with_suffix('.manifest.json')
    manifest = h.read(mp)
    h.pin(exe, manifest['binary_sha256'])
    expected = build['accepted_source_sha256'] | (build['candidate_owned_sha256'] if stem.startswith('E121') else {})
    assert manifest['source_sha256'] == expected
    files.extend([exe, mp])
adoption = [
    'Full raw engine and canonical CPU/device/wholeCFV lifecycle before adoption. Every changed private d_same word independently checked and decoded to original3fields; allotherphysicalmetadata/arrays/guards byteexact, no omittedfield/padding or tolerance.',
    'Broader supportedF32/menu/locks/save/resume/symmetric/paged/stored continuation/fallback controls. Actual hosttemporary/packing/drop/lifetime/error costs and allCPU/GPU/process/memory/capacity/graph/responsiveness/material effects qualified beforeadoption.',
    'Separately frozenfresh16:unroundedaggregate>=1%,>=13improvingpairs,positivepaired/all4block/bothorder medians andstrictfixtureguards. Fixedholdout/freshoriginalcurrentRAMcumulative/actualtemporaryapp qualification. No universal/significance/no-tradeoff claim from primary.'
]
h.save(H / 'protocol.json', {
    'id': 'E121-primary', 'at': h.now(), 'status': 'FROZEN_PRE_ORDINARY_UNITS_AND_INITIAL_TIMING',
    'measurement_epoch': 'RAM20261028', 'build_protocol_sha256': h.sha(build_plan),
    'accepted_source_sha256': build['accepted_source_sha256'], 'candidate_owned_sha256': build['candidate_owned_sha256'],
    'sequence': sequence, 'pairs': [{'baseline': 'B372', 'candidate': 'E121R1'}, {'baseline': 'B373', 'candidate': 'E121R2'}, {'baseline': 'B374', 'candidate': 'E121R3'}],
    'required_ordinary_units': 86, 'required_aggregate_gain_pct': 1.,
    'fixture_guard': 'Reject positive median slowdown AND >=2/3matchedpairs slower, no minimum slowdown percentage.',
    'excluded_samples_allowed': False, 'extension_runs_allowed': False,
    'historical_or_RAM_baseline_timing_pooling_allowed': False, 'required_free_bytes': 66 * 1024**3,
    'adoption_requirements': adoption,
    'scope': 'Sameoriginal3compressedfullcycles/16workers/defaultaffinity/.3%pot/check20/cap400/stops200/200/60/scienceanchor. Freshordinarybuilds includeactualNVRTC12.9/JIT and hostpacking/allocation/drop/upload/setup/copy/solve/fullreadback costs;Cargo/fingerprints/finaldestruction/browser/API/savingexcluded. Fullfold380pairs/760launches+show13300pairs/26600launches exact, allphysicalencodedwords checked/decoded, allotherinputs/wholeoutputs/guards exact. Single2fileRust/CUDAhandword form, no arithmetic/precision/quality/cadence/publicplan/globalpayload changes. Showregister38to39 warning andtemporary<=10608Bnominalpayload costs real/unqualified. Perprospective resourceprotocol initialtiming afterdirect+ordinarytests;fullrawengine/canonical/broad/material/fresh16/holdout/cumulative/app mandatorybeforeadoption. No encoding/sentinel/mask/source/width/helper/flags/quality/sample rescue aftergenuinefailure, no historical/RAMbaselinepooling. E080remainslive, allnewbulkX.',
    'input_sha256': {str(path): h.sha(path) for path in files}, 'candidate_accepted': False
})
for folder, names in [(H, ['protocol.json']), (ROOT / 'runs/E121-build-plan', ['protocol.json']),
                       (ROOT / 'runs/E121-final-build', ['complete.json'])]:
    for name in names:
        path = folder / name
        key = folder.name + '/' + name
        destination = h.ar.DASHBOARD / 'evidence' / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            assert destination.read_bytes() == path.read_bytes()
        else:
            shutil.copyfile(path, destination)
        with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
            assert response.read() == path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    experiment = next(row for row in status['experiments'] if row['id'] == 'E121')
    experiment.update(stage='86 ordinary tests then six complete-solve observations',
                      correctness='380foldpairs+13300showpairs/27360launches bit-exact with full decoded physical metadata',
                      reason='Full direct numerical controls and fresh integratedbuilds passed. Fixed B372/E121R1,E121R2/B373,B374/E121R3 initialscreen;1%aggregate+strictfixtureguards. Broader fullraw/material qualification remains mandatorybeforeadoption.')
    experiment['evidence'] += [{'label': 'Complete fold raw control', 'url': 'evidence/D298-hand-word-fold/report.json'},
                              {'label': 'Complete showdown raw control', 'url': 'evidence/E121-kernel-control-root-check/report.json'},
                              {'label': 'Frozen initial full-solve screen', 'url': 'evidence/E121-primary-plan/protocol.json'}]
    status.update(updated_at=h.now(), active_experiment='E121', stage=experiment['stage'], activity=experiment['reason'])
    h.ar.atomic_json(h.ar.STATUS, status)
h.custody()
print(h.sha(H / 'protocol.json'), flush=True)
