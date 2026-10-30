"""Exact finite-noise and retained-native score controls; no prediction trial."""
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import time
import traceback
import zipfile
import psutil
import stack_context_prediction_noise_scores_v1 as scores
import sampled_evaluation_intervals_v1 as intervals
from stack_context_teacher_path_v1 import encoded

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-prediction-noise-scores-check-v1'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def save(path, document):
    with Path(path).open('xb') as stream:stream.write(encoded(document));stream.flush();os.fsync(stream.fileno())
def close(a, b):assert abs(a-b) < 1e-12


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    attempt, result, failure = [OUT/(NAME+s+'.json') for s in ('-attempt', '-result', '-failure')]
    assert not any(p.exists() for p in (attempt, result, failure))
    native_path = OUT/'stack-context-teacher-native-plan-check-v1-result.json'
    reader_path = OUT/'stack-context-teacher-native-plan-readback-v1-result.json'
    archive_path = OUT/'stack-context-teacher-native-plan-check-v1-archive.json'
    zip_path = OUT/'stack-context-teacher-native-plan-check-v1-artifacts.zip'
    native, reader, archive = read(native_path), read(reader_path), read(archive_path)
    assert all(d['complete'] and d['passed'] for d in (native, reader, archive))
    assert reader['result_sha256'] == archive['consumed_result_sha256'] == sha(native_path)
    assert archive['consumed_readback_sha256'] == sha(reader_path) and archive['archive_sha256'] == sha(zip_path)
    paths = {Path(__file__).resolve(), Path(scores.__file__).resolve(), Path(intervals.__file__).resolve(),
        ROOT/'tools/research/stack_context_teacher_path_v1.py', native_path, reader_path, archive_path, zip_path,
        OUT/'STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md'}
    inputs = {str(p):sha(p) for p in paths}
    save(attempt, dict(inputs=inputs, qualification_only=True, exact_finite_noise_enumeration=True,
        retained_native_label_pairs_only=True, synthetic_predictions=True,
        prospective_scientific_scoring_not_registered=True, scientific_samples=0, fits=0, native_calls=0, gpu=False))
    began = time.monotonic();negative = []
    def reject(name, action):
        try:action()
        except (ValueError, TypeError, KeyError):negative.append(name)
        else:raise AssertionError('Accepted '+name)
    try:
        # Enumerate ALL independent combinations of two zero-mean finite label
        # noises. Their expected cross residual equals known prediction error.
        sigma = [.2, .3, .5];truth = [-2., 3., 1.];e = [1., -2., .5];f = [.5, .5, -1.]
        y = scores.label(truth, sigma, 10., 1.)
        pred_a, pred_b = [.8, -.6, .1, float('nan')], [-.2, .15, .05, 1e100]
        support = [[truth[i]+u*e[i]+v*f[i] for i in range(3)] for u, v in itertools.product((-1, 1), repeat=2)]
        rows = [scores.paired_scores(q_first=a, q_second=b, sigma=sigma, starting_stack=10., dead_money=1.,
                    prediction_A=pred_a, prediction_B=pred_b) for a, b in itertools.product(support, repeat=2)]
        means = {metric:math.fsum(row['scores'][metric] for row in rows)/16 for metric in scores.METRICS}
        true_a = math.fsum((v-z)**2 for v, z in zip(pred_a[:3], y))/3
        true_b = math.fsum((v-z)**2 for v, z in zip(pred_b[:3], y))/3
        centered_e = [(v-sum(p*x for p, x in zip(sigma, e)))/10 for v in e]
        centered_f = [(v-sum(p*x for p, x in zip(sigma, f)))/10 for v in f]
        true_noise = math.fsum(a*a+b*b for a, b in zip(centered_e, centered_f))/3
        close(means['corrected_mse_A'], true_a);close(means['corrected_mse_B'], true_b)
        close(means['label_noise'], true_noise)
        close(means['observed_mse_A'], true_a+true_noise);close(means['observed_mse_B'], true_b+true_noise)
        close(means['prediction_gain_B'], true_a-true_b);close(means['decision_gain_B'], .5)
        assert all(r['decision_policy_A'] == [1., 0., 0.] and r['decision_policy_B'] == [0., 1., 0.] for r in rows)
        negative_score = scores.paired_scores(q_first=[10., -10.], q_second=[-10., 10.], sigma=[.5, .5],
            starting_stack=10., dead_money=0., prediction_A=[0., 0., 0., 0.], prediction_B=[0., 0., 0., 0.])
        assert negative_score['scores']['corrected_mse_A'] == -1.
        assert negative_score['scores']['label_noise'] == 2. and negative_score['scores']['observed_mse_A'] == 1.
        padding = scores.paired_scores(q_first=support[0], q_second=support[1], sigma=sigma,
            starting_stack=10., dead_money=1., prediction_A=pred_a[:3]+[1e200], prediction_B=pred_b[:3]+[float('nan')])
        assert padding['scores'] == rows[1]['scores']
        clipped = scores.paired_scores(q_first=[10., -10.], q_second=[10., -10.], sigma=[.5, .5],
            starting_stack=10., dead_money=0., prediction_A=[100., -100., float('nan'), 1e200],
            prediction_B=[2., -2., 0., 0.])
        assert clipped['clipped_legal_outputs_A'] == 2 and clipped['clipped_legal_outputs_B'] == 0
        close(clipped['scores']['prediction_gain_B'], 0)
        # Exhaustive endpoint geometry verifies the declared loss/gain bounds.
        bound_checks = 0
        for x, y1, y2 in itertools.product((-2., 0., 2.), repeat=3):
            cross = (x-y1)*(x-y2);observed = ((x-y1)**2+(x-y2)**2)/2;noise = (y1-y2)**2/2
            assert -4 <= cross <= 16 and 0 <= observed <= 16 and 0 <= noise <= 8;bound_checks += 1
        for xa, xb, y1, y2 in itertools.product((-2., 0., 2.), repeat=4):
            gain = (xa-y1)*(xa-y2)-(xb-y1)*(xb-y2);assert -16 <= gain <= 16;bound_checks += 1
        config = dict(strata=('synthetic', 'heldout-synthetic'), stratum='synthetic', looks=(2, 4),
            alpha=.05, maximum_advantage_span=2.1)
        sequential = scores.ClusterEvaluation(**config);left = scores.ClusterEvaluation(**config);right = scores.ClusterEvaluation(**config)
        blocks = [[rows[0]]*100, [rows[1]], [rows[2]]*7, [negative_score]*30]
        for i, block in enumerate(blocks):
            sequential.add_cluster('parent'+str(i), block, [1.]*len(block))
            (left if i < 2 else right).add_cluster('parent'+str(i), block, [1.]*len(block))
        assert len(sequential.seen) == 4 and sequential.rows == 138
        expected = math.fsum(block[0]['scores']['corrected_mse_A'] for block in blocks)/4
        close(sequential.evaluations['corrected_mse_A'].mean, expected)
        pooled = math.fsum(r['scores']['corrected_mse_A'] for block in blocks for r in block)/138
        assert abs(expected-pooled) > .01
        left.merge(right)
        for metric in scores.METRICS:
            close(left.evaluations[metric].mean, sequential.evaluations[metric].mean)
            close(left.evaluations[metric].m2, sequential.evaluations[metric].m2)
        summary = sequential.interval();assert summary['clusters'] == 4 and summary['dependent_rows'] == 138
        for metric, interval in summary['intervals'].items():
            assert interval['count'] == 4 and interval['family_error_probability'] == .05
        # Retained native means: metric arithmetic only, with synthetic frozen
        # predictions. No confidence intervals or accuracy claims on these16I.
        records = []
        with zipfile.ZipFile(zip_path, 'r') as z:
            def member(path):
                raw = z.read(path);assert hashlib.sha256(raw).hexdigest() == archive['member_sha256'][path]
                return json.loads(raw)
            for case in native['records']:
                folders = [Path(r['folder']).name for r in case['replicates']]
                a, b = [member(folder+'/result.json') for folder in folders]
                post = member(folders[0]+'/posterior.json');context = json.loads(post['context_source'])
                assert a['posterior_sha256'] == b['posterior_sha256'] == post['sha256'] and a['draw_count'] == b['draw_count'] == 8
                score = scores.paired_scores(q_first=a['action_values'], q_second=b['action_values'], sigma=post['original_sigma'],
                    starting_stack=case['depth'], dead_money=context['dead_money'],
                    prediction_A=[0., 0., 0., 0.], prediction_B=[.2, -.1, .05, .01])
                ya = scores.label(a['action_values'], post['original_sigma'], case['depth'], context['dead_money'])
                yb = scores.label(b['action_values'], post['original_sigma'], case['depth'], context['dead_money'])
                for value, old in zip(ya, a['normalized_advantage']):close(value, old)
                for value, old in zip(yb, b['normalized_advantage']):close(value, old)
                close(score['scores']['label_noise'], math.fsum((x-y)**2/2 for x, y in zip(ya, yb))/len(ya))
                records.append(dict(depth=case['depth'], phase=case['phase'], actor=case['actor'], scores=score,
                    synthetic_predictions=True, native_label_receipts=[case['replicates'][i]['result_sha256'] for i in (0, 1)],
                    no_scientific_confidence_interval=True, accuracy_evidence=False))
        reject('nonpositive stack', lambda:scores.bounds(0, 1))
        reject('negative dead money', lambda:scores.bounds(10, -1))
        reject('nonfinite legal prediction', lambda:scores.prediction([float('nan'), 0, 0, 0], 2, 2))
        reject('missing output slot', lambda:scores.prediction([0, 0], 2, 2))
        reject('invalid teacher sigma', lambda:scores.label([0, 0], [0, 0], 10, 0))
        reject('outside Q ledger', lambda:scores.label([100, 0], [.5, .5], 10, 0))
        reject('zero context ledger span', lambda:scores.ClusterEvaluation(**dict(config, maximum_advantage_span=1.)))
        reject('undeclared stratum', lambda:scores.ClusterEvaluation(**dict(config, stratum='missing')))
        reject('undeclared look type', lambda:scores.ClusterEvaluation(**dict(config, looks=[2, 4])))
        reject('duplicated cluster', lambda:sequential.add_cluster('parent0', [rows[0]], [1.]))
        reject('exhausted cluster budget', lambda:sequential.add_cluster('extra', [rows[0]], [1.]))
        bad = scores.ClusterEvaluation(**config)
        reject('zero cluster weights', lambda:bad.add_cluster('zero', [rows[0]], [0.]))
        reject('negative cluster weights', lambda:bad.add_cluster('negative', [rows[0]], [-1.]))
        damaged = copy.deepcopy(rows[0]);damaged['advantage_span'] = 3.
        reject('unregistered ledger range', lambda:bad.add_cluster('span', [damaged], [1.]))
        damaged = copy.deepcopy(rows[0]);damaged['scores']['corrected_mse_A'] = -100.
        reject('invalid bounded score', lambda:bad.add_cluster('score', [damaged], [1.]))
        reject('undeclared interval look', bad.interval)
        overlap = scores.ClusterEvaluation(**config);overlap.add_cluster('parent0', [rows[0]], [1.])
        reject('overlapping cluster merge', lambda:sequential.merge(overlap))
        reject('self merge', lambda:sequential.merge(sequential))
        incompatible = scores.ClusterEvaluation(**dict(config, stratum='heldout-synthetic'))
        reject('different stratum merge', lambda:sequential.merge(incompatible))
        assert len(bad.seen) == 0 and all(e.count == 0 for e in bad.evaluations.values())
        for p, h in inputs.items():assert sha(p) == h
        answer = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs,
            exact_independent_noise_pairs=16, known_truth_legal_mse_A=true_a, known_truth_legal_mse_B=true_b,
            known_label_variance=true_noise, exact_average_scores=means,
            negative_corrected_score_preserved=-1., illegal_outputs_excluded=True, prediction_clipping_checked=True,
            endpoint_bound_controls=bound_checks, cluster_interval_control=summary,
            equal_cluster_weighting_not_pooled_rows=True, sequential_merged_statistics_equal=True,
            corruption_rejections=negative, retained_native_label_pairs=records, qualification_only=True,
            synthetic_predictions=True, no_native_fixture_confidence_claim=True,
            scientific_samples=0, fits=0, native_calls=0, gpu=False, production_modified=False,
            actual_diagnostic_registered=False, actual_diagnostic_complete=False, scientific_accuracy_evidence=False)
        save(result, answer)
        print(json.dumps(dict(passed=True, seconds=answer['seconds'], exact_noise_pairs=16,
            native_label_pairs=len(records), corruption_rejections=len(negative))), flush=True)
    except BaseException as error:
        save(failure, dict(complete=False, passed=False, error=repr(error), traceback=traceback.format_exc(),
            preserve_evidence=True, automatic_retry_allowed=False));raise


if __name__ == '__main__':main()
