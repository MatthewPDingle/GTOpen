"""Ordering/identity qualification only. Never launch a scientific child."""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import copy
import json
from pathlib import Path
import time
import traceback
from unittest.mock import patch
import psutil
import stack_context_pressure_evaluation_handoff_v1 as h

def state(**values):
 s=dict(failure=[],external_owner=False,training_alive=False,training_complete=False,
  **{p:dict(started=False,alive=False,complete=False) for p in h.PHASES})
 s.update(values);return s

def main():
 name=h.NAME+'-check';attempt,result,failure=(h.OUT/(name+s+'.json') for s in ('-attempt','-result','-failure'))
 folder=h.OUT/(name+'-fixtures')
 h.require(not any(p.exists() for p in (attempt,result,failure,folder)),'Preserve prior qualification')
 psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
 consumer=h.OUT/'stack-context-pressure-consumer-check-v3-result.json';proof=h.read(consumer)
 assert proof['passed'] and proof['complete'] and proof['unchanged_evaluation_transfer_schema_verified']
 h.prior.verify_inputs(proof['inputs'])
 identity,pressure_paths=h.pressure.verify_pressure()
 paths={Path(__file__).resolve(),Path(h.__file__).resolve(),Path(h.prior.__file__).resolve(),consumer,
  h.OUT/'STACK-CONTEXT-PRESSURE-EVALUATION-HANDOFF-V1-PLAN.md',h.REG,*pressure_paths,*map(Path,proof['inputs'])}
 inputs={str(p):h.sha(p) for p in paths}
 h.save(attempt,dict(inputs=inputs,child_launches=0,scientific_fits=0,native_calls=0))
 began=time.monotonic();negative=[];decisions=[]
 def reject(label,fn):
  try:fn()
  except (ValueError,FileNotFoundError,KeyError):negative.append(label)
  else:raise AssertionError('Accepted '+label)
 try:
  cases=[(state(failure=['failure']),'review-failure'),(state(external_owner=True),'wait-owner'),
   (state(training_alive=True),'wait-training'),(state(),'review-training')]
  phases=list(h.PHASES)
  for n in range(4):
   s=state(training_complete=True)
   for p in phases[:n]:s[p]=dict(started=True,alive=False,complete=True)
   cases.append((s,(phases+['done'])[n]))
  for phase in phases:
   s=state(training_complete=True)
   for p in phases[:phases.index(phase)]:s[p]=dict(started=True,alive=False,complete=True)
   for complete in (False,True):
    live=copy.deepcopy(s);live[phase]=dict(started=True,alive=True,complete=complete)
    cases.append((live,'wait-'+phase))
   partial=copy.deepcopy(s);partial[phase]=dict(started=True,alive=False,complete=False)
   cases.append((partial,'review-'+phase))
  for s,expected in cases:
   assert h.decide(s)==expected;decisions.append(dict(state=s,expected=expected))
  guarded=0
  for mask in range(8):
   for guard in ('failure','external_owner','training_alive'):
    s=state(training_complete=True)
    for i,p in enumerate(phases):s[p]=dict(started=bool(mask&(1<<i)),alive=False,complete=bool(mask&(1<<i)))
    s[guard]=['failure'] if guard=='failure' else True
    assert h.decide(s).startswith(('wait-','review-'));guarded+=1
  folder.mkdir()
  fixture_phases={p:dict(v,store=folder/(p+'-store') if v['store'] is not None else None) for p,v in h.PHASES.items()}
  def make_phase(phase):
   p=fixture_phases[phase];a=folder/(p['name']+'-attempt.json');r=folder/(p['name']+'-result.json');reg=folder/(p['name']+'-registration.json')
   prefix=folder/(h.NAME+'-001-'+phase);h.save(a,dict(pid=987654321,process_created=123.));h.save(reg,dict(synthetic=True))
   h.save(Path(str(prefix)+'-started.json'),dict(pid=987654321,created=123.))
   for suffix in ('-stdout.log','-stderr.log'):Path(str(prefix)+suffix).write_bytes(b'')
   h.save(Path(str(prefix)+'-finished.json'),dict(pid=987654321,created=123.,exit_code=0,
    stdout_sha256=h.sha(str(prefix)+'-stdout.log'),stderr_sha256=h.sha(str(prefix)+'-stderr.log')))
   value=dict(production_modified=False,registration_sha256=h.sha(reg),inputs={},complete=True,passed=True)
   if phase=='throughput':value.update(full_played_banks_64=True,cuda_passed=True,reference_agreement_passed=True,new_scientific_deals=False,scientific_fits=False)
   elif phase=='evaluation':value.update(fixed_policy_evaluation_complete=True)
   else:value.update(independent_readback_complete=True)
   h.save(r,value);return a,r,prefix,value
  with patch.object(h,'OUT',folder),patch.object(h,'PHASES',fixture_phases),patch.object(h,'process_alive',return_value=False):
   for phase in phases:
    a,r,prefix,value=make_phase(phase)
    assert h.phase_state(phase)==dict(started=True,alive=False,complete=True)
    for label,change in [('bad result',{'production_modified':True}),('bad registration',{'registration_sha256':'0'*64})]:
     r.write_bytes(h.encoded(dict(value,**change)));reject(phase+' '+label,lambda p=phase:h.phase_state(p));r.write_bytes(h.encoded(value))
    finish=Path(str(prefix)+'-finished.json');pristine=finish.read_bytes();end=h.read(finish)
    finish.write_bytes(h.encoded(dict(end,exit_code=1)));reject(phase+' unsuccessful child',lambda p=phase:h.phase_state(p));finish.write_bytes(pristine)
    Path(str(prefix)+'-stdout.log').write_bytes(b'changed')
    reject(phase+' changed child log',lambda p=phase:h.phase_state(p));Path(str(prefix)+'-stdout.log').write_bytes(b'')
    start=Path(str(prefix)+'-started.json');start_bytes=start.read_bytes();start.write_bytes(h.encoded(dict(pid=987654321,created=124.)))
    reject(phase+' mismatched child identity',lambda p=phase:h.phase_state(p));start.write_bytes(start_bytes)
    with patch.object(h,'process_alive',return_value=True):
     assert h.phase_state(phase)==dict(started=True,alive=True,complete=True)
    r.unlink();assert h.phase_state(phase)==dict(started=True,alive=False,complete=False)
    r.write_bytes(h.encoded(value))
   p=fixture_phases['throughput'];r=folder/(p['name']+'-result.json');value=h.read(r)
   for field in ('cuda_passed','reference_agreement_passed','full_played_banks_64'):
    r.write_bytes(h.encoded(dict(value,**{field:False})));reject('throughput '+field,lambda:h.phase_state('throughput'))
   r.write_bytes(h.encoded(value))
  # The child polling implementation is the unchanged previously qualified
  # original function, including its normal process-exit race handling.
  assert h.poll_child is h.prior.poll_child and h.process_alive is h.prior.process_alive
  class Child:
   def __init__(self,codes):self.codes=iter(codes)
   def poll(self):return next(self.codes)
  with patch.object(h.prior,'process_alive',return_value=False):
   assert h.poll_child(Child([None,0]),h.INITIAL,h.TRAIN_SCRIPT)==0
   reject('live child identity mismatch',lambda:h.poll_child(Child([None,None]),h.INITIAL,h.TRAIN_SCRIPT))
  with patch.object(h.prior,'process_alive',side_effect=ValueError('wrong script')):
   assert h.poll_child(Child([None,0]),h.INITIAL,h.TRAIN_SCRIPT)==0
   reject('live child wrong script',lambda:h.poll_child(Child([None,None]),h.INITIAL,h.TRAIN_SCRIPT))
  for phase in phases:
   cmd=h.command(phase);assert cmd[-1]=='--run' and '--resume' not in cmd and 'training' not in h.PHASES
   assert Path(cmd[2])==h.ROOT/'tools/research'/h.PHASES[phase]['script']
  live=h.observe();assert not live['failure'] and h.decide(live) in ('wait-training','throughput')
  assert all(not live[p]['started'] for p in phases)
  h.prior.verify_inputs(inputs)
  answer=dict(complete=True,passed=True,runner_sha256=h.sha(h.__file__),seconds=time.monotonic()-began,inputs=inputs,
   decisions=decisions,guarded_combinations=guarded,negative_cases=negative,live_observation=live,
   pressure_identity=identity,synthetic_artifacts={str(p):h.sha(p) for p in folder.rglob('*') if p.is_file()},
   ordering_qualified=True,no_training_launch=True,unchanged_child_polling=True,
   child_launches=0,scientific_fits=0,native_calls=0,new_scientific_deals=0,gpu=False,
   actual_full_bank_cuda_check=False,actual_scientific_evaluation=False,production_modified=False)
  h.save(result,answer);print(json.dumps(dict(passed=True,seconds=answer['seconds'],decisions=len(decisions),guarded=guarded,negative_cases=len(negative),live_counts=live['counts'])))
 except BaseException as error:
  h.save(failure,dict(error=repr(error),traceback=traceback.format_exc(),preserve_evidence=True,automatic_retry_allowed=False));raise

if __name__=='__main__':main()
