import ast, json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
OLD=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
h.custody();h.ar.refuse_active(h.ar.live_status());assert not any((ROOT/x).exists() for x in ['gpu-run.lock','epoch-sequence.lock'])
H=ROOT/'runs/D194-parent-chance-census';H.mkdir(exist_ok=False)
queries=[['git','log','--all','--format=%h %s','-G','down_chance_parent|down_chance.*cc_|parent.*reach.*cc_start','--','crates/solver/src/gpu/kernels.cu']]
history=[]
for cmd in queries:
    q=subprocess.run(cmd,cwd=h.REPO,capture_output=True,text=True);assert q.returncode==0 and not q.stderr and not q.stdout.strip();history.append({'command':cmd,'stdout':q.stdout,'stderr':q.stderr,'returncode':q.returncode})
listing=subprocess.run(['rg','--files',str(OLD/'runs'),str(ROOT/'runs'),'-g','*.cu'],capture_output=True,text=True,check=True)
scanned=[];matches=[]
for filename in listing.stdout.splitlines():
    p=Path(filename);text=p.read_text(encoding='utf-8',errors='replace')
    scoped=[]
    for match in re.finditer(r'void\s+(down_chance\w*)\s*\(',text):
        opening=text.index('{',match.end());end=opening+1;depth=1
        while depth:
            if text[end]=='{':depth+=1
            elif text[end]=='}':depth-=1
            end+=1
        body=text[opening:end]
        if 'cc_start' in body or 'cc_count' in body or match[1]!='down_chance':scoped.append(match[1])
    scanned.append({'path':str(p),'sha256':h.sha(p)})
    if scoped:matches.append({'path':str(p),'functions':scoped})
assert not matches,'Review matching down-chance layout before a new candidate'
h.save(H/'history.json',{'at':h.now(),'queries':history,'retained_CUDA_sources':scanned,'matching_parent_down_chance_bodies':matches,'limits':'Bounded local all-ref and retained down_chance-named source-body query, not exhaustive semantic/remote novelty. New work is downward shared-parent reach fanout, not E078 upward fold-parent production/fusion, E081 action warp packing, E046 record layout, E048 card comparison or E086 bit extraction; none is composed.'})
source=ROOT/'runs/D183-plan-phase-diagnostic/visibility-adapter'
oldP=h.read(source/'protocol-r2.json');raw_report=ROOT/'comparisons/D183-plan-phase-diagnostic/report.json';identities=h.read(raw_report)['all36_raw_file_sha256'];fixtures=h.read(source/'fixtures.json')
first=oldP['sequence'][0]['id'];raw_inputs=[]
for fixture in fixtures:
    p=source/first/(fixture['id']+'-baseline.plan.bin');identity=identities[str(p)]
    raw_inputs.append({'path':str(p),'bytes':identity['bytes'],'sha256':identity['sha256'],'fixture':fixture})
runner=ROOT/'runs/D194-census.py';ast.parse(runner.read_text(encoding='utf-8'))
files=[Path(__file__),runner,ROOT/'epoch/common.py',H/'history.json',source/'schema.json',source/'fixtures.json',source/'protocol-r2.json',raw_report,ROOT/'runs/D183-plan-phase-terminal/late-history-addendum.json']+[h.REPO/p for p in ['crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/kernels.cu']]
h.save(H/'protocol.json',{
    'id':'D194','at':h.now(),'status':'FROZEN_PRE_READ_ONLY_CENSUS','input_sha256':{str(p):h.sha(p) for p in files},'raw_inputs':raw_inputs,'schema_path':str(source/'schema.json'),
    'selected_fields':['num_levels','num_nodes','nh','chance_nodes','chance_node_spans','chance_parents','chance_children','chance_cards','chance_spans','cc_start','cc_count','cc_card','cc_child','cc_perm','reach_slot','reach_blocks'],
    'required_cases':6,'fixed_mapping':'One 128-thread CTA per existing chance node, traverse existing cc span, copy only cc_perm==0 edges. Same parent/child/card/physical reach slots. Both player hand loops preserve masks/positivezero stores and p1 reuse passes nh1=0. No new lists, buffers, planner state, FP expression, threshold or quality change.',
    'census_gates':'For all six original canonical iso on/off plans, complete per-level parent/child/card Counter exactly equals existing down-chance edges. Every output slot unique, in bounds and disjoint from all same-level parent source slots for each player. Original ordered spans and all metadata input hashes remain. Counts are not speed/headroom evidence.',
    'D183_timing_exclusion':'Only original whole-byte-validated baseline plan arrays are read. All phase/timing fields are excluded per late history addendum; none used to admit a candidate or speed claim.',
    'new_compilers_CUDA_contexts_kernels_solvers_or_timing_samples':0,
    'future_obligations':'Passing allows only one source/resource prototype. Need actual old/new instructions and ABI, pure-copy/nonfinite/raw edge and multi-parent controls, full canonical physical state, caller/reuse/evaluation/legacy/continuation, ordinary builds/tests and all complete1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application gates. Fewer CTAs can reduce occupancy and hurt; no gain assumed.',
})
for name in ['history.json','protocol.json']:
    p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'cases':len(raw_inputs),'retained_CUDA_sources':len(scanned),'new_native_processes':0}),flush=True)
