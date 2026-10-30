"""Small fresh-seed CUDA integration gate, including exact resumed replay.

This measures mechanics and overhead, not poker strength or convergence.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import copy
import json
from pathlib import Path
import sys
import time
import numpy as np
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_paired_continuation_support_20260925 import guard_for, launch, setup_cuda
from hu_action_integrated_exact_20260925 import bank_args
from showdown_root_training_v1 import initialize, save_state, update, first_action_view
from showdown_root_checkpoint_v1 import restore_checkpoint, model_document, require_config, CONFIG_KEY, POLICY_TYPE
from showdown_root_policy_v1 import probabilities
from showdown_root_targets_v1 import digest
from showdown_control_reference_v1 import score
from showdown_root_accumulator_v1 import ShowdownRootRegrets
import later_action_checkpoint_v1 as old_checkpoint

PREFIX = 'showdown-training-integration-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
COEFFICIENTS = OUT/'showdown-root-control-coefficients-v1.json'
UPDATE = ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
FULL = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
TRACE = ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe'
SCORE = ROOT/'target/release/examples/hu_board_outcomes_v1.exe'


def worker(reg):
    import torch
    setup_cuda(); guard = guard_for(reg); guard(); started = time.monotonic()
    cfg = reg['config']; coefs = read(COEFFICIENTS)
    assert cfg['torch_version'] == torch.__version__ and cfg['numpy_version'] == np.__version__
    assert digest(coefs) == cfg['control_coefficients_sha256']
    STORE.mkdir(exist_ok=False); objects = STORE/'objects'; objects.mkdir()
    cp = OUT/'bb-context-candidate.json'; args = bank_args(cp.read_text())
    cache = load_complete_cache()
    step = dict(context_path=cp, catalog_source=args['catalog_source'],
        matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(),
        matrix_sha256=args['matrix_sha256'], cache=cache, executable=UPDATE,
        integration_executable=FULL, trace_executable=TRACE, batch_prefix=PREFIX,
        guard=guard, coefficients=coefs, score_executable=SCORE)
    state = initialize(objects, cfg, **args); initial = save_state(objects, state, cfg, **args)
    rejected = []
    def reject(name, fn):
        try: fn()
        except ValueError: rejected.append(name)
        else: raise AssertionError('Accepted '+name)
    reject('missing coefficient binding', lambda: require_config({k:v for k,v in cfg.items() if k!='control_coefficients_sha256'}))
    doc = model_document(objects, state['next_model'], **args)
    reject('old model reader', lambda: old_checkpoint.inner_model(doc, **args))
    reject('old checkpoint reader', lambda: old_checkpoint.restore_checkpoint(objects, initial, config=cfg, **args))
    metrics = []; times = []; policy_error = 0.; target_error = 0.; scored = 0
    for iteration in (1,2):
        start = time.monotonic(); folder = STORE/f'iteration-{iteration:04d}'
        metric = update(folder, objects, state, cfg, **step)
        times.append(time.monotonic()-start); metrics.append(metric)
        part = folder/'batch-00'; raw = read(part/'queries.json')
        query = first_action_view(raw, json.loads(cp.read_text())['nodes'][0]['children'][3]+1)
        used = model_document(objects, metric['used_model'], **args)
        infer_args = {k:v for k,v in args.items() if k!='context_source'}
        cpu, _ = probabilities(query, used, device='cpu', **infer_args)
        gpu, _ = probabilities(query, used, device='cuda', **infer_args)
        played = np.array([r['probabilities'] for r in read(part/'policies.json')['policies']])
        policy_error = max(policy_error, float(np.max(abs(cpu-gpu))), float(np.max(abs(gpu-played))))
        assert policy_error < 1e-10
        batch = read(part/'batch.json'); native = read(part/'showdown-output.json')
        assert native['twice_bb_share'] == [score(d) for d in batch['deals']]
        scored += len(batch['deals'])
        original = read(part/'integrated-targets.json'); controlled = read(part/'showdown-targets.json')
        # Scalar check separate from the adapter, including all four advantages.
        for i,(before,after) in enumerate(zip(original['bb_root_corrections'], controlled['bb_root_corrections'])):
            count = batch['allin_counts'][i]
            x = native['twice_bb_share'][i]/2 - (count['wins']+count['ties']/2)/count['boards']
            c = before['hand_class']; expected = list(before['action_values'])
            for action in (1,2): expected[action] -= coefs['call_raise_coefficients'][c][action-1]*x
            assert after['action_values'] == expected
            center = sum(p*v for p,v in zip(played[before['query']], expected))
            target_error = max(target_error, max(abs(v-center-a) for v,a in zip(expected,after['advantages'])))
        assert target_error < 1e-10
        # An incomplete or foreign generation must leave the learner untouched.
        prior = ShowdownRootRegrets(digest_context(args['context_source']),
            args['matrix_sha256'], cfg['control_coefficients_sha256'])
        if iteration == 1:
            snapshot = prior.document()
            reject('incomplete generation', lambda: prior.step(1,[controlled],expected_deals=65,expected_batches=1))
            bad = copy.deepcopy(controlled); bad['identity']['control_coefficients_sha256'] = '0'*64
            reject('foreign coefficients', lambda: prior.step(1,[bad],expected_deals=64,expected_batches=1))
            assert prior.document() == snapshot
        assert state['root_regret_state'].counts.sum() == iteration*64
        print(json.dumps(dict(iteration=iteration,seconds=times[-1],root_samples=iteration*64)),flush=True)
    resumed = restore_checkpoint(objects, metrics[0]['checkpoint'], config=cfg, **args)
    replay = update(STORE/'replay-0002', objects, resumed, cfg, **step)
    assert replay['checkpoint'] == metrics[1]['checkpoint']
    assert resumed['next_model'] == state['next_model'] and resumed['played_bank'] == state['played_bank']
    assert resumed['root_regret_state'].document() == state['root_regret_state'].document()
    assert resumed['exact_btn_state'].document() == state['exact_btn_state'].document()
    assert resumed['action_rng'].bit_generator.state == state['action_rng'].bit_generator.state
    for a,b in zip(resumed['reservoirs'],state['reservoirs']):
        assert a.seen == b.seen and a.rng.bit_generator.state == b.rng.bit_generator.state
        for k in ('keys','active','arity','values','iterations'): assert np.array_equal(getattr(a,k),getattr(b,k))
    for path,h in reg['inputs'].items(): guard(); assert sha(path)==h,path
    artifacts = {str(p):sha(p) for p in STORE.rglob('*') if p.is_file()}
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,terminal=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        store=str(STORE),config=cfg,initial_checkpoint=initial,final_checkpoint=metrics[-1]['checkpoint'],
        completed_iterations=2,unique_training_deals=128,replayed_deals=64,steps=metrics,iteration_seconds=times,
        independent_showdown_scores=scored,maximum_policy_error=policy_error,maximum_target_error=target_error,
        exact_checkpoint_resume=True,rejections=rejected,artifacts=artifacts,
        logical_output_bytes=sum(Path(p).stat().st_size for p in artifacts),seconds=time.monotonic()-started,
        production_modified=False,accuracy_qualified=False,
        scope='Fresh-seed integration and deterministic restart control only. No convergence or strength claim.'))


def digest_context(source):
    import hashlib
    return hashlib.sha256(source.encode()).hexdigest()


if __name__ == '__main__':
    if sys.argv[1:] == ['--worker']: worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:] == ['--run']
        cfg = dict(read(OUT/'later-action-joint-control-v1-result.json')['config'],
            max_iterations=2,deals_per_iteration=64,subbatches_per_iteration=1,deals_per_subbatch=64,
            sampler_seed=9266101,action_seed=9266102,reservoir_seeds=[9266103,9266104],fit_seed_base=9266105,
            control_coefficients_sha256=digest(read(COEFFICIENTS)),
            showdown_root_targets='showdown-controlled-bb-root-targets-v1',**{CONFIG_KEY:POLICY_TYPE})
        launch(Path(__file__).resolve(), PREFIX,
            dict(extra_inputs=[str(p) for p in (COEFFICIENTS,UPDATE,FULL,TRACE,SCORE)],store=str(STORE),config=cfg,
                 scope='Two small fresh-seed training updates and exact replay; no effectiveness trial.'),
            cap=300_000_000, seconds=1800)
