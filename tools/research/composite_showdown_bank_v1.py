"""Evaluation banks for three original arms plus the audited recovered fourth.

Original failure is preserved. Evaluation admission is explicitly composite;
the older single-directory loader is used only for its qualified readback.
"""
import hashlib
import json
from pathlib import Path
import psutil
import numpy as np
from sampled_physical_root_evaluation_v1 import sha
from later_average_support_v1 import OUT, read
from sampled_visible_hybrid_checkpoint_v1 import encoded, digest
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
from compact_showdown_bank_v2 import load_bank as original_load_bank, validated_document
from composite_showdown_evidence_v1 import source_for_iteration, require, ORIGINAL_SHA
import showdown_root_checkpoint_v1 as corrected

TRAINING = ('9266201-baseline', '9266201-corrected', '9266301-baseline', '9266301-corrected')
COMPOSITE_AUDIT = 'showdown-training-readback-composite-v1-9266301-corrected-0078'


def training_gates():
    # The evaluator may own the GPU lock itself; refuse actual training or
    # retirement processes rather than bypassing its legitimate reader lock.
    for process in psutil.process_iter(['name', 'cmdline']):
        if 'python' not in (process.info['name'] or '').lower():
            continue
        require(process.info['cmdline'] is not None, 'Cannot verify process ownership')
        for arg in process.info['cmdline']:
            name = Path(arg).name
            require(not (name.startswith('retain_completed_showdown_arm_') or name in (
                'hu_showdown_matched_training_20260926.py', 'hu_showdown_fourth_arm_continuation_20260927.py')),
                'Training or retention remains active')
    rp = OUT/'showdown-matched-training-v1-registration.json'
    original_status = OUT/'showdown-matched-training-v1-status.json'
    require(sha(rp) == ORIGINAL_SHA and read(original_status)['state'] == 'failed', 'Preserved original identity required')
    trial = read(rp)
    require([a['name'] for a in trial['arms']] == list(TRAINING), 'Fixed four arms required')
    require(not (OUT/'showdown-matched-training-v1-result.json').exists(), 'Original failure was overwritten')
    paths = [rp, original_status]
    for arm in trial['arms'][:3]:
        case = Path(trial['store'])/arm['name']; result_path = case/'result.json'; final = read(result_path)
        require(final['name'] == arm['name'] and final['config'] == arm['config']
                and final['store'] == str(case) and final['completed_iterations'] == 78
                and final['final_restore_verified'], 'Original arm is incomplete or changed')
        ap = OUT/f"showdown-training-readback-v2-{arm['name']}-0078-result.json"
        ar = OUT/f"showdown-training-readback-v2-{arm['name']}-0078-registration.json"
        audit = read(ap)
        require(audit['passed'] and audit['complete_arm'] and audit['completed_updates'] == 78
                and audit['arm'] == arm['name'] and audit['source_registration_sha256'] == sha(rp)
                and audit['readback_registration_sha256'] == sha(ar)
                and audit['bb_roots_reconstructed'] == 39936
                and read(ar)['arm'] == arm['name'] and read(ar)['completed_iterations'] == 78,
                'Original full audit required')
        paths.extend([result_path, ap, ar])
    cr, cp, cs = [OUT/f'showdown-fourth-arm-continuation-v1-{s}.json' for s in ('registration', 'result', 'status')]
    creg, final, status = read(cr), read(cp), read(cs)
    require(status['state'] == 'complete' and status['exit_code'] == 0 and final['passed'] and final['terminal'],
            'Completed continuation required')
    require(final['registration_sha256'] == sha(cr) and final['original_registration_sha256'] == sha(rp)
            and final['name'] == TRAINING[-1] and final['config'] == trial['arms'][-1]['config'] == creg['config']
            and final['completed_iterations'] == 78 and final['training_deals'] == 39936
            and final['final_restore_verified'], 'Full fixed fourth arm required')
    require(creg['arm'] == TRAINING[-1] and Path(final['store']) == Path(creg['store'])/TRAINING[-1]
            and Path(final['original_store']) == Path(trial['store'])/TRAINING[-1], 'Continuation stores differ')
    require(final['predecessor'] == dict(directory=str(Path(trial['store'])/TRAINING[-1]/'objects'),
            retention_sha256=None), 'Continuation predecessor differs')
    local_result = Path(creg['store'])/TRAINING[-1]/'result.json'
    require(read(local_result) == final, 'Continuation result copies differ')
    ar, ap = [OUT/f'{COMPOSITE_AUDIT}-{s}.json' for s in ('registration', 'result')]
    audit = read(ap)
    require(audit['passed'] and audit['complete_arm'] and audit['composite_completed_arm']
            and audit['completed_updates'] == 78 and audit['arm'] == TRAINING[-1]
            and audit['bb_roots_reconstructed'] == 39936
            and audit['source_registration_sha256'] == sha(rp) and audit['readback_registration_sha256'] == sha(ar)
            and audit['continuation_registration_sha256'] == sha(cr) and audit['continuation_result_sha256'] == sha(cp)
            and read(ar)['arm'] == TRAINING[-1] and read(ar)['completed_iterations'] == 78,
            'Matching independent full composite audit required')
    paths.extend([cr, cp, cs, local_result, ar, ap])
    return paths


