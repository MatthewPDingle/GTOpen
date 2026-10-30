"""Freeze one bit-selection chance candidate after all-address source controls."""
import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
D=ROOT/'runs/D097-chance-selection';S=ROOT/'runs/E059-source';H=ROOT/'runs/E059-resource';assert not H.exists();H.mkdir()
address=old.read(D/'report.json');assert address['status']=='pass_source_contract_and_concrete_address_ownership' and len(address['cases'])==12
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
shutil.copyfile(D/'branch_proof.py',H/'branch_proof.py')
parent=ROOT/'runs/E058-resource'
probe=(parent/'probe.rs').read_text().replace('E058','E059').replace('down_action','up_chance');(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(parent/'execute.py').read_text().replace('E058','E059').replace('down_action','up_chance')
needle='\n report='
assert runner.count(needle)==1
runner=runner.replace(needle,"\n from branch_proof import compare as branch_compare\n branch=branch_compare(OUT/'baseline.ptx',OUT/'candidate.ptx');old.save(HERE/'blocker-branch-proof.json',branch);gates.update({'branch:'+k:v for k,v in branch['gates'].items()})\n report=")
runner=runner.replace("'pass_resource_feasibility_only' if all(gates.values()) else 'rejected_resource_gate'","'pass_resource_and_mechanism_prerequisites' if all(gates.values()) else 'rejected_compiled_prerequisite'")
needle=" old.save(HERE/'report.json',report);";assert runner.count(needle)==1
runner=runner.replace(needle," report['blocker_branch_proof_sha256']=old.sha(HERE/'blocker-branch-proof.json');old.save(HERE/'report.json',report);")
assert 'E058' not in runner
(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
anchor=parent/'execution/baseline.ptx';text=anchor.read_text();a=text.index('.entry up_chance(');b=text.index('.visible .entry ',a+10);header=text[a:b].split('{',1)[0]
abi=[m[0] for m in re.findall(r'\.param\s+\.(u\d+)((?:\s+\.ptr\s+\.align\s+\d+)?)\s+up_chance_param_\d+',header)];assert len(abi)==15
sys.path.insert(0,str(H));from branch_proof import analyze
baseline=analyze(anchor);assert len(baseline['mask_dependent_branches'])==7 and baseline['mask_load_instructions'] and not baseline['unknown_calls']
old.save(H/'pre-compile-baseline-control.json',{'at':old.now(),'accepted_ptx_sha256':old.sha(anchor),'analysis':baseline,'candidate_compiles':0,'kernel_launches':0})
P=old.read(parent/'protocol.json');P.update(id='E059-resource',at=old.now(),source_manifest_sha256=old.sha(S/'manifest.json'),changed_entries=['up_chance'],expected_abi={'up_chance':{'baseline':abi,'candidate':abi}},address_proof={'path':str(D/'report.json'),'sha256':old.sha(D/'report.json')},fixed_gates='Only up_chancebody changes, unchanged15parameter ABI and other8entries. D094verified allocation rule/no spill/shared or maxthread/occupancy regression. Find baseline blocker branches and require none in candidate explicit mask-data taint; no unknown call-outs. No semantic, speed or SASS claim from PTX. No mask/control/placement/factor variant rescue.')
P['rustc_command']=[x.replace(str(parent),str(H)) for x in P['rustc_command']]
inputs=[*D.iterdir(),*S.iterdir(),*H.iterdir(),Path(__file__),ROOT/'runs/D097-address-proof.py',anchor,ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/D094-resource-materiality/report.json',ROOT/'runs/D094-resource-materiality/test-report.json',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md']
P['input_sha256']={str(p):old.sha(p) for p in inputs if p.is_file()};P['input_sha256'].update({p:h for p,h in old.read(parent/'protocol.json')['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']})
old.save(H/'protocol.json',P)
published={}
for folder in [D,S,H]:
    for p in folder.iterdir():
        if not p.is_file():continue
        key='evidence/'+folder.name+'/'+p.name;dest=old.ar.DASHBOARD/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
        published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'kernel_launches':0,'source_activated':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);assert not any(e['id'] in ['D097','E059'] for e in s['experiments'])
    s['experiments'].append({'id':'D097','at':old.now(),'title':'Prove unconditional chance-load ownership','kind':'diagnostic','status':'measured','correctness':'pass','stage':'All12layout address/permutation controls passed','reason':'Producer source invariants and16,823,188 concrete ownership/bounds checks pass. Every hand permutation is total; extra child reads are in initialized rows and disjoint from current-level writes. No CUDA numerical or speed claim.','evidence':[{'label':'Source contract and fixed address replay','url':'evidence/D097-chance-selection/protocol.json'},{'label':'Complete12case ownership/bounds report','url':'evidence/D097-chance-selection/report.json'}]})
    s['experiments'].append({'id':'E059','at':old.now(),'title':'Preserve blocked accumulator bits without skip branch','kind':'candidate','status':'running','correctness':'pending','stage':'Frozen no-launch resource and blocker-branch gate','reason':'Original64bit blocker predicate and ordered used sums retained. Select exact prior accumulator bits for blocked cards; new read addresses proven. Require real PTX blocker-branch removal and nonincreasing allocation/resources before raw numerical controls or timing.','evidence':[{'label':'Exact CUDA-only patch','url':'evidence/E059-source/candidate.patch'},{'label':'Frozen resource/mechanism protocol','url':'evidence/E059-resource/protocol.json'},{'label':'Accepted PTX has seven blocker branches','url':'evidence/E059-resource/pre-compile-baseline-control.json'}]})
    s.update(updated_at=old.now(),state='running',active_experiment='E059',stage='E059 compiled chance-control prerequisite',activity='Test one exact accumulator bit-selection form after all-address proofs. No source activation, kernel or solver run, or new gain.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'published':len(published),'baseline_blocker_branches':7,'candidate_sha256':old.sha(S/'candidate.cu')}),flush=True)
