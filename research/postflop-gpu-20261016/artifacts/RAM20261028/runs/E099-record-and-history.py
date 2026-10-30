import json, shutil, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h

OLD = Path(r'S:\GTOpen-research\postflop-gpu-20261016')
h.custody()
assert not (ROOT / 'gpu-run.lock').exists()
assert not (ROOT / 'epoch-sequence.lock').exists()
h.ar.refuse_active(h.ar.live_status())
terminal = h.read(ROOT / 'runs/E099-terminal-checkpoint/report.json')
assert terminal['all_owned_compilers_native_readers_terminal']
assert not terminal['new_gain_accepted_or_deployed']

def inputs(paths):
    return {str(p): {'sha256': h.sha(p), 'bytes': p.stat().st_size} for p in paths}

cache = OLD / 'runs/D100-show-cache-configuration/report.json'
cache_root = OLD / 'comparisons/D100-cache-resource-root-check/report.json'
cr = h.read(cache)
assert cr['status'] == 'rejected_resource_prerequisite'
assert cr['resource']['kernel_launches'] == 0
assert all(x['candidate_blocks'] < x['baseline_blocks'] for x in cr['resource']['occupancy'])
D187 = ROOT / 'runs/D187-cache-preference-history'
D187.mkdir(exist_ok=False)
h.save(D187 / 'report.json', {
    'id': 'D187', 'at': h.now(), 'status': 'declined_closed_family_before_execution',
    'proposal': 'Per-function shared/L1 cache preference for showdown',
    'closed_family': 'D100 per-function cache configuration',
    'original_result': cr['status'],
    'original_all_occupancy_queries_lower': len(cr['resource']['occupancy']),
    'original_no_alternate_preference_carveout_kernel_scope_sweep': True,
    'decision': 'Do not reopen via PREFER_SHARED, carveout or entry subset. No new source, compiler, CUDA query, application kernel or timing sample.',
    'new_native_or_compiler_processes': 0,
    'new_gain_accepted': False, 'inputs': inputs([cache, cache_root]),
})

show_source = OLD / 'runs/E069-source/source-review.json'
show_compare = OLD / 'comparisons/E069-three-pair-comparison/report.json'
show_root = OLD / 'comparisons/E069-root-crosscheck/report.json'
sr, sq = h.read(show_source), h.read(show_compare)
assert sq['decision'] == 'rejected' and not sq['candidate_accepted']
assert sq['performance']['fixture_regression_guard'][1]['failed']
D188 = ROOT / 'runs/D188-show-order-history'
D188.mkdir(exist_ok=False)
h.save(D188 / 'report.json', {
    'id': 'D188', 'at': h.now(), 'status': 'declined_closed_family_before_execution',
    'proposal': 'Group showdown nodes by river slot within existing level spans',
    'closed_family': 'D111/D112/E069 showdown ordering; combined D115/E071 remains separately closed',
    'original_transform': sr['transform'],
    'original_performance': sq['performance'],
    'decision': 'Same river-slot permutation is an equivalent closed GPU locality mechanism even if constructed by counting rather than sorting. No alternate key, threshold, scope or sample rescue.',
    'new_native_or_compiler_processes': 0, 'new_gain_accepted': False,
    'inputs': inputs([show_source, show_compare, show_root]),
})

