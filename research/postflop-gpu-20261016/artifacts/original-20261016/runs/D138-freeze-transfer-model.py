"""Freeze a CPU-only prerequisite; no bounded GPU solver is implemented yet."""
import ast
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=74*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D138-transfer-model';H.mkdir(exist_ok=False)
shutil.copyfile(R/'runs/D138-transfer-model.rs',H/'probe.rs')
shutil.copyfile(R/'runs/D138-transfer-model-audit.py',H/'audit.py')
shutil.copyfile(R/'runs/D134-zero-init-fences-r2/bench_spot.json',H/'bench_spot.json')
history=[]
for cmd in [
    ['git','log','--all','--oneline','-G','bounded.*staging|staging.*limit|pinned.*cap|next_group','--','crates/solver/src/gpu'],
    ['rg','-n','-i','bounded.*staging|staging.*bounded|pinned.*(limit|cap|smaller)|smaller.*pinned|serial.*chunk','research/postflop-gpu-20261016/experiments.md'],
]:
    p=subprocess.run(cmd,cwd=old.REPO,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode in [0,1]
    history.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
old.save(H/'history.json',{'at':old.now(),'bounded_local_search':history,
    'closed_E040':'E040 used two nonoverlapping windows within the original full pinned allocation to overlap DMA and encoding. It failed complete-solve timing. No such pipelining or allocation-retaining source is composed or retested.',
    'distinct_proposal':'Physically bound the pinned allocation and use one serial complete-node window for both warm upload and readback. New complete-node descriptors for full layouts are a prospective cost; paging must discard them when it discards pinned staging. No GPU prototype or source candidate yet.',
    'limits':'Bounded local history only; no remote/exhaustive novelty or speed evidence.'})
design='''A proposed fixed 64 MiB pinned window replaces the full-arena allocation request, enlarged only when needed to hold an entire node. Small arenas retain their full-sized buffer. This is a hypothesis, not an implemented or measured GPU optimization.

This prerequisite uses accepted E080 public Spot/GpuPlan/Store code. It constructs all three original benchmark games with isomorphism off/on and packed/full mapping (12 cases). Full mapping reproduces the accepted private helper statements through public fields. Every original tree node field needed for ownership, both complete active block lists and complete group descriptors are retained. Root decoding reconstructs groups from those original fields. It does not create a Solver, CUDA context, pinned allocation or GPU transfer.

The pure next_group function retains whole node spans in source order, covers every selected device word once, and accounts for larger-than-limit rows. The diagnostic collects group outputs for inspection; a future production iterator need not retain that diagnostic vector. Existing compact active metadata can be reused. Full layouts would require new active metadata, whose Vec capacity is recorded as a prospective cost, not actual process memory. Continuation paging currently shrinks staging to one word; future integration must discard any new full-layout metadata there too.

216 fixed CPU codec cases cover four row shapes (including all-zero lengths and the legal 250-action x1326-hand maximum), contiguous/gapped host storage, three test window limits (257/4097/production16,777,216 words), three Store variants and three float profiles. Each node uses the original complete Store read/write call. Original versus grouped full upload images, source-store immutability, full output q/scale/float images, and all unowned guards are retained. Small limits exercise seams; they are verification inputs, not candidate performance variants or a tuning sweep.

Native observations are correctness-only. No component or complete-cycle gain is inferred from allocation requests or interval counts. Required later work includes actual source/iterator equivalence, all zero/warm/F32/compact/full uploads and downloads, inactive/symmetry restoration, normal/error drain and continuation behavior, material resource costs, and the unchanged complete-solve 1%/fixture/fresh16/broad/holdout/cumulative gates.
'''
(H/'design.txt').write_text(design,encoding='utf-8',newline='\n')
code='''from pathlib import Path
import json,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 old.custody();old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
verify();O=H/'execution';assert not O.exists()and not(H/'probe.exe').exists()and not(H/'output').exists();O.mkdir()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=74*1024**3
 old.child(P['rustc_command'],O,'rustc',old.env(),600);verify()
 old.save(O/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'compiler_terminal':True,'native_executions':0})
 old.child([str(H/'probe.exe'),str(H/'output')],O,'model',old.env(),1000);verify()
 markers=[json.loads(l.split('D138_MODEL ',1)[1])for l in(O/'model.stdout.log').read_text().splitlines()if'D138_MODEL 'in l]
 assert len(markers)==14and all(m['stage']=='layout_complete'for m in markers[:12])and markers[-2]['stage']=='codecs_complete'and markers[-1]['stage']=='complete'
 assert markers[-1]['layouts']==12and markers[-1]['codec_cases']==216and markers[-1]['invalid_controls_rejected']==6
 assert markers[-1]['CUDA_contexts']==markers[-1]['GPU_kernels']==markers[-1]['solver_iterations']==0and markers[-1]['performance_measurement']is False
 paths=list((H/'output').iterdir());assert {p.name for p in paths}=={'nodes.bin','groups.bin','codecs.bin','metadata.json'}
 size=sum(p.stat().st_size for p in paths);assert size<=P['maximum_output_bytes']
 old.save(O/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'all_owned_children_terminal':True,'raw_file_sha256':{str(p):old.sha(p)for p in paths},'raw_bytes':size,'summary':markers[-1],'source_main_live_PTX_custody_pass':True,'production_source_activated':False,'performance_measurement':False})
 verify();print(json.dumps({'raw_bytes':size,'summary':markers[-1]}),flush=True)
'''
code=code.replace('14and','14 and').replace('12and','12 and').replace('216and','216 and').replace('0and','0 and')
ast.parse(code);(H/'execute.py').write_text(code,encoding='utf-8',newline='\n')
manifest=old.read(R/'binaries/E080-postflop_autoresearch.manifest.json')
deps=manifest['dependency_artifact_sha256']
solver_lib=next(p for p in deps if Path(p).name.startswith('libsolver-')and Path(p).suffix=='.rlib')
json_lib=next(p for p in deps if Path(p).name.startswith('libserde_json-')and Path(p).suffix=='.rlib')
cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(Path(solver_lib).parent),'--extern','solver='+solver_lib,'--extern','serde_json='+json_lib,'-o',str(H/'probe.exe')]
paths=[Path(__file__),R/'runs/E086-turn-checkpoint/next-source-lead.json',
    R/'binaries/E080-postflop_autoresearch.manifest.json',C/'common_e080_live.py',C/'protected-main.json',
    old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',
    *[p for p in H.iterdir()if p.is_file()]]
