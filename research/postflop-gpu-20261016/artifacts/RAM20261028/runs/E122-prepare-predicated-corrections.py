"""One fixed explicit rank-predicated addition form; source/resource stage only."""
import ast
import collections
import hashlib
import itertools
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h

h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
D = ROOT / 'runs/D299-predicated-correction-scout'
D.mkdir(exist_ok=False)
pattern = re.compile(r'@[^;\n]{0,100}add(?:\.rn)?\.f32|asm[^;]{0,800}(?:lower_c|higher_c)', re.I | re.S)
seen = {}
hits = []
inventories = []
for folder in [Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs'), ROOT / 'runs']:
    paths = subprocess.check_output(['rg', '--files', str(folder), '-g', '*.cu'], text=True).splitlines()
    inventories.append({'root': str(folder), 'CUDA_files': len(paths)})
    for name in paths:
        data = Path(name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest in seen:
            continue
        seen[digest] = name
        text = data.decode()
        start = text.find('extern "C" __global__ void up_show(')
        if start < 0:
            continue
        end = text.find('extern "C" __global__', start + 20)
        body = text[start:end if end >= 0 else len(text)]
        matches = [match.group() for match in pattern.finditer(body)]
        if matches:
            hits.append({'path': name, 'sha256': digest, 'matches': matches})
revisions = subprocess.check_output(['git', 'log', '--all', '--format=%H', '--', 'crates/solver/src/gpu/kernels.cu'], cwd=h.REPO, text=True).splitlines()
local = []
for revision in revisions:
    text = subprocess.check_output(['git', 'show', revision + ':crates/solver/src/gpu/kernels.cu'], cwd=h.REPO).decode()
    start = text.find('extern "C" __global__ void up_show(')
    if start >= 0:
        end = text.find('extern "C" __global__', start + 20)
        body = text[start:end if end >= 0 else len(text)]
        if pattern.search(body):
            local.append({'revision': revision, 'matches': [match.group() for match in pattern.finditer(body)]})
assert not hits and not local, 'Matching earlier source needs semantic review before admission'
native_path = ROOT / 'runs/D297-hand-word-native/execution/baseline/up_show.sass.txt'
native_sha = h.read(ROOT / 'runs/D297-hand-word-native/capture-report.json')['entry_sections']['baseline']['up_show']['sha256']
h.pin(native_path, native_sha)
native = native_path.read_text()
rows = {int(match[1], 16): match[2] for match in re.finditer(r'/\*([0-9a-f]+)\*/\s*(.*?)\s*;\s*/\*', native)}
inventory = collections.Counter()
for op in rows.values():
    opcode = re.sub(r'^@!?U?P\d+ ', '', op).split()[0]
    if opcode in ['FADD', 'FSEL', 'FFMA', 'FMUL']:
        inventory[('predicated:' if op.startswith('@') else 'unpredicated:') + opcode] += 1
assert inventory['predicated:FADD'] == 30 and inventory['predicated:FSEL'] == 30
sample = [{'PC': hex(pc), 'op': op} for pc, op in rows.items() if 0x1e60 <= pc <= 0x1f80]
h.save(D / 'history-and-native-baseline.json', {
    'at': h.now(), 'inventories': inventories, 'unique_CUDA_hashes': len(seen),
    'retained_matches': hits, 'all_local_ref_revisions': len(revisions), 'local_matches': local,
    'pattern': pattern.pattern, 'native_baseline_path': str(native_path), 'native_baseline_sha256': native_sha,
    'native_FP_select_static_inventory': dict(inventory), 'rank_correction_instruction_sample': sample,
    'classification': 'The existing kernel already has30predicatedFADD and30predicatedFSEL sites, not wholly unpredicated arithmetic. E122 forces both original rank-conditioned corrections to explicit predicatedADD with elsepriority. E068bitselectedblocked accumulation is up_chance(15argumentABI), not this up_show rankconditional form. E089 loopunroll directive/E118zero-tiepayout/E120sparsepositions/E121handencoding remain closed and absent. Boundedliteral/localhistory, not exhaustive semantic/remotenovelty or runtimefrequency/cost proof.'
})
truth = []
for less, greater in itertools.product([False, True], repeat=2):
    original = ('lower' if less else 'higher' if greater else 'none')
    new_lower = less
    new_higher = greater and not less
    assert not (new_lower and new_higher)
    assert original == ('lower' if new_lower else 'higher' if new_higher else 'none')
    truth.append({'pos_lt_lb': less, 'pos_ge_ub': greater, 'original': original, 'lower': new_lower, 'higher': new_higher})
boundaries = [0, 1, 2, 63, 64, 127, 128, 1325, 1326, 0xffffffff]
for pos, lb, ub in itertools.product(boundaries, repeat=3):
    expected = ('lower' if pos < lb else 'higher' if pos >= ub else 'none')
    assert expected == ('lower' if pos < lb else 'higher' if (pos >= ub and not pos < lb) else 'none')
h.save(D / 'predicate-contract.json', {
    'at': h.now(), 'complete_boolean_truth_table': truth, 'unsigned_boundary_triples': len(boundaries)**3,
    'source_argument': 'p_lo=(u32pos<u32lb),p_not_lo=!p_lo,p_hi=(u32pos>=u32ub)&p_not_lo exactly retains original if/elsepriority for allu32triples, including lb>ub. Only originalselected lower_c+=r or higher_c+=r executes;accumulator readwrite constraints retain oldbits whenfalse. tot_c and all other arithmetic/loops/barriers/payload remain original. add.rn.f32 matches default add.f32 RN/noFTZ precision; this still needs actualcompiler/native/NaN/rawGPU checks.',
    'constraints': 'CUDAinlineasm uses +f(readwrite) outputs for bothaccumulators, commonrinput and originalunsignedpos/lb/ubinputs. Outputs represent distinct live state. Predicates mutuallyexclusive; no input/output vector/memory change. Register/scheduling/CSEloss/volatile costs real.',
    'native_mechanism_gate': 'After resources pass require nativeoriginal30FSEL sites reduced to0 in changedup_show, both rank corrections bound to original r/accumulators with exactpriority andoriginalbarriers. Existingpredicatedadds are not called new. No counts-to-speed/dynamic-frequency inference; no source/flag/mask/helper/width/quality/sample rescue if intendednativeform absent.'
})
S = ROOT / 'runs/E122-source'
S.mkdir(exist_ok=False)
original = (h.REPO / 'crates/solver/src/gpu/kernels.cu').read_bytes()
assert original.count(b'\n') == original.count(b'\r\n')
text = original.decode()
start = text.index('extern "C" __global__ void up_show(')
end = text.index('extern "C" __global__ void up_chance(', start)
body = text[start:end]
old = '                if (pos < lb) lower_c += r;\r\n                else if (pos >= ub) higher_c += r;'
new = r'''#if __CUDA_ARCH__ == 1200
                asm volatile(
                    "{\n\t"
                    ".reg .pred p_lo, p_hi, p_not_lo;\n\t"
                    "setp.lt.u32 p_lo, %3, %4;\n\t"
                    "setp.ge.u32 p_hi, %3, %5;\n\t"
                    "not.pred p_not_lo, p_lo;\n\t"
                    "and.pred p_hi, p_hi, p_not_lo;\n\t"
                    "@p_lo add.rn.f32 %0, %0, %2;\n\t"
                    "@p_hi add.rn.f32 %1, %1, %2;\n\t"
                    "}"
                    : "+f"(lower_c), "+f"(higher_c)
                    : "f"(r), "r"(pos), "r"(lb), "r"(ub));
#else
                if (pos < lb) lower_c += r;
                else if (pos >= ub) higher_c += r;
#endif'''.replace('\n', '\r\n')
assert body.count(old) == 1
candidate = (text[:start] + body.replace(old, new, 1) + text[end:]).encode()
assert candidate.replace(new.encode(), old.encode(), 1) == original
(S / 'baseline.cu').write_bytes(original)
(S / 'candidate.cu').write_bytes(candidate)
h.save(S / 'manifest.json', {
    'id': 'E122', 'at': h.now(), 'status': 'FROZEN_OFF_TREE_PRE_COMPILER',
    'baseline_sha256': h.sha(S / 'baseline.cu'), 'candidate_sha256': h.sha(S / 'candidate.cu'),
    'edit': {'old': old, 'new': new}, 'entire_CRLF_source_inverse_exact': True,
    'target': 'up_show only compute120 explicit rank-predicated corrections; compute75originalC++tokens',
    'unchanged': 'All selectedfloatingoperandvalues/order/precision, tot_c, fullprefix/same/valid/tied/payout, hand/card/rank iterationorder, all5barriers,host/publicplan/globalarrays/ABI27/grid/block/dynamicshared/quality/stopping/save unchanged. No closedhunk composed.',
    'risks': 'Inlinevolatile constraints may lose CSE/increase FP/Boolean work/lifetimes/registers/JIT or emit no beneficial nativechange. Sourcepredicate proof is not NaN/compiler/native/GPU orspeedproof. Fixedoneform closesaftergenuinefailure without asm/helper/predicate/scope/architecture/flags/width/quality/sample rescue.',
    'contract_sha256': h.sha(D / 'predicate-contract.json'), 'history_sha256': h.sha(D / 'history-and-native-baseline.json')
})
h.save(D / 'report.json', {
    'id': 'D299', 'at': h.now(), 'status': 'pass_scoped_predicate_source_and_existing_native_selector_review',
    'source_manifest_sha256': h.sha(S / 'manifest.json'), 'complete_boolean_rows': 4,
    'unsigned_boundary_triples': 1000, 'accepted_native_predicated_adds': 30, 'accepted_native_predicated_selects': 30,
    'new_compiler_GPU_module_applicationkernels_solver_or_speed_samples': 0,
    'limits': 'Bounded source/Boolean/static nativebaseline only; no candidate compiled/numerical/performance evidence.', 'candidate_adopted': False
})
R = ROOT / 'runs/E122-resource'
R.mkdir(exist_ok=False)
shutil.copyfile(S / 'candidate.cu', R / 'candidate.cu')
for arch in ['compute_120', 'compute_75']:
    shutil.copyfile(ROOT / 'runs/E118-resource' / ('baseline-' + arch + '.ptx'), R / ('baseline-' + arch + '.ptx'))
(R / 'probe.rs').write_bytes((ROOT / 'runs/E118-resource/probe.rs').read_bytes().replace(b'E118_RESOURCE', b'E122_RESOURCE'))
code = (ROOT / 'runs/E118-resource-execute.py').read_text().replace('E118', 'E122')
code = code.replace('zero-tie fastpath and FP mechanism pending', 'explicit rank-predicated correction mechanism pending')
code = code.replace('Finite zero-tie output prefix; actual guarded absence of tot_c/same/valid/tied work and exact baseline-prefix FP provenance plus barrier/caller reviews remain', 'Explicit rank-predicated corrections; actual originaloperand/order/unsignedpriority and native30FSELto0 gate plus allbarriers/caller reviews remain')
ast.parse(code)
script = ROOT / 'runs/E122-resource-execute.py'
assert not script.exists()
script.write_bytes(code.encode())
parent = h.read(ROOT / 'runs/E118-resource/protocol.json')
files = [Path(__file__), script, ROOT / 'epoch/common.py', ROOT / 'runs/E118-resource-execute.py',
         ROOT / 'runs/E118-resource/probe.rs', native_path,
         h.REPO / 'research/postflop-gpu-20261016/qualification-policy-20261017.md',
         h.REPO / 'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md']
files += [path for folder in [D, S, R] for path in folder.iterdir() if path.is_file()]
files += [path for path in (ROOT / 'reference/accepted-e080-deps').iterdir() if path.is_file()]
h.save(R / 'protocol.json', {
    'id': 'E122-resource', 'at': h.now(), 'status': 'FROZEN_PRE_ONE_COMPILER_AND_MODULE_ONLY_PROCESS',
    'rustc_command': [value.replace('E118-resource', 'E122-resource') for value in parent['rustc_command']],
    'GPU_uuid': parent['GPU_uuid'], 'original_entries': parent['original_entries'], 'target_entries': ['up_show'],
    'required_free_bytes': 16 * 1024**3, 'input_sha256': {str(path): h.sha(path) for path in files},
    'resource_gates': 'All9headers/8untargetedbodies/resources exact;compute120showbodychanged/compute75all9bodiesexact. Same5barriers. No local/constant/dynamic/stackgrowth/maxthreadloss/defaultlimitloss;positive64/128/256occupancy,register/static/residency risks disclosed underD108.',
    'mechanism_before_applicationkernels': 'ActualPTX predicateADD carries originalr/lo/hi and exactunsigned if/elsepriority;allprefix/payout/addresses/barriers retained. Actualnativebaseline30FSELsites->0 in up_show;bothcorrection chains identified, no nativeequivalentno-op. Counts not speed proof.',
    'prospective_order': 'Resource/emittedmechanism ->entireoriginalunencodedE120fullshowcorpus plus retainedE12124single-opponent reachcases(all2660cases/5widths) with all21physicalinputs literalidentical/wholeCFVguards exact ->ordinary86units ->initialfixed3pairfullcycle1%strictfixture. Fullrawengine/canonical/broad/material/fresh16/holdout/currentRAMcumulative/actualapp requiredbeforeadoption. No corpusoutcome/timingpooling. Only originalcase data reused; no failedE121encoding orE120compaction source.',
    'failure': 'CloseexactsingleCUDAasm/guard/predicate/constraint/architecture/helper/loop/flags/width/quality/sampleform after genuinefailure; no sourcevariant or rescue samples. No sourceactivation/livechange.'
})
for folder, names in [(D, ['report.json', 'history-and-native-baseline.json', 'predicate-contract.json']), (S, ['manifest.json']), (R, ['protocol.json'])]:
    for name in names:
        path = folder / name
        key = folder.name + '/' + name
        destination = h.ar.DASHBOARD / 'evidence' / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        assert not destination.exists()
        shutil.copyfile(path, destination)
        with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
            assert response.read() == path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    assert not any(row['id'] in ['D299', 'E122'] for row in status['experiments'])
    status['experiments'] += [
        {'id': 'D299', 'title': 'Showdown rank predicates and existing native selectors', 'kind': 'diagnostic', 'status': 'measured', 'accepted': False,
         'stage': 'Source and baseline instruction review passed', 'reason': 'Existing kernel already has predicated adds; remaining conditional selectors are the specific target. Boolean priority is preserved for every unsigned comparison combination. No candidate GPU result.',
         'evidence': [{'label': name, 'url': 'evidence/' + D.name + '/' + name} for name in ['report.json', 'history-and-native-baseline.json', 'predicate-contract.json']]},
        {'id': 'E122', 'title': 'Explicit rank-predicated showdown corrections', 'kind': 'candidate', 'status': 'staged', 'accepted': False,
         'stage': 'Frozen compiler and resource checks', 'reason': 'One CUDA-only form; original selected additions and if/else priority retained. Actual compiler/native form, GPU equivalence, and speed remain unproven.',
         'evidence': [{'label': 'Fixed source', 'url': 'evidence/' + S.name + '/manifest.json'}, {'label': 'Frozen resource and mechanism gates', 'url': 'evidence/' + R.name + '/protocol.json'}]}
    ]
    status.update(updated_at=h.now(), active_experiment='E122', stage='Explicit rank predication: resource gate',
                  activity='E121 closed. E122 tests explicit predicate additions without changing metadata, arithmetic order, or solve quality. E080 remains live.')
    h.ar.atomic_json(h.ar.STATUS, status)
h.custody()
print(json.dumps({'protocol_sha256': h.sha(R / 'protocol.json'), 'candidate_sha256': h.sha(S / 'candidate.cu'), 'unique_CUDA': len(seen)}), flush=True)
