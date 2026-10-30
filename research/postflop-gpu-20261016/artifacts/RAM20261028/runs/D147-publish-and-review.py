import sys, json, shutil, subprocess, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
h.ar.refuse_active(h.ar.live_status())
H = ROOT / 'runs/D147-readback-diagnostic'
P = h.read(H / 'protocol.json')
for p, digest in P['input_sha256'].items():
    h.pin(p, digest)
assert h.read(H / 'execution/complete.json')['all_owned_children_terminal']
parent_path = ROOT / 'comparisons/D147-readback/report.json'
sub_path = ROOT / 'comparisons/D147-arena-substages/report.json'
q, sub = h.read(parent_path), h.read(sub_path)
assert q['observer_usefulness_pass'] and sub['E011_design_decision'] == 'declined_insufficient_observed_component_headroom'
assert sub['CPU_arena_records'] == 36 and sub['full_scientific_records_exact'] == 18
A = ROOT / 'runs/D148-packed-readback-design'
A.mkdir(exist_ok=False)
reference = A / 'reference'
reference.mkdir()
archive = Path(r'S:\GTOpen-research\postflop-gpu-20261016')
inputs = [
    (archive / 'runs/E010-source/quantized_readback.rs', 'E010-quantized_readback.rs'),
    (archive / 'runs/E010-source/quantized_readback_tests.rs', 'E010-controls.rs'),
    (archive / 'runs/E010-source/mod.rs', 'E010-mod.rs'),
    (archive / 'runs/E010-source/arena.rs', 'E010-arena.rs'),
    (archive / 'runs/E010-source/kernels.cu', 'E010-kernels.cu'),
    (archive / 'comparisons/E009-three-pair-comparison/report.json', 'E009-failed-comparison.json'),
    (archive / 'comparisons/E010-three-pair-comparison/report.json', 'E010-failed-comparison.json'),
    (archive / 'comparisons/D011-init-summary/report.json', 'D011-init-observation.json'),
    (archive / 'comparisons/D012-constructor-summary/report.json', 'D012-constructor-observation.json'),
    (archive / 'comparisons/D013-isolated-summary/report.json', 'D013-isolated-observation.json'),
    (h.REPO / 'crates/solver/tests/postflop_quantization_proof.rs', 'original-encoding-proof.rs'),
    (h.REPO / 'crates/solver/tests/fixtures/postflop_quantization_prototype.cu', 'original-encoding-proof.cu'),
    (h.REPO / 'crates/solver/src/gpu/mod.rs', 'accepted-mod.rs'),
    (h.REPO / 'crates/solver/src/gpu/arena.rs', 'accepted-arena.rs'),
    (h.REPO / 'crates/solver/src/gpu/continuation_storage.rs', 'accepted-continuation-storage.rs'),
    (h.REPO / 'crates/solver/src/gpu/continuation_paging.rs', 'accepted-continuation-paging.rs'),
    (ROOT / 'reference/D141-cfv-width/report.json', 'D141-finite-CFV-model.json'),
]
for src, name in inputs:
    shutil.copyfile(src, reference / name)
    h.pin(reference / name, h.sha(src))
