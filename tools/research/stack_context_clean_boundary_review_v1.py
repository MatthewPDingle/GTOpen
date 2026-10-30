"""Read-only qualification of a clean stop of the already admitted evaluation.

No model inference, native execution, fits, new scientific deals or interim
comparison look. Replay recorded chance/commit lineage and validate the last
archive at each depth, using the original qualified journal implementation.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import concurrent.futures
import hashlib
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, r'T:\Dev\GTOpen\tools\research')
import psutil
import stack_context_matched_evaluation_v5 as ev
import stack_context_matched_readback_v6 as reader
import stack_context_pressure_evaluation_handoff_v1 as helper
from stack_context_evaluation_journal_v1 import EvaluationJournal

EXPECTED_COUNTS = {20:4096, 40:4096, 60:4096, 100:4096, 150:4096, 200:4096, 400:2208}
TARGET = Path(__file__).with_name('clean-boundary-review-v1.json')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def dead(pid, created):
    try:
        p = psutil.Process(pid)
        return abs(p.create_time()-created) >= .01 or not p.is_running()
    except psutil.NoSuchProcess:
        return True

def validate_counts(counts, pending, status, has_scientific_failure, invocation_count):
    require(counts == EXPECTED_COUNTS, 'Unexpected saved evaluation prefix')
    require(not pending, 'An uncommitted scientific batch must not be retried')
    require(not has_scientific_failure, 'Scientific failure requires separate review')
    require(status['stage'] == 'complete-boundary-awaiting-resume'
            and status['depth'] == 400 and status['completed_deals'] == 2208,
            'Not the reviewed clean stop')
    require(invocation_count == 1, 'An explicit continuation has already been attempted')

def review():
    began = time.monotonic()
    require(not TARGET.exists(), 'Preserve existing review evidence')
    spec, attempt = ev.read(ev.REG), ev.read(ev.ATTEMPT)
    original_status = ev.read(ev.STATUS)
    require(not any(p.exists() for p in (ev.LOCK, ev.OTHER, ev.RESULT, ev.FAILURE,
            reader.ATTEMPT, reader.OUTPUT, reader.FAILED, helper.OWNER, helper.RESULT)),
            'Live ownership or terminal/started consumer')
    require(attempt['registration_sha256'] == ev.sha(ev.REG), 'Changed original registration')
    require(spec['maximum_invocation_seconds'] == 12*3600
            and spec['maximum_evaluation_seconds'] == 72*3600
            and time.time() < attempt['admitted_unix']+72*3600,
            'Original time windows must remain unchanged')
    require(spec['depths'] == list(EXPECTED_COUNTS) and spec['deals_per_depth'] == 4096
            and spec['batch_size'] == 32 and spec['one_final_look'] is True
            and spec['seed_by_depth'] == {str(d):9309000+d for d in EXPECTED_COUNTS},
            'Changed scientific budget, seed or final-look policy')
    require(ev.read(ev.STORE/'bank-identities.json') == spec['banks'], 'Changed frozen banks')
    helper_attempt = helper.read(helper.ATTEMPT)
    require(dead(attempt['pid'], attempt['process_created'])
            and dead(helper_attempt['pid'], helper_attempt['created']), 'Original owners still live')
    require(attempt['pid'] == 101396 and abs(attempt['process_created']-1790836790.4066665)<.01
            and helper_attempt['pid'] == 101740
            and abs(helper_attempt['created']-1790820578.6834643)<.01, 'Unexpected original identities')
    prefix = ev.OUT/'stack-context-pressure-evaluation-handoff-v1-002-evaluation'
    start = ev.read(str(prefix)+'-started.json')
    ended = ev.read(str(prefix)+'-finished.json')
    require(all(ended[k] == start[k] for k in start) and ended['exit_code'] == 0
            and start['pid'] == attempt['pid']
            and abs(start['created']-attempt['process_created'])<.01
            and start['command'] == ['C:/Program Files/Python312/python.exe', '-B',
                str(Path(ev.__file__)), '--run'], 'Original invocation did not exit cleanly')
    for stream in ('stdout', 'stderr'):
        require(ev.sha(str(prefix)+'-'+stream+'.log') == ended[stream+'_sha256'], 'Changed original exit log')
    helper_failure = helper.read(helper.FAILED)
    require(helper_failure['error'] == "ValueError('Child returned without terminal completion; no automatic resume')"
            and helper_failure['automatic_retry_allowed'] is False
            and helper_failure['preserve_evidence'] is True
            and helper_failure['production_modified'] is False, 'Unexpected automation failure')
    invocations = list(ev.STORE.glob('invocation-*.json'))
    require(len(invocations) == 1, 'Previous continuation already attempted')
    invocation = ev.read(invocations[0])
    require(invocation['resume'] is False and invocation['pid'] == attempt['pid']
            and abs(invocation['process_created']-attempt['process_created']) < .01,
            'Detached original invocation')
    require(ev.production_available() and psutil.virtual_memory().available >= 40_000_000_000,
            'Yield to current work or memory pressure')
    items = list(spec['inputs'].items())
    def hash_one(item):
        path, expected = item
        require(ev.sha(path) == expected, 'Changed registered input: '+path)
        return path
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for i, _ in enumerate(pool.map(hash_one, items), 1):
            if i % 500 == 0:
                print(json.dumps(dict(stage='registered-inputs-authenticated', completed=i, total=len(items))), flush=True)
    prepared = ev.read(ev.OUT/'stack-context-population-v1-result.json')
    rows = []; pending = []
    for depth, count in EXPECTED_COUNTS.items():
        record = next(r for r in prepared['contexts'].values() if r['depth']==depth)
        source = Path(record['context_path']).read_text()
        folder = ev.STORE/f'stack-{depth}'
        journal = EvaluationJournal(folder, context_source=source, registration_sha256=ev.sha(ev.REG),
            bank_identities_sha256=ev.sha(ev.STORE/'bank-identities.json'),
            cache_sha256=spec['cache_sha256'], guard=lambda:None)
        state = journal.prefix(verify_archives=False)
        expected_intents = {f'test-{offset:06d}'+suffix for offset in range(0,count,32)
                            for suffix in ('.claim.json','.json')}
        expected_work = {f'test-{offset:06d}'+suffix for offset in range(0,count,32)
                         for suffix in ('.claim.json','.receipt.json')}
        actual_intents = {p.name for p in (folder/'intents').iterdir()}
        actual_work = {p.name for p in (folder/'archive'/'.batch-work').iterdir()}
        require(actual_intents == expected_intents and actual_work == expected_work,
                'Incomplete, additional or partially published batch at '+str(depth))
        require(state['completed_deals'] == count, 'Changed expected prefix count')
        final_paths = list(folder.glob(f'commit-{count:06d}-*.json'))
        require(len(final_paths) == 1, 'Ambiguous terminal prefix')
        last = ev.read(final_paths[0]); offset = count-32
        intent = ev.read(folder/'intents'/f'test-{offset:06d}.json')
        parts = journal._proof(f'test-{offset:06d}', last['manifest_sha256'], last['summary_sha256'], full=True)
        summary = journal._evidence(parts, intent)
        require(last['values'] == summary['values'], 'Last saved batch differs from completed native evidence')
        rows.append(dict(depth=depth, completed_deals=count, committed_batches=count//32,
            journal_owner_sha256=journal.owner, last_commit_sha256=state['previous_commit_sha256'],
            exact_intent_and_retired_archive_claim_sets=True, last_archive_validated=True))
        print(json.dumps(dict(stage='clean-complete-prefix-reviewed', depth=depth, completed_deals=count)), flush=True)
    validate_counts({r['depth']:r['completed_deals'] for r in rows}, pending,
                    original_status, ev.FAILURE.exists(),len(invocations))
    require(ev.read(ev.STATUS) == original_status and not any(p.exists() for p in
            (ev.LOCK,ev.OTHER,helper.OWNER,ev.FAILURE,ev.RESULT,reader.ATTEMPT)), 'State changed during review')
    bindings = [ev.REG,ev.ATTEMPT,ev.STATUS,ev.STORE/'bank-identities.json',*invocations,
        helper.ATTEMPT,helper.FAILED,Path(str(prefix)+'-started.json'),Path(str(prefix)+'-finished.json'),
        Path(str(prefix)+'-stdout.log'),Path(str(prefix)+'-stderr.log'),Path(ev.__file__),
        Path(reader.__file__),Path(helper.__file__),Path(__file__).resolve()]
    result = dict(complete=True, passed=True, qualified_clean_boundary_continuation=True,
        review_seconds=time.monotonic()-began, unix=time.time(), registration_sha256=ev.sha(ev.REG),
        original_admitted_unix=attempt['admitted_unix'], original_evaluation_deadline_unix=attempt['admitted_unix']+72*3600,
        verified_registered_inputs=len(items), contexts=rows, remaining_deals=1888,
        read_only_review=True, interim_comparison_values_inspected=False,
        new_scientific_deals=False, fitting=False, model_inference=False, native_execution=False,
        gpu_initialized=False, original_helper_failure_preserved=True,
        partial_scientific_batch_retry_allowed=False, resume_attempts_allowed=1,
        original_budget_seeds_selection_math_and_source_unchanged=True,
        independent_readback_outstanding=True, broad_goal_complete=False,
        inputs={str(p):ev.sha(p) for p in bindings})
    TARGET.write_text(json.dumps(result,sort_keys=True,separators=(',',':')),encoding='utf-8')
    print(json.dumps(dict(passed=True,result=str(TARGET),sha256=ev.sha(TARGET),seconds=result['review_seconds'])),flush=True)

if __name__ == '__main__':
    review()
