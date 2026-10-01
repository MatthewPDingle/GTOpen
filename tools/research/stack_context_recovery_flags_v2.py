"""Recognize only the independently authenticated training recovery boundaries.

The caller must obtain the interruption identity through the unchanged
verify_recovery/verify_correction gates. This only fixes per-cycle metadata
recognition; archive and physical chance reconstruction remain mandatory.
"""
CYCLES = {'A-baseline': 4, 'A-relative': 4, 'B-baseline': 4, 'B-relative': 3}
ACTIONS = {arm: ('publish-already-complete-checkpoint' if arm in ('A-baseline', 'B-relative')
                 else 'continue-retained-partial-cycle') for arm in CYCLES}
AMENDMENT_SHA = '1ed2370e7c48f330ddef537d24d76669540ce7cf83c44bb97ce49e6701859d53'
REGISTRATION_SHA = 'ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def validate(arm, cycle, record, *, receipt_sha256, amendment, interruption):
    require(arm in CYCLES and type(cycle) is int and 1 <= cycle <= 64
            and record['cycle'] == cycle, 'Unknown arm or cycle')
    require(interruption['format'] == 1 and interruption['amendment_sha256'] == AMENDMENT_SHA
            and interruption['original_registration_sha256'] == REGISTRATION_SHA
            and interruption['recovered_cycles'] == CYCLES and interruption['recovered_actions'] == ACTIONS
            and interruption['retained_files_bound'] == 9400
            and interruption['seeds_budgets_targets_unchanged'] is True
            and interruption['completed_cycles_refitted'] is False,
            'Missing exact independently authenticated interruption')
    is_interrupted = cycle == CYCLES[arm]
    is_legacy_recovery = arm == 'A-relative' and cycle == 2
    expected = is_interrupted or is_legacy_recovery
    original_count = 2 if arm == 'A-baseline' else 1
    if cycle > original_count:
        require(record['chance_receipt_sha256'] == receipt_sha256
                and record['continuation_amendment_sha256'] == amendment
                and record['recovered_without_scientific_repeat'] is expected,
                'Undocumented correction/recovery')
    elif 'recovered_without_scientific_repeat' in record:
        require(record['recovered_without_scientific_repeat'] is False, 'Unexpected original-cycle recovery')
    if is_interrupted:
        require(record['interruption_recovery_amendment_sha256'] == interruption['amendment_sha256']
                and record['recovery_action'] == ACTIONS[arm], 'Recovery detached from its verified outcome')
    else:
        require('interruption_recovery_amendment_sha256' not in record
                and 'recovery_action' not in record, 'Recovery extended beyond its declared boundary')
