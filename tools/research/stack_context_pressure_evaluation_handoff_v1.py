"""Finite evaluation-only handoff for the existing reviewed pressure continuation.

Never launch/resume training or retry an admitted scientific consumer. All prior
failures remain preserved. No production, new experiment, push or deployment.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import argparse
from pathlib import Path
import json
import subprocess
import time
import traceback
import psutil
import stack_context_completion_handoff_v3 as prior
import stack_context_pressure_provenance_v1 as pressure

ROOT,OUT,TRAIN,LOCK,OTHER=prior.ROOT,prior.OUT,prior.TRAIN,prior.LOCK,prior.OTHER
NAME='stack-context-pressure-evaluation-handoff-v1'
INITIAL=(90820,1790818100.9586046)
TRAIN_SCRIPT='stack_context_pressure_continuation_v2.py'
INVOCATION='c4d65a61bdc04ae58724969a780ac6ff'
ARMS,REG,REG_SHA=prior.ARMS,prior.REG,prior.REG_SHA
ADMISSION,CONTROL,AUDIT=(OUT/(NAME+s+'.json') for s in ('-admission','-check-result','-readback-result'))
ATTEMPT,STATUS,RESULT,FAILED,OWNER=(OUT/(NAME+s+'.json') for s in ('-attempt','-status','-result','-failure','-owner'))
PHASES={
 'throughput':dict(script='stack_context_final_bank_throughput_v4.py',name='stack-context-final-bank-throughput-v4',store=Path('S:/GTOpen-research/stack-context-final-bank-throughput-v4')),
 'evaluation':dict(script='stack_context_matched_evaluation_v5.py',name='stack-context-matched-evaluation-v5',store=Path('S:/GTOpen-research/stack-context-matched-evaluation-v5')),
 'readback':dict(script='stack_context_matched_readback_v6.py',name='stack-context-matched-readback-v6',store=None)}
require,read,sha,save,encoded=prior.require,prior.read,prior.sha,prior.save,prior.encoded
process_alive,poll_child=prior.process_alive,prior.poll_child

def status(stage,**values):
 tmp=STATUS.with_suffix('.writing')
 save(tmp,dict(stage=stage,pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time(),**values))
 os.replace(tmp,STATUS)

def command(phase):
 return ['C:/Program Files/Python312/python.exe','-B',str(ROOT/'tools/research'/PHASES[phase]['script']),'--run']

def decide(state):
 if state['failure']:return 'review-failure'
 if state['external_owner']:return 'wait-owner'
 if state['training_alive']:return 'wait-training'
 if not state['training_complete']:return 'review-training'
 for phase in PHASES:
  p=state[phase]
  if p['alive']:return 'wait-'+phase
  if p['complete']:continue
  if p['started']:return 'review-'+phase
  return phase
 return 'done'

def phase_state(phase):
 p=PHASES[phase];attempt=OUT/(p['name']+'-attempt.json');result=OUT/(p['name']+'-result.json')
 started=attempt.exists() or (OUT/(p['name']+'-registration.json')).exists() or (p['store'] is not None and p['store'].exists())
 alive=False;complete=False
 if attempt.exists():
  a=read(attempt);created=a.get('process_created',a.get('created',0))
  starts=[q for q in OUT.glob(NAME+'-*-'+phase+'-started.json') if read(q)['pid']==a['pid'] and abs(read(q)['created']-created)<.01]
  require(len(starts)==1,'Consumer attempt has no unique handoff child identity')
  alive=process_alive(a['pid'],created,p['script'])
 if result.exists():
  require(attempt.exists(),'Unbound terminal '+phase+' result')
  finish=Path(str(starts[0]).replace('-started.json','-finished.json'))
  if not alive:
   require(finish.exists() and read(finish)['exit_code']==0,'Consumer terminal lacks successful child exit')
   end=read(finish);prefix=str(starts[0]).removesuffix('-started.json')
   require(end['pid']==a['pid'] and abs(end['created']-created)<.01
    and end['stdout_sha256']==sha(prefix+'-stdout.log') and end['stderr_sha256']==sha(prefix+'-stderr.log'),
    'Changed child completion evidence')
  r=read(result)
  if phase=='throughput':
   complete=r.get('complete') is True and r.get('passed') is True and r.get('full_played_banks_64') is True
   require(r.get('cuda_passed') is True and r.get('reference_agreement_passed') is True
    and r.get('new_scientific_deals') is False and r.get('scientific_fits') is False,'Incomplete full-bank CUDA gate')
  elif phase=='evaluation':complete=r.get('fixed_policy_evaluation_complete') is True
  else:complete=r.get('complete') is True and r.get('passed') is True and r.get('independent_readback_complete') is True
  require(complete and r.get('production_modified') is False,'Unsuccessful terminal '+phase+' outcome')
  if r.get('registration_sha256') is not None:
   require(r['registration_sha256']==sha(OUT/(p['name']+'-registration.json')),'Changed consumer registration')
  for path,identity in r.get('inputs',{}).items():require(sha(path)==identity,'Changed consumer result input')
 return dict(started=started,alive=alive,complete=complete)

def observe():
 require(sha(REG)==REG_SHA,'Changed original scientific registration')
 attempt=read(pressure.coordinator.ATTEMPT)
 require(attempt['pid']==INITIAL[0] and abs(attempt['process_created']-INITIAL[1])<.01
  and attempt['invocation']==INVOCATION,'Unrecognized training coordinator')
 alive=process_alive(*INITIAL,TRAIN_SCRIPT)
 failures=[str(p) for p in (pressure.FAILURE,*(OUT/(v['name']+'-failure.json') for v in PHASES.values())) if p.exists()]
 complete=False
 if not alive and pressure.RESULT.exists() and not failures:
  identity,_=pressure.verify_pressure(read(pressure.RESULT))
  require(identity['training_result_sha256']==sha(pressure.RESULT),'Detached completed training proof')
  for arm in ARMS:
   w=read(OUT/(pressure.coordinator.NAME+'-'+arm+'-started.json'))
   try:worker=psutil.Process(w['pid']);worker_alive=abs(worker.create_time()-w['process_created'])<.01 and worker.is_running()
   except psutil.NoSuchProcess:worker_alive=False
   require(not worker_alive,'Training worker has not released ownership')
  complete=True
 external=OTHER.exists() or (LOCK.exists() and not (alive and LOCK.read_text().strip()==str(INITIAL[0])))
 phases={p:phase_state(p) for p in PHASES}
 require(not phases['throughput']['started'] or complete,'Consumer admitted before terminal training')
 require(not phases['evaluation']['started'] or phases['throughput']['complete'],'Evaluation before actual CUDA/reference gate')
 require(not phases['readback']['started'] or phases['evaluation']['complete'],'Readback before completed evaluation')
 counts={a:read(TRAIN/a/'progress.json')['completed_cycles'] for a in ARMS}
 return dict(failure=failures,external_owner=external,training_alive=alive,training_complete=complete,counts=counts,**phases)

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
  require(child.returncode==0,'Child failed; preserve without automatic retry: '+phase)
 lines=stdout_path.read_text(encoding='utf-8').strip().splitlines();deferred=False
 if len(lines)==1:
  try:deferred=json.loads(lines[0]).get('deferred') is True
  except json.JSONDecodeError:pass
 if deferred:require(not phase_state(phase)['started'],'Resource deferral actually admitted work')
 else:require(phase_state(phase)['complete'],'Child returned without terminal completion; no automatic resume')
 return deferred

def main(run=False):
 if not run:
  print(json.dumps(dict(prepared=True,training_identity=list(INITIAL),started=ATTEMPT.exists(),terminal=RESULT.exists(),failed=FAILED.exists())));return
 psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
 require(not any(p.exists() for p in (ATTEMPT,RESULT,FAILED,OWNER,prior.OWNER)),'Prior/live handoff; preserve without duplicate')
 control,audit,spec=read(CONTROL),read(AUDIT),read(ADMISSION)
 require(control['complete'] and control['passed'] and control['runner_sha256']==sha(__file__)
  and audit['passed'] and audit['check_result_sha256']==sha(CONTROL),'Qualified ordering and independent readback required')
 for record in (control,audit,spec):prior.verify_inputs(record['inputs'])
 require(spec['training_identity']==list(INITIAL) and spec['training_invocation']==INVOCATION
  and spec['evaluation_only'] and spec['no_training_launch'] and spec['scientific_protocol_unchanged']
  and spec['no_scheduled_trigger'] and not spec['automatic_retry_allowed'],'Changed handoff admission')
 require(all(not phase_state(p)['started'] for p in PHASES),'Scientific consumer already admitted')
 self_id=dict(pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time(),admission_sha256=sha(ADMISSION))
 save(OWNER,self_id);save(ATTEMPT,self_id);index=0;began=time.time()
 try:
  while True:
   prior.verify_inputs(spec['inputs']);state=observe();action=decide(state);status(action,state=state)
   if action=='done':
    save(RESULT,dict(handoff_complete=True,unix=time.time(),state=state,child_invocations=index,
     independent_analysis_written=False,prediction_diagnostic_complete=False,broad_goal_complete=False,
     production_modified=False,new_scientific_trial=False,training_launched=False));return
   if action.startswith('review-'):raise ValueError('Preserve evidence and request review: '+action)
   if action.startswith('wait-'):time.sleep(30);continue
   require(time.time()-began<96*3600,'Next-stage admission window expired')
   from river_matched_training_pilot_v1 import available,production_available
   ready,probe=available()
   if not ready or not production_available() or psutil.virtual_memory().available<40_000_000_000:
    status('waiting-before-admission',next_phase=action,probe=probe);time.sleep(30);continue
   if decide(observe())!=action:continue
   index+=1
   if launch(action,index):status('explicit-unstarted-resource-deferral',phase=action);time.sleep(30)
 except BaseException as error:
  save(FAILED,dict(error=repr(error),traceback=traceback.format_exc(),unix=time.time(),preserve_evidence=True,
   automatic_retry_allowed=False,production_modified=False));status('review-required',error=repr(error));raise
 finally:
  if OWNER.exists() and read(OWNER)==self_id:OWNER.unlink()

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
