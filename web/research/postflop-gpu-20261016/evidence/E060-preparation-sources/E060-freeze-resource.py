"""Complete pre-native metadata admission without regenerating the fixed candidate."""
import ast,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
S=ROOT/'runs/E060-source';H=ROOT/'runs/E060-resource';parent=ROOT/'runs/E059-resource'
assert not (H/'protocol.json').exists() and not (H/'execution').exists() and not (H/'probe.exe').exists()
for n,h in old.read(S/'manifest.json')['artifact_sha256'].items():old.pin(S/n,h)
for n in ['baseline.cu','candidate.cu']:assert (S/n).read_bytes()==(H/n).read_bytes()
original=(H/'execute.py').read_text();assert original.count("\nold.save(HERE/'report.json',report)")==1
runner=original.replace("\nold.save(HERE/'report.json',report)","\n old.save(HERE/'report.json',report)")
ast.parse(runner);ast.parse((H/'probe.rs').read_text()) if False else None
(H/'execute-r2.py').write_text(runner,encoding='utf-8',newline='\n')
anchor=parent/'execution/baseline.ptx';t=anchor.read_text();a=t.index('.entry up_action(');b=t.index('.visible .entry ',a+10);header=t[a:b].split('{',1)[0]
abi=[m[0] for m in re.findall(r'\.param\s+\.(u\d+)((?:\s+\.ptr\s+\.align\s+\d+)?)\s+up_action_param_\d+',header)]
assert len(abi)==20 and abi==['u64','u32','u32','u32']+['u64']*14+['u32','u32']
old.save(H/'preparation-repair.json',{'at':old.now(),'native_runs':0,'solver_builds':0,'candidate_regenerated_or_changed':False,'candidate_sha256':old.sha(S/'candidate.cu'),'original_prepare_script_sha256':old.sha(ROOT/'runs/E060-prepare.py'),'preserved_original_runner_sha256':old.sha(H/'execute.py'),'fixed_runner_sha256':old.sha(H/'execute-r2.py'),'repairs':['Preparation stopped at mistaken expected21ABI count; accepted PTX actually20, matching source signature. No compiler or native run had started.','AST preflight found copied reporter indentation after removing previous candidate branch-analysis hook; preserve original and indent report save inside lock in execute-r2.py. Fixed runner AST parses.'],'observed_abi':abi,'outcome_selection_or_variant':False})
P=old.read(parent/'protocol.json');P.update(id='E060-resource',at=old.now(),source_manifest_sha256=old.sha(S/'manifest.json'),changed_entries=['up_action'],expected_abi={'up_action':{'baseline':abi,'candidate':abi}},fixed_gates='Only up_actionbody changes, unchanged20parameter ABI and other8entries exact. D094 allocation/resource gates frozen. Sharing mechanism and GPU scalar/kernel precision unproven. No guard/window/arity/math/factor rescue variants.')
P.pop('address_proof',None);P['rustc_command']=[x.replace(str(parent),str(H)) for x in P['rustc_command']]
inputs=[*S.iterdir(),*H.iterdir(),Path(__file__),ROOT/'runs/E060-prepare.py',ROOT/'comparisons/D098-static-root-check/report.json',ROOT/'runs/D098-driver-machine-code-r2/capture-report.json',ROOT/'runs/D094-resource-materiality/report.json',ROOT/'runs/D094-resource-materiality/test-report.json',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in inputs if p.is_file()};P['input_sha256'].update({p:h for p,h in old.read(parent/'protocol.json')['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']})
old.save(H/'protocol.json',P)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(e['id']=='E060' for e in s['experiments'])
 s['experiments'].append({'id':'E060','at':old.now(),'title':'Share guarded action denominator refinement','kind':'candidate','status':'running','correctness':'pending','stage':'Frozen allocated-resource gate before precision/timing','reason':'One compute120 common-arity guarded reciprocal-refinement form from D098 actual SASS. Native division fallback retained; numerical equivalence unproven. Extra control/register costs gated before kernel execution. Preparation-only ABI/reader errors preserved.','evidence':[]})
 s.update(updated_at=old.now(),state='running',active_experiment='E060',stage='E060 compiler/resource prerequisite',activity='Testing one shared denominator-refinement form. Exactness and speed remain unproven; accepted E051 unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'candidate_sha256':old.sha(S/'candidate.cu'),'abi_parameters':len(abi),'source_activated':False}),flush=True)
