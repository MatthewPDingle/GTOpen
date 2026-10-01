"""Independent synthetic binding arithmetic and source/evidence readback."""
import hashlib
import json
import os
from pathlib import Path
import time
ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-context-fixed-teacher-readback-v1'
def read(p):return json.loads(Path(p).read_bytes())
def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(v):return hashlib.sha256(encoded(v)).hexdigest()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 target=OUT/(NAME+'-result.json');assert not target.exists()
 result=OUT/'stack-context-fixed-teacher-check-v2-result.json';attempt=OUT/'stack-context-fixed-teacher-check-v2-attempt.json'
 r,a=read(result),read(attempt);assert r['passed'] and r['complete'] and a['inputs']==r['inputs']
 assert r['fits']==r['native_calls']==r['new_scientific_deals']==0 and not r['gpu']
 assert r['qualification_only'] and not r['actual_inference_qualified'] and not r['actual_fixed64_teacher_available']
 inputs={str(p):sha(p) for p in (result,attempt,Path(__file__).resolve())}
 for p,h in r['inputs'].items():assert sha(p)==h;inputs[p]=h
 def ref(g):
  h=digest(dict(synthetic_generation=g));return dict(generation=g,file='fullstackmodel-'+h+'.json',sha256=h)
 checkpoint=digest(dict(synthetic_checkpoint=64))
 selected=dict(arm='A-baseline',input_width=362,completed_cycles=64,registry_sha256='1'*64,
  checkpoint=dict(file='jointcontextcheckpoint-'+checkpoint+'.json',sha256=checkpoint),
  played=[ref(i) for i in range(64)],excluded_unplayed=ref(64),weights_by_player=[list(range(1,65)) for _ in (0,1)])
 reg='ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'
 selection=dict(format=4,training_registration_sha256=reg,selection_uses_test_results=False,
  recognized_clean_pressure_stop_only=True,original_selection_and_weights_unchanged=True,
  arms={arm:selected for arm in ('A-relative','B-relative','A-baseline','B-baseline')})
 m=r['synthetic_manifest'];raw=dict(m);raw.pop('sha256');assert digest(raw)==m['sha256']
 for k in selected:assert m[k]==selected[k]
 assert m['selection_sha256']==digest(selection) and m['actual_resource_gate_sha256']=='2'*64
 assert m['original_registration_sha256']==reg
 assert m['prospective_design_sha256']==sha(OUT/'STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md')
 assert not m['selection_uses_test_results'] and not m['diagnostic_scientifically_admitted']
 assert len({p['sha256'] for p in [*m['played'],m['excluded_unplayed']]})==65
 assert all(sum(w)==2080 and w==list(range(1,65)) for w in m['weights_by_player'])
 assert len(r['negative_cases'])==len(set(r['negative_cases']))==18
 old=read(OUT/'stack-context-fixed-teacher-check-v1-preflight-failure.json')
 assert old['error']=="KeyError('inputs')" and not old['attempt_admitted']
 assert old['source_sha256']==sha(ROOT/'tools/research/stack_context_fixed_teacher_check_v1.py')
 assert not (OUT/'stack-context-fixed-teacher-check-v1-attempt.json').exists()
 assert not (OUT/'stack-context-final-bank-throughput-v4-result.json').exists()
 answer=dict(complete=True,passed=True,inputs=inputs,unix=time.time(),reader_source_sha256=sha(__file__),
  check_result_sha256=sha(result),authenticated_inputs=len(inputs),independently_verified_generations=64,
  independently_verified_actor_weight_sums=[2080,2080],excluded_generation=64,
  fixed_teacher_choice='Prospectively A-baseline, no outcome-based choice',
  preserved_preflight_failure_verified=True,qualification_only=True,actual_teacher_inference_qualified=False,
  diagnostic_registered=False,fits=0,native_calls=0,new_scientific_deals=0,gpu=False,
  production_modified=False,scientific_accuracy_evidence=False)
 with target.open('xb') as f:f.write(encoded(answer));f.flush();os.fsync(f.fileno())
 print({k:answer[k] for k in ('passed','authenticated_inputs','independently_verified_generations')})
if __name__=='__main__':main()
