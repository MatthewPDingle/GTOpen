"""Fixed output schedules and admission of the complete physical-pair cache.

No training targets, reservoir weights or player probabilities are altered here.
"""
import json
from pathlib import Path
import numpy as np
from sampled_physical_root_evaluation_v1 import ROOT, sha
from sampled_allin_protocol_v3 import AllinCache

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'


def read(path):
    return json.loads(Path(path).read_text())


def weights(kind, count):
    if type(count) is not int or not 1 <= count <= 78:
        raise ValueError('One to 78 complete played generations required')
    if kind == 'equal':
        row = np.ones(count, dtype=np.float64)
    elif kind == 'linear':
        row = np.arange(1, count+1, dtype=np.float64)
    else:
        raise ValueError('Only the two prospectively specified schedules exist')
    return np.stack([row, row])


def load_complete_cache():
    prefix = 'complete-private-allin-cache-v2'
    rp, pp, ap = [OUT/f'{prefix}-{suffix}.json' for suffix in
                  ('registration','result','independent-review')]
    reg, result, audit = map(read, (rp, pp, ap))
    assert audit['passed'] and audit['result_sha256'] == sha(pp)
    assert result['registration_sha256'] == audit['registration_sha256'] == sha(rp)
    assert audit['canonical_private_pairs'] == 47478 and audit['physical_private_pairs'] == 776650
    for p,h in reg['inputs'].items():
        assert sha(p) == h, p
    population = read(reg['population'])
    assert sha(reg['population']) == reg['population_sha256']
    assert population['context_sha256'] == sha(OUT/'bb-context-candidate.json')
    cache = AllinCache(audit['cache_artifact'], audit['cache_sha256'])
    assert len(cache.rows) == 47478
    return cache
