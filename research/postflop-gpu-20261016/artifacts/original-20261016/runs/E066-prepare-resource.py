import ast,difflib,hashlib,json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
A=ROOT/'runs/D108-resource-feasibility-audit';d=old.read(A/'docket.json');assert d['order']==['E031','E043','E059'] and d['qualification_ids']==['E066','E067','E068']
for p,h in old.read(A/'inputs.json')['sha256'].items():old.pin(p,h)
policy=old.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md';old.pin(policy,d['policy_sha256'])
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip();assert head.startswith('930fa211')
old.save(A/'commit.json',{'at':old.now(),'commit':head,'native_executions_before_commit':0,'committed_paths':['research/postflop-gpu-20261016/experiments.md','research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md','tools/postflop_resource_feasibility.py']})
S=ROOT/'runs/E066-source';H=ROOT/'runs/E066-resource';assert not S.exists() and not H.exists();S.mkdir();H.mkdir()
original=ROOT/'runs/E031-design';base=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();old.pin(old.REPO/'crates/solver/src/gpu/kernels.cu',old.BASE['crates/solver/src/gpu/kernels.cu'])
def show(text):
 a=text.index('extern "C" __global__ void up_show(');b=text.index('{',a);i=b+1;depth=1
 while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return a,i,text[a:i]
