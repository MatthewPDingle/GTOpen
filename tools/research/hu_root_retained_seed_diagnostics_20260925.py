"""Post-hoc description of audited training samples; no strategic holdout reuse."""
import json
import math
from pathlib import Path
import numpy as np
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from hu_root_retained_seed_range_comparison_20260924 import label


def inspect(prefix):
    rp, pp, ap = [OUT/f'{prefix}-{s}.json' for s in ('registration', 'result', 'independent-review')]
    reg, result, audit = map(read, (rp, pp, ap))
    assert result['passed'] and audit['passed'] and audit['completed_updates'] == 78
    assert result['registration_sha256'] == audit['source_registration_sha256'] == sha(rp)
    assert audit['source_result_sha256'] == sha(pp)
    inputs = {str(p): sha(p) for p in (rp, pp, ap)}
    store = Path(result['store'])
    samples = [[] for _ in range(169)]
    regrets = np.zeros((169, 4))
    policies = []
    for step in result['steps']:
        iteration = step['iteration']
        assert iteration == len(policies)+1
        folder = store/f'iteration-{iteration:04d}'
        mp = folder/'metrics.json'
        assert sha(mp) == step['metrics_sha256']
        metrics = read(mp); inputs[str(mp)] = sha(mp)
        ip = folder/'current-initial-policy.json'
        assert sha(ip) == metrics['initial_policy_sha256']
        initial = read(ip); inputs[str(ip)] = sha(ip)
        policies.append(np.asarray(initial['root'], dtype=np.float64))
        assert len(metrics['subbatches']) == 8
        for part in metrics['subbatches']:
            dp = folder/f"batch-{part['chunk']:02d}"/'derived-targets.json'
            assert sha(dp) == part['artifacts']['derived-targets']
            derived = read(dp); inputs[str(dp)] = sha(dp)
            assert derived['iteration'] == iteration
            assert len(derived['bb_root_corrections']) == 64
            for row in derived['bb_root_corrections']:
                c = row['hand_class']
                adv = np.asarray(row['advantages'], dtype=np.float64)
                values = adv+row['derived_root_value']
                assert abs(values[0]+1) < 1e-9
                assert abs(values[3]-row['exact_conditional_jam_value']) < 1e-9
                assert abs(adv@policies[-1][c]) < 1e-9
                regrets[c] += adv
                samples[c].append([iteration, *values.tolist()])
    assert len(policies) == 78 and sum(map(len, samples)) == 39936
    def object_read(ref):
        path = store/'objects'/ref['file']
        assert sha(path) == ref['sha256']
        inputs[str(path)] = sha(path)
        return read(path)
    checkpoint = object_read(result['final_checkpoint'])
    state = object_read(checkpoint['next_model'])['sampled_root']['state']
    assert [len(rows) for rows in samples] == state['sample_counts']
    error = float(np.max(abs(regrets-np.asarray(state['regret_sums']))))
    assert error < 1e-9
    bank = np.asarray(policies)
    classes = []
    for c, rows in enumerate(samples):
        data = np.asarray(rows)
        values = data[:, 1:]
        contrasts = np.stack([values[:, 1]-values[:, 0], values[:, 2]-values[:, 0],
                              values[:, 1]-values[:, 2]], axis=1)
        temporal = []
        for begin in range(1, 79, 13):
            part = contrasts[(data[:, 0] >= begin) & (data[:, 0] < begin+13)]
            temporal.append(dict(first_update=begin, last_update=begin+12, count=len(part),
                contrast_means=part.mean(0).tolist() if len(part) else None))
        classes.append(dict(hand_class=c, hand=label(c), samples=len(rows),
            action_value_means=values.mean(0).tolist(),
            action_value_sample_sd=values.std(0, ddof=1).tolist(),
            contrast_means=contrasts.mean(0).tolist(), contrast_sample_sd=contrasts.std(0, ddof=1).tolist(),
            contrast_min=contrasts.min(0).tolist(), contrast_max=contrasts.max(0).tolist(),
            temporal_blocks=temporal))
    return dict(classes=classes, maximum_regret_reconstruction_error=error,
        sample_count_quantiles=np.quantile([len(x) for x in samples], [0, .25, .5, .75, 1]).tolist(),
        played_root_policies=bank.tolist()), inputs


def main():
    output = OUT/'root-retained-seed-diagnostics-v1-result.json'
    assert not output.exists()
    comparison_path = OUT/'root-retained-seed-range-comparison-v1-result.json'
    comparison = read(comparison_path)
    assert comparison['passed']
    runs = {}; inputs = {str(Path(__file__)): sha(Path(__file__)), str(comparison_path): sha(comparison_path)}
    for key, prefix in [('first', 'root-retained-fresh-pilot-v1'),
                        ('replication', 'root-retained-replication-resume-v1')]:
        runs[key], more = inspect(prefix); inputs.update(more)
    mass = np.asarray([r['entry_mass'] for r in comparison['classes']])
    blocks = []
    for begin, end in [(0, 78), (0, 39), (39, 78), (52, 78), (65, 78)]:
        means = {}
        for key, run in runs.items():
            means[key] = np.average(np.asarray(run['played_root_policies'])[begin:end],
                axis=0, weights=np.arange(begin+1, end+1))
        if begin == 0 and end == 78:
            for key in runs:
                assert np.max(abs(means[key]-np.asarray([r[key] for r in comparison['classes']]))) < 1e-12
        tv = np.abs(means['first']-means['replication']).sum(1)*.5
        blocks.append(dict(first_generation=begin, last_generation=end-1,
            entry_weighted_total_variation=float(mass@tv),
            root_action_mixes={key:(mass@value).tolist() for key,value in means.items()}))
    for run in runs.values():
        del run['played_root_policies']
    for p, h in inputs.items(): assert sha(p) == h, p
    save(output, dict(passed=True, inputs=inputs, runs=runs, descriptive_bank_blocks=blocks,
        actions=['fold','call','raise','jam'], contrasts=['call minus fold','raise minus fold','call minus raise'],
        production_modified=False, accuracy_qualified=False,
        scope='Post-hoc training-sample description only. Policies and opponents evolve across updates; these standard deviations and temporal means are not stationary-policy confidence intervals or action rankings. Later bank slices are diagnostics, not selected replacements. No new deals, model fits, holdout tuning or deployment.'))
    print(json.dumps(dict(count_quantiles={k:v['sample_count_quantiles'] for k,v in runs.items()},
        descriptive_bank_blocks=blocks)))


if __name__ == '__main__': main()
