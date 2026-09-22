"""Check the exact current-policy helper used by the prepared hybrid trainer."""
import copy
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_batch_model_v1 import predict
from sampled_physical_hybrid_policy_v1 import probabilities

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-hybrid-policy-control-v1'


def main():
    import torch
    torch.set_num_threads(2)
    started = time.monotonic()
    def guard():
        assert time.monotonic()-started < 120 and idle()
        assert psutil.virtual_memory().available >= 20_000_000_000
    guard()
    parent_path = OUT/'sampled-physical-hybrid-gpu-control-v1-registration.json'
    parent = json.loads(parent_path.read_text())
    for p,h in parent['inputs'].items(): assert sha(p) == h,p
    paths = [*map(Path,parent['inputs']),parent_path,Path(__file__),
             ROOT/'tools/research/sampled_physical_hybrid_policy_v1.py']
    reg = dict(inputs={str(p):sha(p) for p in paths},production_modified=False,
        scope='CPU correctness of training policy dispatch on existing 16-deal fixture. No training or poker accuracy claim.')
    regpath = OUT/f'{PREFIX}-registration.json'
    assert not regpath.exists()
    save(regpath,reg)
    queries = json.loads(Path(parent['query_fixture']).read_text())
    models = json.loads((OUT/'sampled-physical-hybrid-gpu-control-v1-models.json').read_text())
    cpu_rng = torch.get_rng_state().clone()
    rows = []
    for model in models:
        guard()
        actual,covered = probabilities(queries,model,'cpu')
        _,neural = predict(queries['observations'],model['networks'],'cpu')
        expected = neural.copy(); matched = [0,0]
        lookup = [None if t is None else {(int(r['hi']),int(r['lo'])):r for r in t['rows']}
                  for t in model['preflop_tables']]
        for i,o in enumerate(queries['observations']):
            table = lookup[o['actor']]; key = (int(o['hi']),int(o['lo']))
            if o['phase'] == 0 and table is not None and key in table:
                values = np.array(table[key]['mean_regret'])
                row = np.maximum(values,0.)
                if row.sum() > 0: row /= row.sum()
                else:
                    row[:] = 0.; row[int(np.argmax(values[:o['n']]))] = 1.
                expected[i] = row; matched[o['actor']] += 1
        assert np.array_equal(actual,expected) and covered == matched
        post = [i for i,o in enumerate(queries['observations']) if o['phase'] != 0]
        assert np.array_equal(actual[post],neural[post])
        rows.append(dict(generation=model['generation'],observations=len(actual),
                         exact=True,preflop_table_queries=covered,postflop_rows_unchanged=len(post)))
    assert sum(sum(r['preflop_table_queries']) for r in rows) > 0
    rejected = []
    def reject(label,model,qs):
        try: probabilities(qs,model,'cpu')
        except ValueError: rejected.append(label)
        else: raise AssertionError(('Invalid policy accepted',label))
    old = dict(models[0],format=1)
    reject('legacy-format',old,queries)
    wrong = dict(queries,context_source=queries['context_source']+' ')
    reject('wrong-context',models[-1],wrong)
    swapped = copy.deepcopy(models[-1]); swapped['preflop_tables'].reverse()
    reject('swapped-player-tables',swapped,queries)
    assert torch.equal(cpu_rng,torch.get_rng_state())
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    guard()
    result = dict(passed=True,registration_sha256=sha(regpath),models=rows,
        all_supported_rows_exact=True,all_uncovered_rows_preserve_neural=True,
        rng_unchanged=True,rejections=rejected,seconds=time.monotonic()-started,
        accuracy_qualified=False,production_modified=False,scope=reg['scope'])
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps(result))


if __name__ == '__main__': main()
