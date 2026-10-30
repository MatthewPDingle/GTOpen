import sys, json, shutil, subprocess, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
H = ROOT / 'runs/E091-primary-plan'
P = h.read(H / 'protocol.json')
qp = ROOT / 'comparisons/E091-three-pair-comparison/report.json'
rp = ROOT / 'comparisons/E091-root-crosscheck/report.json'
q, root = h.read(qp), h.read(rp)
perf = q['performance']
passed = perf['primary_timing_pass']
assert root['aggregate_gain_pct'] == perf['observed_gain_pct'] and root['status'] == ('pass_initial_timing_only' if passed else 'pass_rejected')
assert h.read(ROOT / 'runs/E091-primary-execution/complete.json')['all_owned_children_terminal']
for p, digest in P['input_sha256'].items():
    h.pin(p, digest)
raw = h.read(ROOT / 'comparisons/E091-raw-control/report.json')
resource = h.read(ROOT / 'runs/E091-resource/report.json')
incidence = h.read(ROOT / 'comparisons/D144-incidence/report.json')
assert raw['cases'] == 1530 and raw['kernel_launches'] == 3060 and raw['all_full_actual_inputs_and_outputs_exact']
assert resource['status'] == 'pass_compiled_prerequisites' and incidence['decision'] == 'eligible_for_frozen_whole_solve_screen'
O = ROOT / 'runs/E091-initial-decision'
O.mkdir(exist_ok=False)
reason = f"The fixed complete-solve screen measured {perf['observed_gain_pct']:.6f}% aggregate improvement. All 18 scientific records, 138 convergence checkpoints, 86 ordinary tests and 1,530 raw GPU comparisons passed. "
if passed:
    reason += 'The initial speed gate passed. Separate fresh confirmation, broader correctness and material checks, holdout and cumulative qualification remain. Not adopted.'
else:
    why = []
    if perf['observed_gain_pct'] < 1:
        why.append('below the unrounded 1% cutoff')
    failures = [x['fixture_id'] for x in perf['fixture_regression_guard'] if x['failed']]
    if failures:
        why.append('repeatable fixture slowdown: ' + ', '.join(failures))
    reason += 'Rejected: ' + '; '.join(why) + '. The exact zero-reach normalization shortcut is closed; no source, predicate, width, action-menu, fixture or extra-sample rescue.'
decision = {'id': 'E091', 'at': h.now(), 'measurement_epoch': 'RAM20261028', 'decision': q['decision'], 'performance': perf, 'ordinary_units_passed': 86, 'ordinary_units_ignored': 4, 'exact_scientific_records': 18, 'exact_checkpoints': 138, 'direct_raw_pairs': 1530, 'direct_launches': 3060, 'direct_reader_checks': raw['checks'], 'resource_report_sha256': h.sha(ROOT / 'runs/E091-resource/report.json'), 'incidence_report_sha256': h.sha(ROOT / 'comparisons/D144-incidence/report.json'), 'assessment_sha256': h.sha(qp), 'root_replay_sha256': h.sha(rp), 'primary_whole_arena_fingerprints_exact': True, 'primary_raw_arena_bytes_independently_compared': False, 'all_samples_retained': True, 'extension_runs': 0, 'historical_or_RAM_baseline_timing_samples_scored': 0, 'source_adopted': False, 'live_source': 'E080', 'reason': reason}
h.save(O / 'decision.json', decision)
pub = []
folders = [ROOT / 'runs/E091-resource', ROOT / 'runs/E091-raw-control', ROOT / 'runs/D144-incidence', ROOT / 'runs/E091-build-plan', ROOT / 'runs/E091-final-build', H, ROOT / 'runs/E091-primary-execution', qp.parent, rp.parent, O]
for folder in folders:
    for p in folder.rglob('*'):
        if not p.is_file() or p.suffix not in ['.json', '.py', '.rs', '.cu', '.patch', '.log']:
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
    x = next(x for x in s['experiments'] if x['id'] == 'E091')
    x.update(status='measured' if passed else 'rejected', accepted=False, correctness='pass_scoped', stage='Initial pass; separate confirmation pending' if passed else 'Closed: performance gate failed', reason=reason, baseline_full_cycle_ms=perf['baseline_full_cycle_ms'], full_cycle_ms=perf['candidate_full_cycle_ms'], observed_gain_pct=perf['observed_gain_pct'], updated_at=h.now())
    x.setdefault('evidence', []).extend([{'label': 'Complete-solve comparison', 'url': 'evidence/E091-three-pair-comparison/report.json'}, {'label': 'Full-log arithmetic replay', 'url': 'evidence/E091-root-crosscheck/report.json'}, {'label': 'Initial decision', 'url': 'evidence/E091-initial-decision/decision.json'}])
    s.update(updated_at=h.now(), active_experiment='E091' if passed else None, state='running', goal_status='active', stage='E091 separate confirmation preparation' if passed else 'Investigating the next independent performance mechanism', activity=reason + ' E080 remains live; its current RAM baseline is 10.4564 s. The prior 14.74% cumulative gain remains historical.')
    h.ar.atomic_json(h.ar.STATUS, s)
