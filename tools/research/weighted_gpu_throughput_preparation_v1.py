"""Check same-deal 32/64 native query identity without CUDA or payoff analysis."""
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from weighted_gpu_throughput_inputs_v1 import retained_inputs, joined_batch, pack, compare
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from board_study_storage_v1 import create, measure

PREFIX = 'weighted-gpu-throughput-preparation-v1'
STORE = Path('S:/GTOpen-research') / PREFIX


def synthetic_capture(query):
    p = np.asarray([[1/o['n'] if a < o['n'] else 0. for a in range(4)] for o in query['observations']])
    reach = np.asarray([o['actor'] + 1. for o in query['observations']])
    return dict(queries=query, policies=np.stack([p]*4), reaches=np.stack([reach]*4))


def main():
    began = time.monotonic(); assert not STORE.exists()
    assert psutil.cpu_percent(interval=.2) < 50 and psutil.virtual_memory().available > 24_000_000_000
    batches, queries, paths = retained_inputs()
    context = OUT / 'bb-context-candidate.json'
    exe = ROOT / 'target/release/examples/hu_sampled_bank_bridge.exe'
    sources = ('weighted_gpu_throughput_inputs_v1.py', 'weighted_gpu_throughput_preparation_v1.py',
               'weighted_gpu_throughput_control_v1.py')
    paths.extend((context, exe, *(Path(__file__).with_name(n) for n in sources)))
    inputs = {str(p): sha(p) for p in paths}
    rp = OUT / f'{PREFIX}-registration.json'
    save(rp, dict(inputs=inputs, store=str(STORE), retained_deals=64, maximum_seconds=120,
        maximum_logical_bytes=50_000_000, gpu_used=False, training_started=False, production_modified=False,
        scope='Exact native query/history union for identical retained deals; synthetic policies exercise comparison only.'))
    create(STORE); batch_path = STORE / 'query-batch.json'; query_path = STORE / 'queries.json'
    combined = joined_batch(batches); save(batch_path, combined)
    result = subprocess.run([str(exe), 'queries', str(context), str(batch_path), '-', str(query_path)],
        capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode == 0, result.stderr[-2000:]
    query64 = read(query_path)
    assert query64['context_source'] == context.read_text() == queries[0]['context_source']
    assert query64['batch_source'] == batch_path.read_text()
    reference = pack([synthetic_capture(q) for q in queries])
    candidate = pack([synthetic_capture(query64)])
    comparison = compare(reference, candidate)
    assert comparison['maximum_policy_error'] == comparison['maximum_reach_error'] == 0
    # Native array order is not an information-set identity: reindex all links.
    shuffled = copy.deepcopy(query64); n = len(shuffled['observations'])
    shuffled['observations'].reverse()
    for o in shuffled['observations']:
        o['own_history'] = [[n-1-i, a, count] for i, a, count in o['own_history']]
    compare(reference, pack([synthetic_capture(shuffled)]))
    rejected = []
    bad = copy.deepcopy(candidate); bad['policies'][0, 0, 0] += .001
    try: compare(reference, bad)
    except ValueError: rejected.append('policy')
    bad = copy.deepcopy(candidate); bad['reaches'][0, 0] += .001
    try: compare(reference, bad)
    except ValueError: rejected.append('reach')
    bad_query = copy.deepcopy(query64)
    next(o for o in bad_query['observations'] if o['own_history'])['own_history'][0][0] = n
    try: pack([synthetic_capture(bad_query)])
    except ValueError: rejected.append('history')
    bad_query = copy.deepcopy(query64); bad_query['observations'][0]['active_features'][0] = -1
    try: compare(reference, pack([synthetic_capture(bad_query)]))
    except ValueError: rejected.append('feature-identity')
    assert rejected == ['policy', 'reach', 'history', 'feature-identity']
    for p, h in inputs.items(): assert sha(p) == h
    allocation = measure(STORE); assert allocation['logical_bytes'] < 50_000_000
    assert time.monotonic() - began < 120
    value = dict(passed=True, registration_sha256=sha(rp), comparison=comparison,
        rows_per_32_deal_batch=[len(q['observations']) for q in queries], rows_in_64_deal_batch=n,
        original_deal_order_preserved=True, reindexed_history_comparison_passed=True,
        rejected_perturbations=rejected, artifacts={str(p): sha(p) for p in (batch_path, query_path)},
        measurement=allocation, seconds=time.monotonic()-began, gpu_used=False, production_modified=False,
        limitation='Only query geometry and comparison mechanics are qualified. Trained-policy CUDA equivalence and speed remain unmeasured.')
    save(OUT / f'{PREFIX}-result.json', value); print(json.dumps(value), flush=True)


if __name__ == '__main__': main()
