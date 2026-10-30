"""Bounded source/history audit for an independent CPU construction opportunity."""
import hashlib,json,re,subprocess,sys,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
H=ROOT/'runs/D273-spot-construction-scout';H.mkdir(exist_ok=False)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';lines=ledger.read_text(encoding='utf-8').splitlines();closed=[]
for i,line in enumerate(lines):
    if re.search(r'plan/context overlap|NVRTC overlap without headroom|No extra samples, threshold/thread/helper/scope/placement/eligibility variants',line,re.I):closed.append({'line':i+1,'text':line})
assert any('E079' in row['text']for row in closed)
paths=['crates/solver/src/game.rs','crates/solver/src/tree.rs'];revisions=subprocess.check_output(['git','rev-list','--all','--']+paths,cwd=h.REPO,text=True).splitlines();history=[];hits=[]
pattern=re.compile(r'rayon::join|std::thread::scope|spawn_scoped|parallel.{0,40}(tree|river)|overlap.{0,40}(tree|river)',re.I)
for revision in revisions:
    for name in paths:
        proc=subprocess.run(['git','show',revision+':'+name],cwd=h.REPO,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if proc.returncode:continue
        text=proc.stdout.decode('utf-8-sig');found=[{'line':i+1,'text':line.strip()}for i,line in enumerate(text.splitlines())if pattern.search(line)]
        row={'identity':'git:'+revision+':'+name,'sha256':hashlib.sha256(proc.stdout).hexdigest(),'hits':found};history.append(row)
        if found:hits.append(row)
retained=[];unique=set()
for directory in[ROOT/'runs',Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs')]:
    for name in subprocess.check_output(['rg','--files',str(directory),'-g','*.rs'],text=True).splitlines():
        p=Path(name)
        if p.stat().st_size>4*1024**2:continue
        data=p.read_bytes();text=data.decode('utf-8-sig',errors='replace')
        if 'pub struct Spot {'not in text or 'build_river_table('not in text:continue
        digest=hashlib.sha256(data).hexdigest();unique.add(digest);found=[{'line':i+1,'text':line.strip()}for i,line in enumerate(text.splitlines())if pattern.search(line)]
        row={'identity':str(p),'sha256':digest,'hits':found};retained.append(row)
        if found:hits.append(row)
game=(h.REPO/'crates/solver/src/game.rs').read_text(encoding='utf-8');a=game.index('        let tree = TreeBuilder::build_with_options(');b=game.index('        // Suit symmetry group:',a);sequence=game[a:b]
assert sequence.count('TreeBuilder::build_with_options(')==sequence.count('build_river_table(')==1
assert sequence.index('        )?;')<sequence.index('        let river = build_river_table(&board, board_mask, &hands);')
tree=(h.REPO/'crates/solver/src/tree.rs').read_text(encoding='utf-8');assert'fn check_budget(&self)'in tree
report={'id':'D273','at':h.now(),'status':'source_history_scout_not_a_candidate','previous_goal_turn_progress':'E115 full original canonical6science46checks/54.6GBpaired state and ordinary86units pass, primary0.192324921678% andriver guard reject it. Exact form closed; E080 remains live.',
 'closed_lead_declined':{'lead':'Overlap CPU GPU-plan build with context/module/NVRTC preparation, including ownership/budget/eligibility variants','decision':'Decline before code/compiler/native: E079 already rejected after2.9718558844% aggregate/34.3185952486%river regression, no thread/helper/placement/eligibility rescue. D109 context/module/NVRTC cache/overlap headroom work also retained; no retry or false universal headroom from old clocks.','ledger_evidence':closed},
 'local_revisions':len(revisions),'tracked_path_history':history,'retained_game_sources':len(retained),'unique_game_source_hashes':len(unique),'retained_sources':retained,'literal_parallel_tree_river_hits_for_review':hits,
 'current_source_sha256':{name:h.sha(h.REPO/name)for name in paths},
 'current_serial_body':sequence,
 'new_dependency_observation':'Spot::new_impl builds TreeBuilder::build_with_options from treeconfig/board/handcounts/max_nodes/strictness, then build_river_table from board/board_mask/immutable hands. River strengths do not read tree; tree builder does not read river strength tables. Suit symmetry setup follows both. These are earlier CPU Spot construction stages, not GpuPlan sub-stages or CUDA context/compiler work. No implementation or performance gain established.',
 'blocked_naive_form':'Naive rayon::join speculates expensive river evaluation when tree validation or node-budget fails; original ? returns before any river work. A benchmark-only max_nodes=None scope would omit the normal limited API path and is not an adequate application optimization. Do not admit either shortcut.',
 'future_design_questions':['Full local/retained literal hits must be classified, bounded absence is not exhaustive semantic/remote novelty proof.','Preserve all invalid-config/node-budget/error priority, joined cleanup/panic/CPU responsiveness, strict/lenient saves and supported limited API paths. Consider cooperative cancellation on failed tree construction only if actual work/latency/memory costs can be prospectively bounded and tested. No claim that cancellation alone proves no tradeoff.','Rayon tree/river concurrency may contend with existing parallel river evaluation, alter peak allocation/worker/FPU behavior or regress small games. Audit original16-worker policy and exact full Spot/tree/actions/children/river/weights/hand/suit tables before a source form. Do not edit evaluator or omit river/turn/limited paths.','Need fresh source-matched observation/effort budget for current tree/river stages before assuming whole-cycle1% opportunity. Historical D044/D110/D183 timing stays excluded; no old sample pooling, free-time bound or narrow component gain called full-solve gain.','Any eventual fixed form must pass full original numerical/ordinary/fullcycle>=1%/strictfixture/fresh16/broad/material/holdout/fresh-original/cumulative/temporary-app gates, with no helper/field/source/predicate/scope/quality/sample rescue after genuine failure.'],
 'new_source_compiler_CUDA_context_kernel_solver_or_timing_samples':0,'source_candidate_created':False,'next':'Classify bounded source/history evidence; if distinctness holds, audit limited-path cancellation/ownership/FPU/Rayon semantics and fresh Spot-stage evidence before admitting one fixed candidate.','accepted_main_live_protected_PTX_unchanged':True,'all_owned_helpers_terminal':True,'all_new_bulk_X_S_read_only_no_T_access':True,'best_live':'E080/GPU/compressed/16/defaultaffinity','last_primary_baseline':'B362','next_unused_baseline':'B363','goal_active':True}
h.save(H/'report.json',report);h.custody()
dest=h.ar.DASHBOARD/'evidence'/H.name/'report.json';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(H/'report.json',dest)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/report.json',timeout=20)as z:assert z.read()==(H/'report.json').read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D273','title':'Distinct Spot construction source/history scout','kind':'diagnostic','status':'measured','accepted':False,'stage':'Source audit only; no prototype or speed samples','reason':'Declines closed E079 plan/context overlap including variants. Current Spot tree build and river-table build are serial independent CPU stages, but invalid-config/budget failure behavior, existing Rayon competition and material costs block a naive join. Fresh evidence/design required; no gain or candidate admitted.','evidence':[{'label':'Bounded source/history audit and constraints','url':'evidence/'+H.name+'/report.json'}]});s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='D273',stage='Distinct source lead: Spot construction feasibility',activity='E115 rejected/closed at0.1923% andriver guard. D273 declines old context/planner overlap and audits a different earlier CPU tree/river construction opportunity; no source or speed trial admitted. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'local_revisions':len(revisions),'retained_Spot_sources':len(retained),'unique_hashes':len(unique),'literal_hits':len(hits),'new_compilers_GPU_or_speed_samples':0,'closed_E079_not_retried':True}),flush=True)
