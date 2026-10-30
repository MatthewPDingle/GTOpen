import copy,hashlib,json,re,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D108-resource-feasibility-audit';assert not H.exists();H.mkdir()
policy=old.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md';helper=old.REPO/'tools/postflop_resource_feasibility.py'
A=ROOT/'runs/D101-resource-eligibility-audit';prior=old.read(A/'report.json');proofpath=ROOT/'runs/D094-resource-materiality/report.json';proof=old.read(proofpath)
old.pin(proofpath,'86f8062d84a2eba0d5387961abc337b2576072509e1f1d9c0627dce6fc2191f4')
old.pin(old.REPO/'tools/postflop_resource_admission.py','4ff9b4e57b6facb5d6b07a6c67b18695e524f7fd54879fbd6ac6b177892cc720')
status=old.read(old.ar.STATUS);parents={e['id']:e for e in status['experiments'] if re.fullmatch(r'E[0-9]{3}',e['id'])}
assert set(parents)=={f'E{i:03d}' for i in range(1,66)}-{'E011'}
old.save(H/'candidate-registry-snapshot.json',{'at':old.now(),'parents':[parents[k] for k in sorted(parents)],'missing_E011':'unimplemented; no canonical parent/source or runtime result claimed'})
paths=[Path(x['report']) for x in prior['resource_reports']]
paths += [ROOT/'runs'/n/'report.json' for n in ['D049-down-action-pointer-resource','E061-resource','E062-resource','E063-resource','E064-resource']]
assert len(paths)==len(set(paths))==21
resources=[]
for p in paths:
 d=old.read(p);resources.append({'path':str(p),'sha256':old.sha(p),'status':d.get('status'),'kernel_launches':d.get('kernel_launches'),'solver_executions':d.get('solver_executions'),'performance_measured':d.get('performance_measured',d.get('performance_measurement')),'failed_gates':[k for k,v in d.get('gates',{}).items() if v is False]})
rows=[];eligible=['E031','E043','E059'];eligible_sources={
 'E031':(ROOT/'runs/E031-design/base/kernels.cu',ROOT/'runs/E031-design/candidate/kernels.cu','up_show',ROOT/'runs/E031-show-card-offset-resource/report.json'),
 'E043':(ROOT/'runs/E043-design/baseline.cu',ROOT/'runs/E043-design/candidate.cu','down_action',ROOT/'runs/E043-resource-r2/report.json'),
 'E059':(ROOT/'runs/E059-source/baseline.cu',ROOT/'runs/E059-source/candidate.cu','up_chance',ROOT/'runs/E059-resource/report.json')}
assert old.sha(ROOT/'runs/D049-down-action-pointer-resource/candidate.cu')==old.sha(eligible_sources['E043'][1])
for id,e in sorted(parents.items()):
 if id in eligible: reason='Eligible for separately attributed fresh feasibility/mechanism/ABI review, exact numerical controls and fixed solve-speed qualification; no original application execution.'
 elif id=='E046':reason='Recorded ABI failure; integrated caller/layout contract incomplete; excluded rather than waived or redesigned.'
 elif id=='E064':reason='Intended static integer reduction absent (64-bit sites779to788), maxthreads1024to896; excluded, no source variant.'
 elif id in ['E050','E057','E061','E062']:reason='Original source now has failed measured timing via E061/E062; closed including aliases.'
 elif id=='E065':reason='Frozen CPU component screen failed; closed without additional samples/source variants.'
 else:reason='No eligible resource-only unmeasured form in bounded indexed inventory; accepted, known timed/numerical/mechanism failure or no resource-only candidate. Original registry reason retained.'
 rows.append({'id':id,'old_status':e['status'],'original_registry_reason':e.get('reason'),'eligible':id in eligible,'decision':reason})
source_rows=[];inputs=[Path(__file__),policy,helper,A/'report.json',A/'inputs.json',proofpath,old.REPO/'tools/postflop_resource_admission.py',H/'candidate-registry-snapshot.json',*paths]
for id,(b,c,entry,report) in eligible_sources.items():
 d=old.read(report);assert d['kernel_launches']==d['solver_executions']==0 and d.get('performance_measured',d.get('performance_measurement')) is False
 for p in (ROOT/'runs').iterdir(): assert not re.fullmatch(id+r'(R[0-9]+|C[0-9]+|O[0-9]+)',p.name),p
 h=old.sha(c);cmd=['rg','-l','-F',h,str(ROOT/'binaries'),'-g','*.manifest.json'];x=subprocess.run(cmd,capture_output=True,text=True);assert x.returncode==1 and not x.stdout
 source_rows.append({'original_id':id,'alias':'D049 exact same full candidate' if id=='E043' else None,'entry':entry,'baseline':str(b),'baseline_sha256':old.sha(b),'candidate':str(c),'candidate_sha256':h,'original_resource_report':str(report),'original_resource_report_sha256':old.sha(report),'original_application_kernels':0,'original_solver_executions':0,'original_performance_samples':0,'no_primary_cohort_directory':True,'candidate_full_hash_absent_from_integrated_binary_manifest_registry':True,'fresh_intended_mechanism_review_required':True})
 inputs.extend([b,c])