h.save(O / 'publication.json', {'at': h.now(), 'HTTP_verified_artifacts': pub, 'all_owned_children_terminal': True, 'source_main_live_PTX_custody_pass': True, 'all_new_bulk_physical_X': True, 'candidate_adopted': False})
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
before = ledger.read_bytes()
assert b'### E091 zero-reach normalization shortcut' not in before
entry = f"""

### E091 zero-reach normalization shortcut

Previous turn established the current RAM E080 baseline (10.4564109 s), rejected E090, and staged E091. This turn compiled exactly that staged source without production activation. The shortcut follows the unchanged ordered positive-regret sum in unlocked down_action: signed-zero parent reach plus finite sum stores the original signed zero in unchanged action/address order. Nonfinite sums and locked nodes take the original path. All other arithmetic, precision, host plumbing, launches, graph schedule, allocations, quality and persistence are unchanged. No closed E035/E036 terminal shortcut or E090 scratch-stride hunk is composed.

Resource protocol {h.sha(ROOT/'runs/E091-resource/protocol.json')} ran four NVRTC compilations and actual compute120 module queries, with no application launch. Both arch120/75 retain the other eight normalized entries, 18-parameter ABI and barriers. Actual registers40/40, local32/32 bytes, shared/stack/max-thread/default limits and theoretical64/128/256 occupancy are unchanged (128-thread12/12). No dynamic resource or speed inference.

Raw protocol {h.sha(ROOT/'runs/E091-raw-control/protocol.json')} fixed 1530 pairs and3060 launches across both actors/asymmetric widths, common/generic action counts, zero/tail hand counts, five thread shapes, locks, signed zeros, nonfinite/overflow/subnormal inputs and count0. All physical outputs and12 actual immutable vectors match, with full guards. Reader{raw['checks']} checks, both signed-zero witness counts {raw['positive_negative_zero_witness_words']}, nonfinite output words{raw['nonfinite_output_words_both_arms']}. All five raw files remain on X. A preparer parser check caught missing whitespace in the reader before protocol/compiler/native work; originals and pre-native syntax/bookkeeping repair retained, corpus/source unchanged.

D144 diagnostic protocol {h.sha(ROOT/'runs/D144-incidence/protocol-r2.json')} used unchanged E080 training/evaluation code with six synchronized read-only reach/metadata snapshots (flops20/200, river20/60). All3 scientific records/full arena fingerprints and23 checkpoints match E020C1. Reader{incidence['reader_checks']} checks verifies unique physical writers, input-owner bounds and full actual arrays. Observed subsets are actor0 from p1 and actor1 from p0 retained through p1 reuse; p0 actor0 is explicitly unobserved. Sampled flop zero-hand fractions range about52% to75%. This is necessary-condition incidence, not finite-sum eligibility, dynamic time share or predicted saving. Snapshot I/O disqualifies these clocks from performance scoring. One initial diagnostic compile failed E0753 because copied inner documentation followed prefix items; original code/compiler output/protocol retained. R2 changes exactly seven comment markers and bookkeeping paths before any solve. Final native solves/readers passed; the failed compiler remains failed.

Two fresh integrated feature/primary Cargo builds on X passed and restored E080 after each. Primary protocol {h.sha(H/'protocol.json')} froze V091-unit (86 passed,4 ignored) followed by B296/E091R1,E091R2/B297,B298/E091R3. All18 complete scientific results and138 checkpoints match the unchanged reference. Sum fixture medians {perf['baseline_full_cycle_ms']} to {perf['candidate_full_cycle_ms']} ms, unrounded gain {perf['observed_gain_pct']}%; strict guards {json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. No exclusions/extensions or historical/epoch-baseline pooling. Primary whole-arena fingerprints match; primary raw arena bytes were not independently compared. Complete clocks retain tree/CPU allocation, all GPU initialization/NVRTC/JIT, same-quality solve/checks/full readback; Cargo and fingerprints excluded.

{reason}

Independent full-log replay passed{root['checks']} checks, assessment SHA {h.sha(qp)}. {len(pub)} small artifacts HTTP byte-verified. All owned children terminal; locks absent; accepted source/main/live/protected PTX custody passed. No adoption, push or live replacement. All new outputs physically X; last primaryB298; goal active.
"""
newline = b'\r\n' if b'\r\n' in before else b'\n'
ledger.write_bytes(before + entry.encode().replace(b'\n', newline))
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '--only', '-m', 'research: test zero-reach normalization without quality changes', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
h.custody()
print(json.dumps({'decision': q['decision'], 'gain_pct': perf['observed_gain_pct'], 'fixture_guards': perf['fixture_regression_guard'], 'HTTP_artifacts': len(pub)}), flush=True)
