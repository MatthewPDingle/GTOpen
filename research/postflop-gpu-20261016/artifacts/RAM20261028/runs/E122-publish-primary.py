"""Publish the retained E122 complete-solve screen and preserve the ledger."""
import json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
Q = ROOT / 'comparisons/E122-three-pair-comparison/report.json'
A = ROOT / 'comparisons/E122-root-crosscheck/report.json'
P = ROOT / 'runs/E122-primary-plan/protocol.json'
q, a, plan = h.read(Q), h.read(A), h.read(P)
perf = q['performance']
passed = perf['primary_timing_pass']
assert a['aggregate_gain_pct'] == perf['observed_gain_pct']
assert a['status'] == ('pass_initial_timing_only' if passed else 'pass_rejected')
assert q['exactness'] == {'fixture_results': 18, 'convergence_records': 138, 'all_exact': True}
assert q['ordinary_units_passed'] == 86 and q['ordinary_units_ignored'] == 4
assert not q['excluded_samples']
assert q['extension_runs'] == q['historical_timing_samples_used'] == q['RAM_baseline_samples_scored'] == 0
assert h.read(ROOT / 'runs/E122-primary-wrapper/complete.json')['all_owned_children_terminal']
D = ROOT / 'comparisons/E122-kernel-control-root-check/report.json'
direct = h.read(D)
assert direct['status'] == 'pass_scoped_full_predicated_correction_raw_equivalence'
assert direct['inventory']['comparison_pairs'] == 13300 and direct['kernel_launches'] == 26600
assert direct['all21_input_buffers_identical'] and direct['all_actual_inputs_match_exact_expected']
assert direct['whole_physical_outputs_bitwise_equal']
assert h.read(ROOT / 'runs/E122-direct-audit/complete.json')['all_owned_children_terminal']
S = ROOT / 'runs/E122-source'
m = h.read(S / 'manifest.json')
h.pin(S / 'baseline.cu', m['baseline_sha256'])
h.pin(S / 'candidate.cu', m['candidate_sha256'])
raw_complete = h.read(ROOT / 'runs/E122-kernel-control/execution/complete.json')
raw = ROOT / 'runs/E122-kernel-control/execution/raw-results.jsonl'
assert raw.stat().st_size == raw_complete['raw_bytes']
assert raw_complete['raw_sha256'] == direct['raw_sha256']
native = h.read(ROOT / 'runs/D301-predicated-correction-native/report.json')
assert native['status'] == 'pass_scoped_native_selector_removal_and_all30_original_priority_pairs'
receipts = []
for name in ['E122-resource/execution', 'D301-predicated-correction-native/execution',
             'E122-kernel-control/execution', 'E122-direct-audit', 'E122-final-build',
             'E122-primary-execution', 'E122-primary-wrapper']:
    for path in (ROOT / 'runs' / name).rglob('*.exit.json'):
        receipt = h.read(path)
        assert receipt['returncode'] == 0 and receipt.get('error') is None and receipt.get('cleanup') is None
        receipts.append({'path': str(path), 'sha256': h.sha(path), 'returncode': 0})
reason = (f"Complete-solve medians total {perf['baseline_full_cycle_ms']:.4f} to {perf['candidate_full_cycle_ms']:.4f} ms: "
          f"{perf['observed_gain_pct']:.6f}% observed gain. " +
          ('Initial screen passed; separate fresh16 and full raw engine/canonical/broad/material/holdout/current-RAM cumulative/app qualification remain before adoption.' if passed else
           'The fixed form failed the 1% or strict fixture guard and is closed without source variants or extra samples.'))
