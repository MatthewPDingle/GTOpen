"""Stage the single admitted D131 mechanism without activating solver source."""
from pathlib import Path
import difflib,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
D=R/'runs/D131-zero-check-setup-overlap';q=old.read(D/'report.json');assert q['admit_one_integrated_trial']and q['fixed_six_fresh_processes_complete']and len(q['full_layout_raw_replays'])==18
receipt=old.read(R/'runs/D131-manager/component.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
H=R/'runs/E080-source';assert not H.exists();H.mkdir();owned={};candidate_hashes={}
arena_path='crates/solver/src/gpu/arena.rs';mod_path='crates/solver/src/gpu/mod.rs'
arena=(old.REPO/arena_path).read_text(encoding='utf-8');mod=(old.REPO/mod_path).read_text(encoding='utf-8');probe=(D/'probe.rs').read_text(encoding='utf-8')
a=arena.index('        let zero = match store {');b=arena.index('        // Keep previously captured',a);predicate=arena[a:b]
token='''// A constructor-local proof, tied to an immutable borrow of this exact Store.
// It does not survive initialization or permit a later mutation/traversal.
pub(super) struct ZeroCheck<'a> {
    store: &'a Store,
    positive: bool,
}

impl<'a> ZeroCheck<'a> {
    pub(super) fn new(store: &'a Store) -> Self {
PREDICATE        Self { store, positive: zero }
    }

    fn positive_for(&self, store: &Store) -> Option<bool> {
        std::ptr::eq(self.store, store).then_some(self.positive)
    }
}

'''.replace('PREDICATE',predicate)
candidate_arena=arena.replace('impl ArenaLayout {',token+'impl ArenaLayout {',1)
start=candidate_arena.index('    fn can_upload_zeros(');a=candidate_arena.index(predicate,start)
candidate_arena=candidate_arena[:a]+'''        self.can_upload_prechecked(store, which, &ZeroCheck::new(store))
    }

    fn can_upload_prechecked(&self, store: &Store, which: usize, check: &ZeroCheck<'_>) -> bool {
        let zero = check.positive_for(store) == Some(true);
'''+candidate_arena[a+len(predicate):]
signature='''    pub(super) fn upload(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize, which: usize,
        staging: &mut [f32],
    ) -> Result<CudaSlice<f32>, String> {
'''
assert candidate_arena.count(signature)==1
new_signature=signature+'''        self.upload_prechecked(stream, solver, p, which, staging, None)
    }

    pub(super) fn upload_prechecked(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize, which: usize,
        staging: &mut [f32], check: Option<&ZeroCheck<'_>>,
    ) -> Result<CudaSlice<f32>, String> {
'''
candidate_arena=candidate_arena.replace(signature,new_signature,1)
candidate_arena=candidate_arena.replace('''        if self.can_upload_zeros(store, which) {''','''        let zero = match check {
            Some(check) => self.can_upload_prechecked(store, which, check),
            None => self.can_upload_zeros(store, which),
        };
        if zero {''',1)
test=r'''
    #[test]
    fn scoped_zero_checks_reject_other_stores_and_preserve_all_guards_and_bits() {
        fn image(s: &Store) -> Vec<u32> {
            match s {
                Store::I16 { q, scale } => q.as_slice().iter().map(|&x| x as u16 as u32)
                    .chain(scale.as_slice().iter().map(|x| x.to_bits())).collect(),
                Store::U16 { q, scale } => q.as_slice().iter().map(|&x| x as u32)
                    .chain(scale.as_slice().iter().map(|x| x.to_bits())).collect(),
                Store::F32(b) => b.as_slice().iter().map(|x| x.to_bits()).collect(),
            }
        }
        let mut cases = 0;
        for signed in [false, true] {
            let mut store = if signed { Store::i16(257, 4) } else { Store::u16(257, 4) };
            for step in 0..7 {
                if step == 1 {
                    match &mut store {
                        Store::I16 { q, .. } => q.as_mut_slice()[256] = -1,
                        Store::U16 { q, .. } => q.as_mut_slice()[256] = 1,
                        _ => unreachable!(),
                    }
                } else if step >= 2 {
                    let scale_bits = [0x8000_0000, 0x7f80_0000, 0xff80_0000, 0x7fc0_1234, 1][step - 2];
                    match &mut store {
                        Store::I16 { q, scale } => { q.as_mut_slice()[256] = 0; scale.as_mut_slice()[3] = f32::from_bits(scale_bits); }
                        Store::U16 { q, scale } => { q.as_mut_slice()[256] = 0; scale.as_mut_slice()[3] = f32::from_bits(scale_bits); }
                        _ => unreachable!(),
                    }
                }
                let before = image(&store);
                let check = ZeroCheck::new(&store);
                let other = Store::u16(257, 4);
                assert_eq!(check.positive_for(&other), None);
                for compact in [false, true] {
                    let mut arena = layout(compact);
                    for which in 0..2 {
                        assert_eq!(arena.can_upload_prechecked(&store, which, &check), step == 0);
                        assert!(!arena.can_upload_prechecked(&other, which, &check));
                    }
                    arena.initial[0].push(-0.0);
                    assert!(!arena.can_upload_prechecked(&store, 0, &check));
                    assert_eq!(arena.initial[0][0].to_bits(), 0x8000_0000);
                    arena.initial[0].clear();
                    if compact {
                        arena.inactive[0].initial[0] = 0;
                        assert!(!arena.can_upload_prechecked(&store, 0, &check));
                        assert_eq!(arena.inactive[0].initial, [0, usize::MAX]);
                    }
                }
                drop(check);
                assert_eq!(before, image(&store));
                cases += 1;
            }
        }
        let store = Store::f32(257);
        assert_eq!(ZeroCheck::new(&store).positive_for(&store), Some(false));
        assert_eq!(cases + 1, 15);
    }
'''
pos=candidate_arena.rfind('\n}');candidate_arena=candidate_arena[:pos]+test+candidate_arena[pos:]
a=probe.index('fn checks_with_setup<');b=probe.index('struct Mock(',a);helper=probe[a:b]
candidate_mod=mod.replace('use arena::ArenaLayout;','use arena::{ArenaLayout, ZeroCheck};',1)
candidate_mod=candidate_mod.replace('impl GpuSolver {',helper+'\nimpl GpuSolver {',1)
a=candidate_mod.index('        // Compile the PTX for the device we actually found:');b=candidate_mod.index('        let func = |name:',a)
compile_block=candidate_mod[a:b]
a2=candidate_mod.index('        let data_len = plan.arena_elements;',b);b2=candidate_mod.index('        let d_regrets = [',a2)
staging_block=candidate_mod[a2:b2]
setup='''        let stores = [&solver.regrets[0], &solver.regrets[1], &solver.strat[0], &solver.strat[1]];
        let q_bytes: usize = stores.iter().map(|store| match store {
            Store::I16 { q, .. } => q.len() * 2,
            Store::U16 { q, .. } => q.len() * 2,
            Store::F32(_) => 0,
        }).sum();
        let overlap = q_bytes >= 64 * 1024 * 1024;
        // Only immutable store scans leave this caller. Context, compilation,
        // allocation and every CUDA API stay here; joining precedes all uploads.
        let ((module, mut h_staging, mut arena_layout), zero_checks) = checks_with_setup(
            overlap,
            || {
COMPILE
STAGING
                Ok((module, h_staging, arena_layout))
            },
            || overlap.then(|| stores.map(ZeroCheck::new)),
        )?;
'''.replace('COMPILE',compile_block).replace('STAGING',staging_block)
candidate_mod=candidate_mod[:a]+setup+candidate_mod[b:a2]+'''        let data_len = plan.arena_elements;
'''+candidate_mod[b2:]
for p,which,index in[(0,0,0),(1,0,1),(0,1,2),(1,1,3)]:
    before=f'arena_layout[{p}].upload(&stream, solver, {p}, {which}, h_staging.as_mut_slice())?'
    after=f'arena_layout[{p}].upload_prechecked(&stream, solver, {p}, {which}, h_staging.as_mut_slice(), zero_checks.as_ref().map(|checks| &checks[{index}]))?'
    assert candidate_mod.count(before)==1;candidate_mod=candidate_mod.replace(before,after,1)
a=probe.index(' let mut lifecycle=0;');b=probe.index(' let mut predicates=0;',a);mock_body=probe[a:b]
unit='''
    #[test]
    fn zero_check_setup_preserves_caller_error_priority_and_joined_cleanup() {
        use std::sync::atomic::{AtomicUsize, Ordering};
        struct Mock(Arc<AtomicUsize>);
        impl Drop for Mock { fn drop(&mut self) { self.0.fetch_add(1, Ordering::SeqCst); } }
MOCK
        assert_eq!(lifecycle, 12);
    }
'''.replace('MOCK',mock_body)
pos=candidate_mod.rfind('\n}');candidate_mod=candidate_mod[:pos]+unit+candidate_mod[pos:]
for name,text in[(arena_path,candidate_arena),(mod_path,candidate_mod)]:
    short=Path(name).name;base=H/('accepted-'+short);candidate=H/('candidate-'+short)
    base.write_bytes((old.REPO/name).read_bytes());old.pin(base,old.BASE[name]);candidate.write_text(text,encoding='utf-8',newline='\n');candidate_hashes[name]=old.sha(candidate)
    owned[name]={'base':str(base),'candidate':str(candidate)}
    diff=''.join(difflib.unified_diff(base.read_text(encoding='utf-8').splitlines(True),text.splitlines(True),fromfile='accepted/'+name,tofile='E080/'+name));(H/(short+'.patch')).write_text(diff,encoding='utf-8',newline='\n')
assert candidate_arena.count(predicate)==1 and helper in candidate_mod
scope='One scoped CPU-only worker runs the four original full serial scale-first/q predicates while the original caller performs NVRTC/module, pinned staging allocation and ArenaLayout construction. All CUDA/context/stream/budget/plan remain on the original caller. The fixed >=64 MiB quantized-byte eligibility matches admitted D131; smaller/F32 paths retain original in-upload serial checks. Borrowed tokens accept only identical Store and cannot escape initialization; original snapshot guards execute at consumption. No skipped checks, persistent cache, changed integer grouping, kernel/math/quality/upload/state/layout/save changes.'
old.save(H/'source-review.json',{'at':old.now(),'scope':scope,'exact_D131_coordinate_helper':True,'original_predicate_expression_moved_verbatim':True,'original_layout_guards_retained':True,'compile_module_pinned_layout_source_bodies_retained':True,'scan_order':['regrets0','regrets1','strat0','strat1'],'four_tokens_used_once_in_same_order':True,'serial_fallback':'No tokens computed for ineligible fixtures; original per-upload scans remain. F32 contributes zero eligibility bytes. OS spawn failure computes original checks serially after setup.','safety':'Only immutable Store borrows reach worker. Setup reads Spot/tree/plan and owns its allocations; no concurrent traversal, Store write or GPU API on worker. Tokens remain borrowed until final upload and cannot be stored in GpuSolver. Wrong-store token conservatively declines zero path. Setup error priority and joined panic/drop semantics match the 12 tested D131 cases.','risks':'Speculative scans on setup failure, CPU/cache contention, pinned memory allocation, warm/F32/snapshot and process shape differences require integrated/broad/material checks. No component timing is a complete-solve claim.','added_units':2,'expected_ordinary_units_passed':86,'ignored_unchanged':4,'component_report_sha256':old.sha(D/'report.json')})
old.save(H/'manifest.json',{'id':'E080','at':old.now(),'accepted_source_sha256':old.BASE,'candidate_owned_sha256':candidate_hashes,'owned':owned,'scope':scope,'CUDA_source_unchanged':True,'component_report_sha256':old.sha(D/'report.json'),'source_activated':False,'candidate_accepted':False})
for p in H.iterdir():
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);assert not any(x['id']=='E080'for x in s['experiments'])
    s['experiments'].append({'id':'E080','at':old.now(),'title':'Overlap original zero validation with compiler and staging setup','kind':'experiment','status':'running','correctness':'D131 lifecycle, predicate and complete layout controls pass; integrated checks pending','fixture':'Three canonical compressed complete-solve fixtures','stage':'Integrated source staged; fresh builds pending','reason':'D131 saved 148.9565 ms in its component screen with CPU guards passing. One exact integrated trial retains all original scans, snapshot guards and caller-only CUDA APIs. No full-solve gain claimed.','accepted':False,'evidence':[{'label':'Frozen integrated source','url':'evidence/E080-source/manifest.json'},{'label':'Source and ownership review','url':'evidence/E080-source/source-review.json'}]})
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080',stage='Preparing E080 full-solve trial',activity='The zero-validation component passed. Stage its single integrated form with all original checks; fresh builds and exact complete-solve qualification follow. Accepted and live E051 remain unchanged.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'id':'E080','candidate_owned_sha256':candidate_hashes,'source_activated':False}),flush=True)
