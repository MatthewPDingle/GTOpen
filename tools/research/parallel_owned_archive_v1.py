"""Bounded parallel compression using the existing exact owned-archive format.

No raw files are retired here. The caller receives manifests only after every
job succeeds and may then use the existing verified retirement operation.
"""
import concurrent.futures
import threading
from owned_research_archive_v1 import owner, name, pack, MAX_RAW
from owned_columnar_evaluation_archive_v1 import unlinked


def pack_many(jobs, *, root, token, guard, workers=3):
    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError('Use one to four archive workers')
    root = owner(root, token)
    jobs = list(jobs)
    if not 1 <= len(jobs) <= 8:
        raise ValueError('One to eight archive jobs required')
    # The caller's guard may use mutable timestamps or GPU runtime checks.
    # Run it under one lock; concurrent compression stays outside that lock.
    lock = threading.Lock()
    def checked_guard():
        with lock:
            guard()
    checked_guard()
    plans=[]; sources=set(); outputs=set()
    for job in jobs:
        source=unlinked(job['source']); destination=unlinked(job['destination'])
        names=list(job['names'])
        if (source==root or not source.is_relative_to(root)
                or not destination.is_relative_to(root)):
            raise ValueError('Archive and source must stay inside owned scratch')
        if not names or len(names)!=len(set(names)):
            raise ValueError('Distinct nonempty members required')
        manifest=destination.with_suffix(destination.suffix+'.json')
        if (source in sources or destination in outputs or manifest in outputs
                or destination.exists() or manifest.exists()):
            raise ValueError('Overlapping source or existing archive')
        total=0
        for item in names:
            path=unlinked(source/name(item))
            if not path.is_file(): raise ValueError('Missing source member')
            total+=path.stat().st_size
        if total>MAX_RAW: raise ValueError('Archive job exceeds raw bound')
        sources.add(source);outputs.update([destination,manifest])
        plans.append((source,names,destination))
    # Reject output paths nested within any source before concurrent I/O.
    if any(p.is_relative_to(s) for p in outputs for s in sources):
        raise ValueError('Archive output overlaps source contents')
    def execute(plan):
        source,names,destination=plan
        return pack(source,names,destination,root=root,token=token,guard=checked_guard)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers,thread_name_prefix='owned-archive') as pool:
        futures=[pool.submit(execute,plan) for plan in plans]
        try:
            result=[future.result() for future in futures]
        except BaseException:
            for future in futures: future.cancel()
            # Running jobs finish before this context exits. Preserve every
            # archive and raw file; do not mask the failure with partial success.
            raise
    checked_guard()
    return result
