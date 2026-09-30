"""Connect frozen-policy native evaluation to the durable fixed-budget journal.

Admission, banks, locks and resource guards belong to the caller. This driver
never trains, selects checkpoints, changes the chance stream or retries a
partially evaluated batch. It may stop only before starting a fresh batch.
"""
from crossed_complete_policy_batch_v1 import evaluate_batch
from stack_context_matched_analysis_v1 import context_analysis,DEALS


def collect(journal, *, context_path, banks, cache, query_executable, evaluation_executable,
            guard, stop_requested=lambda:False, on_progress=lambda count:None):
    guard()
    state = journal.prefix(verify_archives=True)
    # Recovery only publishes already complete output; it never re-evaluates.
    recovered = journal.recover_next(retire=True)
    if recovered is not None:
        state = journal.prefix(verify_archives=True)
    on_progress(state['completed_deals'])
    while state['completed_deals'] < DEALS:
        guard()
        if stop_requested():
            return dict(complete=False,completed_deals=state['completed_deals'],boundary='before-next-fresh-batch')
        batch,folder = journal.begin()
        evaluate_batch(batch=batch,folder=folder,context_path=context_path,banks=banks,cache=cache,
            query_executable=query_executable,evaluation_executable=evaluation_executable,guard=guard)
        record = journal.recover_next(retire=True)
        if record is None or record['completed_deals'] != state['completed_deals']+len(batch['deals']):
            raise ValueError('Completed native batch did not advance the exact committed prefix')
        state = journal.prefix()
        on_progress(state['completed_deals'])
    # Authentication of every archived source precedes the single final look.
    state = journal.prefix(verify_archives=True)
    return dict(complete=True,completed_deals=DEALS,last_commit_sha256=state['previous_commit_sha256'],
                analysis=context_analysis(state['values'],depth=journal.plan['depth'],dead_money=.5))
