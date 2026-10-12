"""Prospective bounded native batch for the full ExpectedPolicy comparison.

Caller owns scientific registration, source pins, resource admission and the
fresh sampler. This module neither draws deals nor admits/starts a study.
It uses the existing native query and conditional-allin complete evaluator.
All legal actions remain integrated; no root action is forced or omitted.
"""
import hashlib
import json
from pathlib import Path
import time
import numpy as np

from preflop_expected_payoff_bank_v1 import FixedExpectedBank
from preflop_expected_payoff_comparison_v2 import profiles, PROFILE_NAMES

MAX_JSON_BYTES = 64_000_000
MAX_NATIVE_OUTPUT_BYTES = 64_000_000


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_read(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError('Native JSON exceeds the declared in-memory input bound')
    return raw


def read_witness(path, witness):
    raw = bounded_read(path)
    if (not isinstance(witness, dict) or witness.get('path') != str(Path(path).resolve())
            or witness.get('exists') is not True or type(witness.get('bytes')) is not int
            or len(raw) != witness['bytes'] or digest(raw) != witness.get('sha256')):
        raise ValueError('Parsed bytes differ from the verified direct native output witness')
    return raw


def checked_native_values(native, *, deal_count, stack, dead_money):
    """Validate complete ordered per-deal cashflow before returning any values."""
    if (type(deal_count) is not int or not 1 <= deal_count <= 64
            or type(stack) not in (int, float) or not np.isfinite(stack) or stack <= 0
            or type(dead_money) not in (int, float) or not np.isfinite(dead_money) or dead_money < 0):
        raise ValueError('Declared physical batch and payoff bounds required')
    if (native.get('format') != 2 or type(native.get('format')) is not int
            or native.get('terminal_estimator') != 'conditional-preflop-allin-v1'
            or native.get('postflop_outcomes') != 'sampled-board'
            or native.get('fixed_policy_evaluation_only') is not True
            or native.get('bounds_best_response_above') is not False
            or not isinstance(native.get('profiles'), list)
            or [p.get('name') for p in native['profiles']] != list(PROFILE_NAMES)):
        raise ValueError('Unexpected native estimator, fixed-policy scope or profile order')
    for name in ('maximum_forward_cashflow_error', 'maximum_conservation_error'):
        value = native.get(name)
        if type(value) not in (int, float) or not 0 <= value < 1e-10:
            raise ValueError('Missing successful native independent cashflow check')
    flat = []
    for profile in native['profiles']:
        rows = profile.get('deals')
        if (not isinstance(rows, list) or len(rows) != deal_count
                or any(type(row.get('deal_index')) is not int or row['deal_index'] != i
                       for i, row in enumerate(rows))):
            raise ValueError('All profiles must retain the same complete ordered physical batch')
        player_values = []
        for row in rows:
            mass, rake = row.get('terminal_mass'), row.get('expected_rake')
            if (not isinstance(row.get('values'), list) or len(row['values']) != 2
                    or any(type(value) not in (int, float) for value in row['values'])):
                raise ValueError('Two numeric player payoffs required')
            pair = np.asarray(row.get('values'), dtype=np.float64)
            if (pair.shape != (2,) or not np.isfinite(pair).all()
                    or np.any(pair < -stack) or np.any(pair > stack + dead_money)
                    or type(mass) not in (int, float) or not np.isfinite(mass) or abs(mass-1.) >= 1e-10
                    or type(rake) not in (int, float) or not np.isfinite(rake) or rake < 0
                    or abs(float(pair.sum()) + rake - dead_money) >= 1e-10):
                raise ValueError('Per-deal terminal mass, payoff bounds or pot conservation failed')
            player_values.append(pair)
        flat.append(player_values)
    return np.asarray(flat, dtype=np.float64).transpose(1, 0, 2).reshape(deal_count, 2, 4, 2)


def evaluate_batch(*, batch, folder, context_path, banks, cache, query_executable,
                   evaluation_executable, expected_identities, run_native,
                   verify_native, write, guard, native_timeout_seconds):
    """Registered caller supplies bounded IO callbacks; fresh paths only."""
    if (not isinstance(batch, dict) or type(batch.get('format')) is not int or batch['format'] != 2
            or not isinstance(batch.get('deals'), list) or not 1 <= len(batch['deals']) <= 64
            or any(key.startswith('allin_') or key == 'terminal_estimator' for key in batch)
            or type(batch.get('query_limit')) is not int or not 0 < batch['query_limit'] <= 1_000_000
            or type(native_timeout_seconds) not in (int, float) or not 0 < native_timeout_seconds <= 120
            or len(banks) != 4 or any(not isinstance(bank, FixedExpectedBank) for bank in banks)):
        raise ValueError('Bounded unlabelled physical batch and four fixed complete ExpectedPolicy banks required')
    for deal in batch['deals']:
        if (not isinstance(deal, list) or len(deal) != 9 or len(set(deal)) != 9
                or any(type(card) is not int or not 0 <= card < 52 for card in deal)):
            raise ValueError('Nine distinct physical cards required')
    context_path = Path(context_path).resolve()
    context_raw = bounded_read(context_path); context_source = context_raw.decode('utf-8')
    context = json.loads(context_raw)
    if (any(bank.context_source != context_source for bank in banks)
            or any(bank.context_sha256 != digest(context_raw) for bank in banks)):
        raise ValueError('All four frozen banks must refer to the actual same context bytes')
    native_pins = dict(expected_identities)
    for path in (context_path, Path(query_executable).resolve(), Path(evaluation_executable).resolve()):
        if str(path) not in native_pins:
            raise ValueError('Context and both native executables need registered identities')
    if native_pins[str(context_path)] != digest(context_raw):
        raise ValueError('Actual context differs from registration')
    guard(); folder = Path(folder).resolve(); folder.mkdir(exist_ok=False)
    raw_path, labelled_path = folder/'query-batch.json', folder/'conditional-batch.json'
    query_path, transport_path, native_path = folder/'queries.json', folder/'profiles.json', folder/'native.json'
    labelled = cache.batch(batch); cache.check_batch(labelled)
    write(raw_path, batch); write(labelled_path, labelled)
    raw = bounded_read(raw_path); labelled_raw = bounded_read(labelled_path)
    if json.loads(raw) != batch or json.loads(labelled_raw) != labelled:
        raise ValueError('Written physical source differs from the supplied common batch')
    invocations = []

    def invoke(executable, arguments, output, input_paths, label):
        pins = dict(native_pins)
        for path in input_paths:
            pins[str(path.resolve())] = digest(bounded_read(path))
        specs = [dict(path=str(output), argument_index=len(arguments))]
        guard(); started = time.monotonic()
        result = run_native(executable, arguments, folder=folder, label=label,
                            expected_identities=pins, guard=guard, timeout=native_timeout_seconds,
                            max_output_bytes=MAX_NATIVE_OUTPUT_BYTES, stdin_path=None, direct_outputs=specs)
        verify_native(result, executable=executable, arguments=arguments, expected_identities=pins,
                      timeout=native_timeout_seconds, max_output_bytes=MAX_NATIVE_OUTPUT_BYTES,
                      stdin_path=None, direct_outputs=specs)
        witnesses = result['receipt']['direct_output_artifacts']
        if (len(witnesses) != 1 or witnesses[0].get('path') != str(output)
                or witnesses[0].get('argument_index') != len(arguments)):
            raise ValueError('Native receipt lacks the exact requested output role')
        witness = dict(witnesses[0])
        invocations.append(dict(executable=str(Path(executable).resolve()), arguments=arguments,
                                expected_identities=pins, result=result))
        guard()
        return time.monotonic()-started, witness

    query_seconds, query_witness = invoke(query_executable,
        ['queries', str(context_path), str(raw_path), '-', str(query_path)], query_path,
        [raw_path], 'payoff-query')
    query_raw = read_witness(query_path, query_witness); query = json.loads(query_raw)
    if (query.get('format') != 2 or query.get('context_source') != context_source
            or query.get('batch_source') != raw.decode('utf-8')):
        raise ValueError('Native visible queries must retain exact unlabelled source identities')
    policies, coverage, timings = [], [], []
    for bank in banks:
        guard(); started = time.monotonic(); p, support = bank.average(query, guard=guard)
        timings.append(time.monotonic()-started)
        p = np.asarray(p, dtype=np.float64); support = np.asarray(support, dtype=np.float64)
        if (support.shape != (len(query['observations']),) or not np.isfinite(support).all()
                or np.any(support < 0)):
            raise ValueError('Invalid exact own-action support')
        policies.append(p)
        coverage.append(dict(bank=bank.identity(), probabilities_sha256=digest(p.tobytes()),
                             support_sha256=digest(support.tobytes()), zero_reach_rows=int(np.sum(support == 0))))
    crossed = profiles(query, policies)
    transport_document = dict(format=1, context_source=context_source,
                              batch_source=labelled_raw.decode('utf-8'), profiles=crossed)
    write(transport_path, transport_document)
    transport_raw = bounded_read(transport_path)
    if json.loads(transport_raw) != transport_document:
        raise ValueError('Written transport differs from the complete crossed policies')
    native_seconds, native_witness = invoke(evaluation_executable,
        [str(context_path), str(labelled_path), str(transport_path), str(native_path)], native_path,
        [labelled_path, transport_path], 'payoff-values')
    native_raw = read_witness(native_path, native_witness); native = json.loads(native_raw)
    values = checked_native_values(native, deal_count=len(batch['deals']),
                                   stack=context['config']['stack'], dead_money=context['dead_money'])
    original_bytes = {raw_path: raw, labelled_path: labelled_raw, query_path: query_raw,
                      transport_path: transport_raw, native_path: native_raw}
    artifact_hashes = {}
    for path, accepted in original_bytes.items():
        if bounded_read(path) != accepted:
            raise ValueError('Final source/output bytes changed after inference or payoff verification')
        artifact_hashes[path.name] = digest(accepted)
    for invocation in invocations:
        verify_native(invocation['result'], executable=invocation['executable'],
                      arguments=invocation['arguments'], expected_identities=invocation['expected_identities'],
                      timeout=native_timeout_seconds, max_output_bytes=MAX_NATIVE_OUTPUT_BYTES,
                      stdin_path=None, direct_outputs=invocation['result']['receipt']['direct_outputs'])
    result = dict(format=1, method='complete-expected-policy-paired-native-batch-v2',
                  deals=len(batch['deals']), context_sha256=digest(context_raw),
                  values=values.tolist(), profile_order=list(PROFILE_NAMES), coverage=coverage,
                  allin_cache_sha256=cache.sha256, query_seconds=query_seconds,
                  averaging_seconds=timings, native_seconds=native_seconds,
                  native_invocations=invocations, artifacts=artifact_hashes,
                  bounds_best_response_above=False, broad_preflop_accuracy_qualified=False)
    write(folder/'summary.json', result)
    return result
