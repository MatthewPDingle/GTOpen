"""Prepared read-only review of the completed full matched-stack comparison.

Does not sample new scientific hands, fit, select checkpoints, invoke a native
solve, mutate journals, or promote production. Default invocation reports
readiness. --run requires terminal successful evaluation and released owners.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import torch
import stack_context_full_policy_v1 as full
from stack_context_inputs_v1 import Registry, encoded
from stack_context_independent_chance_audit_v1 import load_cycle as audit_chance_cycle
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from stack_context_independent_audit_v1 import audit_comparison, audit_ranges, close, exact, require, DEPTHS, N, PROFILES
from stack_context_evaluation_journal_v1 import EvaluationJournal
from stack_context_matched_learning_v1 import resources_for
from sampled_allin_protocol_v3 import AllinCache
from sampled_visible_hybrid_checkpoint_v1 import read_object
from owned_columnar_evaluation_archive_v1 import ARTIFACTS, durable
from river_matched_training_pilot_v1 import LOCK, OTHER, production_available

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-matched-readback-v2'
EVAL = Path('S:/GTOpen-research/stack-context-matched-evaluation-v2')
TRAIN = Path('S:/GTOpen-research/stack-context-matched-learning-v1')
REG = OUT/'stack-context-matched-evaluation-v2-registration.json'
RESULT = OUT/'stack-context-matched-evaluation-v2-result.json'
FAILURE = OUT/'stack-context-matched-evaluation-v2-failure.json'
TRAIN_REG = OUT/'stack-context-matched-learning-v1-registration.json'
TRAIN_RESULT = OUT/'stack-context-parallel-continuation-v2-training-result.json'
TRAIN_FAILURE = OUT/'stack-context-parallel-continuation-v2-failure.json'
ORIGINAL_FAILURE = OUT/'stack-context-matched-learning-v1-failure.json'
AMENDMENT = OUT/'stack-context-parallel-continuation-v2-amendment.json'
DIAGNOSIS = OUT/'stack-context-paired-chance-readback-v1-result.json'
PARALLEL_CONTROL = OUT/'stack-context-parallel-continuation-v2-check-result.json'
ATTEMPT, OUTPUT, FAILED = (OUT/(NAME+s+'.json') for s in ('-attempt', '-result', '-failure'))
PLAN = OUT/'STACK-CONTEXT-MATCHED-READBACK-V2-PLAN.md'
CONTROL = OUT/'stack-context-matched-readback-check-v2-result.json'
AUDIT_CONTROL = OUT/'stack-context-independent-audit-check-v1-result.json'
ARMS = ('A-baseline', 'A-relative', 'B-baseline', 'B-relative')
REPLAY_STARTS = (0, 4064)  # Prespecified first and last 32-deal batches at every depth.


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(inputs):
    for path, identity in inputs.items():
        require(sha(path) == identity, 'Changed registered input: '+str(path))


def readiness():
    return dict(evaluation_result_present=RESULT.exists(), evaluation_failure_present=FAILURE.exists(),
        training_failure_present=TRAIN_FAILURE.exists(), research_owner_present=LOCK.exists() or OTHER.exists(),
        audit_check_present=AUDIT_CONTROL.exists(), reader_check_present=CONTROL.exists(),
        readback_started=ATTEMPT.exists(), readback_complete=OUTPUT.exists(), readback_failure=FAILED.exists())


def validate_transport(parts, cache):
    """Authenticate labels, query-to-policy rows, all crossings and original bank hashes.

