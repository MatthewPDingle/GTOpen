"""Exact historical full-fit replay across three earlier reservoir sizes."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import sys
import time
import numpy as np
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from hu_action_integrated_exact_20260925 import bank_args
from action_integrated_checkpoint_v1 import restore_checkpoint
from sampled_visible_hybrid_checkpoint_v1 import read_object
from sampled_visible_hybrid_fit_bulk_v1 import fit as reference
from sampled_visible_gradient_graph_fit_v1 import fit as candidate
from hu_paired_continuation_support_20260925 import setup_cuda, guard_for, launch

PREFIX = 'cuda-gradient-graph-early-control-v1'
ITERATIONS = (1, 26, 52)


def worker(reg):
    import torch
    setup_cuda(); guard = guard_for(reg); guard(); started = time.monotonic()
    trial = read(reg['trials'][1]['result']); cfg = trial['config']
    assert torch.__version__ == cfg['torch_version'] and np.__version__ == cfg['numpy_version']
    assert torch.cuda.get_device_name() == cfg['device_name']
    objects = Path(trial['store']) / 'objects'
    args = bank_args((OUT/'bb-context-candidate.json').read_text())
    rows = []
    for iteration in reg['iterations']:
        mp = Path(trial['store']) / f'iteration-{iteration:04d}/metrics.json'
        assert sha(mp) == trial['steps'][iteration-1]['metrics_sha256']
        metric = read(mp)
        assert metric['iteration'] == iteration
        state = restore_checkpoint(objects, metric['checkpoint'], config=cfg, **args)
        assert state['completed_iterations'] == iteration
        expected = json.loads(read_object(objects, metric['next_model']))['exact_model']['base_model']['networks']
        for player, reservoir in enumerate(state['reservoirs']):
            methods = [('reference', reference), ('graph', candidate)]
            if (player + ITERATIONS.index(iteration)) % 2: methods.reverse()
            records = {}
            for label, fn in methods:
                guard(); torch.cuda.reset_peak_memory_stats(); before = time.monotonic()
                net, metrics = fn(reservoir, seed=cfg['fit_seed_base']+iteration*200003+player,
                    steps=cfg['fit_steps'], device='cuda', chunk_size=cfg['chunk_size'],
                    guard=guard, learning_rate=cfg['learning_rate'])
                elapsed = time.monotonic()-before
                assert net == expected[player], (iteration, player, label, 'network changed')
                excluded = {'scope', 'setup_seconds', 'optimizer_seconds', 'graph_capture_seconds'}
                assert {k:v for k,v in metrics.items() if k not in excluded} == {
                    k:v for k,v in metric['fits'][player].items() if k not in excluded}
                records[label] = dict(metrics=metrics, wall_seconds=elapsed,
                    weights_identical=True, nontiming_metrics_identical=True,
                    peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                    peak_reserved_bytes=torch.cuda.max_memory_reserved())
                print(json.dumps(dict(iteration=iteration, player=player, method=label,
                    seconds=elapsed, weights_identical=True)), flush=True)
            rows.append(dict(iteration=iteration, player=player, methods=records))
        del state
    for path, digest in reg['inputs'].items(): guard(); assert sha(path) == digest, path
    save(OUT/f'{PREFIX}-result.json', dict(passed=True,
        registration_sha256=sha(OUT/f'{PREFIX}-registration.json'), fits=rows,
        seconds=time.monotonic()-started, production_modified=False, accuracy_qualified=False,
        scope='Both players, three prespecified earlier checkpoints, full original 512-step fits. Exact historical networks and non-timing metrics required; no whole-training speed or accuracy claim.'))


if __name__ == '__main__':
    if sys.argv[1:] == ['--worker']: worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:] == ['--run']
        prior = OUT/'cuda-gradient-graph-control-v1-result.json'
        assert read(prior)['passed']
        result = read(OUT/'action-integrated-replication-v1-result.json')
        extras = [str(prior)]
        for iteration in ITERATIONS:
            p = Path(result['store'])/f'iteration-{iteration:04d}/metrics.json'
            assert sha(p) == result['steps'][iteration-1]['metrics_sha256']
            extras.append(str(p))
        launch(Path(__file__).resolve(), PREFIX,
            dict(extra_inputs=extras, iterations=list(ITERATIONS),
                scope='Prespecified early/middle/later exact-replay controls for captured gradients, same seeds and complete fits.'),
            cap=10_000_000, seconds=1800)
