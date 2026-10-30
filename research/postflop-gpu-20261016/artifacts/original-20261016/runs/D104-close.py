"""Preserve the single terminal hardware-busy availability result; no retry."""
import json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D104-counter-availability';P=old.read(H/'protocol.json');q=old.read(H/'report.json');checks=0
def check(v):
 global checks
 assert v;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
for n in ['cl','probe']:
 e=old.read(H/'execution'/(n+'.exit.json'));check(e['returncode']==0 and e['error'] is e['cleanup'] is None)
old.pin(H/'build/probe.exe',q['binary_sha256']);old.pin(H/'execution/probe.stdout.log',q['stdout_sha256'])
markers=[json.loads(x.split('D104_RESULT ',1)[1]) for x in (H/'execution/probe.stdout.log').read_text(encoding='utf-8').splitlines() if x.startswith('D104_RESULT ')];check(markers==q['markers'])
check([m['stage'] for m in markers]==['identity','initialize','context_create','availability_size','availability_fill','context_destroy','deinitialize','complete'])
i,init,create,size,fill,destroy,deinit,c=markers
check(i['device']=='NVIDIA GeForce RTX 5090' and i['major']==12 and i['minor']==0 and i['CUPTI_API_VERSION']==28)
check(init['result']==deinit['result']==create['result']==destroy['result']==0)
check(size['result']==0 and size['required_bytes']==9184 and size['struct_size']==40)
check(fill['result']==26 and fill['result_name']=='CUPTI_ERROR_HARDWARE_BUSY' and fill['allocated_bytes']==fill['returned_bytes']==9184 and fill['guards_exact'] and fill['guard_words_checked']==128)
check(c['size_queries']==c['fill_queries']==c['private_contexts_created']==c['private_contexts_destroyed']==1)
check(c['cleanup_success'] and c['current_context_after_is_null'] and c['guards_exact'] and not c['availability_image_obtained'])
for k in ['application_kernel_launches','profiling_sessions','counter_collections','live_process_attachments']:check(c[k]==0)
check(q['image'] is None and not (H/'execution/counter-availability.bin').exists())
cpp=(H/'probe.cpp').read_text(encoding='utf-8');symbols=re.findall(r'fn<decltype\(&([A-Za-z0-9_]+)\)>\([^,]+,"([A-Za-z0-9_]+)"\)',cpp)
expected={'cuInit':'cuInit','cuDeviceGet':'cuDeviceGet','cuDeviceGetName':'cuDeviceGetName','cuDeviceGetAttribute':'cuDeviceGetAttribute','cuDriverGetVersion':'cuDriverGetVersion','cuptiGetVersion':'cuptiGetVersion','cuptiGetResultString':'cuptiGetResultString','cuptiProfilerInitialize':'cuptiProfilerInitialize','cuptiProfilerGetCounterAvailability':'cuptiProfilerGetCounterAvailability','cuptiProfilerDeInitialize':'cuptiProfilerDeInitialize','cuCtxCreate':'cuCtxCreate_v2','cuCtxDestroy':'cuCtxDestroy_v2','cuCtxGetCurrent':'cuCtxGetCurrent'}
check(dict(symbols)==expected and len(symbols)==13)
for forbidden in ['BeginSession','EnableProfiling','cuLaunchKernel','cuptiRangeProfilerEnable']:check(forbidden not in cpp)
check(cpp.count('availability(&p)')==2 and 'requested<=16*1024*1024' in cpp and 'CREATE_NEW' in cpp)
R=ROOT/'comparisons/D104-availability-root-check';R.mkdir();old.save(R/'report.json',{'id':R.name,'at':old.now(),'status':'pass_preserved_hardware_busy_no_collection','checks':checks,'protocol_sha256':old.sha(H/'protocol.json'),'report_sha256':old.sha(H/'report.json'),'single_two_phase_query':True,'size_bytes':9184,'fill_result':26,'fill_result_name':'CUPTI_ERROR_HARDWARE_BUSY','private_context_created_and_destroyed':1,'current_context_restored_null':True,'guards':'128native checked u8 bytes; guard_words_checked label uses u8units, not128f32words. No independent raw guard image retained.','profiling_sessions':0,'counter_collections':0,'application_kernel_launches':0,'source_main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False,'limits':'Root source/transcript/pin replay, not external independent review. HardwareBusy does not identify the resource owner or establish unsupported hardware, disabled counters, insufficient privilege, or availability of any workaround. No fill retry or alternate profiling API attempted.'})
old.save(H/'checkpoint.json',{'at':old.now(),'previous_goal_turn_classification':'progress: two speed failures closed plus fresh integer/compatibility evidence','current_goal_turn_progress':'D104single availability attempt establishes size9184and HardwareBusy26at fill, cleanup verified; no hardware image/counter collection obtained.','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B197','all_owned_children_terminal':True,'profiling_route_closed_without_retry':True,'next':'Continue non-counter source/machine-code research. Audit a distinct compile-time common-arity local action-offset narrowing hypothesis: prove a<NA<=4,0<=i<nh<=1326 gives a*nh+i<=5303; retain original64bit arithmetic for genericNA0and all global reach/CFV slots. Before any kernel, freeze one source form, require actual compiled address-work reduction plus unchanged allocated resources/ABI/other entries. If no mechanism/resource benefit, close without casts/placement/arity variants. Do not revive closed GPU/CPU quantization, readback, reciprocal or mapping forms.','counter_access_limits':'No successful metadata image, enable/session/collection, metric values or profiling speed insight. Error is HardwareBusy, not permission-denied. Owner unknown; no external processes/settings changed.'})
published={}
for folder in [H,R]:
 for p in folder.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.exe','.pdb','.obj','.lib','.dll','.exp']:continue
  key='evidence/'+folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():check(dst.read_bytes()==p.read_bytes())
  else:dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:check(response.read()==p.read_bytes())
  published[key]=old.sha(p)
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='D104');e.update(status='completed',correctness='pass',accepted=False,stage='Availability fill returned HardwareBusy; route closed',reason='Size query succeeds at9,184bytes; single fill returns CUPTI_ERROR_HARDWARE_BUSY26.128u8guard bytes remain exact. Private context destroyed, current context null, profiler deinitialized. No image, counters, sessions, app kernels or retry. Owner/cause unknown; not a permission-denied or unsupported-hardware finding.');e['evidence'].extend([{'label':'Terminal raw query result','url':'evidence/D104-counter-availability/report.json'},{'label':'Root replay and limits','url':'evidence/'+R.name+'/report.json'},{'label':'Continue distinct non-counter source research','url':'evidence/D104-counter-availability/checkpoint.json'}]);s.update(updated_at=old.now(),state='running',active_experiment=None,stage='Distinct address-work source audit',activity='D104fill HardwareBusy26preserved without retry. Audit common-arity local offset32bit lowering with generic64bit fallback; compiler mechanism/resource proof required. Accepted E05112.437227%cumulative gain unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();check(b'### D104 counter availability' not in raw)
note=f'''

### D104 counter availability -- single fill returns hardware busy

Previous goal turn was progress: E062/E063fixed timing failures closed; D102integer proof and D103profiler compatibility changed next action. D104freezes1752475db18f04b7a89992f95a63d70b4d1e4d5159eb231a54753d078c16947fbefore compiler/query,142pinned inputs. Official SDK/API review retained in api-review.json; common cuptiProfilerGetCounterAvailability metadata API uses null-image size then guarded fill, separate from all collection APIs. Typed official extent40bytes and explicit driver v2context aliases. One fresh owned process, one temporary private context, no app kernels/session/collection/live attach/elevation/global settings or source activation.

Compiler/native exit0. Initialize/private context creation succeed; metadata size succeeds at9,184bytes. Exactly one fill returns26/CUPTI_ERROR_HARDWARE_BUSY. Native128u8guard bytes exact (raw label guard_words_checked means u8units, notf32words; no independently retained raw guard image). No metadata image emitted. Context destroy and deinitialize succeed; current context restored null. Binary98007ae807c431f9b23c33f42abec92c381bb9fa3027c70d8fc848481747a3ef;stdout985dc9f43c32140fcc5bfa931ad5388af6afa497d5974b44864e398cf93b1bd9. Root{old.read(R/'report.json')['checks']}pin/transcript/13export allowlist checks, report{old.sha(R/'report.json')}. Root is not external independent audit or native guard-buffer replay.

Close profiling route without fill retry, alternateAPI/SDK, collection, privilege/global changes or external process termination. HardwareBusy identifies neither owner nor cause, and is not permission-denied/unsupported-hardware evidence. Read-only GPU/process observation does not identify a counter owner; no absence/causality claim. No successful enable/collection/metrics/graph/observer/speed evidence. All{len(published)}artifacts HTTP-byte verified; accepted162/main157/live/protectedPTX unchanged, no gain accepted, accepted cumulative12.4372274192%and lastprimaryB197remain.

Continue meaningful non-counter source/machine-code work, not a blocked goal. Bounded source audit found prior GPU quantizationE009/E010, SSEencoderE012/E013and reciprocal/mapping families already measured/closed; do not revive them. Next audit one distinct common-arity local action-index narrowing form only: a<NA<=4and i<nh<=1326bound a*nh+i<=5303, keep genericNA0and all arbitrary global slot addresses64bit. Require an emitted address-work reduction plus current resource/ABI/unchanged-entry gates before any application kernel, and all existing1%/exactness/fixture/fresh16/broad/material/holdout/cumulative gates afterward. No source variant/resampling rescue. Goal active.
'''
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',nl));old.custody()
print(json.dumps({'status':'hardware_busy_preserved_no_retry','root_checks':old.read(R/'report.json')['checks'],'published':len(published),'profiling_route_closed':True,'goal_active':True}),flush=True)
