import difflib, json, shutil, subprocess, sys, tarfile, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'epoch'))
import common as h
OLD = Path(r'S:\GTOpen-research\postflop-gpu-20261016')
h.custody()
assert not any((ROOT/x).exists() for x in ['gpu-run.lock', 'epoch-sequence.lock'])
h.ar.refuse_active(h.ar.live_status())
assert shutil.disk_usage(ROOT).free >= 66*1024**3
H = ROOT/'runs/D190-inline-tree-control'
H.mkdir(exist_ok=False)

# Preserve the exact source/history queries before creating a new matching form.
queries = [
    ['git','log','--all','--format=%h %s','-G','SmallVec|ArrayVec|inline.*Vec','--','crates/solver/src/tree.rs'],
    ['rg','-l','SmallVec|smallvec',str(OLD/'runs'),'--glob','*.rs','--glob','*.py','--glob','*review*.json','--glob','*.md'],
]
history=[]
for i, command in enumerate(queries):
    result=subprocess.run(command,cwd=h.REPO,capture_output=True,text=True,encoding='utf-8')
    assert result.returncode in [0,1]
    history.append({'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    assert not result.stdout.strip(), 'Historical matching form needs review before admission'
h.save(H/'history.json',{'at':h.now(),'bounded_queries':history,'not_exhaustive_remote_semantic_novelty':True})

source=h.REPO/'crates/solver/src/tree.rs'
h.pin(source,'91980344b4926c499b4bcbad6022c423b1ff38a6e1059b5d2fe9f6f0680cf761')
base=source.read_bytes(); candidate=base
replacements=[
    (b'use serde::{Deserialize, Serialize};', b'use serde::{Deserialize, Serialize};\r\nuse smallvec::SmallVec;',1),
    (b'fn legal_actions(&self, st: &BuildState) -> Vec<Action>',b'fn legal_actions(&self, st: &BuildState) -> SmallVec<[Action; 4]>',1),
    (b'let mut actions = Vec::new();',b'let mut actions: SmallVec<[Action; 4]> = SmallVec::new();',1),
    (b'let mut candidates: Vec<f64> = Vec::new();',b'let mut candidates: SmallVec<[f64; 4]> = SmallVec::new();',2),
    (b'let mut tos: Vec<f64> = Vec::new();',b'let mut tos: SmallVec<[f64; 4]> = SmallVec::new();',2),
    (b'fn dedupe_amounts(v: &mut Vec<f64>)',b'fn dedupe_amounts(v: &mut SmallVec<[f64; 4]>)',1),
]
for old,new,count in replacements:
    assert candidate.count(old)==count,(old,candidate.count(old))
    candidate=candidate.replace(old,new)
reverse=candidate
for old,new,count in reversed(replacements):
    assert reverse.count(new)==count
    reverse=reverse.replace(new,old)
assert reverse==base
(H/'baseline-tree.rs').write_bytes(base)
(H/'candidate-tree.rs').write_bytes(candidate)
(H/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='a/crates/solver/src/tree.rs',tofile='b/crates/solver/src/tree.rs')),encoding='utf-8',newline='')

# Existing locked/cached crate, no download, upgrade or global configuration.
crate=Path(r'C:\Users\there\.cargo\registry\cache\index.crates.io-1949cf8c6b5b557f\smallvec-1.15.1.crate')
h.pin(crate,'67b1b7a3b5fe4f1376887184045fcf45c69e92af734b7aaddc05fb777b6fbd03')
dep=H/'smallvec-1.15.1'; dep.mkdir()
with tarfile.open(crate,'r:gz') as archive:
    for member in archive.getmembers():
        assert not member.issym() and not member.islnk()
        if not member.isfile(): continue
        relative=Path(member.name).relative_to('smallvec-1.15.1')
        destination=(dep/relative).resolve()
        assert destination.is_relative_to(dep.resolve())
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(archive.extractfile(member).read())

oldH=OLD/'runs/E065-tree-control'
assert (oldH/'baseline-tree.rs').read_bytes()==base
for name in ['corpus.json','probe.rs']:
    raw=(oldH/name).read_bytes()
    if name=='probe.rs':
        raw=raw.replace(b'E065_TREE ',b'D190_TREE ')
        needle=b'fn main(){let args:Vec<String>=std::env::args().collect();'
        replacement=b'fn main(){emit(json!({"stage":"temporary_container_sizes","baseline_action_vec_bytes":std::mem::size_of::<Vec<baseline::Action>>(),"candidate_action_smallvec_bytes":std::mem::size_of::<smallvec::SmallVec<[candidate::Action;4]>>(),"baseline_amount_vec_bytes":std::mem::size_of::<Vec<f64>>(),"candidate_amount_smallvec_bytes":std::mem::size_of::<smallvec::SmallVec<[f64;4]>>(),"inline_capacity":4}));let args:Vec<String>=std::env::args().collect();'
        assert raw.count(needle)==1
        raw=raw.replace(needle,replacement)
    (H/name).write_bytes(raw)

