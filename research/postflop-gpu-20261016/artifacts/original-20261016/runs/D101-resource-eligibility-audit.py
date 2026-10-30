"""Audit every indexed nominal-only rejection without native execution or timing."""
import json,re,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_admission import evaluate_pair
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D101-resource-eligibility-audit';H.mkdir()
policy=old.REPO/'research/postflop-gpu-20261016/unmeasured-resource-eligibility-20261017.md'
original_policy=old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md'
old.pin(original_policy,'289bafbc20e30832ca3dca5c3d07f39c64271341bbc4027de42563bfcb2974c9')
proofpath=ROOT/'runs/D094-resource-materiality/report.json';old.pin(proofpath,'86f8062d84a2eba0d5387961abc337b2576072509e1f1d9c0627dce6fc2191f4');proof=old.read(proofpath)
old.pin(old.REPO/'tools/postflop_resource_admission.py','4ff9b4e57b6facb5d6b07a6c67b18695e524f7fd54879fbd6ac6b177892cc720')
status=old.read(old.ar.STATUS);parents={e['id']:e for e in status['experiments'] if re.fullmatch(r'E\d{3}',e['id'])}
assert len(parents)==59 and set(parents)=={f'E{i:03d}' for i in range(1,61)}-{'E011'}
old.save(H/'candidate-registry-snapshot.json',{'at':old.now(),'parents':[parents[k] for k in sorted(parents)],'missing_parent_before61':['E011'],'scope':'Indexed canonical registry; absence of E011 is recorded, not silently counted as a reviewed outcome.'})
cmd=['rg','-l','registers_not_increased|register_nonregression_gate',str(ROOT/'runs'),str(ROOT/'comparisons'),'-g','*report*.json']
search=subprocess.run(cmd,capture_output=True,text=True);assert search.returncode==0
files=sorted({Path(x) for x in search.stdout.splitlines()});assert len(files)==16
old.save(H/'resource-report-search.json',{'at':old.now(),'command':cmd,'returncode':search.returncode,'report_sha256':{str(p):old.sha(p) for p in files}})
eligible=[];report_rows=[];inputs=[Path(__file__),policy,original_policy,proofpath,old.REPO/'tools/postflop_resource_admission.py',H/'candidate-registry-snapshot.json',H/'resource-report-search.json']
for path in files:
 q=old.read(path);inputs.append(path);identity=path.parent.name[:4];failed=[k for k,v in q.get('gates',{}).items() if not v]
 row={'original_id':identity,'report':str(path),'report_sha256':old.sha(path),'original_status':q.get('status'),'original_failed_gates':failed,'eligible':False}
 if identity=='E031':
  rr=[v for v in q['records'] if v.get('stage')=='resource'];b={v['shape']:v for v in rr if v['source_variant']=='baseline'};c={v['shape']:v for v in rr if v['source_variant']=='candidate'}
  assert set(b)==set(c) and any(c[k]['static_shared_bytes']>b[k]['static_shared_bytes'] for k in b)
  row.update(reason='Static shared memory increases1040to1248; some actual128thread occupancies decrease12to11. Not a nominal-only rejection.',static_shared_before_after=[1040,1248])
 elif not failed:row['reason']='Original resource filter passed; this is not an unmeasured nominal-only rejection.'
 else:
  if q.get('details'):
   pairs={k:(v['baseline'],v['candidate']) for k,v in q['details'].items()}
  else:
   raw=[x for x in q['raw_markers'] if x.get('stage')=='resource'];pairs={raw[0]['kernel']:(raw[0],raw[1])};assert len(raw)==2
  tests={k:evaluate_pair(b,c,proof) for k,(b,c) in pairs.items()}
  current_pass=all(all(t['gates'].values()) for t in tests.values())
  row.update(current_model_all_pairs_pass=current_pass,current_model_assessment=tests)
  nominal_only=all(k.endswith('registers_not_increased') for k in failed)
  no_execution=q.get('kernel_launches')==q.get('solver_executions')==0 and q.get('performance_measured') is False
  if nominal_only and current_pass and no_execution:
   assert identity in ['E050','E057'] and parents[identity]['status']=='rejected' and len(pairs)==10
   cuda=path.parent/'candidate.cu';sourcehash=old.sha(cuda);basehash=old.sha(path.parent/'baseline.cu')
   grep=['rg','-l','-F',sourcehash,str(ROOT/'runs'),str(ROOT/'binaries'),'-g','report.json','-g','*.manifest.json']
   hits=subprocess.run(grep,capture_output=True,text=True);assert hits.returncode==1 and hits.stdout==''
   assert not any(p.name.startswith(identity) and re.fullmatch(identity+r'(R\d+|C\d+|O\d+)',p.name) for p in (ROOT/'runs').iterdir())
   row.update(eligible=True,reason='Only nominal-register gates failed; all10same-geometry resource pairs pass current unchanged model. Original zero kernel/numerical/solver/timing execution recorded. Exact full CUDA hash absent from timed report/build-manifest registry.',original_source_sha256=sourcehash,original_baseline_sha256=basehash,exact_source_hash_search={'command':grep,'returncode':hits.returncode,'matches':[]},pair_count=10)
   eligible.append({'original_id':identity,'resource_report':str(path),'resource_report_sha256':old.sha(path),'original_candidate_cuda':str(cuda),'original_candidate_cuda_sha256':sourcehash,'original_baseline_cuda_sha256':basehash,'source_review':str(ROOT/'runs'/(identity+'-source')/'source-review.json'),'current_counterfactual_resource_assessment':tests})
   inputs.extend([cuda,path.parent/'baseline.cu',ROOT/'runs'/(identity+'-source')/'source-review.json',ROOT/'runs'/(identity+'-source')/'candidate.patch',ROOT/'runs'/(identity+'-source')/'manifest.json'])
  else:row['reason']='Known non-nominal cost, current allocation/occupancy failure, or non-resource outcome; excluded. No future test authorized by this audit.'
 report_rows.append(row)
