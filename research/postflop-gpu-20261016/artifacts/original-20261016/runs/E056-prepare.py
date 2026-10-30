"""Admit one ordering-only production candidate after CPU exactness controls."""
import json, shutil, sys, urllib.request
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
D=ROOT/'runs/D092-action-arity-order';dr=old.read(D/'report.json')
assert dr['status']=='pass_cpu_metadata_and_concrete_ownership' and len(dr['cases'])==12 and dr['nonorder_fields_exact'] and dr['all_vec_capacities_struct_sizes_equal'] and dr['concrete_same_level_ownership_pass']
for c in dr['cases']:old.pin(c['raw_file'],c['raw_sha256'])
S=ROOT/'runs/E056-source';H=ROOT/'runs/E056-build-plan'
assert not S.exists() and not H.exists();S.mkdir();H.mkdir()
for source,dest in [('accepted-plan.rs','baseline.rs'),('candidate-plan.rs','candidate.rs'),('candidate.patch','candidate.patch')]:shutil.copyfile(D/source,S/dest)
owned={'crates/solver/src/gpu/plan.rs':{'base':str(S/'baseline.rs'),'base_sha256':old.sha(S/'baseline.rs'),'candidate':str(S/'candidate.rs'),'candidate_sha256':old.sha(S/'candidate.rs')}}
old.save(S/'manifest.json',{'at':old.now(),'id':'E056','accepted_source':'E051','candidate_owned_sha256':{n:v['candidate_sha256'] for n,v in owned.items()},'cpu_control_report':{'path':str(D/'report.json'),'sha256':old.sha(D/'report.json')},'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir() if p.is_file()},'source_activated':False,'native_solver_executions':0})
old.save(S/'source-review.json',{'at':old.now(),'id':'E056','status':'pass_root_scoped_plan_permutation','owned_source':'crates/solver/src/gpu/plan.rs','transform':'Ascending actual arity within existing action_by_level lists, in-place unstable sort before flattening; exactly the CPU-control candidate bytes. No threshold or dispatch/key variants.','history_review':old.read(D/'proposal.json')['history_review'],'cpu_controls':{'cases':12,'plan_fields_per_case':53,'root_checks':dr['root_checks'],'all52nonorder_fields_exact':True,'all_vec_capacities_struct_sizes_equal':True,'all_level_multisets_and_concrete_ownership_pass':True,'report_sha256':old.sha(D/'report.json')},'resource_scope':'Unchanged CUDA source, entrypoints, ABI, host launch/graph code, buffer lengths, offsets and span counts. Existing device resources are not a new optimization mechanism. Sorting cost remains in the full clock. Actual captured-graph, peak memory, lifecycle/F32/menu/save/resume/continuation checks still required before adoption if timing qualifies.','cuda_source_sha256':old.sha(old.REPO/'crates/solver/src/gpu/kernels.cu'),'kernel_raw_test_scope':'No CUDA kernel change; rerunning single-node kernel controls would not validate multi-node order. CPU ownership controls plus full exact states and subsequent actual graph/lifecycle controls validate the changed mechanism.','reviewer':'Root review and raw replay; not an external independent audit','performance_measured':False,'optimization_accepted':False})
text=(ROOT/'runs/E055-build-plan/build-r2.py').read_text(encoding='utf-8').replace('E055','E056').replace('build-protocol-r2.json','build-protocol.json').replace('build-r2.py','build.py').replace('E056-final-build-r2','E056-final-build')
assert all(x not in text for x in ['E055','e055','r2'])
(H/'build.py').write_text(text,encoding='utf-8',newline='\n')
p=json.loads(json.dumps(old.read(ROOT/'runs/E055-build-plan/build-protocol-r2.json')).replace('E055','E056').replace('e055','e056'))
for k in ['original_protocol_sha256','repair']:p.pop(k,None)
p.update(id='E056-final-build',at=old.now(),owned=owned,accepted_source_sha256=old.BASE,native_before_builds_terminal=False,not_a_performance_protocol=True)
paths=[*S.iterdir(),H/'build.py',Path(__file__),D/'protocol.json',D/'report.json',D/'field-schema.json',D/'proposal.json',ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/accepted-E051/protected-main.json',ROOT/'runs/accepted-E051/preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
p['input_sha256']={str(x):old.sha(x) for x in paths if x.is_file()}
for phase in p['phases']:
    assert 'e056' in phase['target'] and not Path(phase['target']).exists()
    for name in phase['outputs'].values():assert not (ROOT/'binaries'/(name+'.exe')).exists()
assert not (ROOT/'runs/E056-final-build').exists()
old.save(H/'build-protocol.json',p)
published=[]
def put(path,prefix):
    rel='evidence/'+prefix+'/'+path.name;dest=old.ar.DASHBOARD/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==path.read_bytes()
    else:shutil.copyfile(path,dest)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+rel,timeout=10) as response:assert response.read()==path.read_bytes()
    published.append({'path':str(path),'url':rel,'sha256':old.sha(path)})
for folder in [D,S,H]:
    for path in folder.iterdir():
        if path.is_file():put(path,folder.name)
for path in (D/'execution').glob('*.json'):put(path,'D092-action-arity-order-native')
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);d=next(x for x in st['experiments'] if x['id']=='D092');d.update(status='measured',correctness='pass',stage='CPU metadata and concrete ownership controls passed',reason=f"All12 CPU cases preserve52 nonordering fields bitwise, actual capacities/struct sizes and per-level node multisets. {dr['root_checks']:,} raw metadata/ownership checks passed. Diagnostic setup timings only; no complete-cycle speed claim.")
    d['evidence'].append({'label':'Complete 12-case CPU report and raw artifact identities','url':'evidence/D092-action-arity-order/report.json'})
    assert not any(e['id']=='E056' for e in st['experiments'])
    st['experiments'].append({'id':'E056','at':old.now(),'title':'Order existing action blocks by arity','kind':'candidate','status':'running','correctness':'pending','fixture':'All three registered compressed fixtures','stage':'Frozen one-file build after CPU controls','reason':'Existing CUDA kernels/dispatch/launch spans and memory maps unchanged. CPU permutation controls passed; complete-cycle speed, exact GPU results and material-cost qualification pending.','evidence':[{'label':'Root source/history/resource-scope review','url':'evidence/E056-source/source-review.json'},{'label':'Exact source patch','url':'evidence/E056-source/candidate.patch'},{'label':'Frozen final build protocol','url':'evidence/E056-build-plan/build-protocol.json'}]})
    st.update(updated_at=old.now(),stage='E056 candidate builds',activity='D092 CPU metadata/ownership checks passed. Preparing one ordering-only candidate under the 1% no-tradeoffs policy; no new gain or adoption.',active_experiment='E056');old.ar.atomic_json(old.ar.STATUS,st)
old.save(H/'pre-build-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'build_protocol_sha256':old.sha(H/'build-protocol.json'),'native_solver_executions':0})
old.custody();print(json.dumps({'build_protocol_sha256':old.sha(H/'build-protocol.json'),'published':len(published),'cpu_cases':12,'owned_sources':list(owned)}),flush=True)