class Objects:
    def __init__(self, local, predecessor, guard):
        self.local = ReadOnlyCheckpointObjects(local, guard=guard)
        self.predecessor = ReadOnlyCheckpointObjects(predecessor, guard=guard)

    def read(self, reference):
        name = reference['file']
        def contains(reader):
            return name in reader.members if reader.members is not None else (reader.directory/name).exists()
        if contains(self.local):
            raw = self.local.read(reference)
            if contains(self.predecessor):
                require(raw == self.predecessor.read(reference), 'Local/predecessor object conflict')
            return raw
        return self.predecessor.read(reference)


def load_bank(out, label, *, completed, purpose, bank_args, guard):
    require(Path(out).resolve() == OUT.resolve() and label in TRAINING and type(completed) is int
            and completed == 78 and purpose == 'evaluation', 'Only fully audited study evaluation is supported')
    paths = training_gates()
    bindings = {str(p):sha(p) for p in paths}
    trial = read(OUT/'showdown-matched-training-v1-registration.json')
    arm = next(a for a in trial['arms'] if a['name'] == label)
    if label != TRAINING[-1]:
        models, weights, legacy_identity = original_load_bank(out, label, completed=78,
            purpose='implementation-control', bank_args=bank_args, guard=guard)
        final = read(Path(trial['store'])/label/'result.json')
        require(final['played_bank'] == legacy_identity['model_references']
                and final['final_checkpoint'] == legacy_identity['checkpoint'], 'Original final result differs from audited bank')
        identity = dict(legacy_identity, purpose='evaluation', evaluation_qualified=True,
            admission='three-original-plus-independently-audited-continuation-v1',
            original_readback_identity=legacy_identity, complete_study_bindings=bindings,
            original_trial_status='failed-preserved', accuracy_qualified=False)
    else:
        cfg = arm['config']; corrected.require_config(cfg)
        final = read(OUT/'showdown-fourth-arm-continuation-v1-result.json')
        original = Path(trial['store'])/label; case = Path(final['store'])
        audit_path = OUT/f'{COMPOSITE_AUDIT}-result.json'; audit = read(audit_path)
        audit_reg = OUT/f'{COMPOSITE_AUDIT}-registration.json'
        for path, expected in read(audit_reg)['inputs'].items():
            guard(); require(sha(path) == expected, 'Audited composite source changed: '+path)
        markers = audit['completed_retention_markers']
        expected_paths = [source_for_iteration(original, case, n)/f'retention-{n:04d}.json' for n in range(1, 79)]
        require(set(markers) == {str(p) for p in expected_paths}, 'Composite audit marker set differs')
        refs = []; previous = None
        for n, path in enumerate(expected_paths, 1):
            guard(); require(sha(path) == markers[str(path)], 'Audited marker changed')
            marker = read(path); metric_path = path.parent/f'iteration-{n:04d}/metrics.json'; metric = read(metric_path)
            require(marker['iteration'] == n and marker['metrics_sha256'] == sha(metric_path)
                    and marker['checkpoint'] == metric['checkpoint'], 'Audited metric changed')
            require(metric['used_model']['generation'] == n-1 and metric['next_model']['generation'] == n
                    and (previous is None or previous == metric['used_model']), 'Composite generation chain changed')
            refs.append(metric['used_model']); previous = metric['next_model']
        require(final['played_bank'] == refs and final['final_checkpoint'] == metric['checkpoint'],
                'Continuation final bank changed')
        objects = Objects(case/'objects', original/'objects', guard)
        require(objects.predecessor.retention_sha256 is None, 'Registered raw predecessor identity changed')
        checkpoint = json.loads(objects.read(metric['checkpoint']))
        require(checkpoint['format'] == 8 and checkpoint['policy_type'] == corrected.POLICY_TYPE
                and checkpoint['completed_iterations'] == 78 and checkpoint['played_bank'] == refs
                and checkpoint['next_model'] == previous
                and checkpoint['config_sha256'] == hashlib.sha256(encoded(cfg)).hexdigest()
                and checkpoint['context_sha256'] == digest(bank_args['context_source'])
                and checkpoint['catalog_sha256'] == digest(bank_args['catalog_source'])
                and checkpoint['matrix_sha256'] == bank_args['matrix_sha256'], 'Composite checkpoint identity differs')
        models = []
        for generation, ref in enumerate([*refs, previous]):
            guard(); model = validated_document(objects, ref, treatment=True, bank_args=bank_args)
            require(model['generation'] == generation
                    and sum(model['integrated_root']['state']['sample_counts']) == generation*512
                    and model['integrated_root']['coefficients_sha256'] == cfg['control_coefficients_sha256'],
                    'Composite model identity differs')
            if generation < 78:
                models.append(model)
        weights = np.tile(np.arange(1, 79, dtype=np.float64), (2, 1))
        identity = dict(arm=label, treatment='corrected', purpose='evaluation', evaluation_qualified=True,
            admission='three-original-plus-independently-audited-continuation-v1', complete_study_bindings=bindings,
            registration_sha256=sha(OUT/'showdown-matched-training-v1-registration.json'),
            audit_sha256=sha(audit_path), readback_registration_sha256=sha(audit_reg),
            continuation_result_sha256=sha(OUT/'showdown-fourth-arm-continuation-v1-result.json'),
            checkpoint=metric['checkpoint'], model_references=refs, played_generations=list(range(78)),
            excluded_generation=78, weights=weights.tolist(), inference_type='showdown-controlled-v8',
            predecessor=final['predecessor'], objects_retention_sha256=objects.local.retention_sha256,
            original_trial_status='failed-preserved', accuracy_qualified=False, production_modified=False)
    for path, expected in bindings.items():
        guard(); require(sha(path) == expected, 'Complete-study binding changed while loading')
    return models, weights, identity
