"""Describe variance in an already audited, fixed-policy balanced sample."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import numpy as np
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from hu_root_retained_seed_range_comparison_20260924 import label
from reboot_research_idle_v1 import idle

PREFIX = 'root-fixed-variance-v1'
SOURCE = Path('T:/GTOpen-research/root-retained-wider-study-v1/evaluation')


def main():
    start = time.monotonic()
    def guard():
        assert time.monotonic()-start < 600 and idle()
    guard()
    paths = {key:OUT/f'root-retained-wider-study-v1-{key}.json'
             for key in ('registration','result','evaluation','independent-review')}
    reg, result, evaluation, audit = [read(paths[k]) for k in paths]
    assert result['passed'] and audit['passed'] and evaluation['complete']
    assert result['registration_sha256'] == audit['registration_sha256'] == sha(paths['registration'])
    assert audit['evaluation_sha256'] == sha(paths['evaluation'])
    detail = read(SOURCE/'result.json')
    assert sha(SOURCE/'result.json') == evaluation['result_sha256'] == audit['result_sha256']
    response = read(SOURCE/'response.json')
    assert sha(SOURCE/'response.json') == detail['response_sha256']
    inputs = {str(p):sha(p) for p in [*paths.values(), SOURCE/'result.json', SOURCE/'response.json',
                                     Path(__file__)]}
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists()
    save(rp, dict(inputs=inputs, source=str(SOURCE), maximum_seconds=600,
        analysis='All 169 classes, 256 already evaluated conditional deals each; first/second 128-deal halves; paired action contrasts and covariance.',
        scope='Post-hoc diagnostic of fixed-policy estimator noise. No new deals, neural inference, responder fitting, independent holdout, confidence claim or policy selection.',
        gpu_used=False, production_modified=False))
    cs, qs, hashes = [], [], {}
    for name, h in sorted(detail['batch_summary_hashes'].items()):
        if not name.startswith('train-'): continue
        guard(); p = SOURCE/name/'summary.json'
        assert sha(p) == h
        summary = read(p); hashes[str(p)] = h
        assert summary['terminal_estimator'] == 'conditional-preflop-allin-v1'
        assert summary['postflop_outcomes'] == 'sampled-board'
        cs.extend(summary['classes']); qs.extend(summary['action_values'])
    classes = np.asarray(cs); q = np.asarray(qs)
    assert len(hashes) == 676 and q.shape == (43264,4)
    assert np.array_equal(classes, np.tile(np.arange(169),256))
    assert np.all(np.isfinite(q))
    byclass = q.reshape(256,169,4).transpose(1,0,2)
    masses = np.asarray(reg['exact']['masses'])
    exact = np.stack([np.asarray(reg['exact'][k])/masses for k in ('fold_entries','jam_entries')],axis=1)
    assert abs(masses.sum()-1) < 1e-12 and min(masses) > 0
    rows = []
    for c, values in enumerate(byclass):
        means = values.mean(0); means[[0,3]] = exact[c]
        assert np.max(abs(means-np.asarray(response['class_action_means'][c]))) < 1e-10
        assert int(np.argmax(means)) == response['selected_actions'][c]
        pairs = np.stack([values[:,1]-values[:,0],values[:,2]-values[:,0],values[:,1]-values[:,2]],axis=1)
        cov = np.cov(values[:,1:3],rowvar=False,ddof=1)
        variance = pairs.var(0,ddof=1)
        assert abs(variance[2]-(cov[0,0]+cov[1,1]-2*cov[0,1])) < 1e-9
        half_means = []
        for part in (values[:128],values[128:]):
            v = part.mean(0); v[[0,3]] = exact[c]; half_means.append(v.tolist())
        half_actions = [int(np.argmax(x)) for x in half_means]
        assert half_actions == [half[c] for half in detail['stability']['half_actions']]
        rows.append(dict(hand=label(c), hand_class=c, samples=256, mass=float(masses[c]),
            means=means.tolist(), contrasts_mean=pairs.mean(0).tolist(),
            contrasts_sample_variance=variance.tolist(),
            contrast_descriptive_standard_error=np.sqrt(variance/256).tolist(),
            call_raise_covariance=cov.tolist(),
            call_raise_paired_to_independent_variance_ratio=float(variance[2]/(cov[0,0]+cov[1,1])),
            half_means=half_means, half_actions=half_actions))
    different = np.asarray([r['half_actions'][0]!=r['half_actions'][1] for r in rows])
    assert int(different.sum()) == detail['stability']['disagreeing_classes']
    disagreement_mass = float(masses@different)
    assert abs(disagreement_mass-detail['stability']['disagreement_population_mass']) < 1e-12
    var = np.asarray([r['contrasts_sample_variance'] for r in rows])
    weighted_var = masses@var
    # These are conditional per-hand errors averaged with population mass, not
    # the standard error of a population aggregate (which has different weights).
    rms_class_se = np.sqrt(weighted_var/256)
    denominator = sum(r['mass']*(r['call_raise_covariance'][0][0]+r['call_raise_covariance'][1][1]) for r in rows)
    for p,h in {**inputs,**hashes}.items(): assert sha(p)==h,p
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
        batch_hashes=hashes,classes=rows,contrasts=['call minus fold','raise minus fold','call minus raise'],
        incoming_mass_weighted_class_rms_standard_error=rms_class_se.tolist(),
        class_standard_error_quantiles=np.quantile(np.sqrt(var/256),[0,.25,.5,.75,1],axis=0).tolist(),
        weighted_call_raise_paired_to_independent_variance_ratio=float(weighted_var[2]/denominator),
        half_disagreeing_classes=int(different.sum()),half_disagreement_mass=disagreement_mass,
        seconds=time.monotonic()-start,production_modified=False,accuracy_qualified=False,
        limitations='Descriptive sample variances and standard errors, no simultaneous confidence coverage. Data were used for a prior response fit. Half disagreement is estimator variation with the same fixed continuation, not changing opponents. Conditional all-in endpoints are exact; non-all-in outcomes still use sampled boards. Independent native/model correctness is not established here.'))
    print(json.dumps(dict(rms_class_standard_error=rms_class_se.tolist(),
        paired_variance_ratio=float(weighted_var[2]/denominator),
        half_disagreement_mass=disagreement_mass,seconds=time.monotonic()-start)))


if __name__=='__main__': main()
