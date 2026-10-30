"""Freeze one child-value reload form and its compiler admission gates."""
import ast, json, shutil, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
assert shutil.disk_usage(ROOT).free >= 32 * 1024**3
D = ROOT / 'runs/D303-child-cache-scout'
d = h.read(D / 'report.json')
assert not d['retained_matches'] and not d['local_matches']
S = ROOT / 'runs/E123-source'
S.mkdir(exist_ok=False)
source = (h.REPO / 'crates/solver/src/gpu/kernels.cu').read_bytes()
assert source.count(b'\n') == source.count(b'\r\n')
text = source.decode('utf-8')
begin = text.index('__device__ __forceinline__ void up_action_impl(')
end = text.index('extern "C" __global__ void up_action(', begin)
body = text[begin:end]
edits = [
    ('// register-cache regrets and child values for the common small-na case', '// register-cache regrets; reload child values after the expectation'),
    ('float rc[8], vc[8];', 'float rc[8];'),
    ('                if (small) vc[a] = v;\r\n', ''),
    ('float val = small ? vc[a] : cfv[', 'float val = cfv[')
]
changed = body
for before, after in edits:
    assert changed.count(before) == 1, before
    changed = changed.replace(before, after, 1)
candidate = (text[:begin] + changed + text[end:]).encode('utf-8')
reverse = changed
for before, after in reversed(edits):
    if after:
        assert reverse.count(after) == 1
        reverse = reverse.replace(after, before, 1)
    else:
        anchor = '                out += sig * v;\r\n'
        assert reverse.count(anchor) == 1
        reverse = reverse.replace(anchor, before + anchor, 1)
assert reverse == body
assert b'vc[' not in changed.encode()
assert candidate[:begin] == source[:begin]
(S / 'baseline.cu').write_bytes(source)
(S / 'candidate.cu').write_bytes(candidate)
h.save(S / 'manifest.json', {
    'id': 'E123', 'at': h.now(), 'status': 'FROZEN_OFF_TREE_PRE_COMPILER',
    'baseline_sha256': h.sha(S / 'baseline.cu'), 'candidate_sha256': h.sha(S / 'candidate.cu'),
    'edits': [{'old': a, 'new': b} for a, b in edits], 'whole_CRLF_source_inverse_exact': True,
    'target': 'training up_action helper all original template arities; only child-value cache removed, all rc regret caching retained',
    'unchanged': 'Original childCFV read in ordered expectation stays; late regret phase rereads identical immutable CFV words. No CFV writes until finalparentwrite; regret/strategy stores disjoint from CFV under original allocation/caller ownership. Same floating expressions/order/FMA opportunity, sigma/sum/discounts/locks/opponents/genericfallback,8otherentries/ABIs/host/globalarrays/launches/shared/quality/cadence/saves.',
    'risks': 'Compiler CSE may recreate original register cache; actual register reduction and changed native body required before numerical controls. Extra CFV traffic, scheduling and FMA/CSE changes need actual raw GPU tests; no source-only accuracy or speed proof.',
    'history_report_sha256': h.sha(D / 'report.json'),
    'failure': 'Close single plain-source form without volatile/asm/restrict/arity subset/cache placement/flags/helper/width/source/quality/sample rescue. E024 genericcache removal and E117 earlier childloads remain closed.'})

H = ROOT / 'runs/E123-resource'
H.mkdir(exist_ok=False)
shutil.copyfile(S / 'candidate.cu', H / 'candidate.cu')
for arch in ['compute_120', 'compute_75']:
    shutil.copyfile(ROOT / 'runs/E118-resource' / ('baseline-' + arch + '.ptx'), H / ('baseline-' + arch + '.ptx'))
(H / 'probe.rs').write_bytes((ROOT / 'runs/E122-resource/probe.rs').read_bytes().replace(b'E122_RESOURCE', b'E123_RESOURCE'))
parent_script = ROOT / 'runs/E117-resource-execute.py'
code = parent_script.read_text().replace('E117', 'E123')
code = code.replace('Earlier existing child CFV loads; actual emitted per-path scheduling and unchanged original floating operand/caller contracts remain', 'Removal of child-value cache with original regret cache retained; actual native register reduction, repeated original CFV address/FP dependencies and caller contracts remain')
code = code.replace('earlier child-load mechanism pending', 'child-value reload mechanism pending')
needle = "for arch in ['compute_120','compute_75']:\n gates[arch+':up_action_emitted_change']=not tables[arch]['up_action']['body_alpha_exact']\npassed=all(gates.values());"
replacement = "gates['compute_120:up_action_emitted_change']=not tables['compute_120']['up_action']['body_alpha_exact']\nassert rows['baseline','up_action']['registers']==62, 'Unexpected accepted resource identity'\ngates['up_action:strict_actual_register_reduction']=rows['candidate','up_action']['registers']<rows['baseline','up_action']['registers']\npassed=all(gates.values());"
assert code.count(needle) == 1
code = code.replace(needle, replacement)
ast.parse(code)
script = ROOT / 'runs/E123-resource-execute.py'
with script.open('xb') as stream:
    stream.write(code.encode())
