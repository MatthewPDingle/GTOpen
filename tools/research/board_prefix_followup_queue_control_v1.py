"""Synthetic process-driver checks using real isolated Windows marker files.

No subprocess, CUDA, model training or production API is used by the fixtures.
The real queue's publication and source/result checks remain in the exercised path.
"""
import json
from pathlib import Path
import subprocess
import time
from types import SimpleNamespace
import importlib.util
from sampled_physical_root_evaluation_v1 import ROOT,sha
from later_average_support_v1 import OUT
from board_prefix_publication_v1 import atomic_json

PREFIX='board-prefix-followup-queue-control-v1'
STORE=OUT/PREFIX
QUEUE=ROOT/'tools/research/board_prefix_followup_queue_v1.py'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def case(mode):
    root=STORE/mode;output=root/'out';scripts=root/'tools/research'
    output.mkdir(parents=True);scripts.mkdir(parents=True)
    q=load('isolated_queue_'+mode,QUEUE)
    q.ROOT=root;q.OUT=output;q.__file__=str(scripts/QUEUE.name)
    q.LOCK=output/'research.lock';q.OTHER=output/'other.lock'
    for script,_,_,_,_ in q.STAGES:(scripts/script).write_text('Synthetic source; never executed.\n')
    Path(q.__file__).write_bytes(QUEUE.read_bytes())
    for name in ('BOARD-ROOT-MATCHED-STUDY-PLAN.md','BOARD-TRAINING-BANK-READINESS.md','BOARD-PREFIX-FOLLOWUP-PLAN.md'):
        (output/name).write_text('Synthetic plan.\n')
    upstream_registration=output/f'{q.UPSTREAM}-registration.json'
    atomic_json(upstream_registration,dict(inputs={},synthetic=True))
    second='weighted-complete-evaluation-queue-v1'
    atomic_json(output/f'{second}-registration.json',dict(inputs={},synthetic=True))
    atomic_json(output/f'{second}-result.json',dict(passed=True,synthetic=True,
        registration_sha256=sha(output/f'{second}-registration.json')))
    def upstream_done():
        atomic_json(output/f'{q.UPSTREAM}-result.json',dict(passed=True,synthetic=True,stages=[],
            registration_sha256=sha(upstream_registration)))
    if mode not in ('wait-resources','stale-owner','changed-source'):upstream_done()
    clock=[0.];sleeps=[];started=[];terminated=[];probes=[];created_calls=[0];cpu_calls=[0]
    mutated=[False]
    class Process:
        def __init__(self,pid):self.pid=pid
        def is_running(self):return True
        def cmdline(self):return ['synthetic-python','board_training_pipeline_queue_v2.py']
        def create_time(self):
            created_calls[0]+=1
            return 1234.+(mode=='stale-owner' and created_calls[0]>1)
        def children(self,recursive=False):return [Process(222)]
        def terminate(self):terminated.append(self.pid)
    def sleep(seconds):
        sleeps.append(seconds);clock[0]+=seconds
        if not (output/f'{q.UPSTREAM}-result.json').exists():
            upstream_done()
            if mode=='changed-source':Path(q.__file__).write_text('Changed after registration.\n')
    def cpu(interval):
        cpu_calls[0]+=1
        if mode=='tampered-stage' and len(started)==1 and not mutated[0]:
            p=output/f'{q.STAGES[0][2]}-result.json'
            p.write_bytes(p.read_bytes()+b' ');mutated[0]=True
        return 90 if mode=='wait-resources' and cpu_calls[0]<3 else 0
    def probe(*args,**kwargs):
        probes.append(True)
        busy=mode=='wait-resources' and len(probes)==1
        return SimpleNamespace(returncode=0,stdout='100, 8000' if busy else '0, 8000')
    class Child:
        def __init__(self,argv,**kwargs):
            self.pid=111;self.returncode=None;self.stopped=False
            script=Path(argv[1]).name;arguments=argv[2:]
            matches=[s for s in q.STAGES if s[0]==script and s[1]==arguments]
            assert len(matches)==1
            self.stage=matches[0];started.append((script,arguments))
        def wait(self,timeout=None):
            if self.stopped:self.returncode=0;return 0
            if mode=='child-timeout':raise subprocess.TimeoutExpired('synthetic child',timeout)
            if mode=='stage-failure' and len(started)==2:self.returncode=1;return 1
            prefix=self.stage[2];rp=output/f'{prefix}-registration.json'
            atomic_json(rp,dict(inputs={},synthetic=True))
            atomic_json(output/f'{prefix}-result.json',dict(passed=True,synthetic=True,
                registration_sha256=sha(rp),agrees_with_bounded_audit=True,
                prefix_generations_per_arm=2,mode='prefix',arms=[dict(generations=2),dict(generations=2)]))
            self.returncode=0;return 0
        def poll(self):return self.returncode
        def terminate(self):terminated.append(self.pid);self.stopped=True
    q.psutil=SimpleNamespace(Process=Process,NoSuchProcess=RuntimeError,cpu_percent=cpu,
        virtual_memory=lambda:SimpleNamespace(available=50_000_000_000),
        disk_usage=lambda _:SimpleNamespace(free=100_000_000_000))
    q.subprocess=SimpleNamespace(run=probe,Popen=Child,STDOUT=subprocess.STDOUT,CREATE_NO_WINDOW=subprocess.CREATE_NO_WINDOW)
    q.time=SimpleNamespace(monotonic=lambda:clock[0],sleep=sleep)
    q.production_available=lambda:True
    error=None
    try:q.main(999)
    except (AssertionError,subprocess.TimeoutExpired) as exc:error=repr(exc)
    final=output/f'{q.PREFIX}-result.json';failed=output/f'{q.PREFIX}-failure.json'
    expected_started={'success':5,'wait-resources':5,'stale-owner':0,'changed-source':0,
        'stage-failure':2,'tampered-stage':1,'child-timeout':1}[mode]
    assert len(started)==expected_started
    assert started==[(s[0],s[1]) for s in q.STAGES[:expected_started]]
    if mode in ('success','wait-resources'):
        assert error is None and final.exists() and not failed.exists()
        assert json.loads(final.read_text())['full_training_queued'] is False
    else:assert error is not None and not final.exists() and failed.exists()
    assert terminated==([222,111] if mode=='child-timeout' else [])
    assert 999 not in terminated,'Upstream must never be terminated'
    if mode=='wait-resources':assert len(sleeps)>=4 and len(probes)>=3
    return dict(case=mode,stages_started=len(started),sleeps=sleeps,terminated_fake_pids=terminated,
        failure=error,passed=True)


