"""Fixed stratified-versus-board-root comparison; no sampling or fitting here.

Readiness is read-only. Actual loading requires both complete, independently
audited 78-generation histories. A two-generation bank control is a prerequisite,
not qualification of these complete banks or of their playing strength.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import time
import numpy as np
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
from weighted_complete_evaluation_support_v1 import (
    CONTEXT, MATRIX, CATALOG, args_for_banks, catalog_roots, setup_cuda,
    complete_training_paths as historical_training_paths,
    WeightedReferenceBank)
from weighted_completed_bank_v1 import load_bank as weighted_bank
from board_completed_bank_v1 import load_bank as board_bank
from weighted_training_gpu_bank_v1 import WeightedCudaBank64
from board_training_gpu_bank_v1 import BoardRootCudaBank64
from board_training_policy_v1 import average as board_average
from board_matched_prefix_v2 import specification

ARMS = ('9266201-stratified', '9266201-board-root',
        '9266301-stratified', '9266301-board-root')
TEST_DEALS = 65536
TEST_SEED = 9281101
TRAINING = OUT / 'board-root-matched-continuation-v1-registration.json'
TRAINING_RESULT = OUT / 'board-root-matched-continuation-v1-result.json'
AUDIT_REG = OUT / 'board-matched-complete-readback-v1-registration.json'
AUDIT_RESULT = OUT / 'board-matched-complete-readback-v1-result.json'
CUDA_REG = OUT / 'board-training-bank-cuda-control-v1-registration.json'
CUDA_RESULT = OUT / 'board-training-bank-cuda-control-v1-result.json'
PLAN = OUT / 'BOARD-ROOT-MATCHED-STUDY-PLAN.md'
REQUIRED = (TRAINING, TRAINING_RESULT, AUDIT_REG, AUDIT_RESULT,
            CUDA_REG, CUDA_RESULT)


def validate_design(control, candidates):
    """Reject changed seed pairing, learning budget or any extra treatment."""
    old = control['arms']
    if (control['generations'] != 78 or len(old) != 2 or len(candidates) != 2
            or [a['name'] for a in old] != list(ARMS[::2])
            or [a['name'] for a in candidates] != list(ARMS[1::2])):
        raise ValueError('Fixed two-seed 78-generation pairing required')
    for index, (before, after) in enumerate(zip(old, candidates, strict=True)):
        a, b = before['config'], after['config']
        changed = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
        if (after['control'] != before['name'] or changed != {'policy_type', 'board_root'}
                or b['board_root']['board_seed'] != 9281001 + index
                or b['board_root']['boards_per_generation'] != 4
                or b['board_root']['physical_budget'] != 512):
            raise ValueError('Only the prospectively fixed board-root treatment may differ')
        if tuple(b[k] for k in ('deals_per_generation', 'deals_per_subbatch',
                'reservoir_capacity', 'fit_steps', 'chunk_size', 'learning_rate')) != (
                512, 64, 262144, 512, 4096, .003):
            raise ValueError('Changed learning budget')


def design():
    candidates, paths, _, _ = specification()
    validate_design(read(OUT / 'weighted-stratified-study-v1-registration.json'), candidates)
    return candidates, paths


def readiness():
    candidates, paths = design()
    # Check completed historical controls even when the candidates are pending.
    paths.extend(historical_training_paths())
    pending = [str(p) for p in REQUIRED if not p.exists()]
    if pending:
        return candidates, paths, pending
    reg, result, audit_reg, audit = map(read, (TRAINING, TRAINING_RESULT, AUDIT_REG, AUDIT_RESULT))
    if (reg['arms'] != candidates or reg['generations_per_arm'] != 78
            or not result['passed'] or not result['training_complete']
            or result['registration_sha256'] != sha(TRAINING)
            or result['generations_per_arm'] != 78
            or [r['arm'] for r in result['arms']] != list(ARMS[1::2])
            or not audit['passed'] or not audit['complete_training']
            or audit['registration_sha256'] != sha(AUDIT_REG)
            or audit['source_result_sha256'] != sha(TRAINING_RESULT)
            or [r['arm'] for r in audit['arms']] != list(ARMS[1::2])):
        raise ValueError('Matching complete candidate training and independent audit required')
    for end, checked in zip(result['arms'], audit['arms'], strict=True):
        if (end['completed'] != 78 or checked['generations'] != 78
                or checked['boards_checked'] != 312 or checked['physical_roots_checked'] != 39936
                or checked['final_checkpoint'] != end['checkpoint']):
            raise ValueError('Incomplete candidate audit')
    cuda_reg, cuda = read(CUDA_REG), read(CUDA_RESULT)
    if (not cuda['passed'] or cuda['registration_sha256'] != sha(CUDA_REG)
            or not cuda['gpu_used'] or cuda['trained_models'] != 2
            or cuda['full_78_model_bank_qualified'] is not False):
        raise ValueError('Genuine typed-bank CUDA control required')
    # This is an input gate. Full-bank CUDA/CPU and transport checks are still
    # required by the subsequent evaluation control before fresh test deals.
    for bound in (reg, cuda_reg):
        for p, h in bound['inputs'].items():
            if sha(p) != h:
                raise ValueError('Changed registered source: ' + p)
    for p, h in audit_reg['inputs'].items():
        if Path(p).suffix == '.py' and sha(p) != h:
            raise ValueError('Changed independently audited implementation: ' + p)
    paths.extend(REQUIRED)
    return candidates, paths, []


class BoardReferenceBank:
    def __init__(self, documents, weights, args, root_config):
        self.documents, self.weights = documents, weights
        self.args = {k: v for k, v in args.items() if k != 'context_source'}
        self.args['root_config'] = root_config

    def average(self, queries, *, guard):
        return board_average(queries, self.documents, completed_iterations=78,
                             weights_by_player=self.weights, guard=guard,
                             device='cpu', **self.args)


def load_banks(*, guard, reference=False):
    candidates, _, pending = readiness()
    if pending:
        raise ValueError('Complete candidate banks are not ready: ' + ', '.join(pending))
    args = args_for_banks()
    banks, references, identities, timings = [], [], [], []
    expected_weights = np.tile(np.arange(1., 79.), (2, 1))
    for index, name in enumerate(ARMS):
        guard()
        began = time.monotonic()
        docs, weights, identity = (board_bank if index % 2 else weighted_bank)(
            name, bank_args=args, guard=guard)
        if (len(docs) != 78 or [m['generation'] for m in docs] != list(range(78))
                or not np.array_equal(weights, expected_weights)
                or identity['arm'] != name or identity['completed_iterations'] != 78
                or identity['purpose'] != 'evaluation' or identity['unplayed_excluded']['generation'] != 78):
            raise ValueError('Complete ordered played histories with weights 1-78 required')
        if index % 2:
            cfg = candidates[index // 2]['config']['board_root']
            if identity['root_config'] != cfg:
                raise ValueError('Candidate root configuration differs from the fixed treatment')
            bank = BoardRootCudaBank64(docs, weights, completed_iterations=78,
                models_per_chunk=8, guard=guard, root_config=cfg, **args)
            if reference:
                references.append(BoardReferenceBank(docs, weights, args, cfg))
        else:
            bank = WeightedCudaBank64(docs, weights, completed_iterations=78,
                                      models_per_chunk=8, guard=guard, **args)
            if reference:
                references.append(WeightedReferenceBank(docs, weights, args))
        banks.append(bank)
        identities.append(identity)
        timings.append(time.monotonic() - began)
    return banks, references, identities, timings, args


if __name__ == '__main__':
    _, paths, pending = readiness()
    print(json.dumps(dict(complete_training_available=not pending, pending=pending,
        paths_checked=len(paths), arms=ARMS, test_deals=TEST_DEALS, test_seed=TEST_SEED,
        full_bank_control_required=True, fresh_test_sampling_started=False,
        production_modified=False)), flush=True)
