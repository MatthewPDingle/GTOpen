import ast, difflib, json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not any((ROOT/x).exists() for x in ['gpu-run.lock','epoch-sequence.lock'])
D=ROOT/'comparisons/D194-parent-chance-census/report.json';assert h.read(D)['status']=='pass_scoped_source_and_integer_mapping_admit_one_resource_prototype'
S=ROOT/'runs/E102-source';H=ROOT/'runs/E102-resource';S.mkdir(exist_ok=False);H.mkdir(exist_ok=False)
cuda='crates/solver/src/gpu/kernels.cu';mod='crates/solver/src/gpu/mod.rs'
basecu=(h.REPO/cuda).read_bytes();fragment=(ROOT/'runs/E102-parent-chance.cu').read_bytes();newcu=basecu+fragment
basemod=(h.REPO/mod).read_bytes();text=basemod.decode();nl='\r\n' if b'\r\n' in basemod else '\n'
changes=[]
def replace_once(old,new):
    global text
    assert text.count(old)==1,(old,text.count(old));text=text.replace(old,new,1);changes.append((old,new))
replace_once('    f_down_chance: CudaFunction,'+nl,'    f_down_chance: CudaFunction,'+nl+'    f_down_chance_parent: CudaFunction,'+nl)
replace_once('            f_down_chance: func("down_chance")?,'+nl,'            f_down_chance: func("down_chance")?,'+nl+'            f_down_chance_parent: func("down_chance_parent")?,'+nl)
for begin_name,end_name in [('    fn eval_down(', '    fn eval_up('),('    fn paired_sweep(', '    /// Copy GPU arenas back')]:
    begin=text.index(begin_name);end=text.index(end_name,begin);part=text[begin:end]
    oldspan='let sp = self.chance_spans[l];';newspan='let sp = self.chance_node_spans[l];'
    assert part.count(oldspan)==1;part2=part.replace(oldspan,newspan,1)
    assert part2.count('.launch_builder(&self.f_down_chance)')==1;part2=part2.replace('.launch_builder(&self.f_down_chance)','.launch_builder(&self.f_down_chance_parent)',1)
    oldargs=nl.join(['                        .arg(&self.d_chance_parents)','                        .arg(&self.d_chance_children)','                        .arg(&self.d_chance_cards)','                        .arg(&start)','                        .arg(&count)'])
    newargs=nl.join(['                        .arg(&self.d_chance_nodes)','                        .arg(&start)','                        .arg(&count)','                        .arg(&self.d_cc_start)','                        .arg(&self.d_cc_count)','                        .arg(&self.d_cc_card)','                        .arg(&self.d_cc_child)','                        .arg(&self.d_cc_perm)'])
    assert part2.count(oldargs)==1;part2=part2.replace(oldargs,newargs,1)
    changes.append((part,part2));text=text[:begin]+part2+text[end:]
reverse=text
for old,new in reversed(changes):assert reverse.count(new)==1;reverse=reverse.replace(new,old,1)
assert reverse.encode()==basemod and newcu[:-len(fragment)]==basecu
assert text.count('.launch_builder(&self.f_down_chance_parent)')==2
assert text.count('.launch_builder(&gpu.f_down_chance)')==1 # Original legacy full sweep oracle unchanged.
assert '.arg(&down_nh1)' in text[text.index('    fn paired_sweep('):]
owned={}
for name,base,candidate,stem in [(cuda,basecu,newcu,'kernels'),(mod,basemod,text.encode(),'mod')]:
    a=S/('baseline-'+stem+Path(name).suffix);b=S/('candidate-'+stem+Path(name).suffix);a.write_bytes(base);b.write_bytes(candidate)
    patch=S/(stem+'.patch');patch.write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)),encoding='utf-8',newline='')
    owned[name]={'base':str(a),'candidate':str(b),'base_sha256':h.sha(a),'candidate_sha256':h.sha(b),'patch':str(patch)}