# Additive correction only: retain every original protocol, result and raw byte.
old_plan = OLD / 'comparisons/D110-plan-stage-root-check/report.json'
old_plan_result = h.read(old_plan)
assert old_plan_result['status'] == 'observer_gate_failed_diagnostic_only'
addendum = ROOT / 'runs/D183-plan-phase-terminal/late-history-addendum.json'
h.save(addendum, {
    'id': 'D183-late-history-addendum', 'at': h.now(),
    'status': 'phase_timings_excluded_from_candidate_or_headroom_admission',
    'finding': 'D110 was a prior failed internal planner observer. Its recorded closure prohibits finer/coarser marker or timing rescue. This match should have been found before D183.',
    'correction': 'Keep D183 full plan raw-byte equivalence and original observations. Do not use D183 phase medians, ratios or inferred removable cost to admit an optimizer or headroom claim. Do not repeat or retune the observer.',
    'E099_dependency': 'D184/E099 uses actual retained plan geometry and independent source alignment/ownership checks; no D183 phase timing was scored. E099 independent full raw and complete-cycle rejection stands.',
    'original_artifacts_modified': False, 'native_or_compiler_repeats': 0,
    'inputs': inputs([old_plan, ROOT / 'runs/D183-plan-phase-terminal/report.json']),
})

ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
assert '### E099 complete-cycle rejection and terminal custody' not in ledger.read_text(encoding='utf-8')
with ledger.open('a', encoding='utf-8', newline='\n') as f:
    f.write('''

### E099 complete-cycle rejection and terminal custody

Fixed primary protocol 684f15dc60de40c492bca132a00db147f75cf961c7c2743188d0a290ce084d23 completed V099-unit (86 passed, 4 ignored), then exactly B311/E099R1, E099R2/B312, B313/E099R3. All seven native processes terminal 0; 18 full scientific records and 138 convergence checkpoints exactly match the immutable anchor. Original complete clocks include actual NVRTC 12.9 compilation/JIT, all initialization, same-quality solves/checks and full readback. No exclusions, extensions, historical or RAM-reference pooling.

Unrounded sum of fixture medians 9508.6109 -> 9556.7073 ms, observed gain -0.5058194146949515%. Rainbow median 0.21486756044706876% slower with 1/3 matched pairs slower; two-tone 0.8786664790074625% slower with 1/3; neither fails the strict majority guard. River 2.953243349523569% slower with 2/3 pairs slower, guard failed. Aggregate below 1% and river guard failure REJECT E099. Not a statistical or universal slowdown claim. No vector width, arity, guard, helper, entry subset, flags, source or sample rescue; no fresh16/broad/material/holdout/adoption progression after rejection.

Separate complete-log/science/median/guard replay passes 97 checks with the same rejected outcome. Terminal checkpoint verifies resource/direct/engine/canonical/build/primary receipts, original D185 metadata-reader failure preserved alongside corrected read-only reader with no native repeat, 66 retained canonical raw file extents, source/main/live/protected PTX and absent locks. Entire raw bytes were already compared by the original full reader and were not rehashed at closure. All owned compiler/native/readers terminal. Reports and terminal evidence published and HTTP-byte verified. Accepted E080/GPU/compressed/16 workers remains live; no new gain. Original current-RAM reference 10456.4109 ms remains a separate cohort, last primary control B313. All new output X; archive read-only, no T access; goal active.

### D187/D188 history guards; additive D183 diagnostic correction

D187 read-only history review declines shared/L1 function-cache preference as a variant of closed D100. Original D100 kept code/resources identical but all 216 occupancy queries lowered resident blocks; its closure explicitly excludes alternate preference, carveout or kernel scope sweeps. No new shader, compiler, CUDA query/kernel or timing observation.

D188 declines showdown river-slot grouping within launch spans: D111/D112/E069 already implemented the exact tuple (river_slot,node_id) permutation. E069 all-science-exact complete medians 10809.5565 -> 10807.2525 ms gained only 0.021314472985102632%, with two-tone 2.3173084986056764% slower in 2/3 pairs and a failed guard. A counting construction yielding the same ordering does not establish a new GPU mechanism. No alternate sort key/threshold/scope or sample rescue; no new native/compiler processes.

Late D110 history match exposes an earlier failed internal planner observer whose closure prohibited finer/coarser marker or timing rescue. This should have been found before D183. Additive late-history-addendum.json retains all D183 protocols, native output and full raw-plan equivalence, but EXCLUDES D183 phase timings/ratios from optimization or headroom admission. No diagnostic rerun or retuning. D184/E099 relies on raw geometry/alignment and independent full device/canonical/speed evidence, not those phase timings; E099 rejection stands. No scientific report rewritten. All three read-only reports published with original evidence hashes, zero new native/compiler samples, no gain accepted.
''')

published = []
for p in [D187 / 'report.json', D188 / 'report.json', addendum]:
    dst = h.ar.DASHBOARD / 'evidence' / p.parent.name / p.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    assert not dst.exists()
    shutil.copyfile(p, dst)
    relative = dst.relative_to(h.ar.DASHBOARD).as_posix()
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/' + relative, timeout=20) as response:
        assert response.read() == p.read_bytes()
    published.append({'label': p.parent.name + ' history review', 'url': relative})

with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    s = h.read(h.ar.STATUS)
    item = next(x for x in s['experiments'] if x['id'] == 'E099')
    item['reason'] = 'Complete fixture medians: 9508.6109 to 9556.7073 ms, 0.51% slower. River was 2.95% slower in 2 of 3 matched pairs and failed its guard. All declared exactness checks passed. Rejected; no extra samples or source variants.'
    item['evidence'].extend(published)
    s.update(updated_at=h.now(), stage='Paired loads rejected; new source research continues',
             activity='E099 passed all declared accuracy checks but was 0.51% slower overall and failed the river guard. Two duplicate ideas were declined from retained history. E080 with 16 workers remains live; no new gain adopted.')
    h.ar.atomic_json(h.ar.STATUS, s)
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/status.json', timeout=20) as response:
    assert response.read() == h.ar.STATUS.read_bytes()
h.custody()
subprocess.run(['git', 'add', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
subprocess.run(['git', 'commit', '-m', 'research: reject paired action speed screen and retain history guards'], cwd=h.REPO, check=True)
print(json.dumps({'recorded': 'E099 rejection, D187/D188 declines, D183 additive exclusion', 'new_native_processes': 0, 'published_reports': len(published), 'best_qualified': 'E080 / GPU / compressed / 16 workers'}), flush=True)
