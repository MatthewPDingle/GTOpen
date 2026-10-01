"""Authenticate one reviewed storage stop, with unchanged scientific prefixes.

This module cannot fit, sample, continue training, change a failure, or select a
winning model. Only the exact reviewed clean stop is recognized by consumers.
"""
from pathlib import Path
import copy
import hashlib
import json
import stack_context_pressure_continuation_v2 as coordinator
import stack_context_parallel_continuation_v2 as continuation

OUT=coordinator.OUT
RESULT,FAILURE=coordinator.RESULT,coordinator.FAILURE
REVIEW,READBACK,ADMISSION=coordinator.REVIEW,coordinator.READBACK,coordinator.ADMISSION
QUALIFICATION=OUT/'stack-context-pressure-consumer-check-v1-result.json'
OLD_CONSUMERS=('stack-context-final-bank-throughput-v2','stack-context-matched-evaluation-v3',
               'stack-context-matched-readback-v4')


def require(ok,message):
    if not ok:raise ValueError(message)


def read(path):return json.loads(Path(path).read_bytes())


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def no_old_consumer_attempt():
    for name in OLD_CONSUMERS:
        require(not any((OUT/(name+s+'.json')).exists() for s in
            ('-attempt','-registration','-result','-failure')), 'Earlier scientific consumer started: '+name)
        if name!='stack-context-matched-readback-v4':
            require(not (Path('S:/GTOpen-research')/name).exists(), 'Earlier scientific consumer store exists: '+name)


def validate_prefixes(progress,identity):
    require(identity.get('format')==1 and identity.get('complete_boundary_counts')==coordinator.COUNTS
        and identity.get('original_registration_sha256')==coordinator.REG_SHA
        and identity.get('recognized_pressure_stop_only') is True
        and identity.get('scientific_cycles_retried') is False
        and identity.get('scientific_selection_and_gates_unchanged') is True,
        'Unrecognized resource-pressure identity')
    require(set(progress)==set(coordinator.COUNTS), 'Four complete scientific trajectories required')
    for arm,n in coordinator.COUNTS.items():
        p=progress[arm]
        require(p.get('registration_sha256')==coordinator.REG_SHA
            and coordinator.prefix_hash(p,n)==identity['complete_prefix_sha256'][arm],
            'Reviewed pressure-stop prefix was changed')
    return dict(identity['complete_prefix_sha256'])


def verify_pressure(terminal=None):
    require(not FAILURE.exists(), 'New pressure-continuation failure is not recognized')
    no_old_consumer_attempt()
    review=coordinator.verify_review()
    admission=read(ADMISSION)
    continuation.legacy.verify(admission['inputs'])
    require(admission['coordinator_sha256']==sha(coordinator.__file__)
        and admission['original_worker_sha256']==sha(continuation.__file__)
        and admission['boundary_review_sha256']==sha(REVIEW) and admission['readback_sha256']==sha(READBACK)
        and admission['maximum_concurrent_arms']==2 and admission['logical_reservation']==70_000_000_000
        and admission['global_allocated_cap']==800_000_000_000
        and admission['original_deadline_unix']==read(continuation.legacy.ATTEMPT)['admitted_unix']+72*3600
        and admission['scientific_inputs_gates_unchanged'] is True
        and admission['scientific_cycles_retried'] is False
        and admission['original_failed_evidence_preserved'] is True,
        'Pressure scheduling admission differs')
    identity=dict(format=1,original_registration_sha256=coordinator.REG_SHA,
        pressure_failure_sha256=sha(continuation.FAILURE),boundary_review_sha256=sha(REVIEW),
        boundary_readback_sha256=sha(READBACK),operational_admission_sha256=sha(ADMISSION),
        complete_boundary_counts=dict(coordinator.COUNTS),
        complete_prefix_sha256={a:review['boundaries'][a]['progress_sha256'] for a in coordinator.COUNTS},
        maximum_concurrent_arms=2,recognized_pressure_stop_only=True,scientific_cycles_retried=False,
        scientific_selection_and_gates_unchanged=True)
    paths={Path(__file__).resolve(),Path(coordinator.__file__).resolve(),REVIEW,READBACK,ADMISSION,
        coordinator.CONTROL,continuation.FAILURE,coordinator.ATTEMPT}
    for record in (review,read(READBACK),admission):paths.update(Path(p) for p in record['inputs'])
    if terminal is not None:
        require(RESULT.exists() and read(RESULT)==terminal and terminal.get('training_complete') is True
            and terminal.get('registration_sha256')==coordinator.REG_SHA
            and terminal.get('resource_pressure_failure_sha256')==identity['pressure_failure_sha256']
            and terminal.get('resource_pressure_review_sha256')==identity['boundary_review_sha256']
            and terminal.get('operational_admission_sha256')==identity['operational_admission_sha256']
            and terminal.get('original_scientific_worker_unchanged') is True
            and terminal.get('cycles_retried') is False and terminal.get('production_modified') is False,
            'Incomplete or detached pressure-continuation outcome')
        validate_prefixes(terminal['arms'],identity)
        attempt=read(coordinator.ATTEMPT)
        require(attempt['boundaries']==coordinator.COUNTS and attempt['admission_sha256']==sha(ADMISSION)
            and attempt['original_worker_sha256']==sha(continuation.__file__), 'Detached continuation attempt')
        for arm in coordinator.COUNTS:
            p=terminal['arms'][arm];started_path=OUT/(coordinator.NAME+'-'+arm+'-started.json')
            outcome_path=coordinator.STORE/(continuation.NAME+'-'+attempt['invocation']+'-'+arm+'.json')
            started,outcome=read(started_path),read(outcome_path)
            require(p['completed_cycles']==64 and len(p['updates'])==64
                and read(coordinator.STORE/arm/'progress.json')==p, 'Unfinished or changed actual final arm')
            require(started['arm']==outcome['arm']==arm and started['invocation']==attempt['invocation']
                and started['starts_after_complete_cycle']==coordinator.COUNTS[arm]
                and started['pid']==outcome['pid'] and started['process_created']==outcome['process_created']
                and outcome.get('complete') is True and outcome.get('stopped_at_complete_boundary') is False
                and not outcome.get('failed') and outcome['progress_sha256']==sha(coordinator.STORE/arm/'progress.json'),
                'Missing successful actual final worker outcome')
            paths.update((started_path,outcome_path))
        identity['training_result_sha256']=sha(RESULT);paths.add(RESULT)
    return identity,paths


