"""Complete the failed control's final comparison on its existing trained models.

The native training transport lacks own_history. Use the same structurally
restricted view already used by the unchanged training pipeline, preserve every
old artifact and failure, and record this separate completion explicitly.
No fitting, sampling, seed change, policy change or production write occurs.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
from board_prefix_publication_v1 import atomic_json
from weighted_learning_cuda_control_20260927 import LOCK, OTHER, safe_read_only_resources
from weighted_training_v1 import first_action_view
from board_training_policy_v1 import probabilities
from board_training_pipeline_control_v1 import compare_states
import board_training_checkpoint_v1 as checkpoint
from preflop_allin_matrix_v1 import AllinMatrix

NAME = 'board-pipeline-query-recovery-v1'
CONTROL = 'board-training-pipeline-control-v1'
QUEUE = 'board-training-pipeline-queue-v2'


def main():
    began = time.monotonic()
    rp = OUT/f'{NAME}-registration.json'
    old_rp = OUT/f'{CONTROL}-registration.json'
    old_failure = OUT/f'{CONTROL}-failure.json'
    result_path = OUT/f'{CONTROL}-result.json'
    queue_result = OUT/f'{QUEUE}-result.json'
    assert not any(p.exists() for p in (rp, result_path, queue_result))
    reg = read(old_rp); failure = read(old_failure)
    assert failure['registration_sha256'] == sha(old_rp) and not failure['passed']
    assert failure['error'] == "KeyError('own_history')" and failure['completed_updates'] == 2
    stages = ['physical-targets-complete', 'root-update-complete']
    assert failure['verified_interruptions'] == stages
    for path, digest in reg['inputs'].items(): assert sha(path) == digest, path
    old_queue_rp = OUT/f'{QUEUE}-registration.json'
    old_queue_failure = OUT/f'{QUEUE}-failure.json'
    resource_rp = OUT/'board-pipeline-resource-recovery-v1-registration.json'
    resource_failure = OUT/'board-pipeline-resource-recovery-v1-failure.json'
    qf = read(old_queue_failure); rf = read(resource_failure)
    assert qf['registration_sha256'] == sha(old_queue_rp) and not qf['passed']
    assert rf['registration_sha256'] == sha(resource_rp) and not rf['passed']
    for binding in (read(old_queue_rp)['inputs'], read(resource_rp)['inputs']):
        for path, digest in binding.items(): assert sha(path) == digest, path
    assert [x['script'] for x in qf['completed']] == ['weighted_final_findings_v1.py']
    for item in qf['completed']:
        assert sha(item['result']) == item['sha256']
        for path, digest in read(item['result'])['outputs'].items(): assert sha(path) == digest
    assert not LOCK.exists() and not OTHER.exists() and safe_read_only_resources()
    assert psutil.cpu_percent(interval=1) < 30 and psutil.virtual_memory().available > 28_000_000_000
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
    assert gpu.returncode == 0
    util, free = map(float, gpu.stdout.strip().splitlines()[0].split(','))
    assert util < 20 and free > 6000
    import torch
    assert torch.cuda.is_available()
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    store = Path(reg['store']); objects = store/'objects'; cfg = reg['config']
    paths = [old_rp, old_failure, old_queue_rp, old_queue_failure, resource_rp, resource_failure,
             *Path(__file__).parent.glob('*.py'), *(p for p in store.rglob('*') if p.is_file())]
    inputs = {str(p): sha(p) for p in paths}
    atomic_json(rp, dict(inputs=inputs, original_registration_sha256=sha(old_rp),
        resumed_from_failure=str(old_failure), maximum_seconds=600, maximum_new_bytes=10_000_000,
        retraining=False, policy_changed=False, native_transport_unchanged=True,
        adapter='weighted_training_v1.first_action_view (existing production path of this research trainer)',
        scope='Complete final CPU/CUDA comparison; revalidate prior checkpoint/replay evidence. No playing-strength claim.',
        production_modified=False))
    acquired = False
    def guard():
        assert time.monotonic()-began < 600
        assert safe_read_only_resources() and not OTHER.exists()
        assert psutil.virtual_memory().available > 24_000_000_000
    try:
        with LOCK.open('x') as stream: stream.write(str(os.getpid()))
        acquired = True
        cp = OUT/'bb-context-candidate.json'; mp = OUT/'preflop-allin-matrix-control-v1-matrix.json'
        cat = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
        source = cp.read_text(); context = json.loads(source); matrix = AllinMatrix(read(mp), source)
        args = dict(context_source=source, catalog_source=cat.read_text(), matrix_sha256=sha(mp),
                    entry_mass=matrix.btn_mass, root_config=cfg['board_root'])
        initial_refs = []
        for p in objects.glob('boardrootcheckpoint-*.json'):
            value = read(p)
            if value['completed_iterations'] == 0:
                ref = dict(file=p.name, sha256=sha(p))
                assert p.name == 'boardrootcheckpoint-'+ref['sha256']+'.json'
                initial_refs.append(ref)
        assert len(initial_refs) == 1
        initial = checkpoint.restore_checkpoint(objects, initial_refs[0], cfg, **args)
        assert initial['completed_iterations'] == 0 and not initial['played_bank']
        first = read(store/'generation-0001/metrics.json')
        second = read(store/'generation-0002/metrics.json')
        replay = read(store/'generation-0002-replay/metrics.json')
        assert first['used_model'] == initial['next_model']
        assert second['used_model'] == first['next_model']
        assert second['checkpoint'] == replay['checkpoint'] and second['subbatches'] == replay['subbatches']
        assert second['next_model'] == replay['next_model']
        state = checkpoint.restore_checkpoint(objects, second['checkpoint'], cfg, **args)
        resumed = checkpoint.restore_checkpoint(objects, replay['checkpoint'], cfg, **args)
        compare_states(state, resumed)
        assert state['completed_iterations'] == 2 and state['played_bank'] == [first['used_model'], first['next_model']]
        for folder, metric in ((store/'generation-0001', first), (store/'generation-0002', second),
                               (store/'generation-0002-replay', replay)):
            for batch in metric['subbatches']:
                for name, digest in batch['artifacts'].items():
                    assert sha(folder/f"batch-{batch['chunk']:02d}"/name) == digest
        for i in (1, 2): assert not (store/f'interrupted-{i}/metrics.json').exists()
        guard()
        queries = read(store/'generation-0002/batch-00/queries.json')
        original = copy.deepcopy(queries)
        model = checkpoint.model_document(objects, second['next_model'], **args)
        pa = {k:v for k,v in args.items() if k != 'context_source'}
        try: probabilities(queries, model, device='cpu', **pa)
        except KeyError as error: assert error.args == ('own_history',)
        else: raise AssertionError('Expected the recorded raw-transport contract error')
        jam = [i for i,a in enumerate(context['nodes'][0]['actions']) if a['kind'] == 'jam']
        assert jam == [3]
        response_hi = context['nodes'][0]['children'][jam[0]]+1
        response = context['nodes'][response_hi-1]
        assert response['actor'] == 1 and [a['kind'] for a in response['actions']] == ['fold','call']
        assert all(context['nodes'][i]['kind'] != 0 for i in response['children'])
        view = first_action_view(queries, response_hi)
        changed = 0
        for before, after in zip(queries['observations'], view['observations']):
            if int(before['hi']) in (1, response_hi):
                assert after == dict(before, own_history=[]); changed += 1
            else: assert after == before
        assert queries == original and changed > 0
        bad = copy.deepcopy(queries)
        index = next(i for i,o in enumerate(bad['observations']) if int(o['hi']) in (1,response_hi))
        bad['observations'][index]['own_history'] = [[0,0,4]]
        try: first_action_view(bad, response_hi)
        except ValueError: pass
        else: raise AssertionError('False initial-action history accepted')
        cpu, cpu_coverage = probabilities(view, model, device='cpu', **pa)
        cuda, cuda_coverage = probabilities(view, model, device='cuda', **pa)
        error = float(np.max(abs(cpu-cuda)))
        assert cpu_coverage == cuda_coverage and error < 1e-10
        guard()
        for path, digest in inputs.items(): assert sha(path) == digest, path
        completed = dict(passed=True, registration_sha256=sha(old_rp), config=cfg,
            initial_checkpoint=initial_refs[0], final_checkpoint=second['checkpoint'], exact_restart_replay=True,
            interruption_stages=stages, maximum_cpu_gpu_policy_error=error, trained_generations=2,
            played_generations=[0,1], unplayed_excluded=second['next_model'],
            metrics=[dict(path=str(store/f'generation-{i+1:04d}/metrics.json'),
                sha256=sha(store/f'generation-{i+1:04d}/metrics.json'), seconds=m['seconds'], timings=m['timings'])
                for i,m in enumerate((first,second))],
            replay_metrics_sha256=sha(store/'generation-0002-replay/metrics.json'),
            seconds=failure['seconds']+time.monotonic()-began, seconds_this_recovery=time.monotonic()-began,
            observations_checked=len(cpu), annotated_initial_observations=changed,
            raw_transport_failure_reproduced=True, invalid_initial_history_rejected=True,
            completion_recovery_registration=str(rp), completion_recovery_registration_sha256=sha(rp),
            original_failure=str(old_failure), original_failure_sha256=sha(old_failure),
            gpu_used=True, accuracy_qualified=False, independent_readback_required=True,
            training_experiment_admitted=False, production_modified=False)
        atomic_json(result_path, completed)
        atomic_json(queue_result, dict(passed=True, registration_sha256=sha(old_queue_rp),
            stages=[*qf['completed'], dict(script='board_training_pipeline_control_v1.py', result=str(result_path),
                                         sha256=sha(result_path), completion_recovered=True)],
            recovery_registration=str(rp), recovery_registration_sha256=sha(rp),
            prior_resource_recovery_registration=str(resource_rp), prior_resource_recovery_registration_sha256=sha(resource_rp),
            original_failure=str(old_queue_failure), original_failure_sha256=sha(old_queue_failure),
            scientific_models_unchanged=True, production_modified=False))
        result = dict(passed=True, registration_sha256=sha(rp), completed_control=str(result_path),
            completed_control_sha256=sha(result_path), completed_queue=str(queue_result), completed_queue_sha256=sha(queue_result),
            maximum_cpu_gpu_policy_error=error, observations_checked=len(cpu), seconds=time.monotonic()-began,
            retraining=False, production_modified=False)
        atomic_json(OUT/f'{NAME}-result.json', result)
        print(json.dumps(result), flush=True)
    except BaseException as error:
        atomic_json(OUT/f'{NAME}-failure.json', dict(passed=False, registration_sha256=sha(rp), error=repr(error)))
        raise
    finally:
        if acquired:
            assert LOCK.read_text() == str(os.getpid()); LOCK.unlink()


if __name__ == '__main__': main()