current = (reference / 'accepted-mod.rs').read_text(encoding='utf-8')
assert 'self.stream.synchronize().map_err(e)?;' in current
assert 'mode == 0' in current and 'self.eval_up(p, mode, terminals)?;' in current
cfv = h.read(reference / 'D141-finite-CFV-model.json')
assert len(cfv['cases']) == 12 and all(x['all_rows_independent_of_incoming_CFV_bytes'] for x in cfv['cases'])
design = {
    'id': 'D148', 'at': h.now(), 'status': 'source_design_requires_controls_not_executable',
    'motivation': 'D147 places roughly204ms in full-arena CPU encoding and126ms in compact active encoding; inactive restoration is only42-44ms and cannot satisfy its prospective1% admission proxy even if removed entirely. Focus on active readback transport/encoding rather than that smaller shortcut.',
    'hypothesis': 'Explore GPU packing of active q words and exact per-node scales before download, preserving the shared Rust encoder as the oracle and inactive restoration unchanged. Reduce both transferred bytes and CPU encoding work; no saving is inferred before complete-cycle qualification.',
    'historical_counterevidence': [
        'E009/E010 remain rejected. Their integrated source appended encoding kernels to the main CUDA program and eagerly prepared optional metadata/device output buffers. E010 already reused the pinned host buffer; that is not a new idea.',
        'D011 measured river optional setup only0.1468ms; function loads/direct optional setup did not explain the repeated river regression. D012 located an87ms CPU planning/budget wall stall before context creation. D013 isolated runs still failed timing and changed the observed penalty. No compiler, allocator or driver cause is established.',
        'Do not retime old binaries, pool old samples, add arbitrary thresholds after failure, regrade their decisions or call this a proven fix. Any new form must own a distinct integration/resource contract and pass fresh full timing, fixture, correctness and material gates.'
    ],
    'proposed_distinct_integration': [
        'Keep the accepted main kernels.cu and its runtime NVRTC/JIT path byte unchanged. Generate a separate auxiliary PTX artifact outside measured solves, bind its source/toolchain/options/hash, and load only when the optional path is admitted. This removes auxiliary NVRTC work from runtime but does not eliminate driver JIT/module-load cost.',
        'Use a bounded region of the existing CFV scratch allocation only after the existing readback entry stream synchronization. Place packet descriptors, packed words and scales in disjoint checked regions; reuse the same cached pinned host staging allocation. No additional explicit device output/descriptor allocations. Module code can still consume resources and must be measured.',
        'Keep all four device regret/strategy arrays read-only, original CPU host offsets/scale indices and quantization semantics. Scatter exact q words/scales for active blocks; retain original handling of inactive snapshots, signed zeros, nonfinite data and F32 fallback.',
        'Use original CPU readback for unsupported device/format/endian/size/checked-capacity conditions before auxiliary work. Size/packet rules require prospective calibration/freeze, boundary controls and no tuning after a failed screen. Small-fixture behavior must be tested, not assumed.',
        'Scratch pointers cannot be cached across continuation take/swap/storage operations. Check current lengths/ownership each call. Borrowed staging and device regions must remain alive until their existing completion waits; no global setting, counter retry or alternate executor.'
    ],
    'CFV_lifetime_review': {
        'support': 'D141 finite model checks all incoming-CFV independence in12 accepted layouts. Current training does a complete up pass; evaluation mode0 regenerates terminals before mode1 reuse, and root outputs have separate storage. This motivates a post-completion scratch phase but is not universal runtime proof.',
        'unresolved': [
            'Audit every entry and read of CFV, including graph warm/capture/replay, continuation evaluation, locked/warm states and storage/paging buffers.',
            'Continuation storage and paging explicitly include d_cfv in seven-buffer take/swap/state operations. Verify preservation of their persistent/format contracts and future results; never silently weaken an existing assertion.',
            'Demonstrate byte-exact learning/reach/immutable inputs, CPU q/scales, EV/checkpoints, save/load/resume and subsequent solve/evaluation after scratch contents are replaced. CFV scratch bytes may differ only if its nonpersistent role is proved for every admitted path.'
        ]
    },
    'mandatory_next_before_implementation': [
        'Review novelty against exact E009/E010 sources and budget/lifetime contracts; decline if it is merely an equivalent failed form.',
        'Freeze a finite packet/address/liveness model and check odd tails, u64 offsets, empty blocks, disjoint descriptor/output regions, host q guards and every capacity decline before any application kernel.',
        'Freeze and run a source-bound auxiliary compile/load/resource probe, then full actual input/output CPU-oracle controls covering signed/unsigned, ties, NaN/Inf, signed zeros, subnormals, reciprocal overflow, saturation and source immutability. No performance or adoption claim from these controls.',
        'Only after those prerequisites, decide on a bounded integrated prototype with all setup/readback/destruction costs, fresh1% complete-solve screen, strict fixture guards, fresh16 confirmation and broad CPU/memory/capacity/holdout/cumulative checks.'
    ],
    'official_sources': [
        {'url': 'https://docs.nvidia.com/cuda/archive/12.9.0/nvrtc/index.html', 'supports': 'NVRTC returns PTX that can be loaded through the driver module API. It can run without a GPU. This supports preparing a bound artifact, not a speed or compatibility guarantee.'},
        {'url': 'https://docs.nvidia.com/cuda/archive/12.9.0/cuda-driver-api/group__CUDA__MODULE.html', 'supports': 'Driver module-data loading accepts compiled input and has its own resource/lifetime/error contract. Precompilation does not make loading or JIT free.'}
    ],
    'source_mutation_or_native_execution': False,
    'E011_implementation_created': False,
    'new_performance_candidate_created': False,
    'speed_gain_or_no_tradeoff_claimed': False,
    'reference_sha256': {str(p): h.sha(p) for p in reference.iterdir()}
}
h.save(A / 'design-review.json', design)
h.save(A / 'provenance.json', {'at': h.now(), 'script_sha256': h.sha(__file__), 'D147_protocol_sha256': h.sha(H/'protocol.json'), 'D147_parent_report_sha256': h.sha(parent_path), 'D147_substage_report_sha256': h.sha(sub_path), 'design_review_sha256': h.sha(A/'design-review.json'), 'all_new_artifacts_physical_X': True, 'archive_inputs_read_only': True, 'compiler_or_native_children_started': 0})
pub = []
for folder in [H, parent_path.parent, sub_path.parent, A]:
    for p in folder.rglob('*'):
        if not p.is_file() or p.suffix not in ['.json', '.rs', '.cu', '.py', '.patch', '.log']:
            continue
        key = folder.name + '/' + p.relative_to(folder).as_posix()
        dst = h.ar.DASHBOARD / 'evidence' / key
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            assert dst.read_bytes() == p.read_bytes(), key
        else:
            shutil.copyfile(p, dst)
        with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
            assert response.read() == p.read_bytes()
        pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    s = h.read(h.ar.STATUS)
    x = next(x for x in s['experiments'] if x['id'] == 'D147')
    x.update(status='measured', correctness='pass', stage='Substage observation complete; small shortcut declined', reason='All18 records and138 checkpoints exact;36 CPU records pass. Observer difference-0.224% meets the coarse10% rule. Inactive restoration41.59-44.13ms is below the prospective96.18ms proxy. E011 remains unimplemented. Full encoding203.56ms and compact active125.80ms motivate a broader transport review; no gain adopted.')
    x.setdefault('evidence', []).extend([{'label': 'Nested CPU stage measurements', 'url': 'evidence/D147-arena-substages/report.json'}, {'label': 'Matched observer controls', 'url': 'evidence/D147-readback/report.json'}])
    if any(x['id'] == 'E011' for x in s['experiments']):
        x = next(x for x in s['experiments'] if x['id'] == 'E011')
        x.setdefault('evidence', []).append({'label': 'Current-RAM component admission declined', 'url': 'evidence/D147-arena-substages/report.json'})
    assert not any(x['id'] == 'D148' for x in s['experiments'])
    s['experiments'].append({'id': 'D148', 'title': 'Packed active readback integration review', 'kind': 'diagnostic', 'status': 'staged', 'accepted': False, 'correctness': 'source_only', 'stage': 'Architecture, novelty and lifetime review before code', 'measurement_epoch': 'RAM20261028', 'reason': 'Review prebuilt auxiliary shader and existing CFV/pinned scratch packet transport. E009/E010 remain rejected; their counters do not prove the cause of initialization stalls. Continuation scratch persistence and all resource/fallback contracts must be proved before code or kernels. No optimization or new measurement yet.', 'evidence': [{'label': 'Proposed architecture and required proofs', 'url': 'evidence/D148-packed-readback-design/design-review.json'}]})
    s.update(updated_at=h.now(), active_experiment='D148', stage='Review packed readback architecture and scratch lifetime', activity='Inactive restoration is too small for its1% proxy. Next review a different active-data transport integration; E080 remains live with the current10.4564s baseline. No new speedup claimed.')
    h.ar.atomic_json(h.ar.STATUS, s)
