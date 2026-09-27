"""Admit only the complete independently audited stratified policy histories."""
from pathlib import Path
import numpy as np
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
import weighted_training_checkpoint_v1 as checkpoint


def load_bank(label, *, bank_args, guard):
    registration = OUT / 'weighted-stratified-study-v1-registration.json'
    result_path = OUT / 'weighted-stratified-study-v1-training-result.json'
    reg, result = read(registration), read(result_path)
    if not result['training_complete'] or result['registration_sha256'] != sha(registration):
        raise ValueError('Complete registered training required')
    arms = [a for a in reg['arms'] if a['name'] == label]
    if len(arms) != 1 or reg['generations'] != 78 or result['store'] != reg['store']:
        raise ValueError('Unknown arm or changed training endpoint')
    for path, digest in reg['inputs'].items():
        guard()
        if sha(path) != digest:
            raise ValueError('Registered training source changed: ' + path)
    arm = arms[0]
    prefix = f'weighted-training-readback-parallel-v1-w4-{label}-0078'
    audit_path, audit_registration = [OUT / f'{prefix}-{suffix}.json' for suffix in ('result', 'registration')]
    audit, audit_reg = read(audit_path), read(audit_registration)
    if (not audit['passed'] or not audit['complete_arm'] or audit['completed_updates'] != 78
            or audit['arm'] != label or audit['source_registration_sha256'] != sha(registration)
            or audit['readback_registration_sha256'] != sha(audit_registration)
            or audit['bb_roots_reconstructed'] != 78 * 512
            or audit_reg['arm'] != label or audit_reg['completed'] != 78):
        raise ValueError('Matching full independent readback required')
    # Native transport was authenticated by the audit. Recheck its implementation
    # and the models actually used here, rather than hashing all raw deals again.
    for path, digest in audit_reg['inputs'].items():
        if Path(path).suffix == '.py':
            guard()
            if sha(path) != digest:
                raise ValueError('Audited implementation changed: ' + path)
    case = Path(reg['store']) / label
    endpoint = result['arms'][label]
    if (endpoint['completed'] != 78 or endpoint['registration_sha256'] != sha(registration)
            or endpoint['checkpoint'] != audit['final_checkpoint']
            or sha(endpoint['metrics_path']) != endpoint['metrics_sha256']):
        raise ValueError('Endpoint differs from audited checkpoint')
    if len(audit_reg['folders']) != 78:
        raise ValueError('Incomplete audited folder history')
    references = []
    previous = None
    for generation, folder in enumerate(audit_reg['folders']):
        guard()
        folder = Path(folder)
        if not folder.resolve().is_relative_to(case.resolve()):
            raise ValueError('Audited folder outside its arm')
        path = folder / 'metrics.json'
        if sha(path) != audit_reg['inputs'][str(path)]:
            raise ValueError('Audited metrics changed')
        metric = read(path)
        if (metric['iteration'] != generation + 1 or metric['used_model']['generation'] != generation
                or metric['next_model']['generation'] != generation + 1
                or (previous is not None and previous != metric['used_model'])):
            raise ValueError('Played model chain changed')
        references.append(metric['used_model'])
        previous = metric['next_model']
    if metric['checkpoint'] != endpoint['checkpoint']:
        raise ValueError('Final model chain recovery differs')
    objects = case / 'objects'
    state = checkpoint.restore_checkpoint(objects, endpoint['checkpoint'], arm['config'], **bank_args)
    if (state['completed_iterations'] != 78 or state['played_bank'] != references
            or state['next_model'] != previous):
        raise ValueError('Checkpoint and played model history differ')
    documents = []
    for generation, reference in enumerate(references):
        guard()
        model = checkpoint.model_document(objects, reference, **bank_args)
        if model['generation'] != generation or sum(model['root_state']['sample_counts']) != generation * 512:
            raise ValueError('Wrong weighted model generation')
        documents.append(model)
    weights = np.tile(np.arange(1., 79.), (2, 1))
    identity = dict(arm=label, completed_iterations=78, model_references=references,
                    checkpoint=endpoint['checkpoint'], unplayed_excluded=previous,
                    training_registration_sha256=sha(registration), training_result_sha256=sha(result_path),
                    independent_audit_sha256=sha(audit_path), independent_registration_sha256=sha(audit_registration),
                    averaging='played generations 0-77; weights 1-78; own-action reach',
                    purpose='evaluation', accuracy_qualified=False)
    return documents, weights, identity
