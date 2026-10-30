"""Fixed final banks with the authenticated September 30 interruption included.

The v2 selector and all policy/model math remain unchanged. Only the four
recognized recovery markers are translated after their full prefix proof.
No other repeated or recovered cycle is accepted.
"""
import copy
from pathlib import Path

import stack_context_final_bank_v2 as original
import stack_context_interruption_provenance_v1 as recovery
from stack_context_final_bank_v2 import (
    authenticate_cycle, load_documents, BANK_ORDER, CYCLES, ORIGINAL_PREFIX,
    validate_receipt, read, sha, require,
)

PROOF = recovery.OUT / 'stack-context-interruption-provenance-check-v1-result.json'
READBACK = recovery.OUT / 'stack-context-interruption-readback-v1-result.json'


def _select_with_recovery(result, checkpoints, spec, *, recovery_identity, recovery_outcome, **kwargs):
    """Pure selection for already authenticated inputs; also used by fixtures."""
    prefixes = recovery.validate_prefixes(result['arms'], recovery_outcome,
        amendment_sha256=recovery_identity['amendment_sha256'])
    require(recovery_identity['format'] == 1
        and recovery_identity['result_sha256'] == recovery.publication_sha(recovery_outcome)
        and recovery_identity['recovered_cycles'] == recovery.CYCLES
        and recovery_identity['recovered_actions'] == recovery.ACTIONS
        and recovery_identity['recovered_prefix_sha256'] == prefixes
        and recovery_identity['retained_files_bound'] == 9400
        and recovery_identity['original_registration_sha256'] == kwargs['training_registration_sha256']
        and recovery_identity['seeds_budgets_targets_unchanged'] is True
        and recovery_identity['completed_cycles_refitted'] is False,
        'Selected recovered trajectory is detached from its complete proof')
    translated = copy.deepcopy(result)
    for arm, cycle in recovery.CYCLES.items():
        # v2 accepts only its earlier A-relative cycle-two publication marker.
        # Each additional marker has been authenticated against its immutable
        # prefix and amendment above; translate only these exact four fields.
        translated['arms'][arm]['updates'][cycle-1]['recovered_without_scientific_repeat'] = False
    chosen = original.select_terminal(translated, checkpoints, spec, **kwargs)
    chosen.update(format=3, interruption_recovery=copy.deepcopy(recovery_identity),
        recognized_interrupted_cycles_only=True, original_selection_and_weights_unchanged=True)
    return chosen


def select_terminal(result, checkpoints, spec, **kwargs):
    identity, _ = recovery.verify_recovery(result)
    return _select_with_recovery(result, checkpoints, spec, recovery_identity=identity,
        recovery_outcome=recovery.read(recovery.RESULT), **kwargs)


def verify_correction(result=None):
    paths = set(original.verify_correction(result))
    control, receipt = recovery.read(PROOF), recovery.read(READBACK)
    require(control.get('complete') is True and control.get('passed') is True
        and control['inputs'].get(str(Path(recovery.__file__).resolve())) == sha(recovery.__file__),
        'Qualified recovery verifier is missing or changed')
    require(receipt.get('complete') is True and receipt.get('passed') is True
        and receipt.get('actual_recovered_boundaries_reviewed') is True
        and receipt.get('scientific_fits') == 0 and receipt.get('native_calls') == 0
        and receipt.get('production_modified') is False,
        'Independent completed-boundary readback is missing')
    for proof in (control, receipt):
        for path, digest in proof['inputs'].items():
            require(sha(path) == digest, 'Recovery qualification/readback input changed')
            paths.add(Path(path))
    identity, recovered_paths = recovery.verify_recovery(result)
    require(identity == receipt['recovery'], 'Independent recovery readback and selected trajectory differ')
    paths.update(recovered_paths)
    paths.update((PROOF, READBACK, Path(__file__).resolve(), Path(recovery.__file__).resolve()))
    return paths
