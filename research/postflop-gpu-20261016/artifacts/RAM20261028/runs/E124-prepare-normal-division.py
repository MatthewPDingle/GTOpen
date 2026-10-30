"""Freeze guarded RN-FTZ division with original division fallback."""
import ast, json, shutil, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
assert shutil.disk_usage(ROOT).free > 32 * 1024**3
D = ROOT / 'runs/D305-normal-division-scout'
assert h.read(D / 'report.json')['status'] == 'pass_scoped_history_and_exact_rational_normal_range_contract'
S = ROOT / 'runs/E124-source'
S.mkdir(exist_ok=False)
original = (h.REPO / 'crates/solver/src/gpu/kernels.cu').read_bytes()
assert original.count(b'\n') == original.count(b'\r\n')
text = original.decode('utf-8')
anchor = '#define SENTINEL 0xFFFFFFFFu\r\n'
helper = '''
// Bounds keep both operands and the correctly rounded quotient normal.
// Every other value retains the original division, including signed zeros.
__device__ __forceinline__ float normal_regret_quotient(float n, float d)
{
    const float min_n = 1.08420217248550443400745280086994171142578125e-19f; // 2^-63
    const float max_d = 9223372036854775808.0f; // 2^63
    if (n >= min_n && d <= max_d && n <= d) {
        float q;
        asm("div.rn.ftz.f32 %0, %1, %2;" : "=f"(q) : "f"(n), "f"(d));
        return q;
    }
    return n / d;
}
'''.replace('\n', '\r\n')
assert text.count(anchor) == 1
changed = text.replace(anchor, anchor + helper, 1)
edits = [
    ('v = pr * ((r > 0.f ? r : 0.f) / sum);', 'v = pr * normal_regret_quotient((r > 0.f ? r : 0.f), sum);'),
    ('float sig = sum > 1e-12f ? (r > 0.f ? r : 0.f) / sum : uni;', 'float sig = sum > 1e-12f ? normal_regret_quotient((r > 0.f ? r : 0.f), sum) : uni;')
]
for before, after in edits:
    assert changed.count(before) == 1
    changed = changed.replace(before, after, 1)
reverse = changed.replace(helper, '', 1)
for before, after in edits:
    assert reverse.count(after) == 1
    reverse = reverse.replace(after, before, 1)
assert reverse == text
(S / 'baseline.cu').write_bytes(original)
(S / 'candidate.cu').write_bytes(changed.encode('utf-8'))
h.save(S / 'manifest.json', {'id': 'E124', 'at': h.now(), 'status': 'FROZEN_OFF_TREE_PRE_COMPILER',
    'baseline_sha256': h.sha(S / 'baseline.cu'), 'candidate_sha256': h.sha(S / 'candidate.cu'),
    'helper': helper, 'edits': [{'old': a, 'new': b} for a, b in edits], 'whole_CRLF_source_inverse_exact': True,
    'target': 'Original down_action/up_action normalization quotients only; independent per-action RN division, no denominator sharing or zero/one shortcut',
    'proof_sha256': h.sha(D / 'range-contract.json'),
    'unchanged': 'All original clamp/sum/sigma consumers/uniformfallthrough/multiplications/FMA/discount/regret/strategy/locks/opponent/genericlogic,7otherentries/9ABIs/host/metadata/arrays/launch/shared/graphs/quality/checks/saves. No globalFTZ/fastmath/precision flag, reciprocal or handcrafted refinement introduced.',
    'risks': 'Actual original normal path may already avoid exceptional work. FTZ form may retain identical native RCP/FMA/FCHK/CALL work; guards/codesize/registers/branch divergence may hurt. Source proof is not compiler/GPU/fallbackNaN/accuracy/speed proof.',
    'failure': 'Close fixed2^-63/2^63 plain guarded per-quotient RN-FTZ form without guard/window/asmconstraint/architecture/kernel-subset/arity/zero-bypass/helper/flags/width/source/quality/sample rescue. All E060sharing/E101/E116 bypass forms remainclosed.'})
H = ROOT / 'runs/E124-resource'
H.mkdir(exist_ok=False)
shutil.copyfile(S / 'candidate.cu', H / 'candidate.cu')
for arch in ['compute_120', 'compute_75']:
    shutil.copyfile(ROOT / 'runs/E118-resource' / ('baseline-' + arch + '.ptx'), H / ('baseline-' + arch + '.ptx'))
(H / 'probe.rs').write_bytes((ROOT / 'runs/E123-resource/probe.rs').read_bytes().replace(b'E123_RESOURCE', b'E124_RESOURCE'))
parent_script = ROOT / 'runs/E123-resource-execute.py'
code = parent_script.read_text(encoding='utf-8').replace('E123', 'E124')
needle = "gates['compute_120:up_action_emitted_change']=not tables['compute_120']['up_action']['body_alpha_exact']\nassert rows['baseline','up_action']['registers']==62, 'Unexpected accepted resource identity'\ngates['up_action:strict_actual_register_reduction']=rows['candidate','up_action']['registers']<rows['baseline','up_action']['registers']\n"
replacement = "for arch in ['compute_120','compute_75']:\n for name in P['target_entries']:\n  gates[arch+':'+name+':body_changed']=not tables[arch][name]['body_alpha_exact']\n  candidate=entries(O/('candidate-'+arch+'.ptx'))[name]\n  gates[arch+':'+name+':guarded_RN_FTZ_primitive_present']='div.rn.ftz.f32' in candidate\n  gates[arch+':'+name+':ordinary_division_fallback_present']=re.search(r'\\bdiv\\.rn\\.f32\\b',candidate)is not None\n"
assert code.count(needle) == 1
code = code.replace(needle, replacement)
code = code.replace('Removal of child-value cache with original regret cache retained; actual native register reduction, repeated original CFV address/FP dependencies and caller contracts remain', 'Guarded per-quotient RN-FTZ with original division fallback; actual guard/operand/normal-result and shorter native division-path proof remain')
code = code.replace('child-value reload mechanism pending', 'guarded RN-FTZ division mechanism pending')
code = code.replace('All9ABIs/resources and changed up_action entry', 'All9ABIs/resources and two changed normalization entries')
ast.parse(code)
script = ROOT / 'runs/E124-resource-execute.py'
with script.open('xb') as stream:
    stream.write(code.encode())
