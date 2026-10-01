"""Synthetic fixed-teacher binding controls; no inference, fit, native or CUDA."""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import copy
from pathlib import Path
import time
import traceback
import psutil
import stack_context_fixed_teacher_v1 as t

NAME='stack-context-fixed-teacher-check-v2';OUT=t.OUT
def main():
 attempt,result,failed=(OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure'))
 assert not any(p.exists() for p in (attempt,result,failed))
 psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
 controls=[OUT/(n+'-result.json') for n in ('stack-context-pressure-consumer-check-v3',
  'stack-context-teacher-native-plan-check-v1','stack-context-teacher-native-plan-readback-v1')]
 paths={Path(__file__).resolve(),Path(t.__file__).resolve(),t.DESIGN,OUT/'STACK-CONTEXT-FIXED-TEACHER-BINDING.md',*controls}
 for p in controls:
  c=t.pressure.read(p);assert c['passed'] and c['complete']
  if 'inputs' in c:
   t.pressure.continuation.legacy.verify(c['inputs']);paths.update(map(Path,c['inputs']))
  else:
   assert p.name=='stack-context-teacher-native-plan-readback-v1-result.json'
   original=OUT/'stack-context-teacher-native-plan-check-v1-result.json'
   reader=Path(__file__).with_name('stack_context_teacher_native_plan_readback_v1.py')
   assert c['result_sha256']==t.pressure.sha(original) and c['reader_source_sha256']==t.pressure.sha(reader)
   paths.update((original,reader))
 paths.update((Path(__file__).with_name('stack_context_fixed_teacher_check_v1.py'),
  OUT/'stack-context-fixed-teacher-check-v1-preflight-failure.json'))
 inputs={str(p):t.pressure.sha(p) for p in paths}
 t.pressure.coordinator.save(attempt,dict(inputs=inputs,qualification_only=True))
 begin=time.monotonic();negative=[]
 def reject(name,fn):
  try:fn()
  except (ValueError,KeyError,FileNotFoundError):negative.append(name)
  else:raise AssertionError('Accepted '+name)
 try:
  def ref(g):
   h=t.digest(dict(synthetic_generation=g));return dict(generation=g,file='fullstackmodel-'+h+'.json',sha256=h)
  checkpoint=t.digest(dict(synthetic_checkpoint=64))
  selected=dict(arm='A-baseline',input_width=362,completed_cycles=64,registry_sha256='1'*64,
   checkpoint=dict(file='jointcontextcheckpoint-'+checkpoint+'.json',sha256=checkpoint),
   played=[ref(i) for i in range(64)],excluded_unplayed=ref(64),weights_by_player=[list(range(1,65)) for _ in (0,1)])
  selection=dict(format=4,training_registration_sha256=t.pressure.coordinator.REG_SHA,selection_uses_test_results=False,
   recognized_clean_pressure_stop_only=True,original_selection_and_weights_unchanged=True,
   arms={arm:copy.deepcopy(selected) for arm in t.pressure.coordinator.COUNTS})
  def bind(value=selection,**changes):
   args=dict(selection_identity=t.digest(value),gate_identity='2'*64,training_identity=t.pressure.coordinator.REG_SHA,design_identity=t.DESIGN_SHA)
   args.update(changes);return t.selected_manifest(value,**args)
  manifest=bind();raw=dict(manifest);raw.pop('sha256');assert t.digest(raw)==manifest['sha256']
  assert manifest['played']==selected['played'] and manifest['weights_by_player']==selected['weights_by_player']
  assert manifest['excluded_unplayed']==ref(64) and not manifest['diagnostic_scientifically_admitted']
  for field,new in [('arm','B-baseline'),('input_width',387),('completed_cycles',63),
   ('weights_by_player',[list(range(64)) for _ in (0,1)]),('played',selected['played'][1:]),
   ('excluded_unplayed',ref(63))]:
   value=copy.deepcopy(selection);value['arms']['A-baseline'][field]=new
   reject('wrong fixed teacher '+field,lambda v=value:bind(v))
  value=copy.deepcopy(selection);value['arms']['A-baseline']['played'][0]=ref(64)
  reject('unplayed generation in teacher',lambda:bind(value))
  for field,new in [('format',3),('selection_uses_test_results',True),('recognized_clean_pressure_stop_only',False),
   ('original_selection_and_weights_unchanged',False),('training_registration_sha256','0'*64)]:
   value=copy.deepcopy(selection);value[field]=new;reject('changed selection '+field,lambda v=value:bind(v))
  for name,new in [('selection_identity','0'*64),('training_identity','0'*64),('design_identity','0'*64),('gate_identity','bad')]:
   reject(name,lambda name=name,new=new:bind(**{name:new}))
  manifest['played'][0]['sha256']='0'*64;assert selected['played'][0]['sha256']!=manifest['played'][0]['sha256']
  reject('unrelated arbitrary teacher',lambda:t.evaluate_plan(teacher=object(),teacher_manifest=bind()))
  # Live training has not supplied the required complete-bank gate. Refusal is
  # expected and must precede model loading, native execution or fitting.
  assert not t.GATE.exists();reject('actual incomplete teacher cannot be loaded',lambda:t.actual_manifest(guard=lambda:None))
  t.pressure.continuation.legacy.verify(inputs)
  answer=dict(complete=True,passed=True,inputs=inputs,seconds=time.monotonic()-begin,negative_cases=negative,
   synthetic_manifest=bind(),selection_fixed_a_baseline=True,weights_1_to_64=True,excluded_generation=64,
   teacher_manifest_pairing_checked=True,qualification_only=True,actual_fixed64_teacher_available=False,
   actual_inference_qualified=False,diagnostic_registered=False,fits=0,native_calls=0,new_scientific_deals=0,
   gpu=False,production_modified=False,scientific_accuracy_evidence=False)
  t.pressure.coordinator.save(result,answer)
  print(dict(passed=True,seconds=answer['seconds'],negative_cases=len(negative),actual_inference_qualified=False))
 except BaseException as error:
  t.pressure.coordinator.save(failed,dict(error=repr(error),traceback=traceback.format_exc(),preserve_evidence=True));raise
if __name__=='__main__':main()
