"""Independent artifact and arithmetic readback of the float64 bank control."""
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-hybrid-precision-control-v1'


def main():
    started = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        if now-last >= 2:
            assert idle() and now-started < 600
            assert psutil.virtual_memory().available >= 20_000_000_000
            last = now
    guard()
    paths = {s: OUT/f'{PREFIX}-{s}.json' for s in ('registration', 'result', 'status', 'resources')}
    reg, result, status, resources = [json.loads(paths[s].read_text()) for s in paths]
    assert status['state'] == 'complete' and status['error'] is None and result['passed']
    assert result['registration_sha256'] == sha(paths['registration'])
    assert reg['policy_tolerance'] == 1e-4 and reg['payoff_tolerance_bb'] == 1e-3
    assert reg['played_generations'] == list(range(78)) and result['complete_deals'] == 256
    for p, h in reg['inputs'].items(): assert sha(p) == h, p
    original = json.loads((OUT/'sampled-physical-hybrid-evaluation-v1-registration.json').read_text())
    assert sha(OUT/'sampled-physical-hybrid-evaluation-v1-registration.json') == reg['source_registration_sha256']
    for p, h in original['inputs'].items(): assert sha(p) == h, p
    for p, h in reg['source_control_artifacts'].items(): assert sha(p) == h, p
    assert resources and all(r['free_host_bytes'] >= 20_000_000_000 and r['free_gpu_bytes'] >= 3_000_000_000
                             and r['free_disk_bytes'] >= 40_000_000_000 for r in resources)
    assert [r['offset'] for r in result['records']] == list(range(0, 256, 16))
    policy_error = 0.; value_error = 0.; observed = 0; artifact_hashes = {}
    for record in result['records']:
        guard(); contents = []
        for p, expected in record['summaries'].items():
            path = Path(p); assert sha(path) == expected
            artifact_hashes[p] = expected
            summary = json.loads(path.read_text()); docs = {}
            for name, h in summary['artifacts'].items():
                artifact = path.parent/name; assert sha(artifact) == h
                artifact_hashes[str(artifact)] = h; docs[name] = json.loads(artifact.read_text())
            contents.append((summary, docs))
        (cs, cd), (gs, gd) = contents
        source_batch = Path(original['cpu_reference_batches'][str(record['offset'])]['folder'])/'batch.json'
        assert cd['batch.json'] == gd['batch.json'] == json.loads(source_batch.read_text())
        assert cd['queries.json']['observations'] == gd['queries.json']['observations']
        assert cd['queries.json']['context_source'] == gd['queries.json']['context_source']
        cpu_profiles = cd['profiles.json']['profiles']; gpu_profiles = gd['profiles.json']['profiles']
        assert [p['name'] for p in cpu_profiles] == [p['name'] for p in gpu_profiles] == ['baseline', 'action-0', 'action-1', 'action-2', 'action-3']
        batch_policy_error = 0.
        for cp, gp in zip(cpu_profiles, gpu_profiles):
            assert len(cp['policies']) == len(gp['policies'])
            for c, g in zip(cp['policies'], gp['policies']):
                assert all(c[k] == g[k] for k in ('hi', 'lo', 'actor', 'n'))
                for row in (c, g):
                    p = np.asarray(row['probabilities'])
                    assert np.isfinite(p).all() and np.min(p) >= 0 and abs(p.sum()-1) < 1e-12
                    assert not np.any(p[row['n']:])
                batch_policy_error = max(batch_policy_error, max(abs(a-b) for a, b in zip(c['probabilities'], g['probabilities'])))
        # The published gate covers the baseline; root-forced profiles have no larger difference.
        assert batch_policy_error == gs['cpu_comparison']['maximum_policy_error']
        paired_error = max(float(np.max(np.abs(np.asarray(cs[k])-np.asarray(gs[k]))))
                           for k in ('action_values', 'baseline_values'))
        assert paired_error == gs['cpu_comparison']['maximum_payoff_error_bb']
        assert gs['cpu_comparison'] == record['comparison']
        assert batch_policy_error <= 1e-4 and paired_error <= 1e-3
        policy_error = max(policy_error, batch_policy_error); value_error = max(value_error, paired_error)
        observed += len(cd['queries.json']['observations'])
    assert policy_error == result['maximum_policy_error'] and value_error == result['maximum_payoff_error_bb']
    assert result['scalar_reference_check']['generation_count'] == 78
    assert result['scalar_reference_check']['maximum_error'] < 1e-8
    guard()
    review = dict(passed=True, inputs={str(p): sha(p) for p in paths.values()},
        reviewer_sha256=sha(Path(__file__)), complete_deals=256, queried_observations=observed,
        artifacts_verified=len(artifact_hashes), artifacts=artifact_hashes,
        maximum_policy_error=policy_error, maximum_payoff_error_bb=value_error,
        registration_sha256=sha(paths['registration']), result_sha256=sha(paths['result']),
        seconds=time.monotonic()-started, production_modified=False,
        scope='Independent numerical-result and artifact readback. Inference and native traversal are not rerun. No strength or fresh chance evidence.')
    save(OUT/f'{PREFIX}-independent-review.json', review)
    print(json.dumps({k: v for k, v in review.items() if k not in ('inputs', 'artifacts')}))


if __name__ == '__main__': main()