# Boundary and malformed-input checks are for the decision helper, not a solver-speed result.
b=old.read(ROOT/'runs/E061-resource/report.json')['details']['rainbow_p0']['baseline'];c=copy.deepcopy(b);c['registers']=48;c['static_shared_bytes']+=208;c['occupancy_by_threads']=[[64,10],[128,10],[256,5]]
tests=[]
def check(name,bb,cc,want):
 a=evaluate_feasibility(bb,cc,proof);assert all(a['gates'].values()) is want;tests.append({'name':name,'admitted':all(a['gates'].values()),'warnings':a['resource_warnings']})
check('unchanged',b,b,True);check('feasible register/static/occupancy risk disclosed',b,c,True)
for field,value in [('local_bytes_per_thread',8),('dynamic_shared_bytes',b['dynamic_shared_bytes']+4),('max_threads',896),('fits_default_limits',False),('occupancy_by_threads',[[64,10],[128,0],[256,5]])]:
 q=copy.deepcopy(c);q[field]=value;check('reject '+field,b,q,False)
try:q=copy.deepcopy(c);del q['registers'];evaluate_feasibility(b,q,proof);raise AssertionError('missing attrs admitted')
except ValueError:tests.append({'name':'reject missing register attribute','rejected':True})
old.save(H/'helper-checks.json',{'at':old.now(),'checks':tests,'count':len(tests),'native_compilation_or_execution':0})
old.save(H/'report.json',{'id':'D108','at':old.now(),'status':'prospective_feasibility_policy_and_fixed_docket_frozen','policy_sha256':old.sha(policy),'helper_sha256':old.sha(helper),'prior_strict_helper_preserved':True,'canonical_parents':64,'resource_reports':resources,'candidate_decisions':rows,'eligible_in_fixed_order':source_rows,'known_runtime_or_numerical_failures_reopened':False,'new_native_executions':0,'source_activated':False,'speed_gain_claimed':False,'limits':'Bounded canonical registry/indexed-resource/source-hash audit; not exhaustive semantic uniqueness across all external/unindexed work. No physical allocation counters. Changed resource risk needs actual qualification; this audit cannot establish speed or no material cost. Root review only.'})
old.save(H/'docket.json',{'id':'D108-docket','at':old.now(),'order':eligible,'qualification_ids':['E066','E067','E068'],'original_aliases':{'E043':'D049 exact source, counted once'},'policy_sha256':old.sha(policy),'audit_report_sha256':old.sha(H/'report.json'),'accepted_base':'E051','rule':'Exact original changed entry on then-accepted base only if original/current baseline entry exactly equal; otherwise defer, no context-driven redesign. Fresh stages; no prior timing used. All current1%/fixture/fresh16/broader/material/holdout/cumulative requirements unchanged.','native_executions':0,'candidate_accepted':False})
inputs.extend([H/'report.json',H/'docket.json',H/'helper-checks.json']);old.save(H/'inputs.json',{'at':old.now(),'sha256':{str(p):old.sha(p) for p in inputs}})
published={}
for p in [*H.iterdir(),policy,helper,Path(__file__)]:
 if not p.is_file():continue
 key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(e['id']=='D108' for e in s['experiments'])
 s['experiments'].append({'id':'D108','at':old.now(),'kind':'diagnostic','title':'Separate resource feasibility from measured material cost','status':'measured','correctness':'pass','reason':'64canonical parents and21indexed resource reports reviewed. E031,D049/E043,E059 are exact never-kernel-executed forms in fixed order. Shared/register/occupancy changes are warnings; launch fit, capacity, spills, ABI and emitted mechanism remain gates. Known timing/numerical failures remain closed.','evidence':[{'label':'Prospective feasibility policy','url':'evidence/'+H.name+'/'+policy.name},{'label':'Full inventory and alias audit','url':'evidence/'+H.name+'/report.json'},{'label':'Frozen source-form order','url':'evidence/'+H.name+'/docket.json'},{'label':'Boundary checks','url':'evidence/'+H.name+'/helper-checks.json'}]})
 s.update(updated_at=old.now(),state='running',active_experiment=None,stage='Prospective resource feasibility published before native tests',activity='Resource warnings separated from actual material costs; user1% complete-solve/exactness/fixture gates unchanged. E066 will assess original untimed E031card-offset cache; no old speed failure retried.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'status':'audit_published_before_native','eligible':eligible,'policy_sha256':old.sha(policy),'report_sha256':old.sha(H/'report.json'),'helper_checks':len(tests),'published':len(published),'native':0}),flush=True)