# Stage prospective integration metadata without activating it.
manifest=h.REPO/'crates/solver/Cargo.toml'
manifest_base=manifest.read_bytes(); needle=b'mimalloc = "0.1"'
assert manifest_base.count(needle)==1
(H/'candidate-Cargo.toml').write_bytes(manifest_base.replace(needle,needle+b'\r\nsmallvec = "=1.15.1"'))
lockbase=(h.REPO/'Cargo.lock').read_bytes()
block=lockbase.split(b'name = "solver"',1)[1].split(b'[[package]]',1)[0]
assert b' "smallvec",' not in block
newblock=block.replace(b' "serde_json",',b' "serde_json",\r\n "smallvec",')
assert newblock!=block
(H/'candidate-Cargo.lock').write_bytes(lockbase.replace(block,newblock,1))

deps=ROOT/'reference/accepted-e080-deps'
smallvec_command=['rustc',str(dep/'src/lib.rs'),'--crate-name','smallvec','--crate-type','rlib','--edition=2018','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-o',str(H/'libsmallvec.rlib')]
probe_command=['rustc','--edition=2021',str(H/'probe.rs'),'--crate-name','d190_tree_probe','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1']
for name,filename in [('solver','libsolver-e2d3113d740308c1.rlib'),('serde','libserde-47b4d5f55b04d3b5.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:
    probe_command+=['--extern',name+'='+str(deps/filename)]
probe_command+=['--extern','smallvec='+str(H/'libsmallvec.rlib'),'-L','dependency='+str(deps),'-L','dependency='+str(H),'-o',str(H/'probe.exe')]

review={
    'id':'D190/E100','at':h.now(),'status':'one_exact_off_tree_CPU_form',
    'mechanism':'Replace only legal_actions and candidate/to temporary vectors with SmallVec inline capacity 4; preserve child_indices Vec and all persistent Vec types, extension operations, capacities, numerical expressions, DFS/action/child order, budgets and error behavior.',
    'mechanical_reverse_byte_exact':True,'new_GPU_code_or_resource':False,
    'capacity_basis':'Common existing NA2/3/4 paths; capacity 4 fixed before native evidence. Menus greater than 4 spill to heap. No inline capacity, container, source scope, threshold, helper, flags or sample rescue after real failure.',
    'risks':'Larger CPU stack frames, branching/moves/spills and wide-menu allocations can cost more. Public APIs and output shapes alone do not establish exactness or material neutrality. CPU-only component screen cannot establish solve speed.',
    'history':'Bounded local-all-ref tree and retained old-epoch source queries found no SmallVec form. Distinct from E065 subtree replication (no subtrees copied), D099 by-card scratch reuse (no planner scratch change), E092 GPU quantization and D160 arena allocation. All remain closed.',
    'prior_counterevidence':'Old E065 full tree wrapper sum was about 101 ms, so a 95.086109 ms admission proxy is demanding. Do not label this a proven bound or predict a gain. D183 phase timings are excluded.',
    'dependency':'Already locked/cached SmallVec 1.15.1, verified crate archive SHA. No package download or upgrade; standalone defaults, no optional features. Future production build would add direct solver dependency and solver lock edge only.',
    'documentation_url':'https://github.com/servo/rust-smallvec/tree/v1.15.1',
    'documentation_paraphrase':'Up to the inline capacity is stored within the container; excess elements spill to heap. Standard slice methods are available. This is an API/storage contract, not measured cost or safety evidence for this integration.',
    'limits':'No production source activation, compiler, native tree, kernel or solve yet. If component fails, no GPU/speed qualification follows. Passing only permits separately frozen whole canonical state and ordinary complete-cycle 1%/strict-fixture/fresh16/broad/material/holdout/cumulative/application checks.'
}
h.save(H/'source-review.json',review)

# Separate declined scouts: no executable or candidate was created for either.
D189=ROOT/'runs/D189-prefix-and-readback-scout';D189.mkdir(exist_ok=False)
h.save(D189/'report.json',{
    'id':'D189','at':h.now(),'status':'declined_before_source_or_execution',
    'independent_prefix_consumer':'Exact closed E082 algorithm found before writing a new source. Retain E082 rejection; no prefix/width/chunk/barrier/placement rescue.',
    'readback_active_inactive_queue_join':'No source written. Existing current-RAM D147 records inactive sums [43.4426,44.1279,41.5886] ms versus current samecohort 1% effort proxy 95.086109 ms. Hiding the whole observed inactive stage is insufficient as an optimistic prioritization heuristic. Not a universal bound, achieved speedup or causal claim.',
    'new_compiler_native_or_GPU_processes':0,'new_gain_accepted':False,
    'inputs':{str(p):h.sha(p) for p in [ROOT/'comparisons/D147-arena-substages/report.json',OLD/'comparisons/E082-three-pair-comparison/report.json']},
})

# Original helper/corpus/typed format retained; pin before either compiler.
original_reader=OLD/'runs/E065-tree-root-check.py'
reader=original_reader.read_text(encoding='utf-8')
reader=reader.replace('ROOT=Path(__file__).resolve().parent.parent','ROOT=Path(__file__).resolve().parents[2]')
reader=reader.replace("sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old","sys.path.insert(0,str(ROOT/'epoch'));import common as old")
reader=reader.replace('E065-tree-control','D190-inline-tree-control').replace('E065_TREE ','D190_TREE ').replace('E065-tree-root-check','D190-inline-tree-root-check')
reader=reader.replace("['rustc','canonical-0','canonical-1','canonical-2','controls']","['smallvec-rustc','rustc','canonical-0','canonical-1','canonical-2','controls']")
reader=reader.replace("markers.extend(ms[:-1])","markers.extend(x for x in ms[:-1] if x['stage']!='temporary_container_sizes')")
needle="check(saving<P['minimum_component_saving_ms'] and guards[-1]['failed'] and q['status']=='rejected_component_admission')"
assert reader.count(needle)==1
reader=reader.replace(needle,"passed=saving>=P['minimum_component_saving_ms'] and not any(g['failed'] for g in guards);check(q['status']==('advance_to_integrated_qualification' if passed else 'rejected_component_admission'))")
reader=reader.replace("'status':'pass_preserved_component_rejection'","'status':'pass_component_admission_replay','component_passed':passed")
reader=reader.replace("Historical complete-cycle reference is admission proxy only","Current-RAM separate matched complete-cycle reference is admission proxy only")
(H/'audit.py').write_text(reader,encoding='utf-8',newline='\n')

runner_source=ROOT/'runs/D190-execute.py'
files=[p for p in H.rglob('*') if p.is_file()]+[source,manifest,h.REPO/'Cargo.lock',crate,oldH/'probe.rs',oldH/'corpus.json',original_reader,runner_source,Path(__file__),ROOT/'comparisons/E099-three-pair-comparison/report.json']
files+=list(deps.glob('*.rlib'))+list(deps.glob('*.lib'))+list(deps.glob('*.dll'))
P={
    'id':'D190-inline-tree-control','candidate':'E100','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_NATIVE',
    'measurement_epoch':'RAM20261028','smallvec_command':smallvec_command,'rustc_command':probe_command,
    'input_sha256':{str(p):h.sha(p) for p in files},
    'sequence':[['canonical-0',['canonical','0']],['canonical-1',['canonical','1']],['canonical-2',['canonical','2']],['controls',['controls','all']]],
    'extra_control_cases':15,'warmup_pairs_per_canonical':2,'measured_pairs_per_canonical':9,
    'fixed_reference_ms':9508.6109,'reference':'E099 samecohort E080 controls B311/B312/B313, separate effort proxy only, never pooled into CPU samples',
    'minimum_component_saving_ms':9508.6109*0.01,
    'component_guard':'Reject positive median slowdown AND at least 5 of 9 slower pairs on any canonical fixture; no minimum magnitude.',
    'time_scope':'Same fixed JSON clone/deserialization plus TreeBuilder wrapper; excludes board/range setup, fingerprints, raw serialization and final Tree drop. Every temporary SmallVec drop during build remains inside the clock. Diagnostic only, not complete solve.',
    'raw':'Original full typed node/action/child/config/root/data size/3 capacities; every successful control retained, native same-error assertions on original corpus and caps 0/1/N-1/N/N+1. No tolerance, field exception or fixture filtering.',
    'storage_admission_GiB':66,'conservative_peak_new_raw_GiB':3,'headroom_GiB':63,
    'output_root':str(H),'source_activation':False,'GPU_executions':0,
    'extensions_or_rescue_allowed':False,'post_failure':'Close exact local-vector form. No inline-width/container/scope/helper/flags/threshold/extra-sample rescue; no GPU timing or adoption after a failed component screen.',
}
h.save(H/'protocol.json',P)

for folder,names in [(H,['source-review.json','history.json','protocol.json','candidate.patch']),(D189,['report.json'])]:
    for name in names:
        p=folder/name;dst=h.ar.DASHBOARD/'evidence'/folder.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);assert not any(x['id']=='E100' for x in s['experiments'])
    s['experiments'].append({'id':'E100','title':'Inline temporary betting menus','status':'running','accepted':False,'stage':'Frozen CPU tree equivalence and setup-cost screen','reason':'Keep the same ordered tree and heap fallback for large menus; first test fixed CPU component and full raw outputs. No GPU or complete-cycle result yet.','correctness':'pending','evidence':[{'label':'Frozen CPU protocol','url':'evidence/'+H.name+'/protocol.json'},{'label':'Source and dependency review','url':'evidence/'+H.name+'/source-review.json'},{'label':'Bounded history review','url':'evidence/'+H.name+'/history.json'}]})
    s.update(updated_at=h.now(),active_experiment='E100',stage='Testing tree setup allocation overhead',activity='E100 tests stack storage for small temporary betting menus. Full output and capacity equivalence plus a fixed setup-cost screen come first. E080 with 16 workers remains live; no new gain adopted.')
    h.ar.atomic_json(h.ar.STATUS,s)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:
    f.write('\n\n### D189 duplicate guard and D190/E100 inline temporary betting menus\n\nPrevious turn made progress by closing E099 with exact raw/canonical/science checks and a measured complete-cycle rejection, retaining D187/D188 history guards and excluding D183 phase timings. Current source/main/live/PTX/idle custody passed. D189 declines exact closed E082 independent prefix consumers before code, and declines CPU active/inactive queue overlap from D147 optimistic 44.1279 ms versus 95.086109 ms current effort proxy; no native or candidate there.\n\nOne distinct off-tree E100 form replaces only private legal_actions/candidate/to temporary vectors by SmallVec inline capacity 4. Existing common arities 2/3/4 motivate that single prospective capacity; arbitrary larger menus retain heap spill. Child-indices Vec, all persistent types/extension statements/capacities, DFS/order/math/errors/budgets and GPU source stay unchanged. Byte reversal exact. Existing locked/cached SmallVec 1.15.1 archive SHA 67b1b7a3b5fe4f1376887184045fcf45c69e92af734b7aaddc05fb777b6fbd03 verified and copied privately on X; no download/upgrade/global config. Local-all-ref tree and retained archive source searches have no matching form. Distinct from E065 subtree copying, D099 planner scratch reuse, D160 arena allocation and closed quantization forms. API storage documentation is not numerical/cost proof; larger stack frames and wide-menu allocation risks remain.\n\nD190 protocol '+h.sha(H/'protocol.json')+' freezes smallvec compiler then probe compiler, original E065 full canonical/budget/diverse strict/lenient/legacy/large-menu corpus, 2 warmup pairs and exactly 9 alternating timed pairs per original canonical fixture, plus entire typed raw fields/config/3 capacities and separate full reader. CPU wrapper clocks include same JSON clone/deserialization and all temporary drops, exclude final Tree drop/fingerprints/raw output; not complete solves. Admission needs 95.086109 ms summed median saving (1% of separate matched B311-313 reference) and no positive median slowdown with 5/9 slower pairs. This effort proxy is not a proven bound or gain. Earlier whole tree wrapper was only about 101 ms, disclosed counterevidence. No source activation or GPU work. Any genuine failure closes exact capacity/container/scope form without flags/helper/threshold/source/sample rescue. Passing only permits separately frozen canonical/ordinary complete1%/strictfixture/fresh16/broad/material/holdout/cumulative/application qualification. All artifacts X, archive read-only, no T; E080/16 unchanged, last primary B313, goal active.\n')
h.custody()
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
subprocess.run(['git','commit','-m','research: freeze inline temporary tree allocation controls'],cwd=h.REPO,check=True)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'candidate_tree_sha256':h.sha(H/'candidate-tree.rs'),'CPU_processes_after_two_compilers':4,'GPU_executions':0}),flush=True)