eligible.sort(key=lambda x:x['original_id']);assert [e['original_id'] for e in eligible]==['E050','E057']
old.save(H/'report.json',{'id':'D101','at':old.now(),'status':'two_unmeasured_source_forms_eligible_for_new_resource_revalidation','registry_parent_count':59,'indexed_resource_reports':16,'resource_reports':report_rows,'eligible_in_fixed_order':eligible,'resource_policy_supplement':str(policy),'resource_policy_supplement_sha256':old.sha(policy),'old_policy_unchanged_sha256':old.sha(original_policy),'helper_unchanged_sha256':old.sha(old.REPO/'tools/postflop_resource_admission.py'),'allocation_proof_sha256':old.sha(proofpath),'rule_change':'Explicit prospective supplement permits exact source reuse only for nominal-only never-executed forms, replacing the old blanket future prohibition for this class. No old decisions/samples/labels/gates altered. This is source-form requalification, not a new independent mechanism or rescue of a measured performance/numerical failure.','source_activated':False,'new_native_executions':0,'new_kernel_launches':0,'performance_measured':False,'optimization_accepted':False,'limits':'Bounded indexed registry/report/source-hash audit; not exhaustive semantic uniqueness across unrecorded external work. Model register allocations are calibrated SDK outputs, not hardware counters. Current runtime resource revalidation and all correctness/performance/material gates still required.'})
old.save(H/'docket.json',{'id':'D101-prospective-docket','at':old.now(),'audit_report_sha256':old.sha(H/'report.json'),'policy_sha256':old.sha(policy),'order':['E050','E057'],'new_qualification_ids':['E061','E062'],'accepted_base_now':'E051','source_application_rule':'At each source qualification use exact then-current accepted base and mechanically transfer only the exact original mechanism; declare its ancestry. No retuning or rejected-mechanism composition. Freeze fresh source/resource/numerical/initial and confirmation protocols before each stage.','qualification_rule':'Current1%with strict fixture/no-material-cost/full exactness, separate fresh16/broader/holdout/fresh-original gates. Never pool/retry old timed or failed-numerical forms.','new_native_executions':0,'candidate_accepted':False})
inputs.extend([H/'report.json',H/'docket.json']);old.save(H/'inputs.json',{'at':old.now(),'sha256':{str(p):old.sha(p) for p in inputs}})
published={}
for p in [*H.iterdir(),policy,Path(__file__)]:
 if not p.is_file():continue
 key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(e['id']=='D101' for e in s['experiments'])
 s['experiments'].append({'id':'D101','at':old.now(),'kind':'diagnostic','title':'Audit unmeasured nominal-register rejections','status':'measured','correctness':'pass','stage':'Prospective source requalification docket frozen','reason':'All16indexed resource reports/59registered parents reviewed. Only E050andE057 are nominal-only, never-timed forms passing unchanged current allocated-resource model. Explicit policy supplement permits fresh attributed tests; old outcomes remain frozen. No speed gain or adoption.','evidence':[{'label':'Consistent resource eligibility inventory','url':'evidence/'+H.name+'/report.json'},{'label':'Explicit prospective eligibility supplement','url':'evidence/'+H.name+'/'+policy.name},{'label':'Fixed chronological source docket','url':'evidence/'+H.name+'/docket.json'}]})
 s.update(updated_at=old.now(),state='running',active_experiment=None,stage='Fresh qualification of unmeasured source forms',activity='D101eligibility supplement published before execution. E061will revalidate exact E050asynchronous staging form on accepted E051, then E057form follows as E062. No old timing/numerical failure retried.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'status':'prospective_inventory_published','eligible_forms':['E050','E057'],'source_requalification_ids':['E061','E062'],'resource_reports':16,'new_native_runs':0,'policy_sha256':old.sha(policy)}),flush=True)
