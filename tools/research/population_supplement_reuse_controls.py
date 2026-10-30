"""Read-only admission controls using an already completed real worker."""
import json
import full_population_transfer_queue_20260920 as queue


def main():
    prefix = 'held-validation95-ab-000'
    board = queue.read(queue.OUT/(prefix+'-manifest.json'))['boards'][0]['board']
    frozen = {queue.rel(p):queue.sha(p) for p in [queue.EXE,queue.SUB,*queue.SOURCES.values()]}
    queue.validate_worker(prefix,board,queue.SOURCES['ab'],frozen)
    controls = [
        ('wrong_physical_board','AsAcQh',queue.SOURCES['ab'],frozen),
        ('wrong_source',board,queue.SOURCES['report47'],frozen),
        ('changed_executable',board,queue.SOURCES['ab'],{**frozen,queue.rel(queue.EXE):'0'*64}),
        ('changed_subtree',board,queue.SOURCES['ab'],{**frozen,queue.rel(queue.SUB):'0'*64}),
    ]
    rejected = []
    for name,test_board,source,hashes in controls:
        try:
            queue.validate_worker(prefix,test_board,source,hashes)
        except (AssertionError,KeyError):
            rejected.append(name)
        else:
            raise AssertionError(name+' was accepted')
    prior=queue.read(queue.OUT/'held-validation95-ab-result.json')
    packed=queue.OUT/(prefix+'-result.json.gz')
    queue.verify_previous_aggregate(prior,[packed])
    altered={**prior,'inputs_sha256':{**prior['inputs_sha256'],queue.rel(packed):'0'*64}}
    try:
        queue.verify_previous_aggregate(altered,[packed])
    except AssertionError:
        rejected.append('changed_original_worker_archive')
    else:
        raise AssertionError('changed original archive was accepted')
    # Only exercise the incomplete-queue control while that state really
    # exists; do not fabricate or alter the running queue's status file.
    if queue.read(queue.OUT/'overnight-accuracy-status.json')['step'] != 'complete-awaiting-scientific-review':
        try:
            queue.preflight()
        except AssertionError:
            rejected.append('unfinished_original_queue')
        else:
            raise AssertionError('unfinished queue was accepted')
    print(json.dumps(dict(real_worker_accepted=True,negative_controls_rejected=rejected,gpu_work_started=False)))


if __name__ == '__main__':
    main()
