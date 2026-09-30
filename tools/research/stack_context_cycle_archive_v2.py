"""Continuously feed four independent archive jobs; retain the qualified codec."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading
from stack_context_cycle_archive_v1 import make_plan, finish_retirement, verify_index, sha
from owned_research_archive_v1 import pack
from owned_columnar_evaluation_archive_v1 import durable, encoded


def archive_cycle(source, destination, *, root, token, guard, workers=4, retire=True):
    if type(workers) is not int or not 1<=workers<=4:
        raise ValueError('One to four compression workers required')
    plan=make_plan(source,destination,root=root,token=token,guard=guard)
    # Packing is read-only with respect to source members. Distinct subsets of
    # one directory may safely compress concurrently; retirement happens later.
    members=[str(Path(job['source'])/name) for job in plan['jobs'] for name in job['names']]
    outputs=[job['destination'] for job in plan['jobs']]
    if len(members)!=len(set(members)) or len(outputs)!=len(set(outputs)):
        raise ValueError('Overlapping archive jobs')
    mutex=threading.Lock()
    def checked_guard():
        with mutex:
            guard()
    def execute(job):
        manifest=pack(job['source'],job['names'],job['destination'],root=root,token=token,guard=checked_guard)
        dest=Path(job['destination'])
        return dict(archive=dest.name,manifest_sha256=sha(dest.with_suffix('.xz.json')),packed_bytes=manifest['packed_bytes'])
    with ThreadPoolExecutor(max_workers=workers,thread_name_prefix='cycle-archive') as pool:
        # Ordered results, dynamically assigned work: a large job no longer
        # holds up unrelated jobs waiting behind a four-job wave barrier.
        ordered=list(pool.map(execute,plan['jobs']))
    index=dict(format=1,plan_sha256=sha(Path(destination)/'plan.json'),bundles=ordered,
               packed_bytes=sum(row['packed_bytes'] for row in ordered))
    durable(Path(destination)/'index.json',encoded(index))
    if retire:
        return finish_retirement(destination,root=root,token=token,guard=guard,workers=workers)
    verify_index(destination,root=root,token=token,guard=guard,workers=workers)
    return index