parent = h.read(ROOT / 'runs/E117-resource/protocol.json')
files = [Path(__file__), script, parent_script, ROOT / 'epoch/common.py', D / 'report.json',
         ROOT / 'runs/D303-child-cache-scout.py', ROOT / 'runs/D302-live-UI-check/report.json',
         h.REPO / 'research/postflop-gpu-20261016/qualification-policy-20261017.md',
         h.REPO / 'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md']
files += [p for folder in [S, H] for p in folder.iterdir() if p.is_file()]
files += [p for p in (ROOT / 'reference/accepted-e080-deps').iterdir() if p.is_file()]
h.save(H / 'protocol.json', {
    'id': 'E123-resource', 'at': h.now(), 'status': 'FROZEN_PRE_ONE_COMPILER_AND_MODULE_ONLY_PROCESS',
    'rustc_command': [x.replace('E117-resource', 'E123-resource') for x in parent['rustc_command']],
    'GPU_uuid': parent['GPU_uuid'], 'original_entries': parent['original_entries'], 'target_entries': ['up_action'],
    'required_free_bytes': 16 * 1024**3, 'input_sha256': {str(p): h.sha(p) for p in files},
    'resource_gates': 'All9ABIs/barriers/8untargetedbodies andresources exact for120/75. compute120up_action changed; compatibility75target maychangeorCSE. No local/constant/dynamic/stack growth/maxthreadloss/defaultlimitloss; positive64/128/256occupancy. ActualRTX5090up_actionregisters strictly less than original62 required. Registers/static/occupancy costs still actualmaterialgates beforeadoption.',
    'mechanism_before_applicationkernels': 'Actual resource/register decrease, changed native up_action body, original ordered clamp/sum/sigma/expectation/strategy/discount/regret FP dependencies and same original childCFV word ancestry. No plain source/CSE/no-op or counts-to-speed inference. No forcedvolatile/asm to rescue absentmechanism.',
    'prospective_order': 'Resource/emittedmechanism ->fulloriginal819action/evaluation directrawmatrix(allfields/guards/actualinputs) ->86ordinaryunits ->fixed3pairs >=1%unroundedcompletecycle andstrictfixtureguard. Fullrawengine/canonical/broad/material/fresh16/holdout/currentRAMcumulative/actualapp before adoption. Alloriginalcorpora and quality unchanged; no source/case/outcome selection or historicaltimingpooling.',
    'failure': 'Close one fixed plain-source form without volatile/asm/restrict/aritysubset/placement/helper/flags/width/source/quality/sample rescue. Main/live/source untouched. All newbulkX/Sreadonly/noT.'})

sources = [ROOT / 'runs/D302-live-UI-check/report.json', D / 'report.json', S / 'manifest.json', H / 'protocol.json']
for path in sources:
    dst = h.ar.DASHBOARD / 'evidence' / path.parent.name / path.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    assert not dst.exists()
    shutil.copyfile(path, dst)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + path.parent.name + '/' + path.name, timeout=20) as response:
        assert response.read() == path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    assert not any(e['id'] in ['D302', 'D303', 'E123'] for e in status['experiments'])
    status['experiments'] += [
        {'id': 'D302', 'title': 'Live simplified menu and new-RAM tracker check', 'kind': 'diagnostic', 'status': 'measured', 'accepted': False, 'stage': 'Browser check passed', 'reason': 'Actual rendered menu has no legacy selector. Tracker separates current10.46s baseline and historical14.74%gain. Owned browser closed; no session build/load/solve.', 'evidence': [{'label': 'Scoped live UI evidence', 'url': 'evidence/D302-live-UI-check/report.json'}]},
        {'id': 'D303', 'title': 'Child-value cache lifetime and history review', 'kind': 'diagnostic', 'status': 'measured', 'accepted': False, 'stage': 'Source-only review; no earlier recognized form', 'reason': '142uniqueCUDAhashes/alllocalrefs, no recognized child-cache-only removal with regret cache retained. Bounded review, not universal novelty proof. E024/E117 counterevidence preserved.', 'evidence': [{'label': 'History and source argument', 'url': 'evidence/D303-child-cache-scout/report.json'}]},
        {'id': 'E123', 'title': 'Reload child CFVs after the ordered expectation', 'kind': 'candidate', 'status': 'staged', 'accepted': False, 'stage': 'Frozen resource and register-reduction gate', 'reason': 'One CUDA-only plain-source form, no child-value temporary; original regret cache/arithmetic/metadata/launches retained. Actual registers must decrease from62 before numerical controls. CSE/no-op and extra memory traffic may defeat it.', 'evidence': [{'label': 'Frozen source', 'url': 'evidence/E123-source/manifest.json'}, {'label': 'Prospective compiler gates', 'url': 'evidence/E123-resource/protocol.json'}]}
    ]
    status.update(updated_at=h.now(), active_experiment='E123', stage='Child-value reloads: compiler gate', activity='E122 closed. Live menu/tracker browser checked. E123 tests a register-lifetime hypothesis; no GPU numerical or speed evidence yet. E080 remains qualified/live.')
    h.ar.atomic_json(h.ar.STATUS, status)
h.custody()
print(json.dumps({'candidate_sha256': h.sha(S / 'candidate.cu'), 'protocol_sha256': h.sha(H / 'protocol.json')}), flush=True)
