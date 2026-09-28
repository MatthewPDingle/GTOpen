"""Read back the longer matched continuation and its prespecified analyses.

CPU only. Reuses qualified archive/scalar checks; it is not a second poker
engine, independent neural inference, a best-response bound, or a new test set.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1',
                  PYTHONDONTWRITEBYTECODE='1')
import argparse
import hashlib
import json
import math
from statistics import NormalDist
from pathlib import Path
import sys
import time
import numpy as np
import psutil
import board_training_checkpoint_v1 as checkpoint
from board_root_accumulator_v1 import BoardRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_deals_v1 import PhysicalDeals
from weighted_evaluation_checkpoint_v1 import restore_latest
from weighted_evaluation_readback_v1 import verify_analysis, worker_guard
from weighted_routed_evaluation_readback_v1 import parallel
from board_prefix_publication_v1 import atomic_json

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'river-matched-continuation-v1'
INITIAL=80; FINAL=110; DEALS=16384; SEED=9294101
RP = OUT/(NAME+'-registration.json')
RESULT = OUT/(NAME+'-result.json')
REVIEW_REG = OUT/(NAME+'-review-v1-registration.json')
REVIEW = OUT/(NAME+'-independent-review-v1.json')
ARMS = ('A-baseline', 'A-river', 'B-baseline', 'B-river')


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare_model_parts(a, b, config, context, matrix):
    """Compare numeric state, not provenance hashes that change with model IDs."""
    assert a['generation'] == b['generation']
    ra, rb = [BoardRootRegrets.restore(m['board_root_state'], expected_config=config['board_root']) for m in (a, b)]
    context_sha = hashlib.sha256(context.read_text().encode()).hexdigest()
    ea, eb = [ExactBtnRegrets.restore(m['exact_btn_state'], context_sha256=context_sha, entry_mass=matrix.btn_mass) for m in (a, b)]
    root = [r.probabilities(np.full((169, 4), .25)) for r in (ra, rb)]
    response = [r.probabilities(np.full((169, 2), .5)) for r in (ea, eb)]
    return dict(generation=a['generation'], models_identical=a == b,
        networks_identical=a['networks'] == b['networks'],
        preflop_tables_identical=a['preflop_tables'] == b['preflop_tables'],
        root_regret_max_difference=float(np.max(abs(ra.regrets-rb.regrets))),
        root_policy_max_difference=float(np.max(abs(root[0]-root[1]))),
        root_policy_entry_weighted_tv=float(np.dot(matrix.bb_mass, .5*np.sum(abs(root[0]-root[1]), axis=1))),
        exact_btn_regret_max_difference=float(np.max(abs(ea.regrets-eb.regrets))),
        exact_btn_policy_max_difference=float(np.max(abs(response[0]-response[1]))))


def review_training(reg, result, store, identities, guard):
    context = OUT/'bb-context-candidate.json'
    source = context.read_text()
    matrix_path = OUT/'preflop-allin-matrix-control-v1-matrix.json'
    matrix = AllinMatrix(read(matrix_path), source)
    catalog = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json').read_text()
    assert [r['arm'] for r in identities] == list(ARMS)
    assert [r['arm'] for r in result['training']] == list(ARMS)
    summaries, progress, paired = [], {}, []
    for name, identity, reported in zip(ARMS, identities, result['training']):
        guard(); folder = store/name; arm = reg['arms'][name]; cfg = arm['config']
        pp = folder/'progress.json'; p = read(pp); progress[name] = p
        assert p['registration_sha256'] == sha(RP) and p['initial_source'] == arm['source_checkpoint']
        assert p['completed'] == reported['completed'] == FINAL
        assert p['checkpoint'] == identity['checkpoint'] == reported['checkpoint']
        assert sha(pp) == identity['progress_sha256'] and identity['root_config'] == cfg['board_root']
        state = checkpoint.restore_checkpoint(folder/'objects', p['checkpoint'], cfg,
            context_source=source, catalog_source=catalog, matrix_sha256=sha(matrix_path),
            entry_mass=matrix.btn_mass, root_config=cfg['board_root'])
        assert state['played_bank'] == identity['played_models']
        parent=read(Path(arm['source_objects'])/arm['source_checkpoint']['file'])
        assert sha(Path(arm['source_objects'])/arm['source_checkpoint']['file'])==arm['source_checkpoint']['sha256']
        assert state['played_bank'][:INITIAL]==parent['played_bank']
        assert state['played_bank'][INITIAL]==parent['next_model']
        assert [r['generation'] for r in state['played_bank']] == list(range(FINAL))
        assert identity['unplayed_excluded'] == state['next_model'] and state['next_model']['generation'] == FINAL
        assert [r['iteration'] for r in p['updates']] == list(range(INITIAL+1, FINAL+1))
        rows, replaced = [], 0
        for update in p['updates']:
            guard(); path = folder/update['metrics']; assert sha(path) == update['sha256']
            metric = read(path); rows.append(metric)
            assert metric['iteration'] == update['iteration'] and metric['used_model']['generation'] == metric['iteration']-1
            assert [s['chunk'] for s in metric['subbatches']] == list(range(8))
            for sub in metric['subbatches']:
                part = path.parent/f"batch-{sub['chunk']:02d}"
                for filename, digest in sub['artifacts'].items():
                    assert sha(part/filename) == digest, str(part/filename)
                if name.endswith('-river'):
                    overlay = read(part/'conditional/overlay.json')
                    audit = read(part/'river-targets.json')
                    assert len(overlay['rows']) == len(audit['replacements']) == sub['river']['replacements']
                    replaced += len(overlay['rows'])
            assert metric['workers'] == 8 and metric['board_workers'] == 4
        assert rows[-1]['checkpoint'] == p['checkpoint']
        seconds = math.fsum(r['seconds'] for r in rows)
        wait = math.fsum(r['competing_gpu_wait_seconds'] for r in p['updates'])
        assert abs(seconds-reported['training_seconds']) < 1e-8
        assert abs(wait-reported['competing_gpu_wait_seconds']) < 1e-8
        assert seconds > 0 and 0 <= wait <= seconds+1
        summaries.append(dict(arm=name, updates=FINAL-INITIAL, full_update_seconds=seconds,
            reported_external_gpu_wait_seconds=wait, seconds_less_reported_wait=max(0., seconds-wait),
            river_rows_replaced=replaced,
            maximum_worker_rss_bytes=max(w['rss_bytes'] for r in rows for w in r['worker_stats'])))
        del state
    for label in ('A', 'B'):
        old, new = [label+'-'+t for t in ('baseline', 'river')]
        pa, pb = progress[old], progress[new]
        a = read(store/old/'objects'/pa['checkpoint']['file'])
        b = read(store/new/'objects'/pb['checkpoint']['file'])
        assert a['played_bank'][:79] == b['played_bank'][:79]
        comparisons = []
        for generation in (78, 79, 80, 81, 82, 90, 100, 109, 110):
            refs = [m['next_model'] if generation == FINAL else m['played_bank'][generation] for m in (a, b)]
            docs = [read(store/name/'objects'/r['file']) for name, r in zip((old, new), refs)]
            assert all(sha(store/name/'objects'/r['file']) == r['sha256'] for name, r in zip((old, new), refs))
            row = compare_model_parts(*docs, reg['arms'][old]['config'], context, matrix)
            row['included_in_evaluated_bank'] = generation < FINAL
            comparisons.append(row)
        # First changed fit cannot affect the root target computed BEFORE it.
        assert comparisons[0]['models_identical']
        assert comparisons[1]['root_regret_max_difference'] == 0
        assert comparisons[1]['exact_btn_regret_max_difference'] == 0
        # Other lookup rows are recorded, not assumed bit-identical: the shared
        # regression scaling can produce roundoff even for untouched targets.
        assert comparisons[2]['exact_btn_regret_max_difference'] == 0
        costs = [next(r for r in summaries if r['arm'] == name) for name in (old, new)]
        paired.append(dict(seed=label, models=comparisons,
            candidate_over_baseline_wall_ratio=costs[1]['full_update_seconds']/costs[0]['full_update_seconds'],
            candidate_over_baseline_wait_subtracted_ratio=(costs[1]['seconds_less_reported_wait']/costs[0]['seconds_less_reported_wait'])
                if costs[0]['seconds_less_reported_wait'] > 0 else None))
    return dict(arms=summaries, pairs=paired,
        qualification='Parent recovery and eight-worker full-update controls frozen in source registration; no qualification updates enter this bank.',
        interpretation='Thirty additional updates per arm; component changes are descriptive, not proof of better play.',
        timing_limit='One continuation per seed; execution order and external load matter. Equal-update comparison only.')


def review_secondary(analysis, secondary, values):
    """Recompute from per-deal deltas, separately from the training accumulator."""
    assert secondary['finite_sample_guarantee'] is False and secondary['accuracy_qualified'] is False
    assert secondary['accounts_for_training_seed_uncertainty'] is False
    assert secondary['conditional_on_frozen_banks'] is True
    assert secondary['deals']==DEALS and secondary['nominal_family_alpha']==.05
    critical=NormalDist().inv_cdf(1-.05/16);assert secondary['z']==critical
    assert len(secondary['contrasts'])==8
    diagnostics=[]; maximum_error=0.
    for i,(primary,row) in enumerate(zip(analysis['contrasts'],secondary['contrasts'])):
        assert row['name']==primary['name']
        data=[v[i] for v in values];n=len(data);assert n==DEALS
        mean=math.fsum(data)/n; deviations=[v-mean for v in data]
        squares=sorted((v*v for v in deviations),reverse=True);total=math.fsum(squares)
        variance=total/(n-1);se=math.sqrt(variance/n)
        for key,expected in dict(mean=mean,standard_error=se,lower=mean-critical*se,upper=mean+critical*se).items():
            error=abs(row[key]-expected);assert math.isfinite(error) and error<1e-8
            maximum_error=max(maximum_error,error)
        diagnostics.append(dict(name=row['name'],minimum=min(data),maximum=max(data),
            largest_centered_square_fraction=squares[0]/total if total else 0.,
            ten_largest_centered_squares_fraction=math.fsum(squares[:10])/total if total else 0.,
            third_absolute_standardized_moment=(math.fsum(abs(v)**3 for v in deviations)/n/variance**1.5) if variance else 0.))
    return dict(passed=True,maximum_statistical_error=maximum_error,tail_diagnostics=diagnostics,
        finite_sample_guarantee=False,accuracy_qualified=False)



def main(run=False):
    reg = read(RP)
    assert reg['test_deals'] == DEALS and reg['test_seed'] == SEED
    assert reg['bank_order'] == list(ARMS) and reg['initial_iteration'] == INITIAL and reg['final_iteration'] == FINAL
    if not run:
        print(json.dumps(dict(ready=True, result_available=RESULT.exists(), gpu_used=False,
            reads_existing_evidence_only=True, new_test_deals=0)), flush=True)
        return
    assert RESULT.exists() and not REVIEW_REG.exists() and not REVIEW.exists()
    result = read(RESULT); store = Path(reg['store']); assessment = result['evaluation']
    assert result['passed'] and result['complete'] and result['registration_sha256'] == sha(RP)
    assert result['accuracy_qualified'] is False and result['production_modified'] is False
    assert assessment['deals'] == DEALS and assessment['seed'] == SEED
    started = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic(); assert now-started < 7200
        if now-last > 2:
            worker_guard(); last = now
    guard(); assert psutil.cpu_percent(interval=1) < 60
    inputs = dict(reg['inputs'])
    for path,digest in inputs.items(): guard(); assert sha(path)==digest,path
    paths = [RP, RESULT, Path(__file__), store/'bank-identities.json', store/'analysis.json', store/'secondary-analysis.json']
    for module in list(sys.modules.values()):
        file = getattr(module, '__file__', None)
        if file and Path(file).is_relative_to(ROOT) and Path(file).suffix == '.py': paths.append(Path(file))
    inputs.update({str(p): sha(p) for p in paths})
    for path, digest in inputs.items(): guard(); assert sha(path) == digest, path
    atomic_json(REVIEW_REG, dict(inputs=inputs, source_registration_sha256=sha(RP), source_result_sha256=sha(RESULT),
        workers=8, maximum_seconds=7200, new_test_deals=0, gpu_used=False,
        scope='Complete checkpoints, source chance replay, lossless archives, policy crossings, cashflow identities and independently summed gains; not independent neural inference or a second poker engine.'))
    identities = read(store/'bank-identities.json')
    assert sha(store/'bank-identities.json') == assessment['bank_identities_sha256']
    assert sha(store/'analysis.json') == assessment['analysis_sha256']
    training = review_training(reg, result, store, identities, guard)
    source = (OUT/'bb-context-candidate.json').read_text()
    recovered, accumulator, routes, reference = restore_latest(store,
        registration_sha256=sha(RP), bank_identities_sha256=assessment['bank_identities_sha256'],
        context_source=source, total_deals=DEALS, seed=SEED, guard=guard)
    assert reference == assessment['checkpoint'] and routes == assessment['routes'] and recovered.draws == DEALS
    analysis = read(store/'analysis.json'); assert accumulator.finish() == analysis
    secondary=read(store/'secondary-analysis.json')
    assert sha(store/'secondary-analysis.json')==assessment['secondary_analysis_sha256']
    sampler = PhysicalDeals(source, mode='full_deck', seed=SEED)
    names = [f'test-{n:06d}' for n in range(0, DEALS, 32)]
    assert set(routes) == set(names)
    def jobs():
        for name in names:
            guard()
            yield name, dict(format=2, batch_id=NAME+'-'+name, seed=0, query_limit=100000,
                             deals=sampler.sample(32)['deals'])
    values, reviewed, observations = [], [], 0
    for name, (delta, count, digest) in parallel(jobs(), store=store, routes=routes, source=source,
                                               roots=None, guard=guard, workers=8):
        assert digest == routes[name]['summary_sha256']
        values.extend(delta); reviewed.append(name); observations += count
    assert reviewed == names and sampler.checkpoint() == recovered.checkpoint()
    # The reusable scalar verifier also handles old control runs. Supply that
    # interface flag in memory; the authenticated pilot analysis stays unchanged.
    error = verify_analysis(dict(analysis, control_only=False), values, json.loads(source),
                            expected_deals=DEALS, control_only=False)
    secondary_review=review_secondary(analysis,secondary,values)
    contrasts = [dict(name=r['name'], mean=r['mean'], lower=r['lower'], upper=r['upper'],
        conclusion='positive' if r['lower'] > 0 else 'negative' if r['upper'] < 0 else 'inconclusive')
        for r in analysis['contrasts']]
    for path, digest in inputs.items(): guard(); assert sha(path) == digest, path
    output = dict(passed=True, source_result_sha256=sha(RESULT), readback_registration_sha256=sha(REVIEW_REG),
        deals=DEALS, batches=len(reviewed), observations=observations, maximum_statistical_error=error,
        training=training, contrasts=contrasts, secondary_analysis=secondary, secondary_review=secondary_review, seconds=time.monotonic()-started,
        gpu_used=False, new_test_deals=0, production_modified=False, accuracy_qualified=False,
        next_requirement='Assess both seeds and seats, learning cost and uncertainty; equal-time and broader-context validation before any accuracy promotion.')
    atomic_json(REVIEW, output)
    print(json.dumps(dict(passed=True, result=str(REVIEW), training=training, contrasts=contrasts)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
