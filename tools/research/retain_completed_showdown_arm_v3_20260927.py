"""Retain only a finished, independently audited arm after training is quiescent.

Do not retire files while the original worker scans its output directory: even
completed-arm deletion could race its size guard. This command never stops it.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import shutil
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle
from hu_paired_continuation_support_20260925 import LOCK, OTHER
from hu_action_integrated_exact_20260925 import bank_args
from compact_showdown_bank_v2 import load_bank
from completed_object_retention_v1 import retain

PREFIX = 'showdown-matched-training-v1'
STORE = Path('S:/GTOpen-research') / PREFIX


def quiescent():
    assert idle() and not LOCK.exists() and not OTHER.exists(), 'Research must be quiescent'
    # Verify processes too; missing/stale status is not evidence of termination.
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.pid == os.getpid(): continue
        if 'python' not in (process.info['name'] or '').lower(): continue
        args = process.info['cmdline']
        assert args is not None, 'Cannot determine Python process ownership'
        for arg in args:
            assert Path(arg).name not in (
                'hu_showdown_matched_training_20260926.py',
                'compact_showdown_training_review_v2.py',
                'compact_showdown_training_review_v3.py',
                'compact_checkpoint_fit_replay_20260926.py',
                'retain_completed_showdown_arm_20260926.py',
                'retain_completed_showdown_arm_v2_20260927.py',
                'retain_completed_showdown_arm_v3_20260927.py',
                'hu_showdown_complete_evaluation_20260926.py',
                'hu_showdown_complete_evaluation_v2_20260926.py',
            ), 'Training, readback or evaluation still owns research files'


def resource_admission(label):
    """Bound archive publication before it can consume scarce disk headroom."""
    from hu_root_retained_storage_admitted_study_20260924 import measure, LIMIT, METADATA_RESERVE
    import owned_research_archive_v1 as codec
    probes = {'9266201-corrected': ('corrected', 110_000_000),
              '9266201-baseline': ('baseline', 140_000_000)}
    assert label in probes, 'Only already-qualified completed bundles admitted'
    kind, allowance = probes[label]
    probe_reg = OUT / f'completed-{kind}-archive-probe-v1-registration.json'
    probe_result = OUT / f'completed-{kind}-archive-probe-v1-result.json'
    prereg, probe = read(probe_reg), read(probe_result)
    assert probe['passed'] and probe['exact_bytes_recovered']
    assert probe['registration_sha256'] == sha(probe_reg)
    # No reliance on an old size estimate if even one source byte changed.
    for path, expected in prereg['inputs'].items():
        assert sha(path) == expected, path
    objects = STORE / label / 'objects'
    expected_names = {Path(p).name for p in prereg['inputs'] if Path(p).parent == objects}
    assert expected_names == {p.name for p in objects.iterdir()}
    assert len(expected_names) == probe['objects']
    # Keep 10 MB inside the allowance for manifests/results and roundoff.
    packed_limit = min(codec.MAX_PACKED, allowance - 10_000_000)
    assert probe['packed_bytes'] <= packed_limit
    inventory = measure()
    quiescent()
    total = sum(row['allocated_file_bytes'] for row in inventory)
    projected = total + allowance + METADATA_RESERVE
    dest = OUT / f'completed-object-retention-{label}-v3-admission.json'
    assert not dest.exists(), 'Preserve previous admission; inspect before retry'
    admission = dict(inventory=inventory, allocated_bytes=total,
        new_archive_allowance=allowance, packed_limit=packed_limit,
        metadata_reserve=METADATA_RESERVE, limit=LIMIT, projected_bytes=projected,
        admitted=projected <= LIMIT, arm=label,
        inputs={str(p): sha(p) for p in (probe_reg, probe_result, Path(__file__).resolve())},
        source_probe_inputs_rechecked=True, production_modified=False)
    save(dest, admission)
    print(json.dumps({k: v for k, v in admission.items() if k not in ('inventory', 'inputs')}), flush=True)
    assert admission['admitted'], 'Global storage allowance exceeded'
    # This is process-local only. Frozen codec source remains byte-identical.
    # pack checks this bound on the compressed bytes BEFORE opening its output.
    codec.MAX_PACKED = packed_limit
    return dest


def run(label):
    quiescent()
    admission_path = resource_admission(label)
    started = time.monotonic()
    def guard():
        assert time.monotonic() - started < 600 and idle()
        assert psutil.virtual_memory().available >= 20_000_000_000
        assert shutil.disk_usage('S:/').free >= 40_000_000_000
    guard()
    reg_path = OUT / f'{PREFIX}-registration.json'
    reg = read(reg_path)
    assert reg['store'] == str(STORE)
    arms = [a for a in reg['arms'] if a['name'] == label]
    assert len(arms) == 1
    case = STORE / label
    result_path = case / 'result.json'
    result = read(result_path)
    assert result['name'] == label and result['store'] == str(case)
    assert result['config'] == arms[0]['config']
    assert result['completed_iterations'] == 78 and result['final_restore_verified'] is True
    status = read(OUT / f'{PREFIX}-status.json')
    assert status['state'] in ('complete', 'failed'), 'Training terminal status required'
    audit_path = OUT / f'showdown-training-readback-v2-{label}-0078-result.json'
    audit = read(audit_path)
    assert audit['passed'] and audit['complete_arm'] and audit['completed_updates'] == 78
    assert audit['source_registration_sha256'] == sha(reg_path)
    controls = [OUT / f'{p}-result.json' for p in (
        'archived-checkpoint-objects-control-v1', 'compact-showdown-bank-control-v2',
        'completed-object-retention-control-v1')]
    assert all(read(p)['passed'] for p in controls)
    intent_path = case / 'objects-retention-intent.json'
    if not intent_path.exists():
        models, weights, identity = load_bank(OUT, label, completed=78,
            purpose='implementation-control', bank_args=bank_args((OUT/'bb-context-candidate.json').read_text()), guard=guard)
        assert len(models) == 78 and identity['excluded_generation'] == 78
        del models, weights
    # On interrupted retirement, durable intent already records successful full
    # admission. Recheck every evidence hash without requiring now-retired raws.
    paths = [admission_path, reg_path, result_path, audit_path,
        OUT / f'showdown-training-readback-v2-{label}-0078-registration.json',
        *controls, Path(__file__).resolve(), ROOT/'tools/research/completed_object_retention_v1.py',
        ROOT/'tools/research/compact_showdown_bank_v2.py', ROOT/'tools/research/archived_checkpoint_objects_v1.py']
    hashes = {str(p):sha(p) for p in paths}
    evidence = dict(arm=label, completed_updates=78, inputs=hashes, full_bank_admitted=True)
    def eligibility():
        quiescent()
        for p,h in hashes.items(): assert sha(p) == h
        return evidence
    token = read(STORE/'archive-owner.json')['token']
    result = retain(case, root=STORE, token=token, eligibility=eligibility, guard=guard)
    # The actual full reader must work after retirement, including all admission
    # gates and every played generation, before reporting success.
    models, weights, identity = load_bank(OUT, label, completed=78,
        purpose='implementation-control', bank_args=bank_args((OUT/'bb-context-candidate.json').read_text()), guard=guard)
    assert len(models) == 78 and identity['objects_retention_sha256'] == result['receipt_sha256']
    report = dict(passed=True, arm=label, **result, bank_identity=identity,
        seconds=time.monotonic()-started, production_modified=False, legacy_files_modified=False)
    dest = OUT / f'completed-object-retention-{label}-v3-result.json'
    assert not dest.exists()
    save(dest, report)
    print(json.dumps({k:v for k,v in report.items() if k!='bank_identity'}))


if __name__ == '__main__':
    assert len(sys.argv) == 2
    run(sys.argv[1])
