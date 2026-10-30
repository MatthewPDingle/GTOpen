"""Fresh qualification of the exact unmeasured E050 source form on accepted E051."""
import ast,difflib,hashlib,json,re,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
A=ROOT/'runs/D101-resource-eligibility-audit';audit=old.read(A/'report.json');docket=old.read(A/'docket.json');policy=old.REPO/'research/postflop-gpu-20261016/unmeasured-resource-eligibility-20261017.md'
assert audit['status']=='two_unmeasured_source_forms_eligible_for_new_resource_revalidation' and docket['order']==['E050','E057'];old.pin(policy,docket['policy_sha256'])
for p,h in old.read(A/'inputs.json')['sha256'].items():old.pin(p,h)
parent=ROOT/'runs/E050-resource';original=ROOT/'runs/E050-source';S=ROOT/'runs/E061-source';H=ROOT/'runs/E061-resource';assert not S.exists() and not H.exists();S.mkdir();H.mkdir()
base=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();old.pin(old.REPO/'crates/solver/src/gpu/kernels.cu',old.BASE['crates/solver/src/gpu/kernels.cu'])
def normalized(p):return Path(p).read_text(encoding='utf-8')
def show(text):
 a=text.index('extern "C" __global__ void up_show(');b=text.index('{',a);i=b+1;depth=1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return a,i,text[a:i]