def main():
    began=time.monotonic();assert not STORE.exists()
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    gpu=ROOT/'tools/research/board_training_bank_cuda_control_v1.py'
    inputs={str(p):sha(p) for p in (Path(__file__).resolve(),QUEUE,gpu,ROOT/'tools/research/board_prefix_publication_v1.py')}
    atomic_json(rp,dict(inputs=inputs,store=str(STORE),mechanical_driver_only=True,
        synthetic_processes=True,gpu_used=False,maximum_seconds=30,production_modified=False))
    cases=[case(mode) for mode in ('success','wait-resources','stale-owner','changed-source',
                                  'stage-failure','tampered-stage','child-timeout')]
    # The actual current missing qualifications must reject execution before
    # touching any GPU or attempting a resource probe.
    control=load('unqualified_cuda_control',gpu)
    _,_,_,missing=control.dependencies();assert missing
    calls=[]
    def forbidden():calls.append(True);raise AssertionError('Resource probe must not be reached')
    control.safe_read_only_resources=forbidden
    try:control.main(run=True)
    except AssertionError as exc:assert 'Missing genuine qualifications' in str(exc)
    else:raise AssertionError('Unqualified CUDA control was admitted')
    assert not calls and not (OUT/f'{control.PREFIX}-registration.json').exists()
    for p,h in inputs.items():assert sha(p)==h,p
    files=[p for p in STORE.rglob('*') if p.is_file()]
    assert sum(p.stat().st_size for p in files)<1_000_000 and time.monotonic()-began<30
    result=dict(passed=True,registration_sha256=sha(rp),cases=cases,
        missing_genuine_gpu_evidence_rejected_before_resources=True,fixture_files=len(files),
        fixture_logical_bytes=sum(p.stat().st_size for p in files),
        seconds=time.monotonic()-began,mechanical_driver_only=True,synthetic_processes=True,
        actual_subprocesses_started=0,gpu_used=False,training_started=False,production_modified=False)
    atomic_json(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result),flush=True)


if __name__=='__main__':main()
