"""Post-hoc analysis of the completed fixed comparison; no solver or policy edits.

Reconstruct deviations from terminal values, then omit each board in turn using
paired omissions across sources. This is sensitivity analysis, not a confidence
interval for the systematically selected panel or an accuracy guarantee.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import json
from pathlib import Path
import numpy as np
from storage_phase_run_20260920 import ROOT, OUT, EVIDENCE, SUB, read, sha
from integrated_coverage import CLASSES, COUNTS
from storage_strategic_policy_report_20260920 import hand_label

PREFIX = 'strategic-reserved95-v1'
DEST = OUT/'strategic-reserved95-v1-analysis.json'


def evaluate(nodes, sigma, leaves, weights, normalizer):
    def walk(player, node, post_br, pre_br):
        n = nodes[node]
        if n['kind'] != 0:
            return leaves[2*player+int(post_br), node]
        children = np.asarray([walk(player, c, post_br, pre_br) for c in n['children']])
        if n['actor'] != player:
            return children.sum(0)
        return children.max(0) if pre_br else (children*sigma[node]).sum(0)
    current = np.asarray([walk(p, 0, False, False) for p in range(2)])
    post = np.asarray([walk(p, 0, True, False) for p in range(2)])
    best = np.asarray([walk(p, 0, True, True) for p in range(2)])
    ev = (current*weights).sum(1)/normalizer
    contribution = (best-current)*weights/normalizer
    return ev, contribution.sum(1), ((post-current)*weights).sum(1)/normalizer, contribution


def main():
    assert not DEST.exists()
    status = read(OUT/(PREFIX+'-status.json'))
    assert status['step'] == 'complete-awaiting-scientific-review' and status['completed_workers'] == 285
    complete = read(OUT/(PREFIX+'-review.json'))
    assert complete['comparison_complete'] and complete['response_convergence_passed']
    frozen = {**complete['inputs_sha256'], **complete['evidence_sha256']}
    for name, digest in frozen.items():
        assert sha(ROOT/name) == digest, name
    nodes = read(SUB)['nodes']
    panel = read(OUT/'expansion-reserved-95-evaluation-v1.json')
    chance = np.asarray([b['weight'] for b in panel['boards']], dtype=float)
    chance /= chance.sum()
    assert len(chance) == 95
    weights = np.asarray(read(SUB)['incoming_class_mass'])[:, CLASSES]/COUNTS[CLASSES]
    weights /= weights.max(1)[:, None]
    weights[weights < 1e-5] = 0
    sources = {}; omissions = {}; minima = {'free_host_bytes': float('inf'), 'free_gpu_bytes': float('inf')}
    guard_seconds = []
    for item in complete['results']:
        name = item['source']
        path = OUT/(PREFIX+'-'+name+'-result.json')
        assert sha(path) == item['result_sha256']
        combined = read(path); final = combined['records'][-1]['evaluation']
        sigma = [np.asarray(n) for n in final['preflop_policy']]
        dense = np.zeros((95, 4, len(nodes), 1326)); normalizers = np.zeros(95)
        local_post = np.zeros(95)
        for i, board in enumerate(panel['boards']):
            label = PREFIX+f'-{name}-{i:03}'
            worker = read(OUT/(label+'-result.json'))
            assert worker['boards'] == [board['board']]
            assert worker['records'][-1]['iteration'] == 2000
            assert worker['records'][-1]['evaluation']['preflop_policy'] == final['preflop_policy']
            for k, values in enumerate(worker['terminal_values']['values']):
                for j, n in enumerate(nodes):
                    if n['kind'] != 0:
                        dense[i, k, j] = values[j]
            normalizers[i] = worker['root_normalizer']
            local_post[i] = worker['records'][-1]['evaluation']['postflop_gap_total']
            guard = read(EVIDENCE/(label+'-status.json'))
            assert guard['exit_code'] == 0 and guard['error'] is None
            guard_seconds.append(guard['seconds'])
            assert read(OUT/(label+'-result-review.json'))['preflop_exactly_preserved']
            for sample in read(EVIDENCE/(label+'-resources.json')):
                for k in minima: minima[k] = min(minima[k], sample[k])
        assert np.all(np.isfinite(dense))
        leaves = np.einsum('b,bknh->knh', chance, dense)
        z = chance@normalizers
        ev, gaps, post, contribution = evaluate(nodes, sigma, leaves, weights, z)
        errors = {k:float(np.max(abs(a-final[k]))) for k,a in [('ev',ev),('gaps',gaps),('postflop_gaps',post)]}
        assert max(errors.values()) < 1e-9
        assert abs(float((chance*normalizers)@local_post/z)-sum(post)) < 1e-5
        loo = []
        for i in range(95):
            # Both numerator and normalizer retain the same omitted weight;
            # renormalizing remaining chance weights cancels in their ratio.
            _, g, _, _ = evaluate(nodes, sigma, leaves-chance[i]*dense[i], weights, z-chance[i]*normalizers[i])
            loo.append(float(g.sum()))
        omissions[name] = np.asarray(loo)
        hands = []
        for p in range(2):
            v = np.bincount(CLASSES, weights=contribution[p], minlength=169)
            assert abs(v.sum()-gaps[p]) < 1e-10
            hands.append(sorted([dict(hand=hand_label(c), contribution_bb=float(v[c])) for c in range(169) if v[c]>1e-10], key=lambda h:-h['contribution_bb']))
        sources[name] = dict(full_gap_bb=float(sum(gaps)), per_player_gap_bb=gaps.tolist(),
                             postflop_residual_bb=float(sum(post)), ev=ev.tolist(), expected_rake=final['expected_rake'],
                             reconstruction_errors=errors, full_deviation_hand_contributions=hands,
                             omission_gap_range_bb=[float(min(loo)),float(max(loo))])
    comparisons = []
    for a,b in [('weighted','equal'),('weighted','report47'),('equal','report47')]:
        delta = omissions[a]-omissions[b]
        direct = sources[a]['full_gap_bb']-sources[b]['full_gap_bb']
        comparisons.append(dict(a=a,b=b,gap_difference_bb=direct,relative_reduction_vs_b=-direct/sources[b]['full_gap_bb'],
                                paired_omission_difference_range_bb=[float(delta.min()),float(delta.max())],
                                omissions_favoring_a=int(sum(delta<0)),omissions=95))
    assert minima['free_host_bytes']>=20_000_000_000 and minima['free_gpu_bytes']>=3_000_000_000
    out = dict(complete_evidence_hashes_verified=len(frozen), workers_verified=285, sources=sources, comparisons=comparisons,
               paired_omissions={k:v.tolist() for k,v in omissions.items()}, resource_minima=minima,
               guarded_worker_seconds_total=sum(guard_seconds), maximum_worker_seconds=max(guard_seconds),
               comparison_review_sha256=sha(OUT/(PREFIX+'-review.json')), analysis_script_sha256=sha(Path(__file__)),
               statistical_scope='Post-hoc paired leave-one-board-out sensitivity, not a confidence interval. No training or panel changes. Restricted eligible population; not full-deck or multiway accuracy.',
               production_ready=False)
    with DEST.open('x') as f: json.dump(out,f,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in out.items() if k not in ['sources','paired_omissions']},indent=2))


if __name__ == '__main__': main()