state = 'INITIAL_SPEED_PASS_FULL_QUALIFICATION_PENDING' if passed else 'REJECTED_CLOSED_PREDICATED_CORRECTION_FORM'
H = ROOT / 'runs/E122-primary-checkpoint'
H.mkdir(exist_ok=False)
h.save(H / 'report.json', {
    'id': 'E122-primary-checkpoint', 'at': h.now(), 'status': state, 'measurement_epoch': 'RAM20261028',
    'source_manifest_sha256': h.sha(S / 'manifest.json'), 'candidate_CUDA_sha256': m['candidate_sha256'],
    'change': 'compute120 up_show original if(pos<lb)lower+=r;else if(pos>=ub)higher+=r expressed as explicit inline PTX predicated add.rn.f32 with read/write +f constraints and unsigned else priority. Original metadata, host, all9ABIs, all8untargetedbodies and compute75all9bodies exact. Original tot_c/prefix/same/valid/tied/fullpayout/looporder/5barriers/grid/block/dynamicshared/quality/cadence retained.',
    'resource_warning': 'Show registers38to40. Local0/static1040/dynamicworst26520/stack1024/maxthreads1024/worst64,128,256occupancy3,3,3 unchanged. Resource inventory alone is not material-cost qualification.',
    'compiled_scope': 'D299 four complete Boolean rows/1000unsignedboundarytriples and bounded141uniqueCUDA/localallref history. D300 all30inline PTX corrections original pos/lower/upper/reach/selfreadwrite operands and unsigned else priority;5negativefixtures. D301 fixed-driver native FSEL30to0, predFADD30to60 and unpredFADD106to76: totalstaticFADD136unchanged,1FMUL/2FFMA and5barriers retained. All30nativepairs same position/reach value versions;4negativefixtures. Scoped linear/readers, not universal CFG/pointer/IEEE proof or dynamic instruction savings/speed attribution.',
    'reader_repair': 'Original D301 positive reader passed; first negative mutation made no change because literal whitespace before @P1 differed. V2 changes only negative-fixture anchoring to regex whitespace at fixed PC1ea0. Original script/protocol/failure receipt retained; source/captures/gates unchanged, no compiler/module/native/kernel/solver/speed repeat.',
    'direct_control': {'checks': direct['checks'], 'inventory': direct['inventory'],
                       'kernel_launches': direct['kernel_launches'], 'raw_path': str(raw),
                       'raw_bytes': raw_complete['raw_bytes'], 'raw_sha256': direct['raw_sha256'],
                       'scope': 'Entire E1202636cases/244physicalgeometries retained exactprefix plus24single-opponent reachcases from E121 data only. Original unencoded E120 probe and metadata for BOTH arms; no encodedE121source composition.2660cases x5widths1/32/64/128/256. All21physicalinputs literal equal and expected, wholeCFV/guards/NaNbits exact, acceptedrankoracle/anti-vacuity/2roundingwitnesses retained. Finiteisolatedcontrols only; fullrawengine/canonical/broad still unqualified.'},
    'raw_not_rehashed_after_complete_readers': True,
    'two_fresh_integrated_ordinary_builds_include_actual_NVRTC_JIT': True,
    'ordinary_units_passed': 86, 'ordinary_units_ignored': 4,
    'performance': perf, 'fixtures': q['fixtures'], 'exactness': q['exactness'],
    'primary_protocol_sha256': h.sha(P), 'comparison_sha256': h.sha(Q), 'root_replay_sha256': h.sha(A),
    'full_raw_engine_canonical_broad_material_completed': False,
    'remaining_qualification_requirements': plan['adoption_requirements'] if passed else [],
    'child_receipts': receipts, 'all_owned_screen_work_terminal': True, 'locks_absent': True,
    'accepted_main_live_protected_PTX_unchanged': True, 'candidate_adopted': False,
    'reason': reason, 'extra_or_rescue_samples': 0, 'last_primary_baseline': 'B377',
    'next_unused_primary_baseline': 'B378', 'best_qualified_config': 'E080/GPU/compressed/16workers/defaultaffinity',
    'hardware_epoch_baseline_ms': 10456.4109, 'historical_or_RAMtimings_scored': 0,
    'all_new_bulk_X_S_readonly_noT': True, 'goal_active': True})