current=base.decode().replace('\r\n','\n');a,b,entry=show(current);_,_,priorentry=show((original/'base/kernels.cu').read_text());_,_,newentry=show((original/'candidate/kernels.cu').read_text());assert entry==priorentry and entry!=newentry
candidate=(current[:a]+newentry+current[b:]).replace('\n','\r\n' if b'\r\n' in base else '\n').encode()
(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(candidate)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='accepted-E051/kernels.cu',tofile='E066-original-E031/kernels.cu')),encoding='utf-8',newline='')
old.save(S/'source-review.json',{'id':'E066','at':old.now(),'original_form':'E031','original_candidate_full_sha256':old.sha(original/'candidate/kernels.cu'),'original_baseline_full_sha256':old.sha(original/'base/kernels.cu'),'accepted_base':'E051','accepted_cuda_sha256':old.sha(S/'baseline.cu'),'candidate_cuda_sha256':old.sha(S/'candidate.cu'),'original_current_baseline_up_show_exact':True,'original_new_candidate_up_show_exact':True,'normalized_candidate_entry_sha256':hashlib.sha256(newentry.encode()).hexdigest(),'outside_up_show_exact':True,'host_global_dynamic_launch_payload_unchanged':True,'mechanism':'Exact original53u32static shared table, block-stride preload before original first barrier; original absolute card_base and two per-card offset reads replaced by table reads. Every float expression/order, barrier, buffer, ABI and launch/caller unchanged. No cache-size/placement/map variant or composition.','source_contract':'53valid absolute offsets per river slot including empty arrays; each card0..51 plus1 is in range. Every positive block width covers all53words. Inputs are immutable separately allocated; consumers follow existing barrier; no floating reorder. Fresh numerical tests still required.','history_inputs':{str(p):old.sha(p) for p in [original/'manifest.json',original/'source-checks.json',ROOT/'comparisons/E031-source-review/report.json',ROOT/'comparisons/E031-resource-review/manifest.json',A/'report.json',A/'docket.json',A/'commit.json']},'no_claim':'Root source ancestry/safety review; no new native execution, speed gain or no-material-cost conclusion.'})
owned={'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu')};old.save(S/'manifest.json',{'id':'E066','at':old.now(),'original_form':'E031','candidate_owned_sha256':owned,'source_sha256':old.BASE|owned,'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir() if p.is_file()},'source_activated':False,'no_variant':True})
prior=ROOT/'runs/E061-resource'
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
probe=(prior/'probe.rs').read_text().replace('E061_RESOURCE','E066_RESOURCE').replace('max_threads>=128&&block_limit>=128','max_threads>=256&&block_limit>=256');(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(prior/'execute.py').read_text().replace('E061','E066')
a=runner.index(" gates={'other8_entries_exact'");b=runner.index('\n details={}',a)
runner=runner[:a]+" gates={'other8_entries_exact':set(unchanged)==set(be)-{'up_show'},'other8_sm75_entries_exact':all(bf[k]==cf[k] for k in bf if k!='up_show'),'up_show_changed_actual':be['up_show']!=ce['up_show'],'up_show_changed_sm75':bf['up_show']!=cf['up_show'],'full212byte_cache_emitted_actual':'card_off_sh[212]' in ce['up_show'],'full212byte_cache_emitted_sm75':'card_off_sh[212]' in cf['up_show'],'all_original_barriers_retained':be['up_show'].count('bar.sync')==ce['up_show'].count('bar.sync')==5}"+runner[b:]
runner=runner.replace('from postflop_resource_admission import evaluate_pair','from postflop_resource_feasibility import evaluate_feasibility').replace("admission=evaluate_pair(b,c,old.read(P['allocation_proof']['path']))","admission=evaluate_feasibility(b,c,old.read(P['allocation_proof']['path']))").replace("kg=admission['gates']","kg=admission['gates']|{'same_dynamic_bytes':b['dynamic_shared_bytes']==c['dynamic_shared_bytes']}")
runner=runner.replace("'allocation_admission':admission","'feasibility_admission':admission").replace("'registers':[rows['baseline','rainbow_p0']['registers'],rows['candidate','rainbow_p0']['registers']]","'registers':[rows['baseline','rainbow_p0']['registers'],rows['candidate','rainbow_p0']['registers']],'static_shared':[rows['baseline','rainbow_p0']['static_shared_bytes'],rows['candidate','rainbow_p0']['static_shared_bytes']]")
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=old.read(prior/'protocol.json');P.update(id='E066-resource',at=old.now(),status='FROZEN_PRE_FRESH_SOURCE_RESOURCE_EXECUTION',source_manifest_sha256=old.sha(S/'manifest.json'),original_source_form='E031',eligibility_audit_sha256=old.sha(A/'report.json'),eligibility_supplement_sha256=old.sha(policy),policy_commit=head,fixed_gates='D108feasibility helper all10shapes including conservative1326hands, all64/128/256controls; unchanged27parameter ABI;8other entries exact actual/sm75;full212Bcache emitted and5original barriers retained. Resource differences disclosed, no performance/adoption conclusion.')
P['rustc_command']=[x.replace(str(prior),str(H)) for x in P['rustc_command']]
paths=[*S.iterdir(),*H.iterdir(),Path(__file__),A/'report.json',A/'docket.json',A/'inputs.json',A/'helper-checks.json',A/'commit.json',policy,old.REPO/'tools/postflop_resource_feasibility.py',old.REPO/'tools/postflop_resource_admission.py',ROOT/'runs/D094-resource-materiality/report.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in old.read(prior/'protocol.json')['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']};old.save(H/'protocol.json',P)
for folder in [S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key='evidence/'+folder.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
p=A/'commit.json';key='evidence/'+A.name+'/commit.json';dst=old.ar.DASHBOARD/key;assert not dst.exists();dst.write_bytes(p.read_bytes())
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(e['id']=='E066' for e in s['experiments'])
 next(e for e in s['experiments'] if e['id']=='D108')['evidence'].append({'label':'Policy committed before execution','url':key})
 s['experiments'].append({'id':'E066','at':old.now(),'kind':'candidate','original_form':'E031','title':'Fresh qualification of original shared card-offset cache','status':'running','correctness':'pending','stage':'Fresh resource/ABI/emitted-mechanism review','reason':'Exact original untimed E031entry on E051under prospectively committed D108feasibility policy. No size/placement/source variant. Complete numerical/speed/material gates still required.','evidence':[{'label':'Exact source ancestry','url':'evidence/E066-source/source-review.json'},{'label':'Fresh feasibility protocol','url':'evidence/E066-resource/protocol.json'}]})
 s.update(updated_at=old.now(),state='running',active_experiment='E066',stage='E066 fresh resource feasibility',activity='Original53word shared offset cache, exact source transfer. Driver launch/capacity and emitted-mechanism checks before any application kernel. Accepted E05112.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'candidate_sha256':old.sha(S/'candidate.cu'),'source_activated':False,'policy_commit':head}),flush=True)