File/byte and native-value/summary authentication belongs to the journal reader
and is required before this function. The original four self-profile banks can
be recovered exactly without running any model.
"""
    require(set(parts) == ARTIFACTS, 'Missing native artifact')
    query = json.loads(parts['queries.json']); transport = json.loads(parts['profiles.json'])
    summary = json.loads(parts['summary.json']); conditional = json.loads(parts['conditional-batch.json'])
    raw = json.loads(parts['query-batch.json'])
    cache.check_batch(conditional)
    require(query['batch_source'] == parts['query-batch.json'].decode()
        and transport['batch_source'] == parts['conditional-batch.json'].decode()
        and query['context_source'] == transport['context_source'], 'Changed visible/labelled source binding')
    require(raw['format'] == 2 and not any(k.startswith('allin_') or k == 'terminal_estimator' for k in raw),
        'Hidden all-in labels in visible query batch')
    for cards in raw['deals']:
        require(len(cards) == 9 and len(set(cards)) == 9 and all(type(c) is int and 0 <= c < 52 for c in cards),
                'Invalid shared physical deal')
        require(cards[:2] == sorted(cards[:2]) and cards[2:4] == sorted(cards[2:4])
                and cards[4:7] == sorted(cards[4:7]), 'Physical deal ordering changed')
    obs = query['observations']; profiles = transport['profiles']
    require(len(profiles) == 8 and [r['name'] for r in profiles] == list(PROFILES), 'Changed crossed profile order')
    arity = np.array([r['n'] for r in obs]); actor = np.array([r['actor'] for r in obs])
    require(len(obs) > 0 and np.all((arity >= 1) & (arity <= 4)) and np.all((actor == 0) | (actor == 1)),
            'Invalid query menu or actor')
    arrays = []
    for profile in profiles:
        require(len(profile['policies']) == len(obs), 'Incomplete policy transport')
        for row, observation in zip(profile['policies'], obs):
            require(set(row) == {'hi', 'lo', 'actor', 'n', 'probabilities'} and
                    all(row[k] == observation[k] for k in ('hi', 'lo', 'actor', 'n')), 'Policy row/key substitution')
        p = np.asarray([r['probabilities'] for r in profile['policies']], dtype=np.float64)
        require(p.shape == (len(obs), 4) and np.isfinite(p).all() and np.all(p >= 0), 'Invalid transported probabilities')
        close(p.sum(axis=1), np.ones(len(obs)), 'Transport normalization', atol=1e-12, rtol=0)
        require(np.all(p[np.arange(4)[None, :] >= arity[:, None]] == 0), 'Illegal transported action')
        arrays.append(p)
    banks = [arrays[i] for i in (0, 3, 4, 7)]
    require(len(summary['coverage']) == 4, 'Incomplete bank coverage')
    for bank, proof in zip(banks, summary['coverage']):
        require(hashlib.sha256(bank.tobytes()).hexdigest() == proof['probabilities_sha256'], 'Original bank bytes changed')
        require(type(proof['zero_reach_rows']) is int and 0 <= proof['zero_reach_rows'] <= len(obs), 'Invalid support count')
    for seed in range(2):
        for pairing, (bb, btn) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
            expected = np.where(actor[:, None] == 0, banks[2*seed+bb], banks[2*seed+btn])
            require(np.array_equal(expected, arrays[4*seed+pairing]), 'Incorrect actor or seed crossing')
    return query, banks, summary


def check_reference_policies(query, stored, summary, reference_functions, *, guard):
    require(len(reference_functions) == len(stored) == 4, 'Four full reference banks required')
    rows = []
    for arm, reference, expected, coverage in zip(ARMS, reference_functions, stored, summary['coverage']):
        guard(); p, support = reference(query, guard=guard)
        error = close(p, expected, arm+' complete reference policy', atol=1e-10, rtol=0)
        support = np.asarray(support, dtype=np.float64)
        require(support.shape == (len(p),) and np.isfinite(support).all() and np.all(support >= 0), 'Invalid reference own reach')
        require(int(np.count_nonzero(support == 0)) == coverage['zero_reach_rows'], 'Reference reach support differs')
        rows.append(dict(arm=arm, maximum_policy_error=error, zero_reach_rows=int(np.count_nonzero(support == 0)),
            support_byte_hash_matches=hashlib.sha256(support.tobytes()).hexdigest() == coverage['support_sha256']))
    return rows


def catalog_queries(source, catalog):
    """Rebuild ancestor links directly from tree geometry for the full range replay."""
    context = json.loads(source)
    require(catalog['context_source'] == source, 'Range replay catalog identity')
    observations = [copy.deepcopy(r['observation']) for r in catalog['rows']]
    lookup = {(r['node'], tuple(r['hand'])):i for i, r in enumerate(catalog['rows'])}
    require(len(lookup) == len(observations), 'Duplicate physical catalog row')
    paths = {}; pending = [(0, [])]; visited = set()
    while pending:
        node, path = pending.pop()
        require(node not in visited, 'Shared/cyclic catalog tree')
        visited.add(node); native = context['nodes'][node]
        if native['children']:
            paths[node] = path
            pending.extend((child, path+[(node, action)]) for action, child in enumerate(native['children']))
    for row, observation in zip(catalog['rows'], observations):
        observation['own_history'] = [[lookup[(ancestor, tuple(row['hand']))], action,
            len(context['nodes'][ancestor]['children'])] for ancestor, action in paths[row['node']]
            if context['nodes'][ancestor]['actor'] == observation['actor']]
    return dict(context_source=source, observations=observations)


def bind_range_policy(context, catalog, export, probability, support):
    probability = np.asarray(probability); support = np.asarray(support)
    require(probability.shape == (len(catalog['rows']), 4) and support.shape == (len(probability),), 'Full physical replay required')
    bynode = {r['node']:r for r in export['nodes']}; errors = []; reaches = []
    seen = {}
    for i, row in enumerate(catalog['rows']):
        a, b = row['hand']; lo, hi = sorted((a//4, b//4))
        cls = hi*13+lo if a%4 == b%4 else lo*13+hi
        node = row['node']; arity = len(context['nodes'][node]['children'])
        require(node in bynode and all(0 <= c < 52 for c in (a, b)) and a < b, 'Range replay private holding')
        seen.setdefault(node, set()).add((a, b))
        expected = bynode[node]['action_probabilities_by_class'][cls]+[0.]*(4-arity)
        errors.append(close(probability[i], expected, 'Range model-policy binding', atol=1e-10, rtol=0))
        reaches.append(close(support[i], bynode[node]['own_history_weighted_model_support_by_class'][cls],
                             'Range model-reach binding', atol=1e-8, rtol=0))
    require(set(seen) == set(bynode) and all(len(v) == 1326 for v in seen.values()), 'Incomplete full private holding replay')
    return dict(physical_rows=len(probability), maximum_policy_error=max(errors), maximum_own_reach_error=max(reaches))


def verify_correction(train_result, selection):
    failure,amendment,diagnosis,control=(read(p) for p in (ORIGINAL_FAILURE,AMENDMENT,DIAGNOSIS,PARALLEL_CONTROL))
    require(failure['error']=="ValueError('Matched representations did not use identical physical/action/board streams')"
        and diagnosis['complete'] and diagnosis['passed'] and diagnosis['false_positive_parent_state_comparison']
        and not diagnosis['actual_chance_mismatch'] and diagnosis['inputs'][str(ORIGINAL_FAILURE)]==sha(ORIGINAL_FAILURE),
        'Original failure is not the independently diagnosed matching false positive')
    require(amendment['original_registration_sha256']==sha(TRAIN_REG)
        and amendment['original_failure_sha256']==sha(ORIGINAL_FAILURE) and amendment['diagnosis_sha256']==sha(DIAGNOSIS)
        and amendment['check_sha256']==sha(PARALLEL_CONTROL) and control['complete'] and control['passed']
        and amendment['runner_sha256']==control['runner_sha256']==sha(ROOT/'tools/research/stack_context_parallel_continuation_v2.py')
        and amendment['failed_evidence_preserved'] and not amendment['scientific_cycles_retried']
        and amendment['seeds_models_targets_fits_unchanged'] and amendment['cycles_per_arm']==64
        and amendment['original_deadline_unchanged'] and amendment['evaluation_gates_unchanged'],
        'Continuation correction differs from its qualified record')
    require(train_result['continuation_amendment_sha256']==selection['continuation_amendment_sha256']==sha(AMENDMENT)
        and train_result['original_failure_sha256']==selection['original_failure_sha256']==sha(ORIGINAL_FAILURE)
        and selection['raw_source_hashes_preserved'] and selection['board_plans_validated_against_own_parents'],
        'Terminal outcome/selection detached from preserved correction')
    verify(control['inputs'])


def load_banks(spec, terminal, prepared, *, guard):
    """Independently inspect the entire 64-cycle checkpoint/model boundary."""
    training = read(TRAIN_REG); train_result = read(TRAIN_RESULT)
    require(train_result['training_complete'] is True and train_result['registration_sha256'] == sha(TRAIN_REG),
            'Training did not finish this registration')
    selection = spec['banks']['selection']
    verify_correction(train_result,selection)
    require(selection['bank_order'] == list(ARMS) and selection['selection_uses_test_results'] is False,
            'Changed model selection')
    require(spec['banks']['training_result_sha256'] == sha(TRAIN_RESULT) and
            spec['banks']['training_registration_sha256'] == sha(TRAIN_REG), 'Training evidence identity changed')
    entries = read('S:/GTOpen-research/stack-context-population-v1/entries.json')
    loaded = {}; provenance = []; matched = {}
    for arm in ARMS:
        guard(); chosen = selection['arms'][arm]; progress = train_result['arms'][arm]
        require(read(TRAIN/arm/'progress.json') == progress and progress['completed_cycles'] == 64,
                'Unfinished or changed actual training progress')
        require(progress['checkpoint'] == chosen['checkpoint'] and chosen['completed_cycles'] == 64 and
                chosen['weights_by_player'] == [list(range(1, 65))]*2 and
                [r['generation'] for r in chosen['played']] == list(range(64)) and
                chosen['excluded_unplayed']['generation'] == 64, 'Wrong played model set or weights')
        all_refs = chosen['played']+[chosen['excluded_unplayed']]
        require(len({r['sha256'] for r in all_refs}) == 65, 'Repeated model identity')
        require(len(progress['updates']) == 64 and [u['cycle'] for u in progress['updates']] == list(range(1, 65)),
                'Incomplete checkpoint trajectory')
        registry = (RelativeRegistry if arm.endswith('relative') else Registry)(entries)
        resources, _, _ = resources_for(registry, prepared, 0 if arm.startswith('A-') else 1)
        require(registry.sha256 == chosen['registry_sha256'], 'Actual runtime registry changed')
        for cycle, update in enumerate(progress['updates'], 1):
            guard(); checkpoint = json.loads(read_object(TRAIN/arm/'objects', update['checkpoint']))
            require(checkpoint['completed_cycles'] == cycle and checkpoint['played_bank'] == all_refs[:cycle]
                    and checkpoint['next_model'] == all_refs[cycle]
                    and checkpoint['config'] == training['arms'][arm]['config']
                    and checkpoint['registry'] == registry.manifest, 'Changed played trajectory or configuration')
        documents = []
        for generation, ref in enumerate(all_refs):
            guard()
            require(ref['file'] == 'fullstackmodel-'+ref['sha256']+'.json' and ref['generation'] == generation,
                    'Model immutable name/generation changed')
            value = full.read_model(TRAIN/arm/'objects', ref, registry, resources)
            if generation < 64:documents.append(value)
        require(len(registry.fit_contexts) == 5 and sorted(registry._get(k)['context']['config']['stack']
                for k in registry.fit_contexts) == [20, 40, 100, 200, 400], 'Held-out stack in fit state')
        require(chosen['matched_streams_by_cycle']==[r['paired_sources'] for r in progress['updates']]
            and len(chosen['chance_receipts'])==64 and len(chosen['matched_chance_by_cycle'])==64,
            'Original raw matching evidence or new chance receipts missing')
        matched[arm]=[]
        for cycle,update in enumerate(progress['updates'],1):
            reconstructed=audit_chance_cycle(TRAIN,arm,cycle,update,chosen['chance_receipts'][cycle-1],
                chosen['played'][cycle-1],documents[cycle-1],training['arms'][arm]['config'],
                registration=sha(TRAIN_REG),comparator=sha(ROOT/'tools/research/stack_context_paired_chance_v1.py'),
                amendment=sha(AMENDMENT),guard=guard)
            require(reconstructed==chosen['matched_chance_by_cycle'][cycle-1], 'Selected chance differs from independent reconstruction')
            matched[arm].append(reconstructed)
        loaded[arm] = dict(documents=documents, registry=registry, resources=resources,
                          weights=chosen['weights_by_player'])
        provenance.append(dict(arm=arm, checked_checkpoints=64, played_models=64, excluded_unplayed_generation=64,
                               authenticated_model_files=65, independent_chance_cycles=64, registry_sha256=registry.sha256))
    for seed in ('A','B'):
        require(matched[seed+'-baseline']==matched[seed+'-relative'], 'Independently reconstructed chance differs between arms')
    return loaded, provenance


def reference_function(bank, key):
    def reference(query, *, guard):
        return full.average(bank['documents'], bank['registry'], query, context_sha256=key,
            resources=bank['resources'], weights_by_player=bank['weights'], device='cpu', guard=guard)
    return reference


def review(spec, terminal, *, guard):
    require(terminal['fixed_policy_evaluation_complete'] is True and terminal['registration_sha256'] == sha(REG)
            and terminal['accuracy_qualified'] is False and terminal['production_modified'] is False,
            'Terminal evaluation contract changed')
    require(spec['depths'] == list(DEPTHS) and spec['deals_per_depth'] == N and spec['batch_size'] == 32
            and spec['alpha_per_depth'] == .05/7 and spec['one_final_look'] is True
            and spec['seed_by_depth'] == {str(d):9309000+d for d in DEPTHS}, 'Changed prospective test design')
    require(read(EVAL/'bank-identities.json') == spec['banks'] and
            sha(EVAL/'bank-identities.json') == terminal['bank_identities_sha256'], 'Bank identity changed')
    prepared = read(OUT/'stack-context-population-v1-result.json'); verify(prepared['artifacts'])
    loaded, provenance = load_banks(spec, terminal, prepared, guard=guard)
    cache = AllinCache(spec['cache_artifact'], spec['cache_sha256'])
    all_values = {}; context_records = []; observed_exports = {}
    for depth in DEPTHS:
        guard(); record = next(r for r in prepared['contexts'].values() if r['depth'] == depth)
        key = record['context_sha256']; source = Path(record['context_path']).read_text(); context = json.loads(source)
        folder = EVAL/f'stack-{depth}'
        journal = EvaluationJournal(folder, context_source=source, registration_sha256=sha(REG),
            bank_identities_sha256=terminal['bank_identities_sha256'], cache_sha256=cache.sha256, guard=guard)
        # Replay the durable chance/commit chain, then restore and inspect every
        # archived batch once below. No begin/recover/release operation is used.
        prefix = journal.prefix(verify_archives=False)
        require(prefix['completed_deals'] == N and terminal['journals'][str(depth)] == dict(
            journal_owner_sha256=journal.owner, last_commit_sha256=prefix['previous_commit_sha256'], completed_deals=N),
            'Terminal journal does not bind the complete final prefix')
        reference = [reference_function(loaded[arm], key) for arm in ARMS]
        replays = []; batches = 0
        for path in sorted(folder.glob('commit-*.json')):
            guard(); committed = read(path); start = committed['completed_deals']-32
            intent = read(folder/'intents'/f'test-{start:06d}.json')
            parts = journal._proof(f'test-{start:06d}', committed['manifest_sha256'], committed['summary_sha256'], full=True)
            summary = journal._evidence(parts, intent)
            require(committed['values'] == summary['values'], 'Original native values differ from committed values')
            query, stored, summary = validate_transport(parts, cache)
            if start in REPLAY_STARTS:
                replays.append(dict(start=start, arms=check_reference_policies(query, stored, summary, reference, guard=guard)))
            batches += 1
        require(batches == 128 and [r['start'] for r in replays] == list(REPLAY_STARTS), 'Incomplete archive or prespecified replay')
        all_values[depth] = prefix['values']; range_records = []
        catalog = read(record['physical_catalog']); query = catalog_queries(source, catalog)
        for arm, reference in zip(ARMS, reference):
            guard(); path = folder/(arm+'-preflop-ranges.json'); digest = sha(path)
            require(terminal['range_exports'].get(str(path)) == digest, 'Unbound range export')
            value = read(path)
            require(value['arm'] == arm and value['context_sha256'] == key
                    and value['bank_identities_sha256'] == terminal['bank_identities_sha256'], 'Range identity differs')
            physical = audit_ranges(context, value['range_export'], guard=guard)
            p, support = reference(query, guard=guard)
            policy = bind_range_policy(context, catalog, value['range_export'], p, support)
            range_records.append(dict(arm=arm, physical=physical, model_binding=policy))
            observed_exports[str(path)] = digest
        context_records.append(dict(depth=depth, complete_archives=batches, replayed_test_deals=N,
            native_values_bound_to_sources=True, allin_labels_verified=True, all_crossed_profiles_verified=True,
            reference_policy_batch_replays=replays, ranges=range_records))
        print(json.dumps(dict(stage='depth-reviewed', depth=depth, archives=batches)), flush=True)
    require(observed_exports == terminal['range_exports'], 'Missing or unexpected range export')
    arithmetic = audit_comparison(terminal['comparison'], all_values)
    return dict(complete=True, passed=True, independent_readback_complete=True, provenance=provenance,
        contexts=context_records, arithmetic=arithmetic, reference_policy_replay_batches=14,
        reference_complete_preflop_range_replays=28, original_archive_batches=896,
        training_heldout_stack_separation_verified=True, independent_chance_cycles=256, original_failure_preserved=True,
        strictly_board_disjoint_test=False,
        test_chance='Independent registered full-deck physical draws; collisions with training are not filtered',
        policy_replay_scope='Complete preflop catalogs and first/last 32-deal test batches at every depth; not every postflop policy row',
        native_payoff_oracle_independent=False, prediction_diagnostic_complete=False,
        preflop_accuracy_qualified=False, production_modified=False, new_scientific_deals=False,
        fitting=False, native_execution=False, gpu_used=False)


def main(run=False):
    if not run:
        print(json.dumps(dict(prepared_reader=True, **readiness()))); return
    require(not any(p.exists() for p in (LOCK, OTHER, ATTEMPT, OUTPUT, FAILED, FAILURE, TRAIN_FAILURE)),
            'Live owner, prior readback attempt or failed scientific work; do not duplicate/retry')
    require(RESULT.exists() and TRAIN_RESULT.exists(), 'Definitive successful training and evaluation required')
    control, audit = read(CONTROL), read(AUDIT_CONTROL)
    require(control['complete'] and control['passed'] and control['reader_sha256'] == sha(__file__)
            and audit['complete'] and audit['passed'], 'Current reader/audit implementation checks required')
    verify(control['inputs']); verify(audit['inputs'])
    spec, terminal = read(REG), read(RESULT)
    verify(spec['inputs']); verify(read(TRAIN_REG)['inputs'])
    require(production_available() and psutil.virtual_memory().available >= 28_000_000_000, 'Yield to current work or memory pressure')
    inputs = {str(p):sha(p) for p in (REG, RESULT, TRAIN_REG, TRAIN_RESULT, ORIGINAL_FAILURE, AMENDMENT, DIAGNOSIS, PARALLEL_CONTROL, CONTROL, AUDIT_CONTROL, PLAN, Path(__file__).resolve())}
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix == '.py': inputs[str(Path(p))] = sha(p)
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    started = time.monotonic()
    try:
        durable(ATTEMPT, encoded(dict(inputs=inputs, pid=os.getpid(), process_created=psutil.Process().create_time(),
            maximum_seconds=12*3600, torch_threads=4, new_scientific_work=False, test_batch_starts=list(REPLAY_STARTS))))
        torch.set_num_threads(4); torch.use_deterministic_algorithms(True)
        last = [0.]
        def guard():
            now = time.monotonic()
            if now-last[0] > 2:
                require(now-started < 12*3600 and psutil.virtual_memory().available >= 24_000_000_000
                    and production_available() and not OTHER.exists(), 'Readback resource/time boundary; preserve evidence')
                last[0] = now
        result = review(spec, terminal, guard=guard)
        verify(inputs); verify(spec['inputs']); verify(read(TRAIN_REG)['inputs'])
        result.update(seconds=time.monotonic()-started, inputs=inputs, evaluation_result_sha256=sha(RESULT),
                      evaluation_registration_sha256=sha(REG))
        durable(OUTPUT, encoded(result))
        print(json.dumps(dict(passed=True, seconds=result['seconds'], independent_readback_complete=True)))
    except BaseException as error:
        if ATTEMPT.exists():durable(FAILED, encoded(dict(error=repr(error), traceback=traceback.format_exc(),
            preserve_evidence=True, automatic_retry_allowed=False)))
        raise
    finally:
        if LOCK.exists() and LOCK.read_text() == str(os.getpid()):LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--run', action='store_true')
    main(run=parser.parse_args().run)
