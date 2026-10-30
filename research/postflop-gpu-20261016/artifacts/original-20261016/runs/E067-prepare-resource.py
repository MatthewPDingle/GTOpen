import ast,difflib,hashlib,json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
A=ROOT/'runs/D108-resource-feasibility-audit';d=old.read(A/'docket.json');assert d['order']==['E031','E043','E059']
for p,h in old.read(A/'inputs.json')['sha256'].items():old.pin(p,h)
policy=old.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md';old.pin(policy,d['policy_sha256']);pc=old.read(A/'commit.json')['commit'];assert pc=='930fa211f6b63c3e28777247c5ed54f759cf4c3e'
assert old.read(ROOT/'runs/E066-closure/decision.json')['decision']=='rejected_complete_cycle_screen' and old.read(ROOT/'runs/E066-primary-manager/complete.json')['all_owned_children_terminal']
S=ROOT/'runs/E067-source';H=ROOT/'runs/E067-resource';assert not S.exists() and not H.exists();S.mkdir();H.mkdir()
original=ROOT/'runs/E043-design';alias=ROOT/'runs/D049-down-action-pointer-resource';assert old.sha(original/'candidate.cu')==old.sha(alias/'candidate.cu')
base=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();old.pin(old.REPO/'crates/solver/src/gpu/kernels.cu',old.BASE['crates/solver/src/gpu/kernels.cu'])
def function(text,signature):
 a=text.index(signature);b=text.index('{',a);i=b+1;depth=1
 while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return a,i,text[a:i]
