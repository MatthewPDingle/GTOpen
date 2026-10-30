"""Continue a fixed 78-generation arm without rewriting its qualified prefix.

The caller owns process locks, source/resource admission, checkpoint semantics
and directory limits. This module owns ordered, atomic progress publication.
"""
import copy
from pathlib import Path
import uuid
from board_prefix_publication_v1 import atomic_json
from sampled_physical_root_evaluation_v1 import sha
from later_average_support_v1 import read

GENERATIONS=78
PREFIX_GENERATIONS=2


def check_progress(progress, prefix, prefix_sha, registration_sha, folder):
    assert progress['registration_sha256']==registration_sha
    assert progress['prefix_progress_sha256']==prefix_sha
    assert progress['initial_checkpoint']==prefix['initial_checkpoint']
    count=progress['completed']
    assert type(count) is int and PREFIX_GENERATIONS<=count<=GENERATIONS
    assert len(progress['generations'])==count
    assert progress['generations'][:PREFIX_GENERATIONS]==prefix['generations']
    paths=set()
    for iteration,row in enumerate(progress['generations'],1):
        path=Path(row['path'])
        assert path.resolve()==path and path.parent.parent==folder
        assert path.name=='metrics.json' and str(path) not in paths
        paths.add(str(path)); assert sha(path)==row['sha256']
        metric=read(path); assert metric['iteration']==iteration
        if iteration==count: assert metric['checkpoint']==progress['checkpoint']
    return progress


def advance_arm(*, folder, prefix_path, prefix_sha, registration_sha,
                restore, compare, update, boundary, guard, on_published=lambda progress:None):
    folder=Path(folder); prefix_path=Path(prefix_path)
    assert prefix_path==folder/'progress.json' and sha(prefix_path)==prefix_sha
    prefix=read(prefix_path)
    assert prefix['completed']==len(prefix['generations'])==PREFIX_GENERATIONS
    progress_path=folder/'continuation-progress.json'
    if progress_path.exists():
        progress=read(progress_path)
    else:
        progress=copy.deepcopy(prefix)
        progress.update(registration_sha256=registration_sha,prefix_progress_sha256=prefix_sha)
    check_progress(progress,prefix,prefix_sha,registration_sha,folder)
    state=restore(progress['checkpoint'])
    assert state['completed_iterations']==progress['completed']
    if not progress_path.exists():
        boundary('before-continuation-progress',65_536)
        atomic_json(progress_path,progress)
        boundary('continuation-progress-published',0)
    while progress['completed']<GENERATIONS:
        guard(); iteration=progress['completed']+1
        boundary(f'before-generation-{iteration}',1_000_000_000)
        destination=folder/f'continuation-generation-{iteration:04d}-{uuid.uuid4().hex[:8]}'
        metric=update(destination,state)
        assert metric['iteration']==state['completed_iterations']==iteration
        metric_path=destination/'metrics.json'; assert read(metric_path)==metric
        boundary(f'after-generation-{iteration}',65_536)
        restored=restore(metric['checkpoint']); compare(state,restored)
        row=dict(path=str(metric_path),sha256=sha(metric_path))
        next_progress=dict(progress,completed=iteration,checkpoint=metric['checkpoint'],
            generations=[*progress['generations'],row])
        # Publication is the commit point. Interrupted updates remain outside
        # this list and resume restores the preceding complete checkpoint.
        assert sha(prefix_path)==prefix_sha
        atomic_json(progress_path,next_progress,replace=True)
        progress=next_progress
        boundary(f'generation-{iteration}-published',0)
        on_published(progress)
    assert sha(prefix_path)==prefix_sha
    return dict(progress_path=str(progress_path),progress_sha256=sha(progress_path),
                completed=progress['completed'],checkpoint=progress['checkpoint'])
