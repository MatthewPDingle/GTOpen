"""Independent qualification readback; no scientific execution or admission."""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import ast
import hashlib
import json
from pathlib import Path
import time
import psutil

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-context-pressure-evaluation-handoff-v1'
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def definitions(name):
 return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse((ROOT/'tools/research'/name).read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def main():
 target=OUT/(NAME+'-readback-result.json');assert not target.exists()
 control=OUT/(NAME+'-check-result.json');consumer=OUT/'stack-context-pressure-consumer-check-v3-result.json'
 r,c=read(control),read(consumer)
 assert r['passed'] and r['complete'] and r['child_launches']==r['scientific_fits']==r['native_calls']==0
 assert not r['gpu'] and not r['actual_full_bank_cuda_check'] and not r['actual_scientific_evaluation']
 assert c['passed'] and c['complete'] and c['unchanged_evaluation_functions_verified']
 assert c['qualification_revision']==3 and c['scientific_workers_launched']==c['scientific_fits']==c['native_calls']==0
 assert not c['actual_cuda_qualified'] and not c['scientific_accuracy_qualified']
 inputs={str(control):sha(control),str(consumer):sha(consumer),str(Path(__file__).resolve()):sha(__file__)}
 for record in (r,c):
  for p,h in record['inputs'].items():assert sha(p)==h;inputs[p]=h
 for p,h in r['synthetic_artifacts'].items():assert sha(p)==h;inputs[p]=h
 old=read(OUT/'stack-context-pressure-consumer-check-v2-result.json')
 assert old['passed'] and old['complete'] and 'unchanged_evaluation_functions_verified' not in old
 assert read(OUT/'stack-context-pressure-consumer-check-v1-failure.json')['error']=="AssertionError('main')"
 # Independent comparison: every function is unchanged from the preceding
 # pressure prototype. Globals only route names and corrected control schema.
 for a,b in [('stack_context_matched_evaluation_v4.py','stack_context_matched_evaluation_v5.py'),
  ('stack_context_final_bank_throughput_v3.py','stack_context_final_bank_throughput_v4.py'),
  ('stack_context_matched_readback_v5.py','stack_context_matched_readback_v6.py')]:
  assert definitions(a)==definitions(b)
 phases=('throughput','evaluation','readback')
 for row in r['decisions']:
  s=row['state']
  if s['failure']:expected='review-failure'
  elif s['external_owner']:expected='wait-owner'
  elif s['training_alive']:expected='wait-training'
  elif not s['training_complete']:expected='review-training'
  else:
   expected='done'
   for p in phases:
    q=s[p]
    if q['alive']:expected='wait-'+p;break
    if q['complete']:continue
    expected='review-'+p if q['started'] else p;break
  assert expected==row['expected'] and expected!='training'
 assert len(r['decisions'])==17 and r['guarded_combinations']==24
 assert len(r['negative_cases'])==len(set(r['negative_cases']))==20
 folder=OUT/(NAME+'-check-fixtures')
 for name in ('stack-context-final-bank-throughput-v4','stack-context-matched-evaluation-v5','stack-context-matched-readback-v6'):
  p=read(folder/(name+'-result.json'));assert p['registration_sha256']==sha(folder/(name+'-registration.json'))
 for arm,n in r['pressure_identity']['complete_boundary_counts'].items():
  p=read(Path('S:/GTOpen-research/stack-context-matched-learning-v1')/arm/'progress.json')
  prefix=dict(p,completed_cycles=n,checkpoint=p['updates'][n-1]['checkpoint'],updates=p['updates'][:n])
  digest=hashlib.sha256((json.dumps(prefix,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
  assert digest==r['pressure_identity']['complete_prefix_sha256'][arm]
 reg=OUT/'stack-context-matched-learning-v1-registration.json';assert sha(reg)=='ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'
 p=psutil.Process(90820);assert abs(p.create_time()-1790818100.9586046)<.01 and p.ppid()==2980
 assert any(str(v).endswith('stack_context_pressure_continuation_v2.py') for v in p.cmdline())
 assert all(not (OUT/(name+'-attempt.json')).exists() for name in ('stack-context-final-bank-throughput-v4','stack-context-matched-evaluation-v5','stack-context-matched-readback-v6'))
 answer=dict(complete=True,passed=True,unix=time.time(),inputs=inputs,check_result_sha256=sha(control),consumer_control_sha256=sha(consumer),
  reader_sha256=sha(__file__),independent_order_controls=len(r['decisions']),independent_prefix_controls=4,
  authenticated_inputs=len(inputs),authenticated_synthetic_artifacts=len(r['synthetic_artifacts']),
  original_scientific_functions_unchanged=True,consumer_schema_verified=True,prior_qualification_evidence_preserved=True,
  qualification_only=True,child_launches=0,native_calls=0,fits=0,new_scientific_deals=0,gpu=False,production_modified=False,
  actual_cuda_qualification=False,scientific_accuracy_qualification=False,live_trainer=dict(pid=p.pid,created=p.create_time(),parent=p.ppid()))
 with target.open('xb') as f:f.write((json.dumps(answer,sort_keys=True,separators=(',',':'))+'\n').encode());f.flush();os.fsync(f.fileno())
 print(json.dumps({k:answer[k] for k in ('passed','authenticated_inputs','authenticated_synthetic_artifacts','independent_order_controls')}))
if __name__=='__main__':main()
