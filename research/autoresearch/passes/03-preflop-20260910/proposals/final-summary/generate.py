"""Derive a bounded report from frozen JSON evidence; never touch native saves or APIs."""
import argparse
import json
import math
import gzip
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = HERE.parent.parent


def read_json(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8-sig') as stream:
        return json.load(stream)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def number(value, label, positive=False):
    require(type(value) in (int, float) and math.isfinite(value), label + ': nonfinite/missing number')
    require(not positive or value > 0, label + ': must be positive')
    return value


def reduction(old, new):
    return round(100 * (1 - number(new, 'candidate time', True) / number(old, 'original time', True)), 4)


def fixed_work(rows):
    expected = {'baseline-eight-a', 'baseline-seven-a', 'baseline-six-a', 'baseline-three-a'}
    require(len(rows) == 4 and {r.get('control') for r in rows} == expected, 'incomplete primary GPU comparisons')
    result = []
    for row in rows:
        require(row.get('exact') is True, 'nonexact primary GPU comparison: ' + row['control'])
        item = {k: row[k] for k in ('fixture', 'control', 'candidate')}
        for name in ('iteration_ms', 'check_ms'):
            values = row[name]
            computed = reduction(values['original'], values['final'])
            require(abs(number(values['reduction_percent'], name) - computed) < 0.0001, 'inconsistent primary reduction')
            item[name] = {'original': values['original'], 'final': values['final'], 'reduction_percent': computed}
        item['exact_reported_fingerprint_gap_ev'] = True
        result.append(item)
    return {'scope': 'Same-state fixed work, not time to convergence; iteration medians exclude first iteration.', 'comparisons': result}


def accuracy(rows):
    require(len(rows) == 2 and {r.get('fixture') for r in rows} == {'modeled', 'eight'}, 'incomplete extended comparisons')
    output = []
    for row in rows:
        fixture = row['fixture']
        require(row.get('exact_trajectory_and_final_state') is True and row.get('final_mismatches') == [], 'nonexact extended result: ' + fixture)
        left, right = row['original'], row['candidate']
        a, b = left.get('result'), right.get('result')
        require(isinstance(a, dict) and isinstance(b, dict), 'missing extended result')
        for side in (left, right):
            r = side['result']
            require(side.get('error') is None and side.get('status') == 'target_reached' and r.get('status') == 'target_reached', 'incomplete/failed extended run')
            require(r.get('converged') is True and r.get('roundtrip_verified') is True, 'unverified extended completion')
            require(number(r['learning_gap_bb'], 'gap') <= number(r['target_gap_bb'], 'target', True), 'target not reached')
            require(r['iteration'] == r['start_iteration'] + r['done'] and r['done'] > 0, 'inconsistent native iteration')
            require(r['done'] % r['check_every'] == 0, 'unsupported partial checkpoint cadence')
        for key in ('start_iteration', 'iteration', 'done', 'budget_mb', 'check_every', 'target_gap_bb', 'gaps', 'evs', 'arena_fnv1a64', 'live_seats'):
            require(a.get(key) == b.get(key) and a.get(key) is not None, 'extended final mismatch: ' + key)
        for key in ('gaps', 'evs'):
            require(len(a[key]) == len(a['live_seats']) > 0, 'invalid final vector shape')
            for value in a[key]:
                number(value, key)
        expected = list(range(a['check_every'], a['done'] + 1, a['check_every']))
        checkpoints = row.get('matched_checkpoints', [])
        require([c.get('done') for c in checkpoints] == expected, 'incomplete matched checkpoints')
        for c in checkpoints:
            require(c.get('exact') is True and c.get('mismatched_fields') == [], 'nonexact checkpoint')
        require(len(left['checkpoints']) == len(right['checkpoints']) == len(expected), 'missing source checkpoints')
        for x, y, done in zip(left['checkpoints'], right['checkpoints'], expected):
            for key in ('done', 'iteration', 'gaps', 'evs', 'learning_gap_bb', 'live_seats', 'target_gap_bb', 'target_reached'):
                require(x.get(key) == y.get(key) and x.get(key) is not None, 'source checkpoint mismatch: ' + key)
            require(x['done'] == done and x['iteration'] == a['start_iteration'] + done, 'checkpoint sequence mismatch')
        old, new = a['trajectory_ms'], b['trajectory_ms']
        computed = reduction(old, new)
        require(abs(number(row['trajectory_reduction_percent'], 'extended reduction') - computed) < 0.0001, 'inconsistent extended reduction')
        output.append({'fixture': fixture, 'start_native_iteration': a['start_iteration'], 'final_native_iteration': a['iteration'],
                       'additional_iterations': a['done'], 'target_gap_bb': a['target_gap_bb'], 'final_gap_bb': a['learning_gap_bb'],
                       'exact_checkpoints': len(expected), 'trajectory_seconds': {'original': round(old / 1000, 4), 'final': round(new / 1000, 4)},
                       'trajectory_minutes': {'original': round(old / 60000, 4), 'final': round(new / 60000, 4)},
                       'reduction_percent': computed, 'exact_trajectory_and_final_state': True})
    return {'scope': 'Time from the same frozen starting save to the same fixed target; excludes startup and final save/reload.', 'comparisons': output}


def fresh_qualifier(rows):
    require(len(rows) == 3 and {r.get('pair') for r in rows} == {1, 2, 3}, 'fresh qualification needs all three pairs')
    result = {'source': 'fresh-eight-comparisons.json', 'scope': 'Fresh-state first10-iteration checkpoint and fixed20 work; not convergence time. All pairs miss0.005bb.', 'pairs': []}
    for row in rows:
        require(row.get('exact_checkpoints_and_native') is True, 'nonexact optional fresh comparison')
        end = row['final']
        require(end.get('roundtrip_verified') is True, 'incomplete optional fresh result')
        require(end.get('start_iteration') == 0 and end.get('iteration') == end.get('done') == 20 and end.get('check_every') == 10, 'unexpected fresh qualification scope')
        require(end.get('converged') is False and end.get('status') == 'not_converged_iteration_limit' and end.get('target_gap_bb') == 0.005 and number(end['learning_gap_bb'], 'fresh gap') > 0.005, 'unexpected fresh target result')
        times = row['timings']
        old, new = times['original'], times['compatible']
        result['pairs'].append({'pair': row['pair'], 'order': row['order'], 'start_iteration': end['start_iteration'], 'final_iteration': end['iteration'],
                                'target_reached': end['converged'], 'final_gap_bb': end['learning_gap_bb'], 'target_gap_bb': end['target_gap_bb'],
                                'fixed_work_reduction_percent': reduction(old['fixed_work_ms'], new['fixed_work_ms']),
                                'load_init_first_checkpoint_seconds': {'original': old['load_init_first_checkpoint_ms']/1000, 'final': new['load_init_first_checkpoint_ms']/1000}})
    require(result['pairs'], 'empty optional fresh comparisons')
    return result


def budget_qualifier(value, source):
    expected = {'api-auto-modeled-b.json': (23924, 32, True, True),
                'api-modeled23000-a.json': (23000, 31, False, False)}
    require(source in expected, 'unknown published API budget qualification')
    budget, batch, cache, automatic = expected[source]
    require(value.get('full_native_exact') is True and value.get('fixed_pair_only') is True and
            value.get('outcome') == 'both_completed_full_native_exact', 'incomplete/nonexact API budget outcome')
    require(value.get('candidate_automatic_budget') is automatic, 'wrong API budget mode')
    if not automatic:
        require(value.get('candidate_requested_budget_mb') == budget, 'wrong explicit API budget')
    require(value.get('original_resolved_budget', {}).get('budget_mb') == budget, 'original API budget mismatch')
    layout = value['candidate_layout']
    require(layout.get('budget_mb') == budget and layout.get('multiway_batch') == batch and
            layout.get('hu_equity_cache_enabled') is cache, 'unexpected published API layout')
    require(layout.get('reference_multiway_batch') == layout.get('literal_reference_multiway_batch') == batch and
            layout.get('reference_hu_cache_enabled') is cache and layout.get('literal_reference_hu_cache_enabled') is cache and
            layout.get('batch_policy') == 'deployed_prepass', 'API layout does not preserve literal reference')
    require(layout.get('multiway_particles') == 1024 and layout.get('model') == 'coupled_deck_v1' and layout.get('seats') == 6,
            'unexpected API model/precision scope')
    require(number(layout['planned_need_mb'], 'planned API allocation', True) <= budget, 'API allocation exceeds its budget')
    require(set(value['cases']) == set(value['first_checkpoint_seconds']) == {'original', 'candidate'}, 'incomplete API budget pair')
    intervals = {}
    for side, case in value['cases'].items():
        require(case.get('completed') is True and case.get('loaded_native_exact') is True and case.get('timed_out') is False and
                case.get('error') is None and case.get('guard_failures') == [], 'incomplete/failed API budget case: ' + side)
        timing = number(value['first_checkpoint_seconds'][side], 'API checkpoint time', True)
        require(case.get('first_published_checkpoint_seconds') == timing, 'API timing summary mismatch')
        lo = number(case['publication_interval_lower_seconds'], 'API publication lower bound')
        hi = number(case['publication_interval_upper_seconds'], 'API publication upper bound', True)
        require(0 <= lo <= hi == timing, 'invalid API publication interval')
        intervals[side] = {'lower': lo, 'upper': hi}
    require(value['cases']['candidate']['layout'] == layout, 'candidate API layout summary mismatch')
    require(value['cases']['original']['layout'].get('multiway_batch') == batch, 'original API observed batch mismatch')
    require(value.get('comparator_run') and value.get('finished_utc'), 'missing completed API comparison provenance')
    result = {'source': source, 'outcome': value['outcome'], 'scope': 'One short real-server API budget pair; not convergence time or a general speed estimate.',
              'budget_mb': budget, 'candidate_automatic_budget': automatic, 'particle_batch': batch,
              'candidate_hu_equity_cache_enabled': cache,
              'original_hu_cache_evidence': value['cases']['original']['layout'].get('hu_cache_observation', 'not recorded'),
              'planned_solver_allocation_mb_not_device_residency': layout['planned_need_mb'],
              'first_checkpoint_publication_seconds': intervals, 'full_native_exact': True,
              'finished_utc': value['finished_utc'], 'comparator_run': value['comparator_run']}
    if 'start_native_iteration' in value or 'final_native_iteration' in value:
        require(value.get('start_native_iteration') == 0 and value.get('final_native_iteration') == 2, 'unexpected API native iteration scope')
        result.update(start_native_iteration=0, final_native_iteration=2)
    return result


def budget_raw_case(value, side):
    require(value.get('case', {}).get('side') == side, 'raw API case role mismatch')
    require(value.get('completed') is True and value.get('loaded_native_exact') is True and value.get('error') is None and
            value.get('guard_failures') == [] and value.get('timed_out') is False, 'raw API case incomplete/failed')
    loaded = value['loaded_native']['header']
    final = value['native']['header']
    require(loaded.get('iteration') == 0 and final.get('iteration') == 2, 'raw API native iteration must be0→2')
    require(set(loaded) == set(final) and all(loaded[key] == final[key] for key in loaded if key != 'iteration'),
            'raw API native metadata changed beyond iteration')
    return {'side': side, 'start_native_iteration': 0, 'final_native_iteration': 2,
            'loaded_native_exact': True, 'native_metadata_preserved_except_iteration': True}


def generate(pass_dir=PASS, api_summary=None):
    sources = []
    def read(name):
        path = pass_dir / name
        compressed = path.with_name(path.name + '.gz')
        if compressed.exists():
            path = compressed
        sources.append(path.relative_to(pass_dir).as_posix())
        return read_json(path)
    fixed = fixed_work(read('final-performance.json'))
    extended = accuracy(read('extended-convergence-comparisons.json'))
    protocol = read('extended-convergence-protocol.json')
    accepted = read('proposals/final-integration-audit/accepted-source-manifest.json')
    commit = accepted['accepted_commit']
    for row in extended['comparisons']:
        name = row['fixture']
        original = protocol['runs']['extended-convergence-' + name + '-original-a']
        final = protocol['runs']['extended-convergence-' + name + '-compatible-a']
        require(final['compiled_source'] == commit, 'extended candidate source mismatch')
        for key in ('input_sha256', 'budget_mb', 'additional_iterations', 'target_gap_bb', 'check_every'):
            require(original[key] == final[key], 'unequal frozen extended settings: ' + key)
        require(row['target_gap_bb'] == final['target_gap_bb'] and row['additional_iterations'] <= final['additional_iterations'], 'extended result exceeds frozen scope')
        require(row['exact_checkpoints'] * final['check_every'] == row['additional_iterations'], 'extended cadence differs from protocol')
    expected_files = {'gpu.rs', 'kernels.cu', 'mod.rs', 'multiway.rs', 'checkpoint_tests.rs'}
    require(len(accepted['files']) == 5 and {Path(f['path']).name for f in accepted['files']} == expected_files, 'incomplete accepted source set')
    require(all(f.get('worktree_normalized_matches') is True and f.get('blob') and f.get('sha256_git_bytes') for f in accepted['files']), 'unverified source identity')
    suites = {}
    for name in ('cpu', 'gpu', 'server'):
        suite = read('final-' + name + '-suite.json')
        source = suite.get('source_commit', suite.get('accepted_source', ''))
        require(source and commit.startswith(source) and suite.get('failed') == 0 and suite.get('passed', 0) > 0, 'failed/incomplete/wrong-source suite: ' + name)
        suites[name] = {k: suite[k] for k in ('passed', 'failed', 'ignored', 'ignored_listings') if k in suite}
    deployment = read('deployment-evidence.json')
    require(deployment['accepted_research_commit'] == commit, 'deployment source mismatch')
    report = {'schema_version': 1, 'accepted_research_commit': commit,
              'scope': 'Preflop-only measured performance. No sample, precision, betting-menu or player-data reduction; postflop implementation unchanged.',
              'gpu_fixed_work': fixed, 'gpu_accuracy_targets': extended,
              'test_suites': {'counts_overlap_not_unique': True, 'suites': suites,
                              'manual_postflop_gpu_resume_test': 'Ignored; deployment restore verification is separate evidence.'},
              'accepted_source_files': accepted['files'],
              'deployment': {k: deployment[k] for k in ('recorded_utc', 'deployed_utc', 'production_commit', 'port', 'isolated_smoke_passed', 'live_native_restoration_exact', 'solve_started_during_deployment', 'preflop_native_before_after', 'postflop_iteration_before_after', 'postflop_board')},
              'limitations': ['Fixed-work reductions are not universal convergence speedups.',
                              'The extended eight-seat run begins at native174; its time is not a fresh-game total.',
                              'CPU quadrature preserves the model with f64 arithmetic, not universal CPU bit identity.',
                              'GPU exactness applies to the tested same-input/batch/cache controls, not arbitrary devices, budgets or historical saves.',
                              'VRAM figures in the research report are planned solver allocations, not total device residency.',
                              'The earlier eight-seat100-iteration target miss remains separate evidence.',
                              'The earlier literal original23GB modeled harness timed out; that failure remains separate evidence. Any later successful short real-server API pair does not establish convergence or explain the earlier timeout.',
                              'Optional API observations are one fixed pair with polling uncertainty, not a general speed estimate.'],
              'evidence_sources': sources}
    if (pass_dir / 'fresh-eight-comparisons.json').exists():
        fresh = read('fresh-eight-comparisons.json')
        if len(fresh) < 3:
            report['optional_fresh_eight'] = {'status': 'pending', 'reported_pairs': len(fresh), 'required_pairs': 3, 'scope': 'No headline timings until all three exact pairs are available.'}
        else:
            report['optional_fresh_eight'] = fresh_qualifier(fresh)
    api = api_summary or pass_dir / 'api-first-strategy-eight-a.json'
    require(not api_summary or api.exists(), 'explicit API summary does not exist')
    if api.exists():
        value = json.loads(api.read_text(encoding='utf-8-sig'))
        require(value.get('full_native_exact') is True and value.get('fixed_pair_only') is True, 'unverified optional API result')
        for key in ('first_checkpoint_seconds', 'first_strategy_response_seconds'):
            require(set(value[key]) == {'original', 'candidate'}, 'incomplete optional API pair')
            for timing in value[key].values():
                number(timing, key, True)
        report['optional_api'] = {'evidence': str(api), **value}
    budget_files = ('api-auto-modeled-b.json', 'api-modeled23000-a.json')
    if any((pass_dir / name).exists() for name in budget_files):
        require(all((pass_dir / name).exists() for name in budget_files), 'incomplete published API budget qualification set')
        qualifications = []
        for name in budget_files:
            qualification = budget_qualifier(read(name), name)
            raw_checks = []
            for side in ('original', 'candidate'):
                raw_name = 'raw/' + name.removesuffix('.json') + '-' + side + '.json'
                # The copied JSON can be large due to embedded profile metadata.
                # Parse one at a time and retain only the compact verified facts.
                facts = budget_raw_case(read(raw_name), side)
                raw_checks.append({'source': sources[-1], **facts})
            qualification.update(start_native_iteration=0, final_native_iteration=2, raw_case_checks=raw_checks)
            qualifications.append(qualification)
        report['optional_api_budget_qualifications'] = qualifications
        report['limitations'].append('Both later short real-server modeled API budget pairs completed exactly, including23000MB; they did not reproduce the earlier harness timeout. This does not erase that failure or supply a23GB convergence-speed claim.')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pass-dir', type=Path, default=PASS)
    parser.add_argument('--api-summary', type=Path)
    parser.add_argument('--output', type=Path, help='Must not already exist; omit for stdout.')
    args = parser.parse_args()
    try:
        require(not args.output or not args.output.exists(), 'output already exists')
        report = generate(args.pass_dir, args.api_summary)
        text = json.dumps(report, indent=2, allow_nan=False) + '\n'
        if args.output:
            with args.output.open('x', encoding='utf-8') as stream:
                stream.write(text)
        else:
            print(text, end='')
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, 'Summary refused: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
