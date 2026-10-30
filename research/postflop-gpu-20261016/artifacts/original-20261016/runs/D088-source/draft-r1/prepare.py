"""Freeze a CPU constructor-stage diagnostic, no optimization hypothesis yet."""
import difflib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/D088-source';D.mkdir();H=ROOT/'runs/D088-build-plan';H.mkdir()
files={'crates/solver/src/gpu/mod.rs':'mod.rs','crates/solver/src/gpu/arena.rs':'arena.rs'};owned={}
for path,name in files.items():
 original=(old.REPO/path).read_text(encoding='utf-8');s=original
 if name=='mod.rs':
  needle='        let mut plan = GpuPlan::build(&solver.spot, solver.use_isomorphism);'
  assert s.count(needle)==1
  hooks='''        let mut d088_last = std::time::Instant::now();
        let mut d088_mark = |stage: &str| {
            let elapsed = d088_last.elapsed().as_secs_f64() * 1000.0;
            eprintln!("D088_INIT {{\\"stage\\":\\"{}\\",\\"elapsed_ms\\":{}}}", stage, elapsed);
            d088_last = std::time::Instant::now();
        };
'''
  s=s.replace(needle,hooks+needle)
  for before,after in [
   ('        let ctx = CudaContext::new(0).map_err(e)?;','        d088_mark("plan_budget");\n        let ctx = CudaContext::new(0).map_err(e)?;'),
   ('        unsafe { ctx.disable_event_tracking() };','        unsafe { ctx.disable_event_tracking() };\n        d088_mark("context_stream");'),
   ('        let func = |name: &str| module.load_function(name).map_err(e);','        let func = |name: &str| module.load_function(name).map_err(e);\n        d088_mark("nvrtc_module");'),
   ('        let mut h_staging = PinnedBuf::new(&ctx, data_len[0].max(data_len[1]))?;','        let mut h_staging = PinnedBuf::new(&ctx, data_len[0].max(data_len[1]))?;\n        d088_mark("pinned_staging");'),
   ('        let d_regrets = [','        d088_mark("arena_layouts");\n        let d_regrets = ['),
   ('        let (lock_off, lock_sigma) = build_lock_table(solver);','        let (lock_off, lock_sigma) = build_lock_table(solver);\n        d088_mark("lock_table");'),
   ('        Ok(GpuSolver {','        d088_mark("fold_table");\n        let d088_result = GpuSolver {'),
   ('            _module: module,\n        })','            _module: module,\n        };\n        d088_mark("metadata_upload_and_object");\n        Ok(d088_result)')
  ]:
   assert s.count(before)==1,before;s=s.replace(before,after)
  for p in range(2):
   for which,label in [(0,'regret'),(1,'strategy')]:
    before=f'            arena_layout[{p}].upload(&stream, solver, {p}, {which}, h_staging.as_mut_slice())?,'
    after=f'            {{ let device = arena_layout[{p}].upload(&stream, solver, {p}, {which}, h_staging.as_mut_slice())?; d088_mark("{label}{p}_upload"); device }},'
    assert s.count(before)==1;s=s.replace(before,after)
 else:
  before='    fn can_upload_zeros(&self, store: &Store, which: usize) -> bool {';assert s.count(before)==1
  s=s.replace(before,before+'\n        let d088_start = std::time::Instant::now();')
  before='        zero && self.initial[which].is_empty()\n            && self.inactive.iter().all(|block| block.initial[which] == usize::MAX)'
  after='''        let result = zero && self.initial[which].is_empty()
            && self.inactive.iter().all(|block| block.initial[which] == usize::MAX);
        eprintln!("D088_ZERO {{\\"which\\":{},\\"positive_zero\\":{},\\"elapsed_ms\\":{}}}",
            which, result, d088_start.elapsed().as_secs_f64() * 1000.0);
        result'''
  assert s.count(before)==1;s=s.replace(before,after)
 (D/('baseline-'+name)).write_bytes((old.REPO/path).read_bytes());(D/('diagnostic-'+name)).write_text(s,encoding='utf-8',newline='\n')
 (D/(name+'.patch')).write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='accepted/'+path,tofile='diagnostic/'+path)),encoding='utf-8',newline='\n')
 owned[path]={'base':str(D/('baseline-'+name)),'base_sha256':old.sha(D/('baseline-'+name)),'candidate':str(D/('diagnostic-'+name)),'candidate_sha256':old.sha(D/('diagnostic-'+name))}
