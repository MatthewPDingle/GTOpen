"""One conditional fallback-division candidate under prospective allocation rules."""
import difflib,hashlib,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(ROOT).free>=54*1024**3
D=ROOT/'runs/D095-uniform-division';S=ROOT/'runs/E058-source';H=ROOT/'runs/E058-resource'
assert not any(p.exists() for p in [D,S,H]);D.mkdir();S.mkdir();H.mkdir()
cu=old.REPO/'crates/solver/src/gpu/kernels.cu';base=cu.read_bytes();a=base.index(b'__device__ __forceinline__ void down_action_impl(');z=base.index(b'extern "C" __global__ void down_action(',a)
body=base[a:z];before=b'        float uni = pr / (float)na;';after=b'        float uni = sum > 1e-12f ? 0.f : pr / (float)na;';assert body.count(before)==1
candidate=base[:a]+body.replace(before,after)+base[z:];candidate_hash=hashlib.sha256(candidate).hexdigest()
duplicates=[];checked=0
for p in (ROOT/'runs').rglob('*.cu'):
    if any(x in {'vendor','workspaces'} for x in p.parts):continue
    checked+=1
    if old.sha(p)==candidate_hash:duplicates.append(str(p))
assert not duplicates,duplicates
for folder in [S,H]:
    (folder/'baseline.cu').write_bytes(base);(folder/'candidate.cu').write_bytes(candidate)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='a/crates/solver/src/gpu/kernels.cu',tofile='b/crates/solver/src/gpu/kernels.cu')),encoding='utf-8',newline='')
