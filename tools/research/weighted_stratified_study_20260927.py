"""Fixed-budget stratified candidates against already completed matched baselines."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
import gc
import json
from pathlib import Path
import subprocess
import time
import uuid
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from weighted_learning_cuda_control_20260927 import safe_read_only_resources, LOCK, OTHER
from preflop_allin_matrix_v1 import AllinMatrix
import weighted_training_checkpoint_v1 as checkpoint
from weighted_training_v1 import initialize
from weighted_training_parallel_graph_v2 import update
from ntfs_research_storage_v1 import create_compressed_directory, measure_tree

PREFIX = 'weighted-stratified-study-v1'
STORE = Path('T:/GTOpen-research') / PREFIX
REG = OUT / f'{PREFIX}-registration.json'
PLAN = OUT / 'WEIGHTED-STRATIFIED-STUDY-PLAN.md'


def atomic(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    save(temporary, value)
    os.replace(temporary, path)


def main(resume=False, max_generations=None):
    import torch
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    assert torch.cuda.is_available() and safe_read_only_resources()
    assert not LOCK.exists() and not OTHER.exists()
    query = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free',
                            '--format=csv,noheader,nounits'], capture_output=True, text=True,
                           timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
    assert query.returncode == 0
    utilization, free = map(float, query.stdout.strip().splitlines()[0].split(','))
    assert utilization < 20 and free > 6000 and psutil.cpu_percent(interval=1) < 50
    assert psutil.disk_usage('T:/').free > 50_000_000_000
    cp = OUT / 'bb-context-candidate.json'
    mp = OUT / 'preflop-allin-matrix-control-v1-matrix.json'
    cat = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    source, catalog_source, matrix_source = cp.read_text(), cat.read_text(), mp.read_text()
    matrix = AllinMatrix(json.loads(matrix_source), source)
    cache = load_complete_cache()
    args = dict(context_source=source, catalog_source=catalog_source,
                matrix_sha256=sha(mp), entry_mass=matrix.btn_mass)
    exes = [ROOT / 'target/release/examples' / name for name in (
        'hu_sampled_allin_bridge_v3.exe', 'hu_sampled_action_trace_v2.exe',
        'hu_sampled_profile_allin_evaluation_v1.exe')]
    if resume:
        reg = read(REG)
        assert reg['store'] == str(STORE)
    else:
        baseline_path = OUT / 'showdown-matched-training-v1-registration.json'
        baseline = read(baseline_path)
        pilot = read(OUT / 'weighted-training-pilot-v1-result.json')
        arms = []
        inputs = [cp, mp, cat, baseline_path, PLAN, *exes, *Path(__file__).parent.glob('*.py')]
        for name in ('weighted-parallel-graph-control-v2', 'weighted-graph-fit-control-v2'):
            result_path = OUT / f'{name}-result.json'
            result = read(result_path)
            registration = OUT / f'{name}-registration.json'
            assert result['passed'] and result['registration_sha256'] == sha(registration)
            for path, digest in read(registration)['inputs'].items():
                assert sha(path) == digest, path
            inputs.extend((result_path, registration))
        for old in baseline['arms']:
            if old['treatment'] != 'baseline':
                continue
            old_config = old['config']
            audit_path = OUT / f"showdown-training-readback-v2-{old['name']}-0078-result.json"
            audit = read(audit_path)
            assert audit['passed'] and audit['complete_arm'] and audit['completed_updates'] == 78
            assert audit['source_registration_sha256'] == sha(baseline_path)
            cfg = dict(pilot['config'])
            for key in ('sampler_seed', 'action_seed', 'fit_seed_base', 'reservoir_seeds',
                        'fit_steps', 'chunk_size', 'reservoir_capacity', 'query_limit',
                        'learning_rate', 'deals_per_subbatch', 'allin_cache_sha256'):
                cfg[key] = old_config[key]
            cfg['deals_per_generation'] = old_config['deals_per_iteration']
            assert cfg['deals_per_generation'] == old_config['subbatches_per_iteration'] * cfg['deals_per_subbatch'] == 512
            assert cfg['allin_cache_sha256'] == cache.sha256
            assert old_config['architecture'] == cfg['architecture'] and old_config['representation'] == cfg['representation']
            assert old_config['current_policy_inference'] == cfg['current_policy_inference']
            assert cfg['torch_version'] == torch.__version__ and cfg['numpy_version'] == np.__version__
            checkpoint.require_config(cfg)
            endpoint = Path(baseline['store']) / old['name'] / 'checkpoint-0078.json'
            inputs.extend((audit_path, endpoint))
            arms.append(dict(name=f"{old['seed']}-stratified", baseline=old['name'], config=cfg,
                             baseline_endpoint=str(endpoint), baseline_readback=str(audit_path)))
        assert len(arms) == 2
        create_compressed_directory(STORE)
        reg = dict(inputs={str(p): sha(p) for p in inputs}, arms=arms, store=str(STORE),
                   generations=78, workers=2, maximum_logical_bytes=80_000_000_000,
                   maximum_invocation_seconds=43200, gpu_utilization_before=utilization,
                   gpu_free_MiB_before=free, production_modified=False,
                   stopping='Fixed 78 generations per seed; resource or user-work guards may interrupt. No outcome-based selection.',
                   comparison='Matched settings and seed identities; different sampling algorithms do not produce paired identical deals. Historical baselines were already observed.',
                   accuracy_qualified=False)
        save(REG, reg)
    for path, digest in reg['inputs'].items():
        assert sha(path) == digest, path
    started = time.monotonic()
    last = 0.
    acquired = False
    completed_here = 0
    def guard():
        nonlocal last
        if time.monotonic() - started > reg['maximum_invocation_seconds']:
            raise RuntimeError('Invocation time budget reached; resume completed generation')
        if time.monotonic() - last > 3:
            if not safe_read_only_resources() or OTHER.exists():
                raise RuntimeError('Production activity, RAM pressure, or competing research')
            if psutil.disk_usage('T:/').free < 50_000_000_000 or torch.cuda.mem_get_info()[0] < 4_000_000_000:
                raise RuntimeError('Research disk or VRAM headroom exhausted')
            last = time.monotonic()
    try:
        with LOCK.open('x') as f:
            f.write(str(os.getpid()))
        acquired = True
        step = dict(context_path=cp, catalog_source=catalog_source, matrix_source=matrix_source,
                    matrix_sha256=sha(mp), cache=cache, executable=exes[0], trace_executable=exes[1],
                    integration_executable=exes[2], guard=guard, workers=reg['workers'])
        for arm in reg['arms']:
            guard()
            folder = STORE / arm['name']
            folder.mkdir(exist_ok=True)
            objects = folder / 'objects'
            objects.mkdir(exist_ok=True)
            progress_path = folder / 'progress.json'
            cfg = arm['config']
            if progress_path.exists():
                progress = read(progress_path)
                assert progress['registration_sha256'] == sha(REG)
                state = checkpoint.restore_checkpoint(objects, progress['checkpoint'], cfg, **args)
                assert state['completed_iterations'] == progress['completed']
                if progress['completed']:
                    assert sha(progress['metrics_path']) == progress['metrics_sha256']
            else:
                state = initialize(objects, cfg, **args)
                ref = checkpoint.save_checkpoint(objects, state, cfg, **args)
                progress = dict(completed=0, checkpoint=ref, registration_sha256=sha(REG))
                atomic(progress_path, progress)
            while state['completed_iterations'] < reg['generations']:
                guard()
                if max_generations is not None and completed_here >= max_generations:
                    print(json.dumps(dict(status='checkpointed invocation limit', completed_here=completed_here)), flush=True)
                    return
                before = measure_tree(STORE, guard)
                assert before['logical_bytes'] < reg['maximum_logical_bytes'] - 2_000_000_000
                iteration = state['completed_iterations'] + 1
                # A retry preserves incomplete artifacts and starts from the saved boundary.
                attempt = folder / f'iteration-{iteration:04d}-{uuid.uuid4().hex[:8]}'
                metric = update(attempt, objects, state, cfg, batch_prefix=arm['name'], **step)
                assert metric['root_samples'] == iteration * 512 and metric['root_covered_classes'] == 169
                assert metric['exact_btn_updates'] == iteration
                restored = checkpoint.restore_checkpoint(objects, metric['checkpoint'], cfg, **args)
                assert restored['next_model'] == state['next_model']
                del restored
                progress = dict(completed=iteration, checkpoint=metric['checkpoint'], registration_sha256=sha(REG),
                                metrics_path=str(attempt / 'metrics.json'), metrics_sha256=sha(attempt / 'metrics.json'))
                atomic(progress_path, progress)
                record = dict(arm=arm['name'], completed=iteration, seconds=metric['seconds'],
                              timings=metric['timings'], retained=[r.size for r in state['reservoirs']],
                              visits=[r.seen for r in state['reservoirs']], current_checkpoint=metric['checkpoint'],
                              accuracy_qualified=False)
                atomic(OUT / f'{PREFIX}-status.json', dict(record, pid=os.getpid(), state='running'))
                print(json.dumps(record), flush=True)
                completed_here += 1
                gc.collect()
                torch.cuda.empty_cache()
            del state
        for path, digest in reg['inputs'].items():
            assert sha(path) == digest, path
        final = dict(training_complete=True, accuracy_qualified=False, independently_reviewed=False,
                     registration_sha256=sha(REG), store=str(STORE),
                     arms={a['name']: read(STORE / a['name'] / 'progress.json') for a in reg['arms']},
                     storage=measure_tree(STORE, guard), production_modified=False)
        save(OUT / f'{PREFIX}-training-result.json', final)
        atomic(OUT / f'{PREFIX}-status.json', dict(state='training complete; review and evaluation pending', pid=os.getpid()))
    except BaseException as error:
        atomic(OUT / f'{PREFIX}-status.json', dict(state='interrupted', pid=os.getpid(), error=str(error),
                                                resume='Restore last complete checkpoint; partial attempts retained'))
        raise
    finally:
        if acquired:
            assert LOCK.read_text() == str(os.getpid())
            LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--max-generations', type=int)
    options = parser.parse_args()
    if options.max_generations is not None and options.max_generations < 1:
        parser.error('Positive invocation generation limit required')
    main(options.resume, options.max_generations)
