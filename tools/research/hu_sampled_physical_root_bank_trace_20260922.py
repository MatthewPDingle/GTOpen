"""Describe root action frequencies of every saved pilot generation.

Training artifacts only; no model is selected or newly evaluated for strength.
"""
import json
from pathlib import Path
import time

import numpy as np

from loopback_research_validation import idle
from sampled_batch_model_v1 import predict
from sampled_physical_checkpoint_v1 import read_object, model_document
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import CLASSES
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-root-study-gpu-v1'


def main():
    import torch
    torch.set_num_threads(2)
    started = time.monotonic()
    regpath = OUT / (PREFIX+'-registration.json')
    reg = json.loads(regpath.read_text())
    result = json.loads((OUT/(PREFIX+'-result.json')).read_text())
    review = json.loads((OUT/(PREFIX+'-independent-review.json')).read_text())
    assert review['passed'] and review['result_sha256'] == sha(OUT/(PREFIX+'-result.json'))
    interpretation_path = OUT/(PREFIX+'-interpretation.json')
    interpretation = json.loads(interpretation_path.read_text())
    source = Path(reg['context']).read_text()
    sampler = PhysicalDeals(source, mode='full_deck', seed=0)
    marginal = np.bincount(CLASSES, weights=sampler.first[0], minlength=169)
    observations = {}
    query_hashes = {}
    for offset in range(0, reg['config']['training_deals'], 16):
        assert idle() and time.monotonic()-started < 180
        folder = Path(reg['store'])/f'{PREFIX}-train-{offset}'
        summary_path = folder/'summary.json'
        assert sha(summary_path) == result['batch_summary_hashes'][folder.name]
        summary = json.loads(summary_path.read_text())
        path = folder/'queries.json'
        assert sha(path) == summary['artifacts']['queries.json']
        query_hashes[str(path)] = sha(path)
        for o in json.loads(path.read_text())['observations']:
            if o['phase'] == 0 and int(o['hi']) == 1:
                assert o['actor'] == 0 and o['n'] == 4 and o['own_history'] == []
                key = int(o['lo'])
                c = hand_class([key & 63, (key >> 6) & 63])
                if c in observations: assert observations[c] == o
                else: observations[c] = o
        if len(observations) == 169: break
    assert len(observations) == 169
    obs = [observations[c] for c in range(169)]
    objects = Path(reg['objects'])
    checkpoint = json.loads(read_object(objects, reg['checkpoint']))
    rows = []
    for i, reference in enumerate([*checkpoint['played_bank'], checkpoint['next_model']]):
        assert idle() and time.monotonic()-started < 180
        document = model_document(objects, reference)
        assert document['generation'] == i
        _, policy = predict(obs, document['networks'], 'cpu')
        rows.append(dict(generation=i, played=i<len(checkpoint['played_bank']),
                         root_frequencies=(marginal@policy).tolist(), model=reference))
    bank_average = np.mean([r['root_frequencies'] for r in rows if r['played']], axis=0)
    error = float(np.max(np.abs(bank_average-interpretation['baseline_root_frequencies'])))
    assert error < 1e-4
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    value = dict(registration_sha256=sha(regpath), source_sha256=sha(Path(__file__)),
                 interpretation_sha256=sha(interpretation_path), input_query_hashes=query_hashes,
                 rows=rows, played_bank_frequencies=bank_average.tolist(),
                 comparison_to_gpu_frequency_error=error,
                 last_ten_played_mean=np.mean([r['root_frequencies'] for r in rows if 68<=r['generation']<78],axis=0).tolist(),
                 seconds=time.monotonic()-started, production_modified=False,
                 scope='Descriptive trace of all saved root policies using visible root states and exact compatible-entry class mass. Generation 78 is unplayed and was not part of the tested bank. Frequencies do not establish quality, convergence or justify checkpoint selection. No test outcomes were used to select rows or models.')
    save(OUT/(PREFIX+'-root-bank-trace.json'),value)
    print(json.dumps(dict(first=rows[:3], last=rows[-3:], bank_average=bank_average.tolist(),
                          last_ten_played_mean=value['last_ten_played_mean'], frequency_error=error),indent=2))


if __name__ == '__main__':
    main()
