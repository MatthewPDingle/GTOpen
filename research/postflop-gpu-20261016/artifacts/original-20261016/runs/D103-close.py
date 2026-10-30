"""Root replay and publication of compatibility-only profiler query."""
import json,re,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D103-profiler-support';P=old.read(H/'protocol.json');q=old.read(H/'report.json');checks=0
def check(value):
 global checks
 assert value;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
for name in ['cl','probe']:
 receipt=old.read(H/'execution'/(name+'.exit.json'));check(receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None)
old.pin(H/'build/probe.exe',q['binary_sha256']);old.pin(H/'execution/probe.stdout.log',q['stdout_sha256'])
markers=[json.loads(x.split('D103_RESULT ',1)[1]) for x in (H/'execution/probe.stdout.log').read_text(encoding='utf-8').splitlines() if x.startswith('D103_RESULT ')]
check(markers==q['markers']);check([m['stage'] for m in markers]==['identity','initialize','range_support','deinitialize','complete'])
identity,initialize,support,deinitialize,complete=markers
check(identity['device']=='NVIDIA GeForce RTX 5090' and (identity['major'],identity['minor'])==(12,0));check(identity['CUPTI_API_VERSION']==28);check([identity[k] for k in ['initialize_struct_size','support_struct_size','deinitialize_struct_size']]==[16,52,16])
for m in [initialize,support,deinitialize]:check(m['result']==0 and m['result_name']=='CUPTI_SUCCESS')
check(support['api']==0 and support['supported_enum_value']==3)
for k in ['isSupported','architecture','sli','vGpu','confidentialCompute','cmp','wsl']:check(support[k]==3)
check(complete['device_configuration_compatible'] and complete['support_queries']==1 and complete['cleanup_success'])
for k in ['application_kernel_launches','profiling_sessions','counter_collections','live_process_attachments','explicit_cuda_context_creations']:check(complete[k]==0)
cpp=(H/'probe.cpp').read_text(encoding='utf-8')
symbols=re.findall(r'fn<decltype\(&([A-Za-z0-9_]+)\)>\([^,]+,"([A-Za-z0-9_]+)"\)',cpp)
allowed={'cuInit','cuDeviceGet','cuDeviceGetName','cuDeviceGetAttribute','cuDriverGetVersion','cuptiGetVersion','cuptiGetResultString','cuptiProfilerInitialize','cuptiProfilerDeviceSupported','cuptiProfilerDeInitialize'}
check(len(symbols)==10 and {a for a,b in symbols}==allowed and all(a==b for a,b in symbols))
check('CUPTI_PROFILER_RANGE_PROFILING' in cpp and 'BeginSession' not in cpp and 'EnableProfiling' not in cpp and 'cuCtxCreate' not in cpp and 'cuLaunchKernel' not in cpp)
R=ROOT/'comparisons/D103-profiler-support-root-check';R.mkdir();old.save(R/'report.json',{'id':R.name,'at':old.now(),'status':'pass_compatible_only','checks':checks,'protocol_sha256':old.sha(H/'protocol.json'),'native_report_sha256':old.sha(H/'report.json'),'raw_markers_exact':True,'export_binding_allowlist_checked':sorted(allowed),'application_kernel_launches':0,'counter_collections':0,'profiling_sessions':0,'candidate_accepted':False,'limits':'Root transcript/source/ABI-pin replay, not external independent audit or OS/API internal side-effect tracing. Compatibility only. Permission, actual metric availability, collection/replay/graph/observer effects and speed remain unverified.'})
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip();check(subprocess.check_output(['git','log','-1','--format=%s'],cwd=old.REPO,text=True).strip()=='research: reject packed showdown cutoff precomputation')
old.save(ROOT/'runs/E063-closure/commit.json',{'at':old.now(),'commit':commit,'committed_paths':['research/postflop-gpu-20261016/experiments.md'],'accepted_source':'E051','candidate_accepted':False,'all_owned_children_terminal':True,'main_live_ptx_unchanged':True,'goal_active':True})
old.save(H/'checkpoint.json',{'at':old.now(),'goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B197','all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'progress':'E062andE063closed speed failures; D102exact integer proof; D103separate profiler compatibility query succeeds without collection.','next':'Freeze a fresh owned-process counter-availability/permission diagnostic using the correct installed official API/header for this device. Verify actual API support/limitations before choosing it. Query only, no collection/session/application kernels/live attach/elevation/driver/global changes. Retain unsupported/disabled/permission/error outcomes once; do not bypass or repeat. If usable, independently freeze source-matched workload exactness plus observer controls and actual hardware collection before attributing bottlenecks or selecting another mechanism.','closed_families':['E050/E061async source form','E057/E062prefix map','E063packed per-card cutoff segmentation'],'no_variant_or_resampling_rescues':True,'new_speedup_accepted':False})
published={}
for folder in [H,R,ROOT/'runs/E063-closure']:
 for p in folder.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.exe','.pdb','.obj','.lib','.dll','.exp']:continue
  key='evidence/'+folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():check(dst.read_bytes()==p.read_bytes())
  else:dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:check(response.read()==p.read_bytes())
  published[key]=old.sha(p)
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='D103');e.update(status='completed',correctness='pass',accepted=False,stage='Compatible configuration; counter access still unverified',reason='Official CUPTI API28initialize/query/deinitialize all success. One range-profiling support query reports all7configuration flags SUPPORTED. Zero application kernels, sessions or counter collections. This confirms compatibility only; availability/permission/collection/replay/graph/observer/benefit unverified.');e['evidence'].extend([{'label':'Raw support-query result','url':'evidence/D103-profiler-support/report.json'},{'label':'Root source and transcript replay','url':'evidence/'+R.name+'/report.json'},{'label':'Next prospective diagnostic','url':'evidence/D103-profiler-support/checkpoint.json'}]);ce=next(e for e in st['experiments'] if e['id']=='E063');ce['evidence'].append({'label':'Local closure ledger commit','url':'evidence/E063-closure/commit.json'});st.update(updated_at=old.now(),state='running',active_experiment=None,stage='Counter availability diagnostic preparation',activity='Separate CUPTI profiler API reports compatible configuration. Counter permission/availability not yet tested. Accepted E05112.437227%cumulative gain unchanged; next freeze query-only availability diagnostic.');old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();check(b'### D103 official profiler' not in raw)
note=f'''

### D103 official profiler compatibility query -- compatible; collection unverified

Existing D032/D085no-CLI/elevation constraints and D087activity/graph feasibility did not query this separate profiler API. Freeze655ca2adeec7e54b6395fdaf1cdf273604a4c79f61ae76cff7fed032a79e4dd5before compile/query:135pinned source/header/DLL/driver/tool/provenance inputs, official retained CUDA12.9.79CUPTI API28, typed decltypeexports/macros rather than guessed structures. One fresh owned C++process; direct system driver/private SDK DLLs, per-process PATH only. No live attach, installation, elevation, global driver/settings changes, context creation, application kernels, sessions or counter collection. Actual source explicitly binds only10allowed version/identity/initialize/support/deinitialize exports.

Fresh compile and native child terminal0. RTX5090compute12.0, driverAPI13030, CUPTIheader/runtime28match; official macro struct extents16/52/16bytes. Initialize success, exactly one RANGE_PROFILING compatibility query success, all7overall/architecture/SLI/vGPU/confidential-compute/CMP/WSL flags equal SUPPORTED3, deinitialize success. Binary9f5af84fb7fe38ca8d5b924aac401a32612d3662ad30f0814d21f3eacdd85823; stdout3099f2d0c659423b0f50d881755d2c32089e240b3a8c76f90bd7ef1cc2fde431. Root{old.read(R/'report.json')['checks']}pin/transcript/ABI/source allowlist checks, report{old.sha(R/'report.json')}; root is not external independent review or OS/internal side-effect tracing.

Result is **configuration compatibility only**. Counter availability/permission, actual collection, replay fidelity, captured-graph support, observer overhead and all speed/causal claims remain unverified. No alternative API/version/privilege or retry used. Publish{len(published)}HTTP-byte-verified artifacts and next checkpoint. Accepted162/main157/live/protectedPTX unchanged; no speedup accepted, E051qualified cumulative12.4372274192%remains. LastprimaryB197; no unowned native sessions left.

Next prospectively freeze a correct installed-API counter-availability query in fresh owned process after checking official device/API limitations. No collection/application kernels/session/live attach/elevation/global changes; record unsupported/disabled/permission failure once without bypass/repetition. Only after usable access, separately freeze source-matched exactness/graph/observer-controlled hardware collection. Preserve E061/E062/E063closed source families; goal active.
'''
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',nl));old.custody()
print(json.dumps({'status':'compatible_query_published','root_checks':old.read(R/'report.json')['checks'],'published':len(published),'counter_collections':0,'next':'separately frozen availability query','accepted_source':'E051','goal_active':True}),flush=True)