parent = h.read(ROOT / 'runs/E123-resource/protocol.json')
files = [Path(__file__), script, parent_script, ROOT / 'runs/D305-normal-division-scout.py', ROOT / 'epoch/common.py',
         h.REPO / 'research/postflop-gpu-20261016/qualification-policy-20261017.md',
         h.REPO / 'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md']
files += [p for folder in [D, S, H] for p in folder.iterdir() if p.is_file()]
files += [p for p in (ROOT / 'reference/accepted-e080-deps').iterdir() if p.is_file()]
h.save(H / 'protocol.json', {'id': 'E124-resource', 'at': h.now(), 'status': 'FROZEN_PRE_ONE_COMPILER_AND_MODULE_ONLY_PROCESS',
    'rustc_command': [x.replace('E123-resource', 'E124-resource') for x in parent['rustc_command']],
    'GPU_uuid': parent['GPU_uuid'], 'original_entries': parent['original_entries'], 'target_entries': ['down_action', 'up_action'],
    'required_free_bytes': 16 * 1024**3, 'input_sha256': {str(p): h.sha(p) for p in files},
    'resource_gates': 'Both120/75targetbodies change and eachhas RN-FTZprimitive/originalRNfallback; all9ABIs/barriers/7untargetedbodies/resources exact. No local/constant/dynamic/stackgrowth/maxthreadloss/defaultlimitloss; positive64/128/256occupancy. Register/static/residency costs are warnings perD108 and later actualmaterialgates.',
    'hard_native_mechanism_before_applicationkernels': 'Actual originalclamp/sum and exactnormalguard/operands/fallback provenance. A guarded nonzero native path must remove at least one original division-specific FCHK/CALL site or instruction from corresponding ordinary RN path without more RCP/refinementFMA work; count-only globalhistogram not sufficient. Original ordinarypath alreadyhasfastsequences; FTZvirtualopcode alone not enough. Close no-benefit/no-op form without forcing/tuning.',
    'prospective_order': 'Resource/emittedmechanism ->originalfull1530down-action and819action/evaluation rawcorpora plus scalar exactRN-boundary/NaN/subnormal/fallback/taken witnesses ->86ordinaryunits ->fixed3matchedpairs >=1%unroundedcompletecycle andstrictfixtureguard. Fullrawengine/canonical/broad/material/fresh16/holdout/currentRAMcumulative/actualapp before adoption. No input/outputfields omitted or historical/oldRAMtimingpooling.',
    'failure': 'Close fixednormalbounds/helper/guard/asm/architecture/kernel-subset/arity/flags/width/source/quality/sample form after genuine failure. No E060sharedreciprocal/E101zero/E116singlepositive rescue. No productionactivation; allnewbulkX/Sreadonly/noT.'})
for path in [D / 'report.json', D / 'history.json', D / 'range-contract.json', S / 'manifest.json', H / 'protocol.json']:
    dst = h.ar.DASHBOARD / 'evidence' / path.parent.name / path.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    assert not dst.exists()
    shutil.copyfile(path, dst)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + path.parent.name + '/' + path.name, timeout=20) as response:
        assert response.read() == path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    assert not any(row['id'] in ['D305', 'E124'] for row in status['experiments'])
    status['experiments'] += [
        {'id': 'D305', 'at': h.now(), 'title': 'Exact normal-range RN division contract', 'kind': 'diagnostic', 'status': 'measured', 'accepted': False, 'stage': 'Source/history/rational review passed', 'correctness': 'source_contract_only', 'reason': '143uniqueCUDA/alllocalrefs;1764boundarypairs/2negativeguardcounterexamples. Fixedrange proves normalinputs and RNoutput only under documentedsemantics; no compiler/GPU orspeed proof.', 'evidence': [{'label': name, 'url': 'evidence/D305-normal-division-scout/' + name} for name in ['report.json', 'history.json', 'range-contract.json']]},
        {'id': 'E124', 'at': h.now(), 'title': 'Guarded native RN-FTZ regret division', 'kind': 'candidate', 'status': 'staged', 'accepted': False, 'stage': 'Frozen compiler and native-mechanism gates', 'correctness': 'not_yet_tested', 'reason': 'Native per-action RN division for fixed normal range; original division elsewhere. No shared reciprocal, zero/one shortcut, metadata orquality change. Originalnativepath alreadyfast; actualshorterpath andallrawcontrols required.', 'evidence': [{'label': 'Fixed source and exact inverse', 'url': 'evidence/E124-source/manifest.json'}, {'label': 'Prospective gates', 'url': 'evidence/E124-resource/protocol.json'}]}
    ]
    status.update(updated_at=h.now(), active_experiment='E124', stage='Guarded RN-FTZ division: compiler/resource gate', activity='D304trackerrepair retained. D305normalrangeproof passed; E124may still emit no native saving or worsen resources. E080 remains qualified/live; no newgain adopted.')
    h.ar.atomic_json(h.ar.STATUS, status)
h.custody()
print(json.dumps({'candidate_sha256': h.sha(S / 'candidate.cu'), 'protocol_sha256': h.sha(H / 'protocol.json')}), flush=True)