sources = [ROOT / 'runs/D299-predicated-correction-scout/report.json', S / 'manifest.json',
           ROOT / 'runs/E122-resource/protocol.json', ROOT / 'runs/E122-resource/report.json',
           ROOT / 'runs/D300-predicated-correction-PTX/report.json',
           ROOT / 'runs/D301-predicated-correction-native/protocol.json',
           ROOT / 'runs/D301-predicated-correction-native/capture-report.json',
           ROOT / 'runs/D301-predicated-correction-native/reader-protocol.json',
           ROOT / 'runs/D301-predicated-correction-native/reader-v1-observer-failure.json',
           ROOT / 'runs/D301-predicated-correction-native/reader-protocol-v2.json',
           ROOT / 'runs/D301-predicated-correction-native/report.json',
           ROOT / 'runs/E122-kernel-control/protocol.json', D,
           ROOT / 'runs/E122-direct-audit/complete.json',
           ROOT / 'runs/E122-build-plan/protocol.json', ROOT / 'runs/E122-final-build/complete.json',
           P, Q, A, H / 'report.json']
published = []
for path in sources:
    key = (path.relative_to(ROOT / 'runs') if path.is_relative_to(ROOT / 'runs') else path.relative_to(ROOT / 'comparisons')).as_posix()
    dst = h.ar.DASHBOARD / 'evidence' / key
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        assert dst.read_bytes() == path.read_bytes()
    else:
        shutil.copyfile(path, dst)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
        assert response.read() == path.read_bytes()
    published.append({'url': 'evidence/' + key, 'sha256': h.sha(path)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    e = next(row for row in status['experiments'] if row['id'] == 'E122')
    e.update(status='running' if passed else 'rejected', accepted=False,
             stage='Initial pass; full qualification pending' if passed else 'Closed: complete-solve screen rejected',
             correctness='13300directpairs/26600launches and86ordinaryunits pass; fullscience/checkpoints exact; broaderraw/material unverified',
             performance=perf, reason=reason)
    e['evidence'] += [{'label': 'Complete-solve comparison', 'url': 'evidence/' + Q.parent.name + '/report.json'},
                      {'label': 'Full-log and median replay', 'url': 'evidence/' + A.parent.name + '/report.json'},
                      {'label': 'All controls and checkpoint', 'url': 'evidence/' + H.name + '/report.json'}]
    status.update(updated_at=h.now(), state='running', goal_status='active', active_experiment='E122',
                  stage='Predicated corrections: full qualification next' if passed else 'Predicated correction form closed; next distinct lead',
                  activity=reason + ' E080 remains qualified and live; no gain adopted.')
    h.ar.atomic_json(h.ar.STATUS, status)
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
prefix = ledger.read_bytes()
assert b'\n## E122 explicit rank-predicated corrections' not in prefix
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
entry = f'''

## E122 explicit rank-predicated corrections - {'initial pass, full qualification pending' if passed else 'rejected and closed'}

D299 bounded141uniqueCUDA/localallref review found no equivalent explicit rank-correction predication form. Existing native baseline already had30predFADD+30predFSEL; no claim wholly unpredicated. FourcompleteBooleanrows/1000unsignedboundarytriples preserve original if/else unsignedpriority. Fixed oneCUDAcompute120 up_show form SHA{m['candidate_sha256']}; read/write +f originalaccumulators, add.rn.f32 underoriginalrankpredicates. Allhost/metadata/ABIs/launches/loops/tot_c/prefix/same/valid/tied/fullpayout/5barriers/quality unchanged, compute75 all9bodies exact. One owned resource compiler/two-target NVRTC moduleprobe, all8untargeted120bodies exact. Showregister38->40warning,local0/static1040/dynamic26520/stack1024/maxthreads1024/worstoccupancy3,3,3unchanged.

D300all30PTX originalposition/bounds/reach/selfreadwrite/elsepriority chains and5barriers,5negativefixtures. D301oneownedmodule+CUPTIcapture/one nvdisasm, same-driver acceptedbaseline reused. NativeFSEL30->0, predFADD30->60/unpredFADD106->76,totalstatic136FADDunchanged,1FMUL/2FFMA and5barriersretained. All30nativeconditionalpairs shareposition/reachvalueversions andoriginalGE/negatedGEelsepriority;4negativefixtures. Linear-current-definition/scoped readers only; nativefullpointer/CFG/IEEE/dynamicfrequency/throughput/speed notproved. OriginalD301positiveinspectpassed; negativefixture failed to mutate19literalspaces vsactual15before@P1. AdditiveV2regexwhitespacefixedPC1ea0only; originalprotocol/script/failurereceiptretained. No compiler/module/nativekernel/solver/timingrepeat, sourcegatesunchanged.

FrozenfulloriginalGPUcontrol: E1202636cases/244geometries byteexactprefix plus24single-opponentreachcases fromE121 corpusDATAonly; originalunencodedE120probe/metadata BOTHarms,noencoding/sourcecomposition.2660cases x5widths1/32/64/128/256=13300pairs/26600launches. All21physicalinputbuffers literalidentical/expected,wholephysicalCFV/guards/NaNbits exact; acceptedrankoracle/anti-vacuity/2roundingwitnesses retained. Inventory{json.dumps(direct['inventory'])};{direct['checks']}readerchecks,raw{raw_complete['raw_bytes']}bytes/SHA{direct['raw_sha256']}retainedX. Finiteisolatedcontrols only, notfullengine/canonical/broad equivalence. Twofreshordinaryoffline/locked feature/primary Cargobuilds includeactualNVRTC/JIT; acceptedCUDA restoredaftereach.86ordinaryunits/4ignoredpass.

FrozenB375/E122R1,E122R2/B376,B377/E122R3 once.18fullscientificrecords/138checkpoints exact; sumfixturemedians{perf['baseline_full_cycle_ms']:.10f}->{perf['candidate_full_cycle_ms']:.10f}ms,unroundedgain{perf['observed_gain_pct']:.12f}%,initialpass={passed},strictguards={json.dumps(perf['fixture_regression_guard'])}. Separatefull-log/scientificrecord/sortedmedianreplayagrees. Noexclusions/extensions/historical/RAMbaselinepooling/significanceclaim. {reason} {'Separatefresh16/fullrawengine/canonical/broad/material/holdout/currentRAMcumulative/actualapp remain before adoption.' if passed else 'Close fixedsource/asm/constraint/predicate/architecture/width/helper/flags/quality/sampleform,no rescue. Fullrawengine/canonical/broad/materialnotrunafterclosureandneverclaimed.'}

All{len(receipts)}ownedcompiler/module/disassembly/kernel/reader/build/primaryreceipts terminal0,locksabsent,accepted/main/live/protected2PTXexact. AllnewbulkX/Sreadonly/noT. QualifiedliveE080/GPU/compressed/16/defaultaffinity,newadoptedgain0,RAMreference10456.4109msseparate,lastprimaryB377/nextB378. {len(published)}artifactsHTTPbyteverified,checkpoint{H}. Ledgerprefixbyteexact/localledger-onlycommit/nopush,goalactive.
'''
ledger.write_bytes(prefix + entry.encode())
assert ledger.read_bytes()[:len(prefix)] == prefix
h.custody()
subprocess.run(['git', 'add', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
assert subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).splitlines() == ['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '-m', 'research: measure explicit predicated showdown corrections'], cwd=h.REPO, check=True)
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/status.json', timeout=20) as response:
    assert response.read() == h.ar.STATUS.read_bytes()
h.save(H / 'publication.json', {'at': h.now(), 'local_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip(),
                               'HTTP_byte_verified': published, 'report_sha256': h.sha(H / 'report.json'), 'candidate_adopted': False, 'goal_active': True})
h.custody()
print(json.dumps({'status': state, 'gain_pct': perf['observed_gain_pct'], 'primary_pass': passed, 'candidate_adopted': False}), flush=True)
