"""Unchanged audited comparison reader with the verified post-reboot idle guard.

Numerical read/aggregation body is byte-for-byte copied from the original reader.
The original remains frozen for prior result provenance.
"""
import json
import math
from pathlib import Path
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from reboot_research_idle_v1 import idle
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'


def read(prefix):
    assert idle()
    paths = {k:OUT/f'{prefix}-{k}.json' for k in ('registration','result','independent-review','status')}
    docs = {k:json.loads(p.read_text()) for k,p in paths.items()}
    reg,result,review,status = [docs[k] for k in ('registration','result','independent-review','status')]
    assert review['passed'] and status['state'] == 'complete' and result['terminal']
    assert review['result_sha256'] == sha(paths['result'])
    assert review['registration_sha256'] == sha(paths['registration'])
    assert review['terminal_status_sha256'] == sha(paths['status'])
    assert review['evaluation_deals_replayed'] == 16384
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    store = Path(reg['store']); response_path = store/'response.json'
    assert sha(response_path) == result['response_sha256']
    response = json.loads(response_path.read_text())
    classes = [[] for _ in range(169)]
    for offset in range(0,16384,16):
        if offset % 1024 == 0: assert idle()
        path = store/f'{prefix}-test-{offset}'/'summary.json'
        assert sha(path) == result['batch_summary_hashes'][path.parent.name]
        summary = json.loads(path.read_text())
        for c,values,baseline,mix in zip(summary['classes'],summary['action_values'],
                                        summary['baseline_values'],summary['root_probabilities']):
            classes[c].append((values,baseline,mix))
    rows = []; total_mix = [0.]*4; total_response = [0.]*4
    baselines = []; responses = []
    for c,samples in enumerate(classes):
        n = len(samples); assert n == result['evaluation_class_counts'][c]
        assert n > 0
        mix = samples[0][2]
        assert all(max(abs(a-b) for a,b in zip(s[2],mix)) < 1e-12 for s in samples)
        a,b = divmod(c,13); ranks = '23456789TJQKA'
        hand = ranks[a]*2 if a==b else ranks[max(a,b)]+ranks[min(a,b)]+('s' if a>b else 'o')
        action_means = [math.fsum(s[0][j] for s in samples)/n for j in range(4)]
        baseline_mean = math.fsum(s[1] for s in samples)/n
        selected = response['actions'][c]
        for j in range(4):
            total_mix[j] += n*mix[j]
            total_response[j] += n*(mix[j] if selected < 0 else float(j==selected))
        baselines.extend(s[1] for s in samples)
        responses.extend(s[1] if selected < 0 else s[0][selected] for s in samples)
        rows.append(dict(hand=hand,hand_class=c,test_deals=n,baseline_probabilities=mix,
            mean_action_values_bb=action_means,mean_baseline_bb=baseline_mean,
            call_minus_fold_bb=action_means[1]-action_means[0],
            train_selected_action=selected,training_deals=response['training_counts'][c]))
    mean_baseline = math.fsum(baselines)/16384
    mean_response = math.fsum(responses)/16384
    assert math.isclose(mean_response-mean_baseline,result['intervals']['trained-response']['mean'],abs_tol=1e-10)
    assert math.isclose(-1-mean_baseline,result['intervals']['always-fold']['mean'],abs_tol=1e-10)
    return dict(prefix=prefix,evidence={str(p):sha(p) for p in paths.values()},
        training_seed=reg['config']['train_seed'],test_seed=reg['config']['test_seed'],
        baseline_action_mix=[x/16384 for x in total_mix],
        trained_response_action_mix=[x/16384 for x in total_response],
        mean_baseline_bb=mean_baseline,mean_trained_response_bb=mean_response,
        intervals=result['intervals'],classes=rows)

