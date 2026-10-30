"""Publish the CPU prerequisite; GPU implementation and qualification remain."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
old.custody()
assert not(R/'gpu-run.lock').exists()
assert not(R/'runs/E087-source').exists()
H=R/'runs/D138-transfer-model'
root=R/'comparisons/D138-transfer-model'
P=old.read(H/'protocol.json')
q=old.read(root/'report.json')
assert q['status']=='pass_scoped_CPU_layout_and_codec_equivalence'
assert q['layouts']==12 and q['codec_cases']==216 and not q['performance_measurement']
assert q['GPU_contexts']==q['GPU_kernels']==q['solver_iterations']==0
for p,h in P['input_sha256'].items():old.pin(p,h)
receipts={}
for folder in [R/'runs/D138-model-manager',H/'execution']:
    for p in folder.glob('*.exit.json'):
        x=old.read(p)
        assert x['returncode']==0 and x['error'] is x['cleanup'] is None
        receipts[str(p)]={'sha256':old.sha(p),'returncode':0}
assert len(receipts)==4
for p,h in q['raw_file_sha256'].items():old.pin(p,h)
contract={
    'at':old.now(),'status':'next_integration_required_not_implemented',
    'proposed_candidate':'E087','fixed_window_bytes':64*1024*1024,
    'source_files':['crates/solver/src/gpu/arena.rs','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/continuation_paging.rs'],
    'requirements':[
        'Copy validated complete-node greedy grouping into a nonallocating iterator. Do not retain the diagnostic group vector.',
        'Reuse compact active metadata. Prepare full-layout active descriptors only above the fixed window; measure their actual costs.',
        'Build layouts before selecting shared pinned capacity, holding at least one full node. Preserve E080 worker/predicates/tokens and original CUDA caller.',
        'Keep small arenas and full F32 direct uploads on their original paths. Bounded warm compressed/compact F32 uploads cover every device word using original node reads.',
        'Drain each copy before staging reuse/read/free or error return. Validate error/unwind behavior without assuming atomic recovery.',
        'Read back whole nodes with original encoders. Preserve coalesced F32 spans, inactive snapshots, signed-zero/nonfinite values, iteration and symmetry/query/save restoration.',
        'Avoid new Rayon startup for full F32 or empty inactive restoration.',
        'Discard full-layout transfer metadata when paging discards full staging. Qualify wrapper/memory/capacity/paging/stored behavior.',
        'Leave CUDA bytes, flags, GPU buffers/layouts, graph schedule, math/precision, quality/stopping/check cadence and frozen evaluator unchanged.',
        'GPU/raw controls precede original complete-solve1%/fixture screen. Fresh16,broad/material/capacity/holdout/cumulative gates still control adoption.'
    ],
    'closed_history':'E040 allocation-retaining two-window overlap stays closed. No overlap or threshold/chunk/source-scope rescue. E087 source/build/native execution does not exist yet.',
    'CPU_report_sha256':old.sha(root/'report.json'),
    'CPU_protocol_sha256':old.sha(H/'protocol.json'),
    'limits':'Integration contract only; no actual GPU transfer, pinned/process footprint, speed gain or adoption.'
}
old.save(H/'next-integration-contract.json',contract)
pub=[]
for folder in [H,R/'runs/D138-model-manager',root]:
    prefix=folder.name+'-comparison' if folder==root else folder.name
    for p in sorted(folder.rglob('*')):
        if not p.is_file()or p.suffix not in ['.json','.py','.rs','.txt','.patch','.log']:continue
        key=prefix+'/'+p.relative_to(folder).as_posix()
        dst=old.ar.DASHBOARD/'evidence'/key
        dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:
            assert response.read()==p.read_bytes(),key
        pub.append(key)
reason=(
    'CPU prerequisite passed:12real layouts,216codec cases and6invalid controls. '
    'Reader checked42,291,249conditions,10,774,636original nodes and4,059,144active blocks. '
    'Complete source/upload/output images match. Large-fixture proposed pinned request64MiB; '
    'actual allocation, GPU transfers, memory/CPU costs and complete-solve speed remain unproven. No adoption.'
)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS)
    e=next(x for x in s['experiments']if x['id']=='D138')
    e.update(status='measured',correctness='host_controls_pass',accepted=False,kind='diagnostic',
        scope='CPU_model',stage='Host proof passed; GPU implementation pending',reason=reason,updated_at=old.now())
    e['evidence'].extend([
        {'label':'Complete CPU model raw replay','url':'evidence/D138-transfer-model-comparison/report.json'},
        {'label':'Required GPU integration and qualification','url':'evidence/D138-transfer-model/next-integration-contract.json'}
    ])
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D138',
        stage='Preparing bounded staging GPU prototype',
        activity=reason+' Accepted/live E080 remains14.74% faster on registered complete-solve benchmarks.')
    old.ar.atomic_json(old.ar.STATUS,s)
raw_bytes=old.read(H/'execution/complete.json')['raw_bytes']
old.save(H/'model-publication.json',{
    'at':old.now(),'HTTP_verified_artifacts':pub,'raw_bytes':raw_bytes,
    'raw_files_physically_on_S_only':q['raw_file_sha256'],'terminal_receipts':receipts,
    'source_main_live_PTX_custody_pass':True,'candidate_accepted':False
})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md'
raw=ledger.read_bytes()
assert b'### D138 bounded pinned staging CPU prerequisite' not in raw
paragraphs=[
    '### D138 bounded pinned staging CPU prerequisite',
    'Previous goal turn closed E086 after0.0727951818%initial gain and strict two-tone/river guards. E080 stays accepted/live. Current source lead audits full pinned staging: retained actual canonical requests740,688,652/442,981,120/17,920bytes. Warm uploads also need full staging and node codecs need whole vectors. Paging discards staging after construction and must not retain added full-layout metadata. Bounded all-ref/current-ledger audit distinguishes closed E040 allocation-retaining two-window overlap. No overlap hunk, CUDA change or GPU implementation is composed.',
    'Freeze CPU prerequisite '+old.sha(H/'protocol.json')+' before one standalone Rust compiler/one CPU process/separate reader. Accepted E080 public Spot/GpuPlan/Store ThinLTO library and original fixture JSON pinned. Twelve canonical layouts:threeboards x isooff/on x packed/full mapping. Full mapping mirrors accepted private helper through public fields. Every original kind/player/arity/host/plan offset, complete selected-node list and greedy group retained. Proposed production window64MiB, enlarged only for a whole node; no tuning sweep. Diagnostic vectors are not a production resident allocation design.',
    '216fixed codec cases:four row shapes including zero-only and250x1326wide row, contiguous/gapped host arenas,3verification seam limits,3Store types and3float profiles with signedzero/subnormal/nonfinite/overflow. Complete source immutability, original/grouped upload floats, original/grouped full output Store q/scale/f32 images and all unowned guards pass. Six deliberate gap/overlap/total/overflow/too-small-window controls reject. No Solver/learning arenas, CUDA context/allocation/kernel, pinned memory or solve/timing execution. Seam limits are verification inputs, not candidate performance variants.',
    f'Raw{raw_bytes}bytes stay physicallyS. Separate mmap reader{q["checks"]}checks over{q["original_nodes_read"]}original nodes,{q["complete_active_blocks"]}whole active blocks,{q["transfer_groups"]}groups,{q["full_codec_store_words"]}fullcodec Store words,{q["full_upload_words"]}upload words,{q["unowned_guard_words"]}guards. ReportSHA '+old.sha(root/'report.json')+'. Large modeled request64MiB and tiny river17,920bytes are requests, not measured pinned/process memory or removable setup time. E080 overlaps existing allocation/setup with zero scans; allocator spans alone are not complete-cycle headroom.',
    'Integration contract retains nonallocating iteration/coalesced F32 paths/inactive/symmetry/state behavior, bounded warm uploads/readback with error drain, small/F32 thread behavior and paging metadata cleanup. Actual source/GPU/raw/error/fullcycle/material/compatibility/capacity/holdout/cumulative gates remain. No E087source/build/native process yet. '+str(len(pub))+'small artifacts HTTPbyte-verified. All children terminal, GPUlockabsent, accepted/main/live/protectedPTX custody passes. No adoption/push/livechange. E08014.7414188354%measured cumulative gain,lastprimaryB286 unchanged,goalactive.'
]
entry='\n\n'+'\n\n'.join(paragraphs)+'\n'
nl=b'\r\n' if b'\r\n'in raw else b'\n'
ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: validate bounded staging node and codec model','--',
    'research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody()
assert not(R/'gpu-run.lock').exists()
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as response:
    assert json.load(response)==old.read(old.ar.STATUS)
print(json.dumps({'status':q['status'],'checks':q['checks'],'raw_bytes':raw_bytes,
    'GPU_contexts':0,'HTTP_files':len(pub),'goal_status':'active'}),flush=True)
