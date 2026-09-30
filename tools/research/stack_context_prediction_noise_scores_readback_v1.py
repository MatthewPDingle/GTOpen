"""Independent algebra and source-cluster interval readback of score controls."""
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import time
import psutil

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-prediction-noise-scores-readback-v1-result.json'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def close(a, b):assert math.isfinite(a) and math.isfinite(b) and abs(a-b) < 1e-12


def independent(first, second):
    sigma = [.2, .3, .5];pa = [.8, -.6, .1];pb = [-.2, .15, .05]
    ys = [[(q[i]-sum(p*v for p, v in zip(sigma, q)))/10 for i in range(3)] for q in (first, second)]
    a, b = ys
    observed_a = sum(((p-y)**2+(p-z)**2)/2 for p, y, z in zip(pa, a, b))/3
    observed_b = sum(((p-y)**2+(p-z)**2)/2 for p, y, z in zip(pb, a, b))/3
    noise = sum((y-z)**2 for y, z in zip(a, b))/6
    return dict(observed_mse_A=observed_a, observed_mse_B=observed_b, label_noise=noise,
        corrected_mse_A=sum((p-y)*(p-z) for p, y, z in zip(pa, a, b))/3,
        corrected_mse_B=sum((p-y)*(p-z) for p, y, z in zip(pb, a, b))/3,
        prediction_gain_B=observed_a-observed_b,
        decision_gain_B=((first[1]+second[1])-(first[0]+second[0]))/20)


def main():
    target = OUT/NAME
    if target.exists():raise ValueError('Preserve existing readback')
    result_path = OUT/'stack-context-prediction-noise-scores-check-v1-result.json'
    attempt_path = OUT/'stack-context-prediction-noise-scores-check-v1-attempt.json'
    r, a = read(result_path), read(attempt_path)
    assert r['complete'] and r['passed'] and r['inputs'] == a['inputs']
    assert not (OUT/'stack-context-prediction-noise-scores-check-v1-failure.json').exists()
    for p, h in r['inputs'].items():assert sha(p) == h
    assert r['qualification_only'] and r['synthetic_predictions'] and r['no_native_fixture_confidence_claim']
    assert r['scientific_samples'] == r['fits'] == r['native_calls'] == 0 and r['gpu'] is False
    assert not r['production_modified'] and not r['actual_diagnostic_registered'] and not r['actual_diagnostic_complete']
    assert not r['scientific_accuracy_evidence']
    close(r['known_truth_legal_mse_A'], .62);close(r['known_truth_legal_mse_B'], .005)
    close(r['known_label_variance'], .02285)
    expected = dict(observed_mse_A=.64285, observed_mse_B=.02785, label_noise=.02285,
        corrected_mse_A=.62, corrected_mse_B=.005, prediction_gain_B=.615, decision_gain_B=.5)
    for k, v in expected.items():close(r['exact_average_scores'][k], v)
    assert r['exact_independent_noise_pairs'] == 16 and r['endpoint_bound_controls'] == 108
    assert r['negative_corrected_score_preserved'] == -1 and r['illegal_outputs_excluded']
    assert len(r['corruption_rejections']) == len(set(r['corruption_rejections'])) == 19
    support = [[-2+u*1+v*.5, 3+u*(-2)+v*.5, 1+u*.5+v*(-1)]
        for u, v in itertools.product((-1, 1), repeat=2)]
    all_scores = [independent(x, y) for x, y in itertools.product(support, repeat=2)]
    for k in expected:close(sum(s[k] for s in all_scores)/16, expected[k])
    negative = dict(observed_mse_A=1., observed_mse_B=1., label_noise=2., corrected_mse_A=-1.,
        corrected_mse_B=-1., prediction_gain_B=0., decision_gain_B=0.)
    clusters = [all_scores[0], all_scores[1], all_scores[2], negative]
    summary = r['cluster_interval_control'];config = summary['registered_config']
    assert summary['clusters'] == 4 and summary['dependent_rows'] == 138
    assert config['strata'] == ['synthetic', 'heldout-synthetic'] and config['looks'] == [2, 4]
    assert config['alpha'] == .05 and config['maximum_advantage_span'] == 2.1
    span = 2.1;limits = {'observed_mse_A':(0, 4*span**2), 'observed_mse_B':(0, 4*span**2),
        'label_noise':(0, 2*span**2), 'corrected_mse_A':(-span**2, 4*span**2),
        'corrected_mse_B':(-span**2, 4*span**2), 'prediction_gain_B':(-4*span**2, 4*span**2),
        'decision_gain_B':(-span, span)}
    log = math.log(4*14*2/.05)
    for metric, interval in summary['intervals'].items():
        values = [s[metric] for s in clusters];mean = sum(values)/4
        variance = sum((v-mean)**2 for v in values)/3
        lower, upper = limits[metric]
        radius = math.sqrt(2*variance*log/4)+7*(upper-lower)*log/(3*3)
        close(interval['mean'], mean);close(interval['sample_variance'], variance);close(interval['radius'], radius)
        close(interval['lower'], max(lower, mean-radius));close(interval['upper'], min(upper, mean+radius))
        assert interval['count'] == 4 and interval['bounds_best_response_above'] is False
    assert len(r['retained_native_label_pairs']) == 16 and all(
        d['synthetic_predictions'] and d['no_scientific_confidence_interval'] and not d['accuracy_evidence']
        for d in r['retained_native_label_pairs'])
    reg = OUT/'stack-context-matched-learning-v1-registration.json'
    assert sha(reg) == 'ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'
    processes = []
    for pid, created, parent in ((84788,1790752536.9318762,2980),(94544,1790753443.077002,84788),
        (100604,1790753511.1853917,94544),(93416,1790753512.997676,94544),
        (104568,1790753514.8583736,94544),(81788,1790753516.7905183,94544)):
        p = psutil.Process(pid);assert abs(p.create_time()-created) < .01 and p.ppid() == parent
        processes.append(dict(pid=pid, created=p.create_time(), parent=p.ppid(), command=p.cmdline()))
    status_path = OUT/'stack-context-parallel-continuation-v2-status.json';status = read(status_path)
    assert time.time()-status_path.stat().st_mtime < 60 and status['stage'] == 'parallel-training' and status['pid'] == 94544
    assert not list(OUT.glob('stack-context-parallel-continuation-v2*failure.json'))
    store = Path('S:/GTOpen-research/stack-context-matched-learning-v1')
    counts = {a:read(store/a/'progress.json')['completed_cycles'] for a in ('A-baseline','A-relative','B-baseline','B-relative')}
    answer = dict(complete=True, passed=True, unix=time.time(), reader_source_sha256=sha(__file__),
        result_sha256=sha(result_path), attempt_sha256=sha(attempt_path), authenticated_inputs=len(r['inputs']),
        independent_closed_form_truth=expected, independent_cluster_intervals_checked=7,
        source_cluster_count=4, dependent_row_count=138, retained_native_numeric_controls=16,
        qualification_only=True, scientific_samples=0, native_calls=0, fits=0, gpu=False,
        production_modified=False, actual_diagnostic_registered=False, actual_diagnostic_complete=False,
        scientific_accuracy_evidence=False, registration_sha256=sha(reg), live_processes=processes, published_cycles=counts)
    with target.open('xb') as stream:
        stream.write((json.dumps(answer, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode())
        stream.flush();os.fsync(stream.fileno())
    print(json.dumps({k:answer[k] for k in ('passed','authenticated_inputs','independent_cluster_intervals_checked','published_cycles')}))


if __name__ == '__main__':main()