old.save(D/'source-review.json',{'id':'D088-CPU-constructor-stages','at':old.now(),'kind':'diagnostic_only','basis_report':str(ROOT/'comparisons/D087-driver-phase-root-check/report.json'),'basis_sha256':old.sha(ROOT/'comparisons/D087-driver-phase-root-check/report.json'),'motivation':'D087init657ms includes417ms outsideAPI/device records. Distinguish planning, NVRTC/CPU work, arena layouts and actual positive-zero scanning before choosing any optimizer.','instrumentation':'Local Instant spans and stderr JSON only; 12outer stages and four nested zero-scan measurements. Same accepted E051 CUDA, factory call/field order, owned allocations, integer/FP formulas, quality/stop/evaluator. Individual uploads wrapped in expression blocks; same owners and lifetimes returned. No additional GPU call or resource.','scope':'Fresh compressed rainbow, exact accepted6full states/60checkpoints, fixed3ordinary/diagnostic pairs. Observer absolute complete/native/outer wall changes<=10%in everypair; no extensions/exclusions/pooling. No optimizer accepted or gate relaxed.','prior_counterevidence':'D012 early-ctor wall stalls were not established algorithm costs; D019 already validated final vectorized readback code; E049zero metadata full-cycle rejection remains closed. Aggregate gaps alone do not reopen those implementations.','limits':'Instrumentation can alter compiler/allocator/scheduling behavior. Matched observer gate required; stage sums exclude marker logging and nested scans must not be added to enclosing upload spans. No global bias or universal bottleneck proof.'})
old.save(D/'manifest.json',{'at':old.now(),'id':'D088','accepted_source_sha256':old.BASE,'candidate_owned_sha256':{p:v['candidate_sha256'] for p,v in owned.items()},'diagnostic_only':True,'optimization_accepted':False,'source_review_sha256':old.sha(D/'source-review.json')})
(H/'build.py').write_text((ROOT/'runs/E054-build-plan/build.py').read_text(encoding='utf-8').replace('E054','D088'),encoding='utf-8',newline='\n')
p=old.read(ROOT/'runs/E054-build-plan/build-protocol.json');p.update(id='D088-diagnostic-build',at=old.now(),accepted_source_sha256=old.BASE,owned=owned)
p['phases']=[{**x,'target':x['target'].replace('e054','d088'),'outputs':{k:v.replace('E054','D088') for k,v in x['outputs'].items()}} for x in p['phases'] if x['id']=='primary']
refs=[H/'build.py',D/'source-review.json',D/'manifest.json',*D.glob('baseline-*'),*D.glob('diagnostic-*'),*D.glob('*.patch'),ROOT/'comparisons/D087-driver-phase-root-check/report.json',ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/accepted-E051/protected-main.json',old.REPO/'tools/postflop_autoresearch.py']
p['input_sha256']={str(x):old.sha(x) for x in refs};old.save(H/'build-protocol.json',p)
published={}
for directory in [D,H]:
 for src in directory.iterdir():
  key=directory.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20).read()==src.read_bytes();published[key]=old.sha(src)
old.save(H/'pre-build-publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id']=='D088' for e in st['experiments']);st['experiments'].append({'id':'D088','title':'CPU constructor stage timing','kind':'diagnostic','status':'preparing','stage':'Frozen diagnostic build','reason':'Locate CPU initialization time measured outsideAPI/device activity. No optimization source is being adopted.','evidence':[{'label':'D088 diagnostic source review and gates','url':'evidence/D088-source/source-review.json'},{'label':'D088 frozen isolated build','url':'evidence/D088-build-plan/build-protocol.json'}]});st.update(state='running',stage='D088 constructor diagnostic build',activity='Build one primary diagnostic with local CPU timers; preserve acceptedE051 and assess observer effects before interpreting stage timings.',active_experiment='D088',updated_at=old.now());old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'build-protocol.json'),'source_files':list(owned),'published':len(published)}),flush=True)