O = ROOT / 'runs/D147-readback-checkpoint'
O.mkdir(exist_ok=False)
h.save(O / 'publication.json', {'at': h.now(), 'HTTP_verified_artifacts': pub, 'all_owned_children_terminal': True, 'source_main_live_PTX_custody_pass': True, 'new_optimization_source_or_D148_native_execution': False})
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
old = ledger.read_bytes()
assert b'### D147 CPU substage observations and D148 architecture review' not in old
proxy = sub['prospective_component_admission_proxy']
entry = f"""

### D147 CPU substage observations and D148 architecture review

Previous turn made progress by executing D146 and staging optional CPU-substage timers. Frozen D147 protocol {h.sha(H/'protocol.json')} retains original numerical work and all writes/joins, with one compiler and matched B1/P1,P2/B2,B3/P3. All18 full scientific records/full arena fingerprints and138 checkpoints match the original anchor. Parent reader256checks validates nine14-span traces; nested reader{sub['reader_checks']} checks all36 arena records, branch shapes, byte geometry, split endpoints and parent containment. All children terminal0; no preparation repair or sample extension.

Observer difference {q['observer_aggregate_perturbation_pct']}% passes the coarse absolute10% usefulness rule, not significance or per-component unbiasedness. Full rainbow write median203.5561ms; compact two-tone active125.7978ms and inactive43.4426ms; river full0.6755ms. Three per-process inactive sums {sub['per_instrumented_process_inactive_wall_sum_ms']}ms. The optimistic maximum {proxy['optimistic_observed_proxy_ms']}ms is below the prospectively defined1% fresh-ordinary proxy {proxy['required_ms']}ms. Decline E011 without implementation or timing a candidate. This is a finite optimistic admission heuristic, not a rigorous universal wall-time bound; removing a max scan could save less than removing the whole inactive stage.

New D148 source/design review targets the larger full/active work. It localizes exact rejected E009/E010 code and D011/D012/D013 counterevidence: old kernels were appended to the main CUDA source, not compiled as a separate quantization module; optional river setup/function loads were too small to explain the stall. D012 located CPU planning/budget wall excess before context creation; allocator/compiler/driver cause remains unproven. No old decision, sample or timing is regraded or reused as a performance score.

Proposed distinct integration keeps main CUDA source/runtime compilation unchanged, uses a source-bound auxiliary prebuilt PTX artifact with lazy admitted loading, and considers checked packet descriptors/q/scales in existing CFV scratch plus the existing pinned staging allocation. No new explicit output/descriptor device buffers are proposed, but module resource/JIT costs remain and must be measured. Original CPU inactive/F32/small/unsupported fallback and quantizer semantics must remain. This is only a hypothesis, with no optimization source, compiler or application kernel created.

D141's12 finite all-row dependency models support reviewing post-completion CFV reuse; they do not prove all runtime paths. Actual continuation storage/paging take and swap d_cfv within seven-buffer state. Contract/lifetime/format preservation, subsequent graph/evaluation/continuation behavior, descriptor/packing/u64/tail/capacity proofs and exact CPU-oracle kernel controls are mandatory before an integrated prototype. Official archived NVIDIA12.9 NVRTC/module APIs support prebuilt PTX loading; they do not establish zero loading/JIT cost, universal compatibility or performance. D148 design SHA {h.sha(A/'design-review.json')} records unresolved obligations and old failure counterevidence. No source/corpus/sample rescue of E009/E010 or E091.

{len(pub)} small artifacts HTTP byte-verified, bulk/source artifacts on X and S archive read-only. Accepted/main/live/protected PTX custody pass; all owned children terminal, locks absent. Current five-run baseline10.4564109s and prior-RAM14.7414% gain remain separate. No adoption, push or server replacement; goal active.
"""
nl = b'\r\n' if b'\r\n' in old else b'\n'
ledger.write_bytes(old + entry.encode().replace(b'\n', nl))
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '--only', '-m', 'research: qualify readback substage observations and review transport', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
h.custody()
h.save(O / 'report.json', {'at': h.now(), 'research_git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip(), 'D147_parent_report_sha256': h.sha(parent_path), 'D147_substage_report_sha256': h.sha(sub_path), 'E011_decision': sub['E011_design_decision'], 'D148_status': 'source_design_only_requires_novelty_lifetime_and_packet_proofs', 'current_E080_baseline_ms': 10456.4109, 'all_owned_children_terminal': True, 'source_main_live_PTX_custody_pass': True, 'GPU_sequence_locks_absent': True, 'all_new_artifacts_physical_X': True, 'goal_status': 'active'})
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/status.json', timeout=20) as response:
    served = json.load(response)
assert served['active_experiment'] == 'D148' and served['current_hardware_baseline']['aggregate_ms'] == 10456.4109
print(json.dumps({'observer_difference_pct': q['observer_aggregate_perturbation_pct'], 'inactive_ms': sub['per_instrumented_process_inactive_wall_sum_ms'], 'required_ms': proxy['required_ms'], 'E011': sub['E011_design_decision'], 'D148_source_only': True, 'HTTP_artifacts': len(pub)}), flush=True)