def verify_qualification():
    proof=read(QUALIFICATION)
    require(proof.get('passed') is True and proof.get('complete') is True
        and proof.get('pressure_provenance_sha256')==sha(__file__)
        and proof.get('unchanged_scientific_functions_verified') is True
        and proof.get('scientific_workers_launched')==0 and proof.get('native_calls')==0
        and proof.get('scientific_fits')==0, 'Current pressure-consumer software qualification required')
    continuation.legacy.verify(proof['inputs'])
    return {QUALIFICATION,*map(Path,proof['inputs'])}


def verify_prior_correction(result=None):
    # The imported old basis below has exactly one removed failure-absence
    # guard. This complete pressure proof replaces it; every old basis guard
    # and the earlier recovery proof are retained and separately qualified.
    _,paths=verify_pressure(result)
    return paths|verify_prior_basis(result)


def verify_prior_basis(result=None):
    """Only recognize the documented false positive; keep all failure evidence."""
    diagnosis=continuation.known_failure()
    amendment=read(continuation.AMENDMENT); control=read(continuation.CONTROL)
    expected=dict(original_registration_sha256=sha(continuation.legacy.REG),
        original_failure_sha256=sha(continuation.legacy.FAILURE),diagnosis_sha256=sha(continuation.DIAGNOSIS),
        runner_sha256=sha(continuation.__file__),plan_sha256=sha(continuation.PLAN),check_sha256=sha(continuation.CONTROL),
        failed_evidence_preserved=True,scientific_cycles_retried=False,seeds_models_targets_fits_unchanged=True,
        cycles_per_arm=64,maximum_concurrent_arms=4,target_workers_per_arm=4,board_workers_per_arm=1,
        cuda_bytes_per_arm=2_000_000_000,combined_cuda_bytes=8_000_000_000,logical_reservation=70_000_000_000,
        global_allocated_cap=800_000_000_000,original_deadline_unchanged=True,evaluation_gates_unchanged=True,
        production_modified=False)
    require(all(amendment.get(k)==v for k,v in expected.items()), 'Unrecognized continuation correction or operational change')
    require(control['passed'] and control['complete'] and control['runner_sha256']==expected['runner_sha256']
        and control['scheduling']['scientific_pipeline_calls']==0
        and control['scheduling']['old_progress_unchanged'], 'Missing qualified recovery/parallel evidence')
    continuation.legacy.verify(control['inputs'])
    if result is not None:
        require(result.get('continuation_amendment_sha256')==sha(continuation.AMENDMENT)
            and result.get('original_failure_sha256')==sha(continuation.legacy.FAILURE), 'Terminal correction identities differ')
    return {continuation.AMENDMENT,continuation.CONTROL,continuation.legacy.FAILURE,continuation.DIAGNOSIS,continuation.PLAN}
