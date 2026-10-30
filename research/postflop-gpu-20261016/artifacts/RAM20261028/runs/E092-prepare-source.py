import sys,shutil,difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not (ROOT/'gpu-run.lock').exists()
design=ROOT/'runs/D153-packet-integration-review/design-review.json'
D=h.read(design)
for p,digest in D['source_sha256'].items():h.pin(p,digest)
H=ROOT/'runs/E092-source';H.mkdir(exist_ok=False)
for arm in ['baseline','candidate']:(H/arm).mkdir()
source=h.REPO/'crates/solver/src/gpu'
for name in ['mod.rs','arena.rs','kernels.cu','plan.rs']:
    shutil.copyfile(source/name,H/'baseline'/name)
    shutil.copyfile(source/name,H/'candidate'/name)
mod=(source/'mod.rs').read_text(encoding='utf-8')
changes=[('mod arena;','mod arena;\nmod packet_readback;'),('    arena_layout: [ArenaLayout; 2],','    arena_layout: [ArenaLayout; 2],\n    packet_functions: Option<packet_readback::Functions>,'),('            arena_layout,','            arena_layout,\n            packet_functions: None,')]
for strategy in [False,True]:
    name='sync_strategy' if strategy else 'sync_to_cpu'
    before=f'    pub fn {name}(&mut self, solver: &mut Solver) -> Result<(), String> {{\n        self.stream.synchronize().map_err(e)?;'
    after=before+f'\n        if self.try_packet_sync(solver, {str(strategy).lower()}, packet_readback::MIN_SOURCE_BYTES)? {{return Ok(());}}'
    changes.append((before,after))
candidate=mod
for before,after in changes:
    assert candidate.count(before)==1,before
    candidate=candidate.replace(before,after,1)
reverse=candidate
for before,after in reversed(changes):reverse=reverse.replace(after,before,1)
assert reverse==mod
(H/'candidate/mod.rs').write_bytes(candidate.replace('\n','\r\n').encode())
arena=(source/'arena.rs').read_text(encoding='utf-8');extra=(ROOT/'runs/E092-arena-append.rs').read_text(encoding='utf-8')
(H/'candidate/arena.rs').write_bytes((arena+'\n'+extra).replace('\n','\r\n').encode())
shutil.copyfile(ROOT/'runs/E092-packet-readback.rs',H/'candidate/packet_readback.rs')
ptx=ROOT/'runs/D151-auxiliary-resource/execution/packet-compute_120.ptx'
h.pin(ptx,'579e3c44469c9c8052097970f7bb37cb307e2bb18ded5aed15aed40f47e19292')
shutil.copyfile(ptx,H/'candidate/packet-sm120.ptx')
shutil.copyfile(ROOT/'runs/D151-auxiliary-resource/packet.cu',H/'candidate/packet-source.cu')
assert (H/'candidate/kernels.cu').read_bytes()==(H/'baseline/kernels.cu').read_bytes()
assert (H/'candidate/plan.rs').read_bytes()==(H/'baseline/plan.rs').read_bytes()
inactive=extra[extra.index('        self.inactive.par_iter()'):extra.index('\n    }\n}',extra.index('        self.inactive.par_iter()'))]
assert inactive in arena
patch=''.join(difflib.unified_diff(mod.splitlines(True),candidate.splitlines(True),fromfile='accepted/mod.rs',tofile='candidate/mod.rs'))
(H/'mod.patch').write_bytes(patch.encode())
h.save(H/'source-review.json',{'at':h.now(),'id':'E092','status':'isolated_integration_source_before_compiler','D153_fixed_contract_sha256':h.sha(design),'fallback_mod_reversal_exact':True,'arena_original_text_exact_prefix':True,'inactive_restore_body_exact_original_duplicate':True,'main_CUDA_and_plan_bytes_exact':True,'admission':'Exactly frozen16MiB aggregate selected source,compressed I16/U16,cc120,currentCFV/pinned>=65544words,31descriptors,128threads. Private min_source_bytes parameter exists solely so same checked internal path can be forced in separate correctness controls. Actual application entry points pass the fixed16MiB constant.','new_allocations':'Two host Block vectors per admitted sync. No per-packet heap, extra explicit device buffers or pinned allocations. Option of two CudaFunctions retains auxiliary module owners; wrapper/host/module resource changes require actual qualification. Lazy load errors decline before data writes after draining the stream. Runtime copy/launch failures drain and propagate.','bounds':'Whole-call preflight validates selected Store/q/scale formats and current lengths, unique increasing node ownership, disjoint increasing host/source intervals, u64/usize overflow and every packet block footprint before optional work. Unsupported layouts decline to original path.','pinned':'Raw-zero exactly checked65544word prefix before typed f32 views. Descriptor and packed output bits travel as f32 storage without arithmetic. Exact borrowed prefix retained through upload/download completion; no cached scratch pointer or escaped borrow.','CPU_state':'Direct q raw bits and exact scale scatter, exact duplicated original inactive restoration. Iteration and symmetry publication copied. All learning source arrays remain read-only; only completed CFV scratch and CPU output stores written.','not_proven':'Compilation, actual source/host engine equivalence, intended activation, default fallback silence, resource/memory/capacity effects and complete-cycle speed remain unproven. No numerical/source/threshold/shape rescue after actual failed form; old E009/E010 stay closed.'})
files=[p for p in H.rglob('*') if p.is_file()]+[Path(__file__),ROOT/'runs/E092-packet-readback.rs',ROOT/'runs/E092-arena-append.rs',design]
h.save(H/'manifest.json',{'at':h.now(),'id':'E092','accepted_source_sha256':h.custody(),'owned_source_sha256':{str(p):h.sha(p) for p in files},'candidate_source_sha256':{p.name:h.sha(p) for p in (H/'candidate').iterdir()},'compiler_or_native_execution':False,'accepted_application_source_activated':False})
print(h.sha(H/'manifest.json'),flush=True)
