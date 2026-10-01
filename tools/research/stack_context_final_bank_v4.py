"""Original final-bank selection, additionally bound to the exact clean storage stop."""
from pathlib import Path
import copy
import stack_context_final_bank_v3 as original
import stack_context_pressure_provenance_v1 as pressure
import stack_context_interruption_provenance_v1 as recovery
from stack_context_final_bank_v3 import authenticate_cycle,load_documents,BANK_ORDER,CYCLES,ORIGINAL_PREFIX,validate_receipt,read,sha,require
PROOF,READBACK=original.PROOF,original.READBACK


def _select_with_pressure(result,checkpoints,spec,*,pressure_identity,**kwargs):
    pressure.validate_prefixes(result['arms'],pressure_identity)
    require(result.get('resource_pressure_failure_sha256')==pressure_identity['pressure_failure_sha256']
        and result.get('resource_pressure_review_sha256')==pressure_identity['boundary_review_sha256']
        and result.get('operational_admission_sha256')==pressure_identity['operational_admission_sha256']
        and result.get('original_scientific_worker_unchanged') is True
        and result.get('cycles_retried') is False,'Terminal pressure provenance differs')
    chosen=original.select_terminal(result,checkpoints,spec,**kwargs)
    chosen.update(format=4,resource_pressure=copy.deepcopy(pressure_identity),
        recognized_clean_pressure_stop_only=True)
    return chosen


def select_terminal(result,checkpoints,spec,**kwargs):
    identity,_=pressure.verify_pressure(result)
    return _select_with_pressure(result,checkpoints,spec,pressure_identity=identity,**kwargs)


def verify_correction(result=None):
    paths = set(pressure.verify_prior_correction(result))
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
