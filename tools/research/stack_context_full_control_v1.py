"""Bounded CPU/CUDA and context-routing control, with no scientific fitting."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np
import psutil
import torch

import stack_context_full_policy_v1 as full
import stack_context_policy_v1 as base
import stack_context_relative_policy_v1 as relative
from stack_context_inputs_v1 import Registry, digest
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from board_root_accumulator_v1 import BoardRootRegrets, TARGET, digest as document_hash
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_preflop_table_v1 import build as build_table
from sampled_physical_root_evaluation_v1 import hand_class
from test_stack_context_full_policy_v1 import FullContextPolicyTests as Retained
from river_matched_training_pilot_v1 import ROOT, OUT, available, LOCK, OTHER, sha, verify
from bounded_parallel_evaluation_archive_v2 import production_available
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create, measure
from global_research_inventory_v3 import measure as inventory

NAME = 'stack-context-full-control-v1'
STORE = Path('S:/GTOpen-research') / NAME
REG, ATTEMPT, RESULT, FAILURE = (OUT / (NAME + x + '.json') for x in
                                ('-registration', '-attempt', '-result', '-failure'))
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
QUERIES = Path('S:/GTOpen-research/stack-context-model-control-v1')
EXE = ROOT / 'target/release/examples/hu_preflop_visible_catalog_v1.exe'
DEPTHS = (20, 40, 60, 100, 150, 200, 400)
LIMIT = 64_000_000


def read(p):
    return json.loads(Path(p).read_bytes())


def specification():
    Retained.setUpClass()  # Read/pin the fixtures; do not run earlier CPU tests.
    paths = [Path(__file__).resolve(), OUT / 'STACK-CONTEXT-FULL-CONTROL-PLAN.md', EXE,
             ROOT / 'crates/solver/examples/hu_preflop_visible_catalog_v1.rs']
    geometry = read(OUT / 'stack-geometry-control-v1-result.json')
    query_proof = read(OUT / 'stack-context-model-control-v1-result.json')
    assert geometry['passed'] and query_proof['passed']
    paths += [OUT / 'stack-geometry-control-v1-result.json', OUT / 'stack-context-model-control-v1-result.json']
    entries = []
    for depth in DEPTHS:
        cp = GEOMETRY / 'fixtures' / f'stack-{depth}-context.json'
        pp = GEOMETRY / f'stack-{depth}-public.json'
        qp = QUERIES / f'stack-{depth}-queries.json'
        for p in (cp, pp):
            assert sha(p) == geometry['artifacts'][str(p)]
        assert sha(qp) == query_proof['artifacts'][str(qp)]
        paths += [cp, pp, qp]
        entries.append(dict(name=f'{depth}bb', split='heldout' if depth in (60,150) else 'fit',
                            context_source=cp.read_text(), public_document=read(pp)))
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix == '.py':
            paths.append(Path(p))
    inputs = dict(Retained.identities)
    inputs.update({str(p):sha(p) for p in paths})
    return dict(inputs=inputs, depths=list(DEPTHS), heldout=[60,150],
        input_widths=[362,387], maximum_seconds=600, maximum_cuda_bytes=512_000_000,
        maximum_new_bytes=LIMIT, reserve_bytes=16_000_000, policy_absolute_tolerance=1e-10,
        reach_absolute_tolerance=1e-10, synthetic_network_seed=9300101,
        native_catalog=True, synthetic_multi_context_accumulators=True,
        true_trained_multi_context_policy=False, scientific_training=False, new_poker_labels=False,
        production_modified=False), entries


def native_catalog(source, path, guard):
    guard()
    done = subprocess.run([str(EXE), str(path)], capture_output=True, timeout=30,
                          creationflags=subprocess.CREATE_NO_WINDOW)
    assert done.returncode == 0, done.stderr.decode(errors='replace')[-1000:]
    native = json.loads(done.stdout); assert native['context_source'] == source
    context = json.loads(source); root = context['nodes'][0]
    response = root['children'][3]
    chosen = {}; physical = {0:set(), response:set()}
    for row in native['rows']:
        node, hand = row['node'], row['hand']
        if node not in physical:
            continue
        physical[node].add(tuple(hand)); obs = row['observation']
        cls = hand_class(hand); actor = context['nodes'][node]['actor']
        assert (obs['actor'], obs['phase'], int(obs['hi'])) == (actor,0,node+1)
        key = (actor, cls)
        if key in chosen:
            assert chosen[key] == obs
        else:
            chosen[key] = obs
    assert all(len(v) == 1326 for v in physical.values()) and len(chosen) == 338
    result = dict(format=1, context_source=source, native_observations=[
        dict(player=a, hand_class=c, observation=dict(chosen[(a,c)], own_history=[]))
        for a,c in sorted(chosen)])
    return result, hashlib.sha256(done.stdout).hexdigest()


def synthetic_state(key, seed, action):
    """Sentinel state for routing only; its numbers are not poker payoffs."""
    mass = np.full(169, 1/169)
    matrix = digest('synthetic-control-matrix|' + key)
    root = BoardRootRegrets(context_sha256=key, matrix_sha256=matrix, entry_mass=mass,
                            physical_budget=169, boards_per_generation=1, board_seed=seed)
    exact = ExactBtnRegrets(key, mass)
    zero = (root.document(), exact.document())
    plan = root.plan(); played = np.full((169,4), .25)
    terms = np.zeros((169,4)); terms[:,action] = 1.
    empty = np.zeros((169,4)).tolist(); identity = digest('synthetic-control-only|' + key)
    evidence = dict(format=1, method=TARGET, generation=0, plan_sha256=document_hash(plan),
        context_sha256=key, matrix_sha256=matrix, model_sha256=identity,
        played_policy_sha256=document_hash(played.tolist()), exact_terms_sha256=document_hash(terms.tolist()),
        draws=[dict(draw_index=0, board=plan['boards'][0], model_sha256=identity,
                    tree_sha256=identity, policy_recipe_sha256=identity,
                    values=empty, values_sha256=document_hash(empty))])
    root.step(plan, evidence, played_policy=played, exact_terms=terms)
    # Alternate exact BTN sentinels across contexts as a separate routing signal.
    exact.step(1, np.full(169,.5), mass/2, np.zeros(169), mass*(.25 if action%2 else -.25))
    return root, exact, zero


def main():
    assert not any(p.exists() for p in (REG, ATTEMPT, RESULT, FAILURE, STORE, LOCK, OTHER))
    ready, admission = available()
    if not ready:
        print(json.dumps(dict(deferred=True, admission=admission))); return
    spec, entries = specification()
    with LOCK.open('x') as f:
        f.write(str(os.getpid()))
    began = time.monotonic()
    try:
        accounting = inventory()
        assert sum(r['allocated_file_bytes'] for r in accounting) + LIMIT + spec['reserve_bytes'] <= 800_000_000_000
        assert psutil.disk_usage('S:/').free > 40_000_000_000
        atomic_json(REG, spec); create(STORE)
        atomic_json(ATTEMPT, dict(pid=os.getpid(), process_created=psutil.Process().create_time(),
                                 registration_sha256=sha(REG), admission=admission))
        atomic_json(STORE / 'admission.json', accounting)
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(spec['maximum_cuda_bytes']/torch.cuda.get_device_properties(0).total_memory)
        def guard():
            assert time.monotonic()-began < spec['maximum_seconds']
            assert not OTHER.exists() and production_available()
            assert psutil.virtual_memory().available > 24_000_000_000
            assert psutil.disk_usage('S:/').free > 40_000_000_000
            assert torch.cuda.memory_reserved() < spec['maximum_cuda_bytes']

        records = []
        # CUDA implementation agrees with the already-tested retained CPU path.
        for fixture_index, fixture in enumerate(Retained.fixtures):
            for registry in Retained.registries:
                for old in fixture['originals']:
                    guard(); value = Retained.lift(old, registry, fixture['resources'])
                    cpu, _, coverage = full.predict(value, registry, fixture['queries'], context_sha256=Retained.key,
                                                    resources=fixture['resources'])
                    gpu, _, gcov = full.predict(value, registry, fixture['queries'], context_sha256=Retained.key,
                                                resources=fixture['resources'], device='cuda')
                    error = float(np.max(abs(cpu-gpu))); assert error <= spec['policy_absolute_tolerance'] and gcov == coverage
                    records.append(dict(kind='retained', fixture=fixture_index, width=registry.manifest['representation']['input_width'],
                                        generation=old['generation'], rows=len(cpu), maximum_error=error))
                models = [Retained.lift(m, registry, fixture['resources']) for m in fixture['originals'][:2]]
                args = dict(context_sha256=Retained.key, resources=fixture['resources'], weights_by_player=[[1.,2.],[3.,4.]], guard=guard)
                cpu, reach = full.average(models, registry, fixture['queries'], device='cpu', **args)
                gpu, greach = full.average(models, registry, fixture['queries'], device='cuda', **args)
                error = float(np.max(abs(cpu-gpu))); rerr = float(np.max(abs(reach-greach)))
                assert error <= spec['policy_absolute_tolerance'] and rerr <= spec['reach_absolute_tolerance']
                records.append(dict(kind='retained_average', fixture=fixture_index,
                    width=registry.manifest['representation']['input_width'], maximum_error=error, maximum_reach_error=rerr))

        resources = {}; states = {}; initial_states = {}; tables = {}; catalog_keys = {}
        for depth, entry in zip(DEPTHS, entries):
            if entry['split'] != 'fit':
                continue
            guard(); key = digest(entry['context_source'])
            catalog, rawsha = native_catalog(entry['context_source'], GEOMETRY/'fixtures'/f'stack-{depth}-context.json', guard)
            cp = STORE / f'stack-{depth}-catalog.json'; atomic_json(cp, catalog)
            root, exact, zero = synthetic_state(key, 9300101+depth, DEPTHS.index(depth)%4)
            args = dict(catalog_source=cp.read_text(), matrix_sha256=root.config['matrix_sha256'],
                        entry_mass=np.full(169,1/169), root_config=root.config)
            resources[key] = args
            states[key] = full.local_document(catalog_source=args['catalog_source'], matrix_sha256=args['matrix_sha256'],
                                             root_config=root.config, root=root, exact=exact)
            initial_states[key] = dict(states[key], board_root_state=zero[0], exact_btn_state=zero[1])
            tables[key] = []
            for actor in (0,1):
                observation = next(r['observation'] for r in catalog['native_observations'] if r['player']==actor)
                reservoir = WeightedPhysicalReservoir(2, actor, 0, entry['context_source'])
                reservoir.add(observation, [1.,0.,0.,0.], 1, deal_weight=1.)
                tables[key].append(build_table(reservoir, entry['context_source']))
            catalog_keys[key] = dict(path=str(cp), raw_native_sha256=rawsha)

        routing = []; negative = []
        for registry, api in ((Registry(entries),base), (RelativeRegistry(entries),relative)):
            width = api.SHAPES['w0'][1]
            rng = np.random.default_rng(spec['synthetic_network_seed'])
            nets = [{k:rng.normal(0,.03,int(np.prod(s))).astype(np.float32).tolist() for k,s in api.SHAPES.items()} for _ in (0,1)]
            for net in nets:
                net['b0']=[.2]*64; net['b1']=[.2]*64; net['b2']=[1.]*4
                if width==387:
                    w=np.asarray(net['w0']).reshape(64,387); w[0,362:371]=.5; net['w0']=w.reshape(-1).tolist()
            value = full.model(registry, api.model(registry,generation=1,networks=nets,preflop_tables=tables),states,resources)
            initial = full.model(registry,api.initial(registry),initial_states,resources)
            baseline_by_key = {}
            for depth, entry in zip(DEPTHS, entries):
                guard(); key=digest(entry['context_source']); q=read(QUERIES/f'stack-{depth}-queries.json')
                cpu, prepared, cov = full.predict(value,registry,q,context_sha256=key,resources=resources)
                gpu, _, gcov = full.predict(value,registry,q,context_sha256=key,resources=resources,device='cuda')
                error=float(np.max(abs(cpu-gpu))); assert error<=spec['policy_absolute_tolerance'] and cov==gcov
                if entry['split']=='heldout':
                    reference,_=api.predict(value['shared'],registry,q,context_sha256=key)
                    assert np.array_equal(cpu,reference) and not cov['learned_local_state']
                    assert cov['board_root_rows']==cov['exact_btn_rows']==0
                else:
                    ids=[i for i,o in enumerate(q['observations']) if o['hi']=='1']
                    assert ids and np.all(cpu[ids,DEPTHS.index(depth)%4]==1.)
                    assert cov['board_root_rows']>0 and cov['exact_btn_rows']>0
                args=dict(context_sha256=key,resources=resources,weights_by_player=[[1.,2.],[3.,4.]],guard=guard)
                mean,reach=full.average([initial,value],registry,q,device='cpu',**args)
                gmean,greach=full.average([initial,value],registry,q,device='cuda',**args)
                assert np.max(abs(mean-gmean))<=spec['policy_absolute_tolerance']
                assert np.max(abs(reach-greach))<=spec['reach_absolute_tolerance']
                baseline_by_key[key]=cpu
                path=STORE/f'{width}-{depth}-comparison.npz'
                with path.open('xb') as f:
                    np.savez_compressed(f,cpu=cpu,gpu=gpu,average_cpu=mean,average_gpu=gmean,reach_cpu=reach,reach_gpu=greach)
                routing.append(dict(width=width,stack=depth,split=entry['split'],rows=len(cpu),maximum_error=error,coverage=cov))
            # Alter one synthetic local root; no other fitting or held-out context may change.
            changed=copy.deepcopy(value); chosen=registry.fit_contexts[0]
            rootdoc=changed['local_states'][chosen]['board_root_state']; rootdoc['regret_sums']=np.tile([1.,2.,3.,4.],(169,1)).tolist()
            rootdoc.pop('state_sha256'); rootdoc['state_sha256']=document_hash(rootdoc)
            changed_here=0
            for depth,entry in zip(DEPTHS,entries):
                key=digest(entry['context_source']);q=read(QUERIES/f'stack-{depth}-queries.json')
                p,_,_=full.predict(changed,registry,q,context_sha256=key,resources=resources)
                if key==chosen:
                    changed_here=int(np.count_nonzero(np.any(p!=baseline_by_key[key],axis=1))); assert changed_here>0
                else:
                    assert np.array_equal(p,baseline_by_key[key])
            def reject(label,fn):
                try:fn()
                except (ValueError,KeyError):negative.append(dict(width=width,case=label))
                else:raise AssertionError('Accepted '+label)
            keys=list(registry.fit_contexts)
            swapped=copy.deepcopy(value);swapped['local_states'][keys[0]],swapped['local_states'][keys[1]]=swapped['local_states'][keys[1]],swapped['local_states'][keys[0]]
            reject('swapped_context_state',lambda:full.validate(swapped,registry,resources))
            absent=copy.deepcopy(value);del absent['local_states'][keys[0]]
            reject('missing_context_state',lambda:full.validate(absent,registry,resources))
            for depth,entry in zip(DEPTHS,entries):
                if entry['split']!='heldout':continue
                key=digest(entry['context_source']);bad=copy.deepcopy(value);bad['local_states'][key]=states[keys[0]]
                reject('heldout_local_state_'+str(depth),lambda bad=bad:full.validate(bad,registry,resources))
                reject('heldout_fit_'+str(depth),lambda depth=depth,key=key:registry.prepare(read(QUERIES/f'stack-{depth}-queries.json'),context_sha256=key,purpose='fit'))
            ref=full.write_model(STORE/'objects',value,registry,resources)
            assert full.read_model(STORE/'objects',ref,registry,resources)==value
            atomic_json(STORE/f'{width}-fixture.json',dict(model=value,registry=registry.manifest,
                resources={k:dict(v,entry_mass=v['entry_mass'].tolist()) for k,v in resources.items()},
                catalog_keys=catalog_keys,changed_context=chosen,changed_rows=changed_here))
        guard();verify(spec['inputs']);size=measure(STORE);assert size['logical_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),retained_checks=records,
            multi_context_checks=routing,negative_controls=negative,storage=size,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            seconds=time.monotonic()-began,peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            scientific_training=False,accuracy_qualified=False,training_checkpoint_qualified=False,
            scope='Retained policy CPU/CUDA equivalence plus synthetic local-state isolation in native seven-depth contexts.')
        atomic_json(RESULT,result)
        print(json.dumps(dict(passed=True,retained_checks=len(records),contexts=len(routing),seconds=result['seconds'],storage=size)))
    except BaseException as error:
        atomic_json(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),retry_allowed=False));raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    main()
