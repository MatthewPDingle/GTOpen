"""Actual Windows file publication with mock training, including 2-to-78 resume."""
import contextlib
import copy
import io
import json
from pathlib import Path
import time
from unittest.mock import patch
import board_continuation_sequence_v1 as sequence
import board_matched_continuation_v1 as runner
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure
from sampled_physical_root_evaluation_v1 import sha,save
from later_average_support_v1 import OUT,read
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-continuation-sequence-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def failure(call,message):
    try:call()
    except (AssertionError,RuntimeError,OSError) as exc:
        if message is not None:assert message in str(exc),(message,str(exc))
    else:raise AssertionError('Expected rejection: '+str(message))


def fixture(name):
    folder=STORE/name;folder.mkdir()
    generations=[]
    for i in (1,2):
        generation=folder/f'generation-{i:04d}';generation.mkdir()
        metric=generation/'metrics.json'
        save(metric,dict(iteration=i,checkpoint=dict(completed_iterations=i)))
        generations.append(dict(path=str(metric),sha256=sha(metric)))
    prefix=folder/'progress.json'
    save(prefix,dict(registration_sha256='qualified-prefix',completed=2,
        checkpoint=dict(completed_iterations=2),initial_checkpoint=dict(completed_iterations=0),generations=generations))
    before=prefix.read_bytes();calls=[];published=[];boundaries=[]
    def update(destination,state):
        destination.mkdir();state['completed_iterations']+=1;i=state['completed_iterations'];calls.append(i)
        metric=dict(iteration=i,checkpoint=copy.deepcopy(state))
        save(destination/'metrics.json',metric);return metric
    def compare(left,right):assert left==right
    def boundary(stage,reserve):boundaries.append((stage,reserve))
    kwargs=dict(folder=folder,prefix_path=prefix,prefix_sha=sha(prefix),registration_sha='continuation',
        restore=copy.deepcopy,compare=compare,update=update,boundary=boundary,guard=lambda:None,
        on_published=lambda p:published.append(p['completed']))
    return folder,prefix,before,calls,published,boundaries,kwargs


def main():
    began=time.monotonic();assert production_available() and not STORE.exists()
    create(STORE)
    inputs={str(p):sha(p) for p in (Path(__file__).resolve(),Path(sequence.__file__).resolve(),Path(runner.__file__).resolve())}
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    save(rp,dict(inputs=inputs,scope='Synthetic training state; actual file publication and resume control. No CUDA or native poker execution.',
        maximum_seconds=180,production_modified=False))
    results=[]
    # Full fixed endpoint, including a second call after completion.
    folder,prefix,before,calls,published,bounds,kwargs=fixture('normal')
    result=sequence.advance_arm(**kwargs)
    assert calls==published==list(range(3,79)) and result['completed']==78
    assert prefix.read_bytes()==before
    prior=list(calls);sequence.advance_arm(**kwargs);assert calls==prior
    assert all((f'after-generation-{i}',65_536) in bounds for i in range(3,79))
    assert all((f'generation-{i}-published',0) in bounds for i in range(3,79))
    results.append('Fixed endpoint 78; no reinitialization, prefix rewrite or generation 79')
    # A fully written generation whose progress rename fails is retained but
    # excluded from published history; resume replays that one generation only.
    folder,prefix,before,calls,published,bounds,kwargs=fixture('publication-failure')
    real=sequence.atomic_json
    def interrupted(path,value,**options):
        if value['completed']==4:
            with patch('board_prefix_publication_v1.os.replace',side_effect=OSError('injected rename failure')):
                return real(path,value,**options)
        return real(path,value,**options)
    with patch.object(sequence,'atomic_json',side_effect=interrupted):
        failure(lambda:sequence.advance_arm(**kwargs),'injected rename failure')
    assert read(folder/'continuation-progress.json')['completed']==3 and calls==[3,4]
    assert list(folder.glob('.partial-*')) and prefix.read_bytes()==before
    sequence.advance_arm(**kwargs)
    assert calls==[3,4,*range(4,79)] and published==[3,*range(4,79)]
    assert len(list(folder.glob('continuation-generation-0004-*')))==2
    results.append('Failed progress publication preserves the prior checkpoint and retries only the unpublished update')
    # Resource failure after an update must not publish it.
    folder,prefix,before,calls,published,bounds,kwargs=fixture('after-update-limit')
    good=kwargs['boundary']
    def rejected(stage,reserve):
        good(stage,reserve)
        if stage=='after-generation-3':raise RuntimeError('injected allocation rejection')
    with patch.dict(kwargs,boundary=rejected):failure(lambda:sequence.advance_arm(**kwargs),'injected allocation rejection')
    assert read(folder/'continuation-progress.json')['completed']==2 and not published
    sequence.advance_arm(**kwargs);assert calls==[3,*range(3,79)] and prefix.read_bytes()==before
    results.append('After-update storage rejection cannot advance published progress')
    # Failure after publication resumes beyond, rather than repeats, that update.
    folder,prefix,before,calls,published,bounds,kwargs=fixture('after-publication-limit')
    good=kwargs['boundary']
    def rejected(stage,reserve):
        good(stage,reserve)
        if stage=='generation-3-published':raise RuntimeError('injected post-publication rejection')
    with patch.dict(kwargs,boundary=rejected):failure(lambda:sequence.advance_arm(**kwargs),'injected post-publication rejection')
    assert read(folder/'continuation-progress.json')['completed']==3
    sequence.advance_arm(**kwargs);assert calls==list(range(3,79)) and prefix.read_bytes()==before
    results.append('Published updates are not repeated after a later guard fails')
    # Existing source/hash/endpoint mismatches reject before any new update.
    folder,prefix,before,calls,published,bounds,kwargs=fixture('identity-rejections')
    with patch.dict(kwargs,prefix_sha='0'*64):failure(lambda:sequence.advance_arm(**kwargs),None)
    assert not calls and not (folder/'continuation-progress.json').exists()
    sequence.advance_arm(**kwargs);count=len(calls)
    with patch.dict(kwargs,registration_sha='wrong'):failure(lambda:sequence.advance_arm(**kwargs),None)
    progress=read(folder/'continuation-progress.json');progress['completed']=79
    atomic_json(folder/'continuation-progress.json',progress,replace=True)
    failure(lambda:sequence.advance_arm(**kwargs),None);assert len(calls)==count
    assert prefix.read_bytes()==before
    results.append('Wrong prefix, wrong continuation registration and generation beyond 78 are rejected')
    # The actual runtime wrapper must stop before even checking resources if
    # the genuine prefix/admission qualifications are absent.
    with patch.object(runner,'preparation',return_value=([],[],{},{},None,None,None,['missing-genuine-audit'])), \
         patch.object(runner,'safe_read_only_resources',side_effect=AssertionError('resources reached')):
        failure(lambda:runner.main(run=True),'Genuine prefix audit')
    results.append('Missing genuine audit blocks the runtime before resource or CUDA admission')
    for p,h in inputs.items():assert sha(p)==h,p
    usage=measure(STORE);assert usage['logical_bytes']<20_000_000 and usage['allocated_file_bytes']<20_000_000
    assert time.monotonic()-began<180 and production_available()
    result=dict(passed=True,registration_sha256=sha(rp),checks=results,measurement=usage,
        seconds=time.monotonic()-began,synthetic_training=True,gpu_used=False,native_poker_executed=False,
        actual_continuation_admitted=False,production_modified=False)
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result),flush=True)


if __name__=='__main__':main()