anchor=ROOT/'runs/E051-resource/execution/candidate.ptx';ptx=anchor.read_text();i=ptx.index('.entry down_action(');j=ptx.index('.visible .entry ',i+10);down=ptx[i:j]
(D/'accepted-down-action.ptx.txt').write_text(down,encoding='utf-8',newline='\n')
abi=[m[0] for m in re.findall(r'\.param\s+\.(u\d+)((?:\s+\.ptr\s+\.align\s+\d+)?)\s+down_action_param_\d+',down.split('{')[0])];assert len(abi)==18
review={'id':'D095-uniform-division','at':old.now(),'proposal':'One source expression in down_action_impl: form the fallback pr/na only when sum>1e-12f is false; initialize the otherwise unused uni to0. The original per-action condition, division operands, stores and loop order remain unchanged.','compiled_baseline_observation':'Accepted E051 down_action PTX has pr/3 before the sum-threshold branch and pr/na before the generic action loop. Common2/4 paths use selected constant fractions. Compiler may speculate or transform the candidate back; a real compiled body difference is required, and no division saving or speedup is assumed.','semantic_argument':['If sum>1e-12f, every unlocked action writes pr*((r>0?r:0)/sum) and never consumes uni; changing that unused scalar to0 does not change any stored value.','Otherwise, including unordered sum, source evaluates the identical pr/(float)na expression and writes the original uni for every action. No reciprocal substitution or reassociation is proposed.','Locked path, regret loads, ordered positive-regret sum, threshold, parent reach, child addresses, common2/3/4/generic dispatch and all other entries unchanged. No new storage, host/ABI/layout/graph/launch/precision/quality setting.','GPU floating operations that produce stored results retain original expressions and order; exact direct device controls including signedzero/nonfinite/extremes and full solver state/checkpoint qualification remain required before any adoption.'], 'history_scope':'Distinct from E055 immutable discount loads in up_action, E051 strategy-store scheduling, E047 dispatch, E028 probability cache and closed register/cache/ordering variants. No matching conditional fallback source found by scoped retained source search; exact hash checked across retained CU files.','retained_cuda_files_hash_checked':checked,'exact_hash_duplicates':duplicates,'resource_policy':'Prospective D094 allocation-based prefilter. No increased allocated registers, spill/shared bytes or reduced occupancy/maxthreads; ABI and other8entries exact. Report nominal counts too. No retry/conditional syntax/placement/arity/factor variant to rescue a failed gate.','performance_policy':'Current >=1% complete-cycle/no repeatable fixture slowdown; separate fixed16 confirmation and all broader/F32/state/menu/save/resume/continuation/material/holdout/cumulative gates. No performance observation or historical candidate reopening.','reviewer':'Root source review, not external independent audit','source_activated':False,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False}
old.save(D/'proposal.json',review);old.save(S/'source-review.json',review)
old.save(S/'manifest.json',{'at':old.now(),'baseline':'E051','baseline_source_sha256':old.BASE,'candidate_owned_sha256':{'crates/solver/src/gpu/kernels.cu':candidate_hash},'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir()},'no_production_activation':True})
parent=ROOT/'runs/E055-resource'
probe=(parent/'probe.rs').read_text().replace('E055','E058').replace('up_action','down_action');(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(parent/'execute.py').read_text().replace('E055','E058').replace('up_action','down_action')
start=runner.index(' from conditional_proof import review');end=runner.index('\n report=',start);runner=runner[:start]+runner[end:]
runner=runner.replace(" report['conditional_read_proof_sha256']=old.sha(HERE/'conditional-proof.json');",' ')
start=runner.index("  kg={'changed_body'");end=runner.index('\n  abi[k]={}',start)
runner=runner[:start]+"  sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_admission import evaluate_pair\n  admission=evaluate_pair(b,c,old.read(P['allocation_proof']['path']))\n  kg={'changed_body':be[k]!=ce[k],**admission['gates']}\n"+runner[end:]
runner=runner.replace("details[k]={'baseline':b,'candidate':c,'gates':kg}","details[k]={'baseline':b,'candidate':c,'gates':kg,'allocation_admission':admission}")
assert all(x not in runner for x in ['E055','conditional_proof','conditional_read_proof','registers_not_increased'])
(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=old.read(parent/'protocol.json');P.update(id='E058-resource',at=old.now(),source_manifest_sha256=old.sha(S/'manifest.json'),changed_entries=['down_action'],expected_abi={'down_action':{'baseline':abi,'candidate':abi}},allocation_proof={'path':str(ROOT/'runs/D094-resource-materiality/report.json'),'sha256':old.sha(ROOT/'runs/D094-resource-materiality/report.json')},fixed_gates=review['resource_policy'])
P['rustc_command']=[x.replace(str(parent),str(H)) for x in P['rustc_command']]
inputs=[*D.iterdir(),*S.iterdir(),H/'baseline.cu',H/'candidate.cu',H/'probe.rs',H/'execute.py',Path(__file__),anchor,ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/D094-resource-materiality/report.json',ROOT/'runs/D094-resource-materiality/test-report.json',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md']
P['input_sha256']={str(p):old.sha(p) for p in inputs if p.is_file()};P['input_sha256'].update({p:h for p,h in old.read(parent/'protocol.json')['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']})
old.save(H/'protocol.json',P)
published={}
for folder in [D,S,H]:
    for p in folder.iterdir():
        if not p.is_file():continue
        key='evidence/'+folder.name+'/'+p.name;dest=old.ar.DASHBOARD/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
        published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'kernel_launches':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);assert not any(e['id'] in ['D095','E058'] for e in st['experiments'])
    st['experiments'].append({'id':'D095','at':old.now(),'title':'Inspect unused fallback division in action-down','kind':'diagnostic','status':'measured','correctness':'pending','stage':'Source and accepted PTX review complete','reason':'Accepted PTX forms pr/3 and generic pr/na before their threshold branch. Propose one conditional fallback expression; compiler may undo it. No numerical or speed claim.','evidence':[{'label':'Source/compiled-baseline review','url':'evidence/D095-uniform-division/proposal.json'}]})
    st['experiments'].append({'id':'E058','at':old.now(),'title':'Conditionally form action-down fallback division','kind':'candidate','status':'running','correctness':'pending','stage':'Frozen no-launch compiler/resource gate','reason':'One source expression; same used operands/order, buffers, dispatch and quality. Future allocation-based resource gate applies; no historical reopening. Numerical and timed solves remain pending.','evidence':[{'label':'Exact one-expression CUDA patch','url':'evidence/E058-source/candidate.patch'},{'label':'Frozen resource protocol and D094 proof','url':'evidence/E058-resource/protocol.json'}]})
    st.update(updated_at=old.now(),state='running',active_experiment='E058',stage='E058 compiled-resource prerequisite',activity='Test one conditional fallback-division form under the verified allocation-based resource gate. No source activation, kernel or solver run, or new gain.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'candidate_sha256':candidate_hash,'resource_protocol_sha256':old.sha(H/'protocol.json'),'published':len(published),'hash_checked_cuda_files':checked}),flush=True)
