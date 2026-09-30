"""Fixed final banks with authenticated parallel-continuation provenance.

Original raw source hashes remain evidence. Chance receipts distinguish board
draws from each representation's learned parent state. Selection stays at all
played generations 0..63, with no result-dependent selection or extra fitting.
"""
import copy
import hashlib
import json
from pathlib import Path
from stack_context_final_bank_v1 import select, load_documents, BANK_ORDER, CYCLES, require
from stack_context_inputs_v1 import encoded
from sampled_visible_hybrid_checkpoint_v1 import read_object
from sampled_physical_root_evaluation_v1 import sha
import stack_context_parallel_continuation_v2 as continuation

ORIGINAL_PREFIX = {'A-baseline':2, 'A-relative':1, 'B-baseline':1, 'B-relative':1}


def read(path):return json.loads(Path(path).read_bytes())


def validate_receipt(document, arm, cycle, progress_record, played, cfg, registration, comparator):
    require(set(document) == {'format','arm','cycle','registration_sha256','parent_model','original_source_hashes',
        'board_chance','matched_input_identities','own_parent_validated','comparator_sha256'}, 'Unexpected chance receipt contract')
    require(document['format'] == 1 and document['arm'] == arm and document['cycle'] == cycle
        and document['registration_sha256'] == registration and document['parent_model'] == played
        and document['own_parent_validated'] is True and document['comparator_sha256'] == comparator,
        'Chance receipt identifies the wrong parent, cycle or implementation')
    raw = progress_record['paired_sources']
    expected_names = set()
    for key in cfg['context_order']:
        expected_names.update((key+'/board-plan.json',key+'/source-generation.json'))
        expected_names.update(key+f'/batch-{i:03d}/batch.json' for i in range(13))
    require(set(raw) == expected_names and document['original_source_hashes'] == raw
        and set(document['board_chance']) == set(cfg['context_order']), 'Original matching evidence omitted or changed')
    compared = dict(raw)
    for key, row in document['board_chance'].items():
        require(row['generation'] == cycle-1 and len(row['boards']) == 1,
            'Chance receipt has wrong generation or board budget')
        compared[key+'/board-plan.json'] = row['chance_sha256']
    require(document['matched_input_identities'] == compared, 'Receipt changed a non-board input or ignored a board draw')


def select_terminal(result, checkpoints, spec, *, training_registration_sha256, receipts,
                    amendment_sha256, original_failure_sha256, comparator_sha256):
    require(result.get('training_complete') is True and result.get('registration_sha256') == training_registration_sha256
        and result.get('production_modified') is False and result.get('continuation_amendment_sha256') == amendment_sha256
        and result.get('original_failure_sha256') == original_failure_sha256, 'Successful bound continuation required')
    require(set(result['arms']) == set(checkpoints) == set(receipts) == set(BANK_ORDER), 'All four complete arms required')
    selected = {arm:select(arm,result['arms'][arm],checkpoints[arm],spec,
        training_registration_sha256=training_registration_sha256) for arm in BANK_ORDER}
    for arm in BANK_ORDER:
        require(len(receipts[arm]) == 64, 'All 64 authenticated chance receipts required')
        for i, evidence in enumerate(receipts[arm]):
            cycle = i+1; record = result['arms'][arm]['updates'][i]
            validate_receipt(evidence['document'], arm, cycle, record, selected[arm]['played'][i],
                spec['arms'][arm]['config'], training_registration_sha256, comparator_sha256)
            if cycle > ORIGINAL_PREFIX[arm]:
                require(record.get('chance_receipt_sha256') == evidence['sha256']
                    and record.get('continuation_amendment_sha256') == amendment_sha256,
                    'Post-correction cycle lacks bound evidence')
                require(record.get('recovered_without_scientific_repeat') is (arm == 'A-relative' and cycle == 2),
                    'Unexpected recovery or repeated scientific cycle')
        selected[arm]['matched_chance_by_cycle'] = [copy.deepcopy(r['document']['matched_input_identities']) for r in receipts[arm]]
        selected[arm]['chance_receipts'] = [{k:v for k,v in r.items() if k != 'document'} for r in receipts[arm]]
    for seed in ('A','B'):
        for a,b in zip(receipts[seed+'-baseline'],receipts[seed+'-relative']):
            continuation.compare_receipts(a['document'],b['document'])
    return dict(format=2,bank_order=list(BANK_ORDER),arms=selected,
        training_registration_sha256=training_registration_sha256,continuation_amendment_sha256=amendment_sha256,
        original_failure_sha256=original_failure_sha256,selection_uses_test_results=False,
        raw_source_hashes_preserved=True,board_plans_validated_against_own_parents=True)


