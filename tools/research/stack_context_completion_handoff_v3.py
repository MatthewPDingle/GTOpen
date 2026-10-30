"""Finite, demand-started handoff for the existing registered comparison.

Never change scientific inputs or retry a failed/partial attempt. Continue only
an authenticated complete training boundary, using the unchanged original runner.
No production writes, new diagnostic, push, deployment or accuracy conclusion.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import traceback
import uuid
import psutil

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
TRAIN=Path('S:/GTOpen-research/stack-context-matched-learning-v1')
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
NAME='stack-context-completion-handoff-v3'
INITIAL=(94544,1790753443.077002)
ARMS=('A-baseline','A-relative','B-baseline','B-relative')
REG=OUT/'stack-context-matched-learning-v1-registration.json'
REG_SHA='ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'
ADMISSION=OUT/(NAME+'-admission.json');CONTROL=OUT/(NAME+'-check-result.json')
ATTEMPT,STATUS,RESULT,FAILED,OWNER=(OUT/(NAME+s+'.json') for s in ('-attempt','-status','-result','-failure','-owner'))
TRAIN_NAME='stack-context-parallel-continuation-v2'
PHASES={
    'training':dict(script='stack_context_parallel_continuation_v2.py',name=TRAIN_NAME,store=None),
    'throughput':dict(script='stack_context_final_bank_throughput_v2.py',name='stack-context-final-bank-throughput-v2',
        store=Path('S:/GTOpen-research/stack-context-final-bank-throughput-v2')),
    'evaluation':dict(script='stack_context_matched_evaluation_v3.py',name='stack-context-matched-evaluation-v3',
        store=Path('S:/GTOpen-research/stack-context-matched-evaluation-v3')),
    'readback':dict(script='stack_context_matched_readback_v4.py',name='stack-context-matched-readback-v4',store=None)}


def require(ok,message):
    if not ok:raise ValueError(message)
def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def save(path,value):
    with Path(path).open('xb') as f:f.write(encoded(value));f.flush();os.fsync(f.fileno())
def status(stage,**values):
    tmp=STATUS.with_suffix('.writing')
    save(tmp,dict(stage=stage,pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time(),**values))
    os.replace(tmp,STATUS)
def command(phase):return ['C:/Program Files/Python312/python.exe','-B',str(ROOT/'tools/research'/PHASES[phase]['script']),'--run']
def same_script(cmd,script):return any(str(v).replace('\\','/').lower().endswith('/'+script.lower()) for v in cmd)
def process_alive(pid,created,script):
    try:
        p=psutil.Process(pid)
        if abs(p.create_time()-created)>.01:return False
        require(same_script(p.cmdline(),script),'Expected process identity has another command')
        return p.is_running()
    except psutil.NoSuchProcess:return False
def poll_child(child,identity,script):
    code=child.poll()
    if code is not None:return code
    try:alive=process_alive(*identity,script)
    except (ValueError,psutil.Error):
        # A normal child exit can race the separate process inspection.
        code=child.poll()
        if code is not None:return code
        raise
    if alive:return None
    code=child.poll()
    require(code is not None,'Live child handle has mismatched process identity')
    return code
def current_failure_paths():
    return [OUT/(v['name']+'-failure.json') for v in PHASES.values()]


def decide(state):
    """Pure ordering control; every field is authenticated by observe()."""
    if state['failure']:return 'review-failure'
    if state['external_owner']:return 'wait-owner'
    if state['training_alive']:return 'wait-training'
    if not state['training_complete']:
        if not state['clean_training_boundary']:return 'review-training'
        if state['training_deadline_expired']:return 'review-deadline'
        return 'training'
    for phase in ('throughput','evaluation','readback'):
        p=state[phase]
        if p['complete']:continue
        if p['alive']:return 'wait-'+phase
        if p['started']:return 'review-'+phase
        return phase
    return 'done'


def boundary(status_doc,counts,train=TRAIN):
    require(status_doc['stage']=='complete-boundary-awaiting-resume'
        and status_doc['completed_cycles']==counts and set(counts)==set(ARMS)
        and all(type(n) is int and 1<=n<=64 for n in counts.values()) and any(n<64 for n in counts.values()),
        'Not an exact completed training boundary')
    matches=[p for p in train.glob(TRAIN_NAME+'-invocation-*.json')
        if read(p).get('pid')==status_doc['pid'] and abs(read(p).get('process_created',0)-status_doc['process_created'])<.01]
    require(len(matches)==1,'Unique terminal training invocation required')
    invocation=matches[0].stem.split('-invocation-')[1];original=read(matches[0])['boundaries']
    for arm in ARMS:
        if original[arm]==64:
            require(counts[arm]==64,'Changed previously complete arm');continue
        outcome=read(train/(TRAIN_NAME+'-'+invocation+'-'+arm+'.json'))
        require(not outcome.get('failed') and (outcome.get('complete') is True or outcome.get('stopped_at_complete_boundary') is True)
            and outcome['progress_sha256']==sha(train/arm/'progress.json'), 'Missing or changed successful arm boundary')
        require(counts[arm]>=original[arm],'Published training went backwards')
        require(outcome.get('complete') is (counts[arm]==64),'Arm completion disagrees with 64-cycle horizon')
        if counts[arm]<64:
            require(not (train/arm/f"cycle-{counts[arm]+1:04d}").exists()
                and not (train/arm/f"archive-{counts[arm]+1:04d}").exists(),
                'An unpublished next cycle requires review, not automatic continuation')
    return dict(invocation_sha256=sha(matches[0]),counts=counts)


def phase_state(phase):
    p=PHASES[phase];attempt=OUT/(p['name']+'-attempt.json');result=OUT/(p['name']+'-result.json')
    started=attempt.exists() or (OUT/(p['name']+'-registration.json')).exists() or (p['store'] is not None and p['store'].exists())
    alive=False
    if attempt.exists():
        a=read(attempt);alive=process_alive(a['pid'],a.get('process_created',a.get('created',0)),p['script'])
    complete=False
    if result.exists():
        require(attempt.exists(),'Unbound terminal '+phase+' result')
        r=read(result)
        if phase=='throughput':
            complete=r.get('complete') is True and r.get('passed') is True and r.get('full_played_banks_64') is True
            require(r.get('cuda_passed') is True and r.get('reference_agreement_passed') is True
                and r.get('new_scientific_deals') is False and r.get('scientific_fits') is False,'Incomplete throughput gate')
        elif phase=='evaluation':complete=r.get('fixed_policy_evaluation_complete') is True
        else:complete=r.get('complete') is True and r.get('passed') is True and r.get('independent_readback_complete') is True
        require(complete and r.get('production_modified') is False,'Terminal '+phase+' result not successful')
        if r.get('registration_sha256') is not None:
            require(r['registration_sha256']==sha(OUT/(p['name']+'-registration.json')),'Changed '+phase+' registration')
        for path,identity in r.get('inputs',{}).items():require(sha(path)==identity,'Changed '+phase+' result input')
    return dict(started=started,alive=alive,complete=complete)


def observe(known_trainers):
    require(sha(REG)==REG_SHA,'Changed original registration')
    s=read(OUT/(TRAIN_NAME+'-status.json'))
    ident=(s['pid'],s['process_created'])
    require(any(ident[0]==p and abs(ident[1]-c)<.01 for p,c in known_trainers),'Unrecognized training invocation; review ownership')
    alive=process_alive(*ident,PHASES['training']['script'])
    failure=[str(p) for p in current_failure_paths() if p.exists()]
    counts={a:read(TRAIN/a/'progress.json')['completed_cycles'] for a in ARMS}
    train_result=OUT/(TRAIN_NAME+'-training-result.json');complete=False;clean=False
    if train_result.exists():
        r=read(train_result);require(r.get('training_complete') is True and r['registration_sha256']==REG_SHA,
            'Terminal training result not successful')
        require(all(counts[a]==64 and r['arms'][a]==read(TRAIN/a/'progress.json') for a in ARMS),'Actual complete64 banks required')
        complete=True
    elif not alive and s['stage']=='complete-boundary-awaiting-resume' and not failure:
        boundary(s,counts);clean=True
    external=OTHER.exists() or (LOCK.exists() and not (alive and LOCK.read_text().strip()==str(ident[0])))
    if ident[0]==INITIAL[0] and not alive and not external:
        # The original services-owned wrapper must also have finished normally.
        proof=OUT/'stack-context-durable-recovery-entry-v1-result.json'
        if not proof.exists():external=True
        else:
            d=read(proof);require(d.get('complete') is True,'Initial durable wrapper not complete')
            p=d['phases'][-1];require(p['phase']=='parallel-training' and p['pid']==INITIAL[0]
                and abs(p['created']-INITIAL[1])<.01 and p['exit_code']==0,'Initial trainer exit is not authenticated')
    deadline=read(OUT/'stack-context-matched-learning-v1-attempt.json')['admitted_unix']+72*3600
    stages={p:phase_state(p) for p in ('throughput','evaluation','readback')}
    require(not stages['throughput']['started'] or complete,'Throughput admitted before actual64 training completed')
    require(not stages['evaluation']['started'] or stages['throughput']['complete'],'Evaluation admitted before complete resource gate')
    require(not stages['readback']['started'] or stages['evaluation']['complete'],'Readback admitted before complete evaluation')
    return dict(failure=failure,external_owner=external,training_alive=alive,training_complete=complete,
        clean_training_boundary=clean,training_deadline_expired=time.time()>=deadline,
        counts=counts,training_identity=list(ident),**stages)


def verify_inputs(inputs):
    for p,h in inputs.items():require(sha(p)==h,'Changed handoff input: '+p)


def launch(phase,index):
    prefix=OUT/(NAME+'-'+str(index).zfill(3)+'-'+phase)
    stdout_path=Path(str(prefix)+'-stdout.log');stderr_path=Path(str(prefix)+'-stderr.log')
    with stdout_path.open('xb') as stdout,stderr_path.open('xb') as stderr:
        child=subprocess.Popen(command(phase),cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        identity=(child.pid,psutil.Process(child.pid).create_time())
        record=dict(phase=phase,index=index,pid=identity[0],created=identity[1],unix=time.time(),command=command(phase))
        save(Path(str(prefix)+'-started.json'),record)
        while poll_child(child,identity,PHASES[phase]['script']) is None:
            status('running-child',phase=phase,child=record)
            try:child.wait(timeout=30)
            except subprocess.TimeoutExpired:pass
        record.update(exit_code=child.returncode,finished_unix=time.time(),stdout_sha256=sha(stdout_path),stderr_sha256=sha(stderr_path))
        save(Path(str(prefix)+'-finished.json'),record)
        require(child.returncode==0,'Child failed; no automatic retry: '+phase)
    # Only an explicit, wholly unstarted admission deferral may be polled again.
    deferred=False
    lines=stdout_path.read_text(encoding='utf-8').strip().splitlines()
    if len(lines)==1:
        try:d=json.loads(lines[0])
        except json.JSONDecodeError:d={}
        deferred=d.get('deferred') is True
    return identity,deferred


def main(run=False):
    if not run:
        print(json.dumps(dict(prepared=True,initial_trainer=list(INITIAL),started=ATTEMPT.exists(),terminal=RESULT.exists(),failed=FAILED.exists())))
        return
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    require(not any(p.exists() for p in (ATTEMPT,RESULT,FAILED,OWNER)),'Existing handoff; preserve without duplicate/retry')
    control,spec=read(CONTROL),read(ADMISSION)
    require(control['complete'] and control['passed'] and control['runner_sha256']==sha(__file__),'Current handoff control required')
    verify_inputs(control['inputs']);verify_inputs(spec['inputs'])
    require(spec['initial_trainer']==list(INITIAL) and spec['registered_training_deadline_unchanged']
        and spec['no_new_scientific_trial'] and spec['no_scheduled_trigger'],'Changed handoff scope')
    self_id=dict(pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time(),admission_sha256=sha(ADMISSION))
    save(OWNER,self_id);save(ATTEMPT,self_id)
    known=[INITIAL];index=0;admitted=time.time()
    try:
        while True:
            verify_inputs(spec['inputs']);state=observe(known);action=decide(state)
            status(action,state=state)
            if action=='done':
                save(RESULT,dict(handoff_complete=True,unix=time.time(),state=state,child_invocations=index,
                    independent_analysis_written=False,prediction_diagnostic_complete=False,
                    broad_goal_complete=False,production_modified=False,new_scientific_trial=False));return
            if action.startswith('review-'):raise ValueError('Preserve evidence and request review: '+action)
            if action.startswith('wait-'):
                # An admitted child may legitimately finish beyond this helper's
                # admission window. Never terminate it because observation expired.
                time.sleep(30);continue
            require(time.time()-admitted<96*3600,'Completion admission window expired before next stage')
            # Reuse the original resource policy. Importing does not run a trial.
            from river_matched_training_pilot_v1 import available
            ready,probe=available()
            if not ready or psutil.virtual_memory().available<40_000_000_000:
                status('waiting-before-admission',next_phase=action,probe=probe);time.sleep(30);continue
            # Recheck current ownership/outcomes immediately before launching.
            state=observe(known)
            if decide(state)!=action:continue
            index+=1;identity,deferred=launch(action,index)
            if action=='training' and not deferred:
                terminal=read(OUT/(TRAIN_NAME+'-status.json'))
                require(terminal['pid']==identity[0] and abs(terminal['process_created']-identity[1])<.01
                    and terminal['stage'] in ('complete-boundary-awaiting-resume','training-complete-awaiting-fresh-evaluation'),
                    'Training returned without an authenticated terminal boundary; no automatic repeat')
                known.append(identity)
            if deferred:
                require(not phase_state(action)['started'] if action!='training' else not any(
                    read(p).get('pid')==identity[0] and abs(read(p).get('process_created',0)-identity[1])<.01
                    for p in TRAIN.glob(TRAIN_NAME+'-invocation-*.json')),'Admission deferral actually started work')
                status('explicit-unstarted-deferral',phase=action);time.sleep(30)
    except BaseException as error:
        save(FAILED,dict(error=repr(error),traceback=traceback.format_exc(),unix=time.time(),preserve_evidence=True,
            automatic_retry_allowed=False,production_modified=False));status('review-required',error=repr(error));raise
    finally:
        if OWNER.exists() and read(OWNER)==self_id:OWNER.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