h.save(S/'manifest.json',{'id':'E102','at':h.now(),'status':'STAGED_OFF_TREE_NOT_ACTIVATED','owned':owned,'candidate_owned_sha256':{n:v['candidate_sha256'] for n,v in owned.items()},'tracked_owned_paths':list(owned),'new_owned_paths':[],'byte_exact_reverse':True,'original9_CUDA_source_prefix_exact':True,'legacy_down_reference_exact':True,'accepted_source_sha256':h.custody()})
h.save(S/'source-review.json',{
    'id':'E102','at':h.now(),'status':'one_parent_fanout_form_staged_for_compiler_gate',
    'mechanism':'One existing128-thread block per existing chance parent instead of one per representative edge. Each hand loads parent reach and mask before traversing that parents original cc span, copying only cc_perm==0 edges. Original 9 CUDA entries remain byte-identical source prefix; new16-parameter pure-copy entry appended.',
    'host':'Add one CudaFunction field/lookup. Change exactly two production sites (training paired_sweep and eval_down) to existing chance_node_spans/chance_nodes/cc arrays and new entry. All original device allocations and metadata payloads retained. Original f_down_chance/legacy_down test oracle remains unchanged. p1 reuse still transmits nh1=0; no own-player reconstruction or normalization change.',
    'integer_proof':'D194 complete selected arrays in all6canonical iso on/off baseline metadata files: 2,839,622 checks. Per-level Counter of parent/child/card triples exact; output reach slots unique/in bounds/disjoint from all same-level parent source slots for both players. Phase timings from D183 explicitly excluded.',
    'representative_selection':'Plan starts rep=c,k_rep=0 and updates k only when permuted card is lower. Permutation0 is identity. Thus cc_perm==0 iff c remains its own representative; these are exactly the original rep_edges. No new plan/list/encoding/sort/threshold/padding.',
    'preserved':'No floating arithmetic added or removed: each old reachable output still copies the original parent f32 bits or stores positivezero on the same dealt-card/mask test. Lock/evaluation/traverser/CFR update/upward arithmetic, actor+chancelevel sequence, quality/cadence/stops, save format and GPU payload remain. Actual raw exceptional/nonfinite/multi-parent/tail/zero/reuse controls still mandatory.',
    'risks':'Fewer blocks can reduce parallelism and serialized card loops can lose. CC identity checks add metadata work; added export/function lookup may cost compile/JIT/setup even on river. Module/graph/CPU/RAM/compiled resources and capacity need actual measurement. No speed forecast from CTA counts or old activity traces.',
    'novelty':'Bounded D194 local all-ref and636retainedCUDA source-body search found no parent-grouped down_chance. Distinct from E078 upward parent-block fold producer/fusion, E081 action warp packing, E046 interleaved record encoding, E048/E086 membership predicates. None composed/reopened.',
    'compile_gate':'Original9 alpha-normalized entry bodies/ABIs on120/75 exact. New16argument ABI/no barriers/no float arithmetic. Default-resource feasibility and parent reach32-bit input loads outside representative-card loops mandatory before application kernels. Same payload, no local/dynamic/stack growth or maxthread loss; positive64/128/256occupancy, disclose reg/occupancy warnings under D108.',
    'closure':'Any genuine gate failure closes this exact parent-fanout form. No edge tile/blockwidth/parent grouping/guard/threshold/field/loop/helper/caller/source/flags/sample rescue. All full raw/state/ordinary/complete1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application gates remain.',
    'source_activated':False,'candidate_accepted':False,
})
parent=ROOT/'runs/E096-resource/probe.rs';code=parent.read_text(encoding='utf-8').replace('E096_RESOURCE','E102_RESOURCE')
needle='for kernel in ["up_chance","up_action","up_action_eval"]'
assert code.count(needle)==1
code=code.replace(needle,'for kernel in if variant=="baseline" { &['+'"down_chance"'+'][..] } else { &['+'"down_chance","down_chance_parent"'+'][..] }')
assert code.count('"resource_rows":6')==1;code=code.replace('"resource_rows":6','"resource_rows":3')
(H/'probe.rs').write_text(code,encoding='utf-8',newline='\n')
(H/'baseline.cu').write_bytes(basecu);(H/'candidate.cu').write_bytes(newcu)
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for n,f in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',n+'='+str(deps/f)]
cmd+=['-o',str(H/'probe.exe')]
runner=ROOT/'runs/E102-resource-execute.py';ast.parse(runner.read_text(encoding='utf-8'))
files=[Path(__file__),runner,ROOT/'runs/E102-parent-chance.cu',ROOT/'epoch/common.py',parent,D,ROOT/'runs/D194-parent-chance-census/protocol.json',ROOT/'runs/D194-parent-chance-census/history.json']+[p for p in S.iterdir() if p.is_file()]+[p for p in H.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]+list(Path(h.ar.NVRTC).glob('*.dll'))
h.save(H/'protocol.json',{'id':'E102-resource','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_MODULE_ONLY_QUERY','GPU_uuid':'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee','rustc_command':cmd,'expected_original_entries':h.read(ROOT/'runs/E101-resource/protocol.json')['expected_entries'],'new_entry':'down_chance_parent','new_entry_parameters':16,'required_free_bytes':16*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'sequence':'OneRustcompiler, one module-only process, four NVRTC12.9 actual120/compat75 builds, no application kernels. Full original9 body/ABI equivalence, newABI/copy-only/barrier/resources, then separately verify reach-load hoisting/loop relation before raw numerical tests. Original PTX artifacts never overwritten.','candidate_accepted':False,'extensions_or_source_rescue_allowed':False})
for folder,names in [(S,['manifest.json','source-review.json','kernels.patch','mod.patch']),(H,['protocol.json'])]:
    for name in names:
        p=folder/name;dst=h.ar.DASHBOARD/'evidence'/folder.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='E102' for x in status['experiments'])
    status['experiments'].append({'id':'E102','at':h.now(),'title':'Shared-parent chance reach fanout','status':'running','accepted':False,'correctness':'pending','stage':'Frozen compiler/resource prerequisite','reason':'Reuse each parent reach across its existing representative dealt-card edges in one GPU block. Original allocations, data and upward arithmetic remain. Integer mapping passed; GPU raw controls and speed are unmeasured.','evidence':[{'label':'Frozen metadata census and ownership proof','url':'evidence/D194-parent-chance-census/protocol.json'},{'label':'Complete selected-field integer census','url':'evidence/D194-parent-chance-census/report.json'},{'label':'Source and caller review','url':'evidence/'+S.name+'/source-review.json'},{'label':'Frozen compiler prerequisite','url':'evidence/'+H.name+'/protocol.json'}]})
    # Comparison folders share the same public basename; the census result is present there.
    status.update(updated_at=h.now(),active_experiment='E102',stage='Parent chance fanout compiler prerequisite',activity='E102 groups chance edges by their existing parent and reuses input reach values. Six original plan cases preserve every edge and disjoint output. No GPU correctness or speed claim; E080 with 16 workers remains live.')
    h.ar.atomic_json(h.ar.STATUS,status)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:
    f.write('\n\n### D194/E102 shared-parent downward chance fanout\n\nPrevious goal turn progressed by compiling E101 and rejecting its required quotient bypass before numerical/timing trials. Current source/main/live/PTX/idle custody and absent locks passed. Read-only source review finds standard async device allocation already selected by cudarc on supported devices; no allocator/pool/pinned-cache candidate is admitted. Persistent unrounded GPU state across compressed resumes would change state and idle retention would cost memory; no runtime/cache scope change.\n\nD194 freezes c059b18b012989c81422fdc35321f4b18685618a2428c7195c6005fa26a10f65 before reading six full-hash-verified original D183 baseline plan arrays, phase timings excluded. 2,839,622 integer checks pass: every per-level parent/child/card Counter from cc_perm==0 equals original edge lists, both-player output slots unique/in bounds/disjoint from every current-level parent input. Full down-sweep CTA counts old/new: rainbow156016/3250, two-tone iso94890/2392, no-iso156016/3250, river0/0. Counts are geometry, not speed/headroom. Bounded local-all-ref and636retainedCUDA down_chance body search finds no parent-fanout match; not exhaustive semantic/remote novelty. Distinct from E078 upward fold producer/fusion, E081 action warp mapping, E046 record layout and E048/E086 predicate forms, none composed.\n\nOne exact off-tree two-file E102 appends down_chance_parent (16params) after byte-identical original9CUDA source. Each unchanged128-thread CTA processes one existing chance parent, holds each hand parent reach/mask before original cc span and copies cc_perm==0 representative edges with original mask/positivezero choice. Same bit copies, no FP arithmetic or shared scratch/newglobalpayload. Host adds one function field/lookup and changes exactly training/evaluation production callers to existing parent spans/nodes/cc fields; old down_chance and legacy_down oracle preserved. p1reuse nh1=0 remains. All original arrays/allocations/plan/upward math/quality/cadence/save bytes retained; byte reversal exact. FewerCTAs, serial loops and extra module lookup can hurt; no speed prediction or resource-neutrality claim.\n\nResource protocol '+h.sha(H/'protocol.json')+' fixes oneRustcompiler/module-only process, fourNVRTC12.9 actual120/compat75 builds, original9alphaexactABIs/bodies, new16ABI/no barriers/no FP arithmetic and D108samepayload/defaultlimits/local/stack/maxthreads/positive64/128/256occupancy feasibility. Separate parent-load outside card-loop mechanism proof required before appkernels. Any genuine gate failure closes exact grouping/width/tile/guard/threshold/field/loop/helper/caller/source/flags/sample form without rescue. All direct raw/multiparent/zero/reuse/nonfinite/physicalcanonical/ordinary/complete1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application gates remain. AllnewoutputX, archive readonly, noT; E080/16live unchanged, lastprimaryB313, goalactive.\n')
h.custody();subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: freeze shared parent chance fanout compiler gate'],cwd=h.REPO,check=True)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'candidate_CUDA_sha256':h.sha(S/'candidate-kernels.cu'),'candidate_host_sha256':h.sha(S/'candidate-mod.rs'),'application_kernels':0}),flush=True)
