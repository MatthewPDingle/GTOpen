"""Fresh qualification of exact E057prefix mapping, second fixed D101docket form."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
A=ROOT/'runs/D101-resource-eligibility-audit';d=old.read(A/'docket.json');assert d['order']==['E050','E057'] and d['new_qualification_ids']==['E061','E062']
assert old.read(ROOT/'runs/E061-closure/decision.json')['alias_now_has_known_speed_outcome'] and old.read(ROOT/'runs/E061-primary-manager/complete.json')['all_owned_children_terminal']
policy=old.REPO/'research/postflop-gpu-20261016/unmeasured-resource-eligibility-20261017.md';old.pin(policy,d['policy_sha256'])
for p,h in old.read(A/'inputs.json')['sha256'].items():old.pin(p,h)
original=ROOT/'runs/E057-source';parent=ROOT/'runs/E057-resource';S=ROOT/'runs/E062-source';H=ROOT/'runs/E062-resource';assert not S.exists() and not H.exists();S.mkdir();H.mkdir()
base=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();assert base==(original/'baseline.cu').read_bytes()
assert old.sha(original/'candidate.cu')=='b9c1b260895debf954def29b28804d3cd1cc0b431a668c698d72dda55693cec3'
for n in ['baseline.cu','candidate.cu','candidate.patch']:(S/n).write_bytes((original/n).read_bytes())
oldp=old.read(parent/'protocol.json')
for k in ['cpu_model_report','cpu_model_correction']:old.pin(oldp[k]['path'],oldp[k]['sha256'])
model=old.read(oldp['cpu_model_report']['path']);assert model['status']=='admit_no_launch_resource_probe' and all(model['gates'].values())
old.save(S/'source-review.json',{'id':'E062','at':old.now(),'kind':'attributed_source_form_requalification','original_source_form':'E057','baseline_full_sha256':old.sha(S/'baseline.cu'),'candidate_full_sha256':old.sha(S/'candidate.cu'),'both_complete_CUDA_files_byte_identical_to_original':True,'original_source_review_sha256':old.sha(original/'source-review.json'),'cpu_model_report':oldp['cpu_model_report'],'preserved_model_correction':oldp['cpu_model_correction'],'eligibility_audit_sha256':old.sha(A/'report.json'),'policy_sha256':old.sha(policy),'mechanism':'Only physical prefix indices change in complete32word tiles: k XOR((k>>5)&31), final partial tile identity. Enable only for power-of-two per-thread chunk lengths>1. Exact original helper, guard, all5source accesses and all other source bytes retained. No storage/barrier/metadata/ABI/launch/FPoperation-order/precision/quality changes.','safety':'Each complete tile keeps its ID and XORs a tile-constant into low5bits, hence bijection/involution; partial tail disjoint. Same logical producer/consumer dependency and order. Existing D093CPUcontrols cover all0..1326lengths,both flags,all1..256block widths. Actual GPU numerical controls still required.','limits':'CPU bank model is not a hardware conflict counter or speed result. Root source review, not external independent review. First source-form numerical and timing outcomes remain unmeasured at this preparation.'})
owned={'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu')};old.save(S/'manifest.json',{'id':'E062','at':old.now(),'original_form':'E057','candidate_owned_sha256':owned,'source_sha256':old.BASE|owned,'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir() if p.is_file()},'source_activated':False,'no_variant':True})
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
(H/'probe.rs').write_text((parent/'probe.rs').read_text(encoding='utf-8').replace('E057','E062'),encoding='utf-8',newline='\n')
runner=(parent/'execute.py').read_text(encoding='utf-8').replace('E057','E062')
a=runner.index("  kg={'registers_not_increased'");b=runner.index('\n  details[shape]',a)
runner=runner[:a]+"  sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_admission import evaluate_pair\n  admission=evaluate_pair(b,c,old.read(P['allocation_proof']['path']))\n  kg=admission['gates']"+runner[b:]
needle="details[shape]={'baseline':b,'candidate':c,'gates':kg}";assert runner.count(needle)==1;runner=runner.replace(needle,"details[shape]={'baseline':b,'candidate':c,'gates':kg,'allocation_admission':admission}")
needle=" details={};abi={}"
assert runner.count(needle)==1;runner=runner.replace(needle," for variant in ['baseline','candidate']:\n  for arch in ['compute_120','compute_75']:\n   gates[variant+'_'+arch+'_legacy_ptx_exact']=old.sha(OUT/(variant+'-'+arch+'.ptx'))==P['legacy_ptx_sha256'][variant+'-'+arch]\n"+needle)
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=oldp.copy();P.update(id='E062-resource',at=old.now(),status='FROZEN_PRE_FRESH_RESOURCE',source_manifest_sha256=old.sha(S/'manifest.json'),original_source_form='E057',allocation_proof={'path':str(ROOT/'runs/D094-resource-materiality/report.json'),'sha256':old.sha(ROOT/'runs/D094-resource-materiality/report.json')},eligibility_supplement_sha256=old.sha(policy),fixed_gates='Unchanged current D094allocated-resource gates all10shapes, exact27parameter ABI, other8entries exact120/75, changed showbody and all4full PTX files exact original unmeasured source artifact. Exact source form only; no index/flag/guard/width/block/scheduling variant. Numerical/timing still unproven.')
P['rustc_command']=[x.replace(str(parent),str(H)) for x in P['rustc_command']]
P['legacy_ptx_sha256']={v+'-'+arch:old.sha(parent/'execution'/(v+'-'+arch+'.ptx')) for v in ['baseline','candidate'] for arch in ['compute_120','compute_75']}
paths=[*S.iterdir(),*H.iterdir(),Path(__file__),A/'report.json',A/'docket.json',A/'inputs.json',ROOT/'runs/E061-closure/decision.json',policy,original/'source-review.json',Path(oldp['cpu_model_report']['path']),Path(oldp['cpu_model_correction']['path']),ROOT/'runs/D094-resource-materiality/report.json',ROOT/'runs/D094-resource-materiality/test-report.json',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
paths.extend(parent/'execution'/(v+'-'+a+'.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75'])
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in oldp['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']};assert P['up_show_parameter_count']==27;old.save(H/'protocol.json',P)
published={}
for folder in [S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key='evidence/'+folder.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id']=='E062' for e in st['experiments'])
 st['experiments'].append({'id':'E062','at':old.now(),'kind':'candidate','title':'Fresh qualification of original E057prefix mapping','original_form':'E057','status':'running','correctness':'pending','stage':'Fresh current-source resource revalidation','reason':'Fixed second D101docket form after E050/E061closed. Entire source byte-identical to original E057; no retuning. Preserve current allocated resources, exact ABI/other entries, then first complete raw numerical and fresh speed tests.','evidence':[{'label':'Exact source ancestry','url':'evidence/E062-source/source-review.json'},{'label':'Fresh compiler/resource protocol','url':'evidence/E062-resource/protocol.json'}]})
 st.update(updated_at=old.now(),state='running',active_experiment='E062',stage='E062 fresh resource revalidation',activity='Second fixed source-form qualification: exact original prefix address map. No FPorder/precision change and no previous speed observations.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'candidate_sha256':old.sha(S/'candidate.cu'),'exact_original_source':True,'native_executions':0}),flush=True)
