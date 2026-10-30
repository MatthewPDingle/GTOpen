"""Finish read-only bank verification after the retention command's time guard.

The original archive, retirement receipt, admission, and command are immutable.
This result qualifies the completed retention only, never poker accuracy.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle
from hu_action_integrated_exact_20260925 import bank_args
from compact_showdown_bank_v2 import load_bank
from retain_completed_showdown_arm_v3_20260927 import quiescent, STORE

PREFIX = 'completed-retention-baseline-final-readback-v1'


def main():
    quiescent()
    started = time.monotonic()
    last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        assert now-started < 600
        if now-last >= 2:
            assert idle() and psutil.virtual_memory().available >= 20_000_000_000
            last = now
    case = STORE/'9266201-baseline'
    receipt = case/'objects-retention.json'
    value = read(receipt)
    assert value['passed'] and value['originals_retired']
    assert not any((case/'objects').iterdir())
    # Original durable intent binds its precise admission and implementation.
    for path, expected in value['evidence']['inputs'].items():
        assert sha(path) == expected, path
    paths = [receipt, case/'objects.xz', case/'objects.xz.json',
             case/'objects-retention-intent.json', Path(__file__).resolve(),
             ROOT/'tools/research/compact_showdown_bank_v2.py']
    inputs = {str(p): sha(p) for p in paths}
    registration = OUT/f'{PREFIX}-registration.json'
    result_path = OUT/f'{PREFIX}-result.json'
    assert not registration.exists() and not result_path.exists()
    save(registration, dict(inputs=inputs, maximum_seconds=600, gpu_used=False,
        prior_command_outcome='600-second guard reached during final full-bank load after durable retirement receipt',
        scope='Read-only completion of the already-retained baseline bank check'))
    try:
        models, weights, identity = load_bank(OUT, '9266201-baseline', completed=78,
            purpose='implementation-control', bank_args=bank_args((OUT/'bb-context-candidate.json').read_text()),
            guard=guard)
        assert len(models) == 78 and identity['excluded_generation'] == 78
        assert identity['objects_retention_sha256'] == sha(receipt)
        for path, expected in inputs.items():
            guard(); assert sha(path) == expected, path
        for path, expected in value['evidence']['inputs'].items():
            guard(); assert sha(path) == expected, path
        manifest = read(case/'objects.xz.json')
        result = dict(passed=True, registration_sha256=sha(registration),
            bank_identity=identity, played_generations=78, excluded_generation=78,
            receipt_sha256=sha(receipt), objects=len(manifest['members']),
            raw_bytes=sum(row['bytes'] for row in manifest['members']),
            packed_bytes=manifest['packed_bytes'], seconds=time.monotonic()-started,
            prior_command_success=False, final_bank_readback_complete=True,
            original_evidence_modified=False, production_modified=False, gpu_used=False,
            accuracy_qualified=False)
        save(result_path, result)
        print(json.dumps({k:v for k,v in result.items() if k != 'bank_identity'}), flush=True)
    except BaseException as exc:
        save(result_path, dict(passed=False, error=repr(exc), registration_sha256=sha(registration)))
        raise


if __name__ == '__main__':
    main()