P={'id':'D138-transfer-model','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_CPU_NATIVE',
    'rustc_command':cmd,'input_sha256':deps|{str(p):old.sha(p)for p in paths},
    'canonical_layouts':12,'fixed_codec_cases':216,'invalid_controls':6,
    'fixed_prospective_production_window_bytes':64*1024*1024,'maximum_output_bytes':8*1024**3,
    'scope':'OneRustcompiler/oneCPU-only model process/separate raw reader. Accepted source/library,public plan/helper mapping and Store codecs; no CUDA context, GPU allocation/kernel, Solver or solve/timing score. Preserve all complete raw fields/images on S.',
    'failure_policy':'An actual coverage/codec failure closes this exact grouping design; no row slicing/window/source-scope/precision/threshold/ownership or extra-case rescue. Pre-native build-only adapter corrections may preserve the same source algorithm/cases/gates; reader-only bookkeeping may replay retained data.',
    'candidate_accepted':False,'production_source_activated':False}
old.save(H/'protocol.json',P)
pub=[]
for p in H.iterdir():
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
    assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
    pub.append(key)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'protocol_sha256':old.sha(H/'protocol.json'),'compiler_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);assert not any(x['id']=='D138'for x in s['experiments'])
    s['experiments'].append({'id':'D138','at':old.now(),'title':'Bound pinned staging with complete-node transfers','status':'running','correctness':'pending','accepted':False,'stage':'CPU layout and codec prerequisite','reason':'Test exact grouping against12real plans and216codec cases before any GPU prototype. Proposed smaller allocation may save setup work but introduces transfer/metadata costs. No speed result.','evidence':[{'label':'Distinct staging design and required checks','url':'evidence/D138-transfer-model/design.txt'},{'label':'Frozen CPU model protocol','url':'evidence/D138-transfer-model/protocol.json'},{'label':'Bounded history audit','url':'evidence/D138-transfer-model/history.json'}]})
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D138',stage='D138 CPU transfer-layout and codec control',activity='Validate complete-node grouping and unchanged per-node encoding before implementing bounded GPU staging. No source adoption or solve-speed result. Accepted/live E080 remains14.74% faster on registered benchmarks.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'protocol.json'),flush=True)