current=base.decode().replace('\r\n','\n');ob=(original/'baseline.cu').read_text();oc=(original/'candidate.cu').read_text()
sig='template<int NA>\n__device__ __forceinline__ void down_action_impl('
a,b,helper=function(current,sig);_,_,oldhelper=function(ob,sig);_,_,newhelper=function(oc,sig);assert helper==oldhelper and helper!=newhelper
wrapper='extern "C" __global__ void down_action(';assert function(current,wrapper)[2]==function(ob,wrapper)[2]==function(oc,wrapper)[2]
reversed_helper=newhelper.replace('const u32* rsrc_a = actor == 0 ? rsrc0 : rsrc1;\n    u32 src = rsrc_a[n];','u32 src = actor == 0 ? rsrc0[n] : rsrc1[n];').replace('rsrc_a[child]','(actor == 0 ? rsrc0[child] : rsrc1[child])');assert reversed_helper==helper
candidate=(current[:a]+newhelper+current[b:]).replace('\n','\r\n' if b'\r\n' in base else '\n').encode()
(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(candidate)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='accepted-E051/kernels.cu',tofile='E067-original-D049-E043/kernels.cu')),encoding='utf-8',newline='')
old.save(S/'source-review.json',{'id':'E067','at':old.now(),'original_form':'D049/E043 exact same source counted once','original_candidate_full_sha256':old.sha(original/'candidate.cu'),'original_baseline_full_sha256':old.sha(original/'baseline.cu'),'accepted_base':'E051','accepted_cuda_sha256':old.sha(S/'baseline.cu'),'candidate_cuda_sha256':old.sha(S/'candidate.cu'),'original_current_baseline_helper_exact':True,'original_new_candidate_helper_exact':True,'exported_wrapper_source_unchanged_original_baseline_candidate_current':True,'normalized_candidate_helper_sha256':hashlib.sha256(newhelper.encode()).hexdigest(),'outside_down_action_impl_exact':True,'exact_reversal_of_three_integer_pointer_statements_to_accepted':True,'same_floating_expressions_guards_loops_and_order':True,'host_global_dynamic_launch_payload_unchanged':True,'mechanism':'Exact original selected immutable actor map pointer before hand loops; use it for original parent and child reach-slot indices. Actor0selectsmap0; allotheractors selectmap1 as before. No restrict, explicit hoist, table, cache, FP, buffer, ABI, host or launch change.','policy_interpretation':'D108changed down_action entry is implemented by its inlined template helper; transfer that exact original helper only. Original/current baseline helper AND exported wrapper are byte-exact after newline normalization. No helper redesign or new form.','source_contract':'Same original separately allocated immutable map buffers, valid source/child indices, player/hand dimensions, nonaliasing child writes, lock/threshold/fallback guards. Only integer pointer selection rearranged, all FP statements unchanged. Requires fresh actual kernel controls.','history_inputs':{str(p):old.sha(p) for p in [original/'manifest.json',alias/'protocol.json',alias/'report.json',alias/'ptx-inspection.json',A/'report.json',A/'docket.json',A/'commit.json']},'no_claim':'Root source ancestry/safety review only; no new native execution, numerical proof, speed or no-material-cost conclusion.'})
owned={'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu')};old.save(S/'manifest.json',{'id':'E067','at':old.now(),'original_form':'D049/E043','candidate_owned_sha256':owned,'source_sha256':old.BASE|owned,'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir() if p.is_file()},'source_activated':False,'no_variant':True})
prior=ROOT/'runs/E066-resource'
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
probe=(prior/'probe.rs').read_text().replace('E066','E067').replace('up_show','down_action')
a=probe.index(' let shapes=');b=probe.index('\n for arch',a);probe=probe[:a]+' let shapes=["all_action_hands_menus"];'+probe[b:]
probe=probe.replace('for (shape,nh_o,m) in shapes','for shape in shapes').replace('let dynamic=4*nh_o+16*m;','let dynamic=0u32;').replace('"resource_rows":20','"resource_rows":2')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(prior/'execute.py').read_text().replace('E066','E067').replace('up_show','down_action').replace('len(markers)==22','len(markers)==4').replace('len(rows)==20','len(rows)==2').replace("'rainbow_p0'","'all_action_hands_menus'")
a=runner.index(" gates={'other8_entries_exact'");b=runner.index('\n details={}',a)
runner=runner[:a]+" gates={'other8_entries_exact':set(unchanged)==set(be)-{'down_action'},'other8_sm75_entries_exact':all(bf[k]==cf[k] for k in bf if k!='down_action'),'down_action_changed_actual':be['down_action']!=ce['down_action'],'down_action_changed_sm75':bf['down_action']!=cf['down_action']}"+runner[b:]
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=old.read(prior/'protocol.json');P.update(id='E067-resource',at=old.now(),status='FROZEN_PRE_FRESH_SOURCE_RESOURCE_EXECUTION',shapes=['all_action_hands_menus'],changed_entries=['down_action'],source_manifest_sha256=old.sha(S/'manifest.json'),original_source_form='D049/E043',eligibility_audit_sha256=old.sha(A/'report.json'),eligibility_supplement_sha256=old.sha(policy),policy_commit=pc,fixed_gates='D108feasibility helper at actual128andfixed64/128/256, zero dynamic shared independent of hands/menu. Unchanged18parameterABI and8other entries actual/sm75. Separate frozen static CFG/source gate must show actor branch removal in NA2/3/4, original source floating expressions/guards/order unchanged. Resource pass alone cannot admit numerical controls.',additional_required_gate='Frozen E067-ptx-mechanism.py on fresh actual/sm75 PTX: every NA2/3/4 baseline has actor-predicated branches in loops; candidate none; one selected map pointer per specialized path; equal floating opcode histogram. Root source review exact original integer-only delta. Full raw numerical proof still required.')
P.pop('up_show_parameter_count');P['down_action_parameter_count']=18
P['rustc_command']=[x.replace(str(prior),str(H)) for x in P['rustc_command']]
paths=[*S.iterdir(),*H.iterdir(),Path(__file__),ROOT/'runs/E067-ptx-mechanism.py',A/'report.json',A/'docket.json',A/'inputs.json',A/'helper-checks.json',A/'commit.json',policy,old.REPO/'tools/postflop_resource_feasibility.py',old.REPO/'tools/postflop_resource_admission.py',ROOT/'runs/D094-resource-materiality/report.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/E066-closure/decision.json']
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in old.read(prior/'protocol.json')['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']};old.save(H/'protocol.json',P)
published={}
for folder in [S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key='evidence/'+folder.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
for p in [Path(__file__),ROOT/'runs/E067-ptx-mechanism.py']:
 key='evidence/E067-preparation-sources/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'new_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id']=='E067' for e in st['experiments'])
 st['experiments'].append({'id':'E067','at':old.now(),'kind':'candidate','original_form':'D049/E043','title':'Fresh qualification of original actor-map pointer selection','status':'running','correctness':'pending','stage':'Fresh compiler resources and per-arity mechanism review','reason':'Exact original inlined down_action helper transferred; original/current baseline helper and exported wrapper exact. Original form never application-kernel/numerical/timed; D049/E043duplicate counted once. No pointer/hoist/table/guard variant or composition. Fresh feasibility and NA2/3/4mechanism review before full raw controls.','evidence':[{'label':'Exact original helper ancestry and source contract','url':'evidence/E067-source/source-review.json'},{'label':'Fresh feasibility and mechanism protocol','url':'evidence/E067-resource/protocol.json'},{'label':'Frozen per-arity CFG inspector','url':'evidence/E067-preparation-sources/E067-ptx-mechanism.py'}]})
 st.update(updated_at=old.now(),state='running',active_experiment='E067',stage='E067 fresh resource and mechanism inspection',activity='Next fixed D108source form: one selected actor map pointer, original helper unchanged except exact3integer statements. No speed/accuracy/material conclusion yet.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'candidate_sha256':old.sha(S/'candidate.cu'),'original_form':'D049/E043','source_activated':False}),flush=True)
