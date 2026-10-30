import ast, difflib, json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
OLD=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
h.custody();h.ar.refuse_active(h.ar.live_status());assert not any((ROOT/x).exists() for x in ['gpu-run.lock','epoch-sequence.lock'])
S=ROOT/'runs/E101-source';H=ROOT/'runs/E101-resource'
assert not S.exists() and not H.exists()
name='crates/solver/src/gpu/kernels.cu';base=(h.REPO/name).read_bytes()
replacements=[
    (b'pr * ((r > 0.f ? r : 0.f) / sum)',b'pr * (r > 0.f ? r / sum : 0.f)',1),
    (b'sum > 1e-12f ? (r > 0.f ? r : 0.f) / sum : uni',b'sum > 1e-12f ? (r > 0.f ? r / sum : 0.f) : uni',1),
    (b'sum > 1e-12f ? (s > 0.f ? s : 0.f) / sum : uni',b'sum > 1e-12f ? (s > 0.f ? s / sum : 0.f) : uni',1),
]
candidate=base
for before,after,count in replacements:
    assert candidate.count(before)==count
    candidate=candidate.replace(before,after)
reverse=candidate
for before,after,count in reversed(replacements):
    assert reverse.count(after)==count
    reverse=reverse.replace(after,before)
assert reverse==base

# Search retained source before adding a new source with the same form.
command=['git','log','--all','--format=%h %s','-G',r'[rs] > 0.*\? [rs] / sum','--',name]
p=subprocess.run(command,cwd=h.REPO,capture_output=True,text=True);assert p.returncode==0 and not p.stderr and not p.stdout.strip()
listing=subprocess.run(['rg','--files',str(OLD/'runs'),str(ROOT/'runs'),'-g','*.cu'],capture_output=True,text=True,check=True)
scanned=[];matches=[]
for filename in listing.stdout.splitlines():
    path=Path(filename);raw=path.read_text(encoding='utf-8',errors='replace')
    stripped=re.sub(r'/\*.*?\*/|//[^\r\n]*','',raw,flags=re.S);compact=re.sub(r'\s+','',stripped)
    found=[v for v in ['r>0.f?r/sum:0.f','s>0.f?s/sum:0.f'] if v in compact]
    scanned.append({'path':str(path),'sha256':h.sha(path)})
    if found:matches.append({'path':str(path),'forms':found})
