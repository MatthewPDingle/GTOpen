"""Create one fixed bounded-staging host candidate outside both checkouts."""
import ast
import difflib
import hashlib
from pathlib import Path
import shutil
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=74*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
q=old.read(R/'comparisons/D138-transfer-model/report.json')
assert q['status']=='pass_scoped_CPU_layout_and_codec_equivalence'
assert q['layouts']==12 and q['codec_cases']==216 and q['checks']==42291249
S=R/'runs/E087-source'
if S.exists():assert not list(S.iterdir())
else:S.mkdir()
rels=['crates/solver/src/gpu/arena.rs','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/continuation_paging.rs']
base={n:(old.REPO/n).read_bytes()for n in rels}
texts={n:b.decode().replace('\r\n','\n')for n,b in base.items()}
arena=texts[rels[0]];mod=texts[rels[1]];paging=texts[rels[2]]
model=(R/'runs/D138-transfer-model/probe.rs').read_text()
a=model.index('fn next_group(');b=model.index('fn plan(',a)
original_group=model[a:b].strip()
group=original_group.replace('fn next_group(','fn next_transfer_group(').replace('Block','ActiveBlock').replace('Group','TransferGroup')
assert group.replace('fn next_transfer_group(','fn next_group(').replace('ActiveBlock','Block').replace('TransferGroup','Group')==original_group
methods=(R/'runs/E087-bounded-methods.rs').read_text()
assert methods.count('// VALIDATED_NEXT_GROUP')==1
methods=methods.replace('// VALIDATED_NEXT_GROUP',group,1)
start=arena.index('        let mut scratch = vec![0.0; self.zeros.len()];')
end=arena.index('        let device = stream.clone_htod(&packed[..])',start)
capture=arena[start:end].rstrip()
w=arena.index('    pub(super) fn write(')
a=arena.index('            self.inactive.par_iter().for_each(|block| {',w)
b=arena.index('            });',a)+len('            });')
f32_restore=arena[a:b]
a=arena.index('        self.inactive.par_iter().for_each(|block| {',b)
b=arena.index('        });',a)+len('        });')
compressed_restore=arena[a:b]
for marker,body in [
    ('        // ORIGINAL_INACTIVE_CAPTURE',capture),
    ('            // ORIGINAL_F32_RESTORE',f32_restore),
    ('        // ORIGINAL_COMPRESSED_RESTORE',compressed_restore),
]:
    assert methods.count(marker)==1
    methods=methods.replace(marker,body,1)
assert 'ORIGINAL_' not in methods
derive='#[derive(Clone, Copy)]\nstruct ActiveBlock {'
assert arena.count('struct ActiveBlock {')==1
candidate_arena=arena.replace('struct ActiveBlock {',derive,1)
branch=(
    '        if self.len > staging.len()\n'
    '            && (self.compact || !matches!(store, Store::F32(_))) {\n'
    '            return self.upload_bounded(stream, solver, p, which, staging);\n'
    '        }\n'
)
needle='        if !self.compact {\n            if let Store::F32(b) = store {'
assert candidate_arena.count(needle)==1
candidate_arena=candidate_arena.replace(needle,branch+needle,1)
test_marker='#[cfg(test)]\nmod tests {'
assert candidate_arena.count(test_marker)==1
candidate_arena=candidate_arena.replace(test_marker,methods+'\n\n'+test_marker,1)
assert candidate_arena.replace(methods+'\n\n','',1).replace(branch,'',1).replace(derive,'struct ActiveBlock {',1)==arena

ctor_before='''        let data_len = plan.arena_elements;
        let mut h_staging = PinnedBuf::new(&ctx, data_len[0].max(data_len[1]))?;
        let mut arena_layout = [
            ArenaLayout::new(solver, &plan, 0),
            ArenaLayout::new(solver, &plan, 1),
        ];'''
ctor_after='''        let mut arena_layout = [
            ArenaLayout::new(solver, &plan, 0),
            ArenaLayout::new(solver, &plan, 1),
        ];
        let staging_len = arena_layout[0]
            .prepare_bounded(solver, 0, arena::PINNED_WORD_LIMIT)?
            .max(arena_layout[1].prepare_bounded(solver, 1, arena::PINNED_WORD_LIMIT)?);
        let mut h_staging = PinnedBuf::new(&ctx, staging_len)?;'''
full_before='''            let len = self.d_regrets[p].len();
            self.stream
                .memcpy_dtoh(&self.d_regrets[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            self.arena_layout[p].write(solver, p, 0, &self.h_staging.as_slice()[..len]);
            self.stream
                .memcpy_dtoh(&self.d_strat[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            self.arena_layout[p].write(solver, p, 1, &self.h_staging.as_slice()[..len]);'''
full_after='''            self.arena_layout[p].download(&self.stream, solver, p, 0,
                &self.d_regrets[p], self.h_staging.as_mut_slice())?;
            self.arena_layout[p].download(&self.stream, solver, p, 1,
                &self.d_strat[p], self.h_staging.as_mut_slice())?;'''
strategy_before='''            let len = self.d_strat[p].len();
            self.stream
                .memcpy_dtoh(&self.d_strat[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            self.arena_layout[p].write(solver, p, 1, &self.h_staging.as_slice()[..len]);'''
strategy_after='''            self.arena_layout[p].download(&self.stream, solver, p, 1,
                &self.d_strat[p], self.h_staging.as_mut_slice())?;'''
candidate_mod=mod
mod_edits=[(ctor_before,ctor_after),(full_before,full_after),(strategy_before,strategy_after)]
for before,after in mod_edits:
    assert candidate_mod.count(before)==1
    candidate_mod=candidate_mod.replace(before,after,1)
