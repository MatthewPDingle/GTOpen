"""Explicit review of the failed read-only checker; never retry scientific work."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import time
import psutil

ROOT = Path(r'T:\Dev\GTOpen')
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PINS = {
    'stack-context-matched-evaluation-v5-terminal-transition-20261002-v1.json': '8966201ec14f0f29cccb1e0076bf3618d30bba8929a425c957150156e5ff6c53',
    'stack-context-readback-recovery-diagnosis-20261002-v1.json': '224d55eb5dd88b2906adc6419f3c7993eb64a9cf1bf973056247589fa628154a',
    'stack-context-independent-chance-audit-v2-check-result.json': '17958a4cf2720a3d418ec26d50dd6bb17cb4085f7b71af7a033e2eede18476d9',
}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def read(path):
    return json.loads(Path(path).read_bytes())

def dead(record, key='created'):
    try:
        p = psutil.Process(record['pid'])
        return abs(p.create_time() - record[key]) >= .01 or not p.is_running()
    except psutil.NoSuchProcess:
        return True

def reviewed_failure():
    inputs = {}
    evidence = {}
    for name, digest in PINS.items():
        path = OUT / name
        require(sha(path) == digest, 'Changed explicit checker-defect review')
        value = read(path)
        require(value['complete'] and value['passed'] and not value['production_modified'], 'Incomplete checker-defect review')
        for p, identity in value['inputs'].items():
            require(p not in inputs or inputs[p] == identity, 'Conflicting reviewed input')
            inputs[p] = identity
        inputs[str(path)] = digest
        evidence[name] = value
    chance = evidence['stack-context-independent-chance-audit-v2-check-result.json']
    diagnosis = evidence['stack-context-readback-recovery-diagnosis-20261002-v1.json']
    require(chance['actual_independent_chance_cycles'] == diagnosis['actual_metadata_cycles_checked'] == 256
            and chance['archive_and_chance_source_unchanged_except_documented_recovery_gate'] is True
            and len(chance['original_false_positive_reproduced']) == len(diagnosis['mismatches']) == 4
            and len(diagnosis['synthetic_negative_cases_refused']) == 17,
            'Actual documented recovery correction not qualified')
    require(sha(ROOT / 'tools/research/stack_context_independent_chance_audit_v2.py') == chance['candidate_source_sha256']
            and sha(ROOT / 'tools/research/stack_context_recovery_flags_v2.py') == diagnosis['candidate_sha256'], 'Corrected component source changed')
    def check(item):
        p, digest = item
        require(sha(p) == digest, 'Changed existing audit evidence: ' + p)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(check, inputs.items()))
    attempt_path = OUT / 'stack-context-matched-readback-v6-attempt.json'
    attempt = read(attempt_path)
    start_path = OUT / 'stack-context-resumed-readback-v1-reader-started.json'
    end_path = OUT / 'stack-context-resumed-readback-v1-reader-finished.json'
    start, end = read(start_path), read(end_path)
    helper = read(OUT / 'stack-context-resumed-readback-v1-attempt.json')
    failed = read(OUT / 'stack-context-matched-readback-v6-failure.json')
    require(attempt['pid'] == start['pid'] == 116480 and abs(attempt['process_created'] - 1790890806.0150957) < .01
            and abs(start['created'] - attempt['process_created']) < .01
            and end['exit_code'] == 1 and all(end[k] == start[k] for k in start)
            and start['parent_pid'] == helper['pid'] == 114432 and dead(start) and dead(helper)
            and failed['error'] == "ValueError('Undocumented correction/recovery')"
            and failed['automatic_retry_allowed'] is False and failed['preserve_evidence'] is True
            and attempt['new_scientific_work'] is False and attempt['maximum_seconds'] == 43200
            and attempt['torch_threads'] == 4 and attempt['test_batch_starts'] == [0, 4064], 'Different failed read-only audit')
    deadline = attempt['process_created'] + attempt['maximum_seconds']
    require(time.time() < deadline, 'Original audit deadline has expired')
    require(not any((OUT / (name + suffix + '.json')).exists() for name, suffix in (
        ('stack-context-matched-evaluation-v5', '-failure'), ('stack-context-clean-boundary-resume-v1', '-failure'),
        ('stack-context-matched-readback-v6', '-result'), ('stack-context-resumed-readback-v1', '-owner'))), 'Scientific failure, completed audit or unreleased old owner')
    terminal_path = OUT / 'stack-context-matched-evaluation-v5-result.json'
    require(sha(terminal_path) == start['evaluation_result_sha256'], 'Failed checker used another evaluation')
    inputs[str(Path(__file__).resolve())] = sha(__file__)
    return dict(original_deadline_unix=deadline, original_failed_attempt=attempt,
        failed_readback_sha256=sha(OUT / 'stack-context-matched-readback-v6-failure.json'), inputs=inputs)