assert not matches,'Review old candidate before compiler admission'
S.mkdir();H.mkdir()
(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(candidate)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)),encoding='utf-8',newline='')
h.save(S/'history-review.json',{'at':h.now(),'git_query':{'command':command,'stdout':p.stdout},'retained_CUDA_source_count':len(scanned),'scanned_sources':scanned,'literal_forms_found':matches,'limits':'Bounded local-all-ref and whitespace/comment-normalized literal retained-source search, not exhaustive semantic or remote uniqueness. Semantic distinctions from E058/E060/E091 separately recorded.'})
h.save(S/'manifest.json',{'id':'E101','at':h.now(),'status':'STAGED_OFF_TREE_NOT_ACTIVATED','owned':{name:{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu'),'base_sha256':h.sha(S/'baseline.cu'),'candidate_sha256':h.sha(S/'candidate.cu')}},'accepted_source_sha256':h.custody(),'candidate_owned_sha256':{name:h.sha(S/'candidate.cu')},'tracked_owned_paths':[name],'new_owned_paths':[],'byte_exact_reverse':True})
h.save(S/'source-review.json',{
    'id':'E101','at':h.now(),'status':'one_exact_zero_numerator_strength_reduction',
    'source_changes':[{'baseline':a.decode(),'candidate':b.decode(),'count':n} for a,b,n in replacements],
    'scope':'Only three normalization expressions in down_action_impl, up_action_impl and up_action_eval. All existing positive-sum tests, ordered sums, positive-numerator native divisions, uniform fallbacks, multiplication by parent reach (including zero/nonfinite), child sums, updates, addresses, locks, dispatch, other kernels, host/allocation/ABI/launch/graph/quality/precision/save format remain.',
    'algebraic_contract':'Replacement occurs only when existing sum>1e-12f. This ordered predicate rejects NaN and nonpositive/zero/subnormal denominators; positive infinity remains possible. When r>0 or s>0 is false, the old selected numerator is exactly +0. For a positive nonzero finite denominator or +infinity, its quotient is +0. Keep original native division when numerator is positive, including +infinity/+infinity. NaN/nonpositive/signedzero source values still select +0. Keep the outer parent-reach multiplication so signedzero/NaN/Inf behavior is not bypassed. Native raw checks remain mandatory; documentation/algebra alone is not a local-GPU full-output proof.',
    'not_closed_rescues':'E091 bypassed an entire down-action hand based on parent reach zero plus finite sum. This has no parent-reach predicate and retains its multiplication. E060 shared an approximate reciprocal/refinement across positive and zero numerators under new numeric guard windows; this adds no approximation/window and leaves every nonzero division native. E058 tried to suppress uniform pr/na fallback work; that expression is unchanged here. No old hunk composed, denominator threshold/entry subset/arity/flags changed.',
    'compiler_hypothesis':'The original compiler may already suppress zero-numerator quotient work, or the extra branch may hurt divergence/resources. Require all three actual full entries to change AND a separate full-entry control-flow proof that the zero-numerator arm bypasses quotient work before application kernels. Changed PTX or instruction counts alone do not pass mechanism qualification.',
    'official_reference':'https://docs.nvidia.com/cuda/archive/12.9.1/floating-point/index.html',
    'official_reference_scope':'NVIDIA describes IEEE operations, rounding and the importance of operation order/compiler settings. No speed or whole-integration equivalence is inferred. Existing compiler default math flags remain untouched.',
    'resource_gates':'D108 feasibility: same payload and shapes; no local/spill or dynamic shared growth, no lowered maxthread/default stack, positive64/128/256 occupancy and default feasibility. Disclose registers/shared/occupancy changes. Same ABI/barriers/other6entries on120/75. Compatibility75 mechanism differences retained, actual120 bypass is mandatory.',
    'failure':'Any genuine compiler/mechanism/resource/raw/numerical/material/speed failure closes this exact form. No conditional syntax, predicate, denominator, placement, helper, arity, entry subset, flags, source or sample rescue. All complete1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application gates remain before adoption.',
    'source_activated':False,'application_kernels':0,'candidate_accepted':False,
})
parent=ROOT/'runs/E096-resource/probe.rs'
code=parent.read_text(encoding='utf-8').replace('E096_RESOURCE','E101_RESOURCE').replace('["up_chance","up_action","up_action_eval"]','["down_action","up_action","up_action_eval"]')
assert code!=parent.read_text(encoding='utf-8')
(H/'probe.rs').write_text(code,encoding='utf-8',newline='\n')
for variant in ['baseline','candidate']:shutil.copyfile(S/(variant+'.cu'),H/(variant+'.cu'))
deps=ROOT/'reference/accepted-e080-deps'
cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for n,f in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',n+'='+str(deps/f)]
cmd+=['-o',str(H/'probe.exe')]
runner=ROOT/'runs/E101-resource-execute.py';ast.parse(runner.read_text(encoding='utf-8'))
files=[Path(__file__),runner,ROOT/'epoch/common.py',parent]+[p for p in S.iterdir() if p.is_file()]+[p for p in H.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]+list(Path(h.ar.NVRTC).glob('*.dll'))
assert len(list(Path(h.ar.NVRTC).glob('*.dll')))>=2
P={'id':'E101-resource','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_MODULE_QUERY','measurement_epoch':'RAM20261028','GPU_uuid':'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee','rustc_command':cmd,'required_free_bytes':16*1024**3,'expected_entries':h.read(ROOT/'runs/E091-resource/protocol.json')['expected_entries'],'targets':{'down_action':{'parameters':18},'up_action':{'parameters':20},'up_action_eval':{'parameters':17}},'input_sha256':{str(p):h.sha(p) for p in files},'scope':'One Rustcompiler/module query process, four NVRTC12.9 actual120/compat75 builds, zero application kernels. Stage1 checks ABI/barriers/unaffected6entries/bodychanges/device feasibility and retains every quotient site/full-entry body for mandatory separate static control-flow bypass review. No numeric/solve/speed claim. Failures close exact source without rescue.'}
h.save(H/'protocol.json',P)
for folder,names in [(S,['manifest.json','source-review.json','history-review.json','candidate.patch']),(H,['protocol.json'])]:
    for filename in names:
        q=folder/filename;dst=h.ar.DASHBOARD/'evidence'/folder.name/filename;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(q,dst)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+filename,timeout=20) as response:assert response.read()==q.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='E101' for x in status['experiments'])
    status['experiments'].append({'id':'E101','at':h.now(),'title':'Zero-numerator division bypass','status':'running','accepted':False,'correctness':'pending','stage':'Frozen compiler and resource prerequisite','reason':'Three normalization expressions bypass a quotient only when the old selected numerator is positive zero. Keep all positive divisions and original reach multiplication. Compiler may already do it; no raw or speed result yet.','evidence':[{'label':'Source and exactness obligations','url':'evidence/'+S.name+'/source-review.json'},{'label':'Frozen no-launch compiler prerequisite','url':'evidence/'+H.name+'/protocol.json'},{'label':'Bounded history and normalized source census','url':'evidence/'+S.name+'/history-review.json'}]})
    status.update(updated_at=h.now(),active_experiment='E101',stage='Zero-numerator compiler prerequisite',activity='E101 first checks that the compiler actually bypasses zero-numerator quotient work, with unchanged resources and arithmetic elsewhere. No application kernel or speed claim. E080 with 16 workers remains live.')
    h.ar.atomic_json(h.ar.STATUS,status)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:
    f.write('\n\n### D192/E101 zero-numerator quotient strength reduction\n\nPrevious goal turn was progress: D190/E100 completed 27 CPU pairs, all full raw tree/capacity controls and a failed fixed component admission; D191 declined a closed record-layout scope variant. Current accepted source/main/live/PTX/idle and absent locks revalidated. Current server source rebuilds GPU per solve, but retaining raw f32 between compressed resumes would alter state and retention would cost VRAM; no persistence prototype or benchmark rewrite follows. Pair normalization already uses O(nh) blocker sums, and symmetry materialization is outside frozen benchmark clocks; neither is treated as free removable work.\n\nOne exact E101 CUDA-only form changes three normalization ternaries: select native r/sum (or s/sum) only for a positive numerator, otherwise +0. Existing sum>1e-12 excludes zero/negative/NaN denominator; positive infinity remains. Positive numerator divisions (including Inf/Inf), uniform fallback, ordered sums/updates and outer parent reach multiplication remain native/original, preserving exceptional and signedzero obligations. Byte reversal exact. This differs from E091 whole zero-reach hand skipping, E060 shared reciprocal refinement and E058 uniform fallback division; none is composed/reopened. Bounded local-all-ref and '+str(len(scanned))+' retained CUDA sources have no matching normalized literal, not an exhaustive semantic/remote novelty proof. NVIDIA12.9 floating-point reference reviewed; no doc/algebra-only numerical or speed claim.\n\nResource protocol '+h.sha(H/'protocol.json')+' freezes one Rustcompiler/module-only process, four exact12.9 NVRTC120/75 builds, original18/20/17 ABIs/barriers and six other entry bodies, all three actual body changes, D108 payload/default-limit/local/maxthread/stack/positive occupancy feasibility. All quotient sites and full entries retained for a mandatory separate static bypass control-flow review before any application kernel. Changed code/counts alone do not prove the mechanism. No production activation, GPU application kernel, solve or speed measurement yet. Genuine failure closes exact syntax/predicate/denominator/placement/helper/arity/entrysubset/flags/source/sample form without rescue. All full raw/physicalstate/ordinary/complete1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application gates remain. Main/live E080/16 unchanged, last primary B313, all new output X/archive read-only/no T, goal active.\n')
h.custody()
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
subprocess.run(['git','commit','-m','research: freeze zero numerator compiler prerequisite'],cwd=h.REPO,check=True)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'candidate_source_sha256':h.sha(S/'candidate.cu'),'retained_CUDA_sources_searched':len(scanned),'application_kernels':0}),flush=True)