def authenticate_cycle(train, arm, cycle, progress, terminal_checkpoint, spec, rt, *, guard):
    """Reconstruct the receipt from immutable models and authenticated boards."""
    train = Path(train)
    require(train.resolve() == continuation.legacy.STORE.resolve(), 'Unregistered training store')
    folder=train/arm; record=progress['updates'][cycle-1]; archive=folder/f'archive-{cycle:04d}'
    path=folder/f'chance-{cycle:04d}.json'
    require(record['cycle']==cycle and record['archive']==str(archive.relative_to(train)), 'Reordered cycle archive')
    require(sha(archive/'index.json')==record['archive_index_sha256']
        and sha(archive/'retired.json')==record['retirement_sha256'], 'Changed published archive or retirement')
    index=read(archive/'index.json'); plan=read(archive/'plan.json'); retired=read(archive/'retired.json')
    require(index['plan_sha256']==sha(archive/'plan.json') and retired['index_sha256']==sha(archive/'index.json')
        and retired['raw_files_remaining']==0 and plan['destination']==str(archive)
        and plan['source']==str(folder/f'cycle-{cycle:04d}') and plan['owner']==str(train), 'Archive ownership/binding differs')
    require(len(plan['jobs'])==len(index['bundles']), 'Incomplete archive index')
    members={r['path']:r for r in plan['members']}
    require(len(members)==len(plan['members']), 'Duplicate original member')
    for name, identity in record['paired_sources'].items():
        require(name in members and members[name]['sha256']==identity, 'Recorded input differs from archived source')
    paths={path,archive/'index.json',archive/'plan.json',archive/'retired.json',folder/'objects'/record['checkpoint']['file']}
    checkpoint=json.loads(read_object(folder/'objects',record['checkpoint']))
    require(checkpoint['completed_cycles']==cycle and checkpoint['config']==spec['arms'][arm]['config']
        and checkpoint['played_bank']==terminal_checkpoint['played_bank'][:cycle], 'Changed complete training trajectory')
    next_expected=(terminal_checkpoint['played_bank'][cycle] if cycle<64 else terminal_checkpoint['next_model'])
    require(checkpoint['next_model']==next_expected, 'Unplayed/future model substituted into trajectory')
    for key in spec['arms'][arm]['config']['context_order']:
        matches=[(j,r) for j,r in zip(plan['jobs'],index['bundles'])
            if Path(j['source']).name==key and 'board-plan.json' in j['names']]
        require(len(matches)==1, 'Missing/duplicated board archive')
        job,row=matches[0]; packed=Path(job['destination']); manifest=packed.with_suffix('.xz.json')
        require(packed.parent==archive and packed.name==row['archive'] and sha(manifest)==row['manifest_sha256'],
            'Board archive manifest/path differs')
        paths.update((packed,manifest))
    expected=continuation.chance_receipt(arm,cycle,terminal_checkpoint['played_bank'][cycle-1],
        record['paired_sources'],spec,rt,guard)
    actual=read(path)
    require(actual==expected, 'Receipt does not reconstruct from its authentic parent and original boards')
    paths.add(folder/'objects'/terminal_checkpoint['played_bank'][cycle-1]['file'])
    return dict(path=str(path),sha256=sha(path),document=actual),paths


def verify_correction(result=None):
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
    require(not continuation.FAILURE.exists(), 'A new continuation failure has no approved correction')
    if result is not None:
        require(result.get('continuation_amendment_sha256')==sha(continuation.AMENDMENT)
            and result.get('original_failure_sha256')==sha(continuation.legacy.FAILURE), 'Terminal correction identities differ')
    return {continuation.AMENDMENT,continuation.CONTROL,continuation.legacy.FAILURE,continuation.DIAGNOSIS,continuation.PLAN}
