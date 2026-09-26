"""Read-only admission of audited compact training banks, preserving model types.

Evaluation requires all four registered arms to finish and this arm's full audit.
An explicitly labelled implementation control may load an audited prefix; its
identity is never evaluation-qualified. Raw and losslessly archived objects share the same validation. No archive extraction or object writes.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from sampled_physical_root_evaluation_v1 import sha
from sampled_visible_hybrid_checkpoint_v1 import encoded, digest
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
import later_action_checkpoint_v1 as baseline
import showdown_root_checkpoint_v1 as corrected

PREFIX = 'showdown-matched-training-v1'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def validated_document(objects, reference, *, treatment, bank_args):
    """Preserve the original model validator and reference generation check."""
    value = json.loads(objects.read(reference))
    if treatment:
        corrected.validate_model(value, **bank_args)
    else:
        baseline.inner_model(value, **bank_args)
    require(type(reference['generation']) is int
            and value['generation'] == reference['generation'], 'Model generation mismatch')
    return value


def load_bank(out, label, *, completed, purpose, bank_args, guard):
    require(purpose in ('evaluation', 'implementation-control'), 'Explicit bank purpose required')
    require(type(completed) is int and 0 < completed <= 78, 'Invalid audited update count')
    evaluation = purpose == 'evaluation'
    require(not evaluation or completed == 78, 'Partial training cannot enter evaluation')
    out = Path(out)
    registration_path = out / f'{PREFIX}-registration.json'
    registration = read(registration_path)
    arms = [a for a in registration['arms'] if a['name'] == label]
    require(len(arms) == 1, 'Unknown or duplicate registered arm')
    arm = arms[0]
    config = arm['config']
    require(config['max_iterations'] == 78, 'Registered training budget changed')
    require(arm['treatment'] in ('baseline', 'corrected'), 'Unknown treatment')
    case = Path(registration['store']) / label
    audit_prefix = f'showdown-training-readback-v2-{label}-{completed:04d}'
    audit_path = out / f'{audit_prefix}-result.json'
    readback_path = out / f'{audit_prefix}-registration.json'
    audit, readback = read(audit_path), read(readback_path)
    require(audit.get('passed') is True and audit['arm'] == label
            and audit['completed_updates'] == completed
            and audit['complete_arm'] == (completed == 78)
            and audit['source_registration_sha256'] == sha(registration_path)
            and audit['readback_registration_sha256'] == sha(readback_path),
            'Matching successful independent readback required')
    require(readback['arm'] == label and readback['completed_iterations'] == completed,
            'Readback registration differs from requested bank')
    require(audit['bb_roots_reconstructed'] == completed * config['subbatches_per_iteration']
            * config['deals_per_subbatch'], 'Audit root sample count changed')
    # Recheck frozen implementation and experiment inputs, without rereading all
    # archived training transport: the scalar audit authenticates those bytes.
    dependencies = dict(registration['inputs'])
    for path, expected in readback['inputs'].items():
        require(path not in dependencies or dependencies[path] == expected,
                'Conflicting frozen input identity')
        dependencies[path] = expected
    for path, expected in dependencies.items():
        guard()
        require(sha(path) == expected, 'Frozen input changed: ' + path)
    markers = audit['completed_retention_markers']
    expected_paths = [case / f'retention-{i:04d}.json' for i in range(1, completed + 1)]
    require(set(markers) == {str(p) for p in expected_paths}, 'Incomplete audited marker set')
    references = []
    previous = None
    for i, path in enumerate(expected_paths, 1):
        guard()
        require(sha(path) == markers[str(path)], 'Audited completion marker changed')
        marker = read(path)
        metric_path = case / f'iteration-{i:04d}' / 'metrics.json'
        require(marker['iteration'] == i and sha(metric_path) == marker['metrics_sha256'],
                'Audited metric identity changed')
        metric = read(metric_path)
        require(previous is None or previous == metric['used_model'], 'Played model chain broken')
        require(metric['used_model']['generation'] == i - 1
                and metric['next_model']['generation'] == i, 'Played generation changed')
        require(marker['checkpoint'] == metric['checkpoint'], 'Recovery reference differs')
        references.append(metric['used_model'])
        previous = metric['next_model']
    require(metric['checkpoint'] is not None, 'Bank must end at a verified recovery boundary')
    objects = ReadOnlyCheckpointObjects(case / 'objects', guard=guard)
    checkpoint = json.loads(objects.read(metric['checkpoint']))
    treatment = arm['treatment'] == 'corrected'
    reader = corrected if treatment else baseline
    reader.require_config(config)
    require(checkpoint['format'] == (8 if treatment else 7)
            and checkpoint['policy_type'] == reader.POLICY_TYPE
            and checkpoint['completed_iterations'] == completed
            and checkpoint['played_bank'] == references and checkpoint['next_model'] == previous
            and checkpoint['config_sha256'] == hashlib.sha256(encoded(config)).hexdigest()
            and checkpoint['context_sha256'] == digest(bank_args['context_source'])
            and checkpoint['catalog_sha256'] == digest(bank_args['catalog_source'])
            and checkpoint['matrix_sha256'] == bank_args['matrix_sha256'],
            'Recovery checkpoint does not identify the audited model history')
    documents = []
    for g, ref in enumerate([*references, previous]):
        guard()
        doc = validated_document(objects, ref, treatment=treatment, bank_args=bank_args)
        require(doc['generation'] == g, 'Model order changed')
        require(sum(doc['integrated_root']['state']['sample_counts']) == g
                * config['subbatches_per_iteration'] * config['deals_per_subbatch'],
                'Model root sample count changed')
        if treatment:
            require(doc['integrated_root']['coefficients_sha256']
                    == config['control_coefficients_sha256'], 'Model coefficient identity changed')
        if g < completed:
            documents.append(doc if treatment else baseline.inner_model(doc, **bank_args))
    source_result = None
    if evaluation:
        result_path = out / f'{PREFIX}-result.json'
        result = read(result_path)
        require(result.get('passed') is True and result.get('terminal') is True
                and result['registration_sha256'] == sha(registration_path)
                and result['store'] == registration['store'], 'Complete registered trial required')
        require([a['name'] for a in result['arms']] == [a['name'] for a in registration['arms']]
                and all(a['completed_iterations'] == 78 and a['final_restore_verified'] is True
                        for a in result['arms']), 'All four fixed-budget arms must finish')
        final = next(a for a in result['arms'] if a['name'] == label)
        require(final == read(case / 'result.json') and final['config'] == config
                and final['store'] == str(case) and final['played_bank'] == references
                and final['final_checkpoint'] == metric['checkpoint'],
                'Final arm result differs from audited bank')
        source_result = sha(result_path)
    weights = np.tile(np.arange(1, completed + 1, dtype=np.float64), (2, 1))
    identity = dict(arm=label, treatment=arm['treatment'], purpose=purpose,
        evaluation_qualified=evaluation, registration_sha256=sha(registration_path),
        audit_sha256=sha(audit_path), readback_registration_sha256=sha(readback_path),
        trial_result_sha256=source_result, checkpoint=metric['checkpoint'],
        objects_retention_sha256=objects.retention_sha256,
        played_generations=list(range(completed)), excluded_generation=completed,
        model_references=references, weights=weights.tolist(),
        inference_type='showdown-controlled-v8' if treatment else 'baseline-v7-inner-v6',
        accuracy_qualified=False, production_modified=False)
    return documents, weights, identity