reverse=candidate_mod
for before,after in reversed(mod_edits):
    if after==strategy_after:
        at=reverse.rfind(after);assert at>=0
        reverse=reverse[:at]+before+reverse[at+len(after):]
    else:
        assert reverse.count(after)==1
        reverse=reverse.replace(after,before,1)
assert reverse==mod
page_before='        gpu.h_staging = PinnedBuf::new(&gpu._ctx, 1)?;'
page_after=page_before+'\n        for layout in &mut gpu.arena_layout { layout.discard_bounded(); }'
assert paging.count(page_before)==1
candidate_paging=paging.replace(page_before,page_after,1)
assert candidate_paging.replace(page_after,page_before,1)==paging
values=dict(zip(rels,[candidate_arena,candidate_mod,candidate_paging]))
owned={}
for n in rels:
    before=S/'baseline'/Path(n).name;after=S/'candidate'/Path(n).name
    before.parent.mkdir(exist_ok=True);after.parent.mkdir(exist_ok=True)
    before.write_bytes(base[n])
    nl=b'\r\n' if b'\r\n'in base[n] else b'\n'
    after.write_bytes(values[n].encode().replace(b'\n',nl))
    (S/(Path(n).name+'.patch')).write_text(''.join(difflib.unified_diff(texts[n].splitlines(True),values[n].splitlines(True),fromfile='accepted/'+n,tofile='E087/'+n)),encoding='utf-8',newline='\n')
    owned[n]={'base':str(before),'candidate':str(after)}
old.save(S/'source-review.json',{
    'at':old.now(),'scope':'Three host files only. One serial bounded staging window for warm uploads/full and strategy readback. Fixed64MiB limit, complete-node enlargement, nonallocating group iteration, existing compact metadata/copy spans/inactive snapshots reused. Paging releases added full-layout active metadata.',
    'source_reverse_exact':True,
    'validated_group_function':'Exact D138 function after type/name substitutions; source strings reverse to the original CPU-model function.',
    'original_inactive_body_sha256':hashlib.sha256(capture.encode()).hexdigest(),
    'original_F32_restore_body_sha256':hashlib.sha256(f32_restore.encode()).hexdigest(),
    'original_compressed_restore_body_sha256':hashlib.sha256(compressed_restore.encode()).hexdigest(),
    'unchanged':'CUDA/plan/Store codecs/flags/math/precision/quality/graphs/device layouts and payloads. E080 worker/check predicates and borrow proofs exact; all CUDA calls remain original caller. Existing small-layout writes and complete-row codecs preserved. No new persistent fields or production group vector.',
    'ordering':'Large full layouts collect original owner nodes at exact host/device offsets. Coverage/row capacity checked before bounded copies. Whole row decoding/encoding uses original methods in ascending descriptor order; independent rows retain disjoint q/scales. Original coalesced compact F32 spans intersect each group. Full F32 copies avoid Rayon. Full F32 upload remains direct clone_htod.',
    'drain':'Bounded uploads and all new download calls synchronize after copy even when submission reports an error. Copy error wins if both copy/wait fail. No pending copy crosses CPU encoding or staging reuse. Small full-F32 direct upload keeps its original branch. Error/unwind control still required; no atomic rollback or hardware-failure claim.',
    'costs':'Full active descriptor Vec allocations and scanning are additional CPU/host costs. Fewer pinned bytes are requested, but additional calls/waits/metadata/encoder chunking may erase benefit. E080 overlaps setup with zero checks, so allocation spans are not removable complete-cycle headroom. Paging frees extra descriptors after replacing staging.',
    'new_unit_tests':2,'expected_ordinary_units':88,'ordinary_ignored':4,
    'primary_sources':['https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__MEM.html','https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__STREAM.html'],
    'pending':'Standalone type/unit checks; actual constructor/upload/readback/device/CPU raw error/unwind/symmetry controls; fresh full builds; original complete-cycle1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative gates.'
})
manifest={
    'id':'E087','at':old.now(),'owned':owned,
    'candidate_owned_sha256':{n:old.sha(v['candidate'])for n,v in owned.items()},
    'scope':'Bound actual host pinned allocation with one serial complete-node transfer window;3host files,CUDA unchanged.',
    'fixed_window_bytes':64*1024*1024,
    'D138_report_sha256':old.sha(R/'comparisons/D138-transfer-model/report.json'),
    'source_activated':False,'candidate_accepted':False,'previous_accepted':'E080'
}
old.save(S/'manifest.json',manifest)
pub=[]
for p in sorted(S.rglob('*')):
    if not p.is_file():continue
    key=S.name+'/'+p.relative_to(S).as_posix()
    dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
    assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
    pub.append(key)
old.save(S/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'source_activated':False,'compiler_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);assert not any(x['id']=='E087'for x in s['experiments'])
    s['experiments'].append({'id':'E087','at':old.now(),'title':'Bound the actual pinned staging allocation','status':'planned','stage':'Host source and type/control preparation','correctness':'pending','accepted':False,'reason':'Fixed64MiB serial complete-node staging candidate prepared in3host files. Extra metadata/calls/waits may erase benefit; no GPU or timing result.','evidence':[{'label':'Source and ordering review','url':'evidence/E087-source/source-review.json'},{'label':'Exact candidate scope','url':'evidence/E087-source/manifest.json'}]})
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E087',stage='E087 source/type and raw-control preparation',activity='Prepared bounded staging for fresh/warm/full/compact/F32 paths and paging cleanup. GPU correctness and speed remain unproven; E080 stays live.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(S/'manifest.json'),flush=True)