current=base.decode().replace('\r\n','\n');oldbase=normalized(original/'baseline.cu');oldcandidate=normalized(original/'candidate.cu')
a,b,entry=show(current);_,_,historical_entry=show(oldbase);_,_,newentry=show(oldcandidate)
assert entry==historical_entry and entry!=newentry
candidate=(current[:a]+newentry+current[b:]).replace('\n','\r\n' if b'\r\n' in base else '\n').encode()
(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(candidate)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='accepted-E051/kernels.cu',tofile='E061-requalify-E050/kernels.cu')),encoding='utf-8',newline='')
old.save(S/'source-review.json',{'id':'E061','at':old.now(),'kind':'attributed_source_form_requalification','original_id':'E050','original_candidate_full_sha256':old.sha(original/'candidate.cu'),'original_baseline_full_sha256':old.sha(original/'baseline.cu'),'accepted_base':'E051','accepted_full_sha256':old.sha(S/'baseline.cu'),'candidate_full_sha256':old.sha(S/'candidate.cu'),'original_and_current_up_show_baseline_exact':True,'original_and_new_up_show_candidate_exact':True,'normalized_up_show_candidate_sha256':hashlib.sha256(newentry.encode()).hexdigest(),'outside_up_show_source_unchanged':True,'audit_report_sha256':old.sha(A/'report.json'),'docket_sha256':old.sha(A/'docket.json'),'policy_sha256':old.sha(policy),'source_safety_review_sha256':old.sha(original/'source-review.json'),'mechanism':'Exact original4byte cp.async.ca staging of disjoint aligned reach/card-position words, overlap existing independent CFVclear, per-thread wait_all then original CTAbarrier. Pre-sm80 fallback unchanged. Same floating operations/order, buffers/launch/ABI/quality; no width/guard/placement/source-form variant.','source_contract':'Existing separately allocated global inputs, aligned dynamic shared ranges and disjoint terminal output rows. Copies complete per thread before barrier; no consumer before wait+barrier. wait_all commits and waits prior copies; empty group completes. Full CPU/GPU actual numerical controls still required.','source_documentation_reference':'https://docs.nvidia.com/cuda/archive/12.9.1/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-wait-group-cp-async-wait-all','no_claim':'Root source review only, not external independence, numerical proof, speed or adoption.'})
owned={'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu')};old.save(S/'manifest.json',{'id':'E061','at':old.now(),'original_form':'E050','candidate_owned_sha256':owned,'source_sha256':old.BASE|owned,'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir() if p.is_file()},'source_activated':False,'no_variant':True})
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
probe=(parent/'probe.rs').read_text(encoding='utf-8').replace('E050_RESOURCE','E061_RESOURCE');(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(parent/'execute.py').read_text(encoding='utf-8').replace('E050','E061').replace("HERE.parent/'small-gain-confirmation-plan'","HERE.parent/'accepted-E051'").replace('import common as old','import common_e051 as old')
a=runner.index("  kg={'registers_not_increased'");b=runner.index('\n  details[shape]',a)
runner=runner[:a]+"  sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_admission import evaluate_pair\n  admission=evaluate_pair(b,c,old.read(P['allocation_proof']['path']))\n  kg=admission['gates']"+runner[b:]
needle="details[shape]={'baseline':b,'candidate':c,'gates':kg}";assert runner.count(needle)==1;runner=runner.replace(needle,"details[shape]={'baseline':b,'candidate':c,'gates':kg,'allocation_admission':admission}")
needle="print(json.dumps({'status':report['status'],'details':details,'gates':gates,'report_sha256':old.sha(HERE/'report.json')},indent=2),flush=True)";assert runner.count(needle)==1
runner=runner.replace(needle,"print(json.dumps({'status':report['status'],'registers':[rows['baseline','rainbow_p0']['registers'],rows['candidate','rainbow_p0']['registers']],'failed_gates':[k for k,v in gates.items() if not v],'report_sha256':old.sha(HERE/'report.json')}),flush=True)")
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=old.read(parent/'protocol.json');P.update(id='E061-resource',at=old.now(),status='FROZEN_PRE_FRESH_SOURCE_RESOURCE_EXECUTION',source_manifest_sha256=old.sha(S/'manifest.json'),original_source_form='E050',eligibility_audit_sha256=old.sha(A/'report.json'),eligibility_supplement_sha256=old.sha(policy),allocation_proof={'path':str(ROOT/'runs/D094-resource-materiality/report.json'),'sha256':old.sha(ROOT/'runs/D094-resource-materiality/report.json')},fixed_gates='D094allocated-register/helper gates all10shapes; unchanged27parameter ABI,8other entries exact,9sm75fallback entries exact,2async sites and wait_all emitted. No numerical or timing admission on any failure. Exact original E050form, no variant.')
P['rustc_command']=[x.replace(str(parent),str(H)) for x in P['rustc_command']]
old.pin(ROOT/'runs/D094-resource-materiality/report.json',P['allocation_proof']['sha256']);assert P['up_show_parameter_count']==27
paths=[*S.iterdir(),*H.iterdir(),Path(__file__),A/'report.json',A/'docket.json',A/'inputs.json',policy,original/'source-review.json',original/'candidate.cu',original/'baseline.cu',ROOT/'runs/D094-resource-materiality/report.json',ROOT/'runs/D094-resource-materiality/test-report.json',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in old.read(parent/'protocol.json')['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']};old.save(H/'protocol.json',P)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip();assert subprocess.check_output(['git','log','-1','--format=%s'],cwd=old.REPO,text=True).strip()=='research: admit fresh tests of unmeasured nominal-only resource forms'
old.save(A/'commit.json',{'at':old.now(),'commit':commit,'committed_paths':['research/postflop-gpu-20261016/unmeasured-resource-eligibility-20261017.md','research/postflop-gpu-20261016/experiments.md'],'native_executions_before_commit':0,'goal_active':True,'accepted_source':'E051'})
for folder in [S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key='evidence/'+folder.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
key='evidence/'+A.name+'/commit.json';dst=old.ar.DASHBOARD/key;assert not dst.exists();dst.write_bytes((A/'commit.json').read_bytes())
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==(A/'commit.json').read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(e['id']=='E061' for e in s['experiments'])
 next(e for e in s['experiments'] if e['id']=='D101')['evidence'].append({'label':'Prospective policy local commit','url':key})
 s['experiments'].append({'id':'E061','at':old.now(),'kind':'candidate','title':'Fresh qualification of original E050async staging','status':'running','correctness':'pending','stage':'Fresh current-source compiler/resource revalidation','reason':'Exact previously unmeasured E050up_show source form on accepted E051, admitted by explicit D101supplement before execution. Preserve original width/guards/ordering. Same physical resource and full numerical/performance gates required.','original_form':'E050','evidence':[{'label':'Exact source ancestry and transfer','url':'evidence/E061-source/source-review.json'},{'label':'Fresh resource and ABI protocol','url':'evidence/E061-resource/protocol.json'}]})
 s.update(updated_at=old.now(),state='running',active_experiment='E061',stage='E061 fresh resource revalidation',activity='Original asynchronous staging form, current E051base. No prior speed samples exist; no timing or numerical claim yet.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'candidate_sha256':old.sha(S/'candidate.cu'),'original_form':'E050','source_activated':False}),flush=True)
