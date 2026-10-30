"""Freeze the SDK's two-phase counter-availability metadata query, no collection."""
import ast,json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>=54*1024**3
parent=ROOT/'runs/D103-profiler-support';prior=old.read(parent/'protocol.json');assert old.read(parent/'report.json')['status']=='configuration_reports_compatible_collection_unverified'
H=ROOT/'runs/D104-counter-availability';assert not H.exists();H.mkdir()
cpp=(parent/'probe.cpp').read_text(encoding='utf-8').replace('D103_RESULT','D104_RESULT')
cpp=cpp.replace('#include <stdexcept>','#include <stdexcept>\n#include <vector>\n#include <algorithm>')
needle='auto supported=fn<decltype(&cuptiProfilerDeviceSupported)>(lib,"cuptiProfilerDeviceSupported");'
assert cpp.count(needle)==1;cpp=cpp.replace(needle,'auto availability=fn<decltype(&cuptiProfilerGetCounterAvailability)>(lib,"cuptiProfilerGetCounterAvailability");')
needle='  bool compatible=false;';a=cpp.index(needle);b=cpp.index('\n }catch(',a)
body=r'''  auto create=fn<decltype(&cuCtxCreate)>(d,"cuCtxCreate_v2");auto destroy=fn<decltype(&cuCtxDestroy)>(d,"cuCtxDestroy_v2");auto current=fn<decltype(&cuCtxGetCurrent)>(d,"cuCtxGetCurrent");
  CUcontext before=nullptr;if(current(&before)!=CUDA_SUCCESS||before!=nullptr)throw std::runtime_error("fresh process already has current context");
  bool obtained=false;int size_calls=0,fill_calls=0,created=0,destroyed=0;size_t requested=0,returned=0;bool guards=true;CUptiResult dr=CUPTI_SUCCESS;CUresult cr=CUDA_SUCCESS;
  if(ir==CUPTI_SUCCESS){
   CUcontext ctx=nullptr;auto context_result=create(&ctx,0,device);
   printf("D104_RESULT {\"stage\":\"context_create\",\"result\":%d,\"private_context\":true,\"flags\":0}\n",int(context_result));fflush(stdout);
   if(context_result==CUDA_SUCCESS){
    created=1;CUpti_Profiler_GetCounterAvailability_Params p={};p.structSize=CUpti_Profiler_GetCounterAvailability_Params_STRUCT_SIZE;p.ctx=ctx;
    auto ar=availability(&p);size_calls=1;requested=p.counterAvailabilityImageSize;
    printf("D104_RESULT {\"stage\":\"availability_size\",\"result\":%d,\"result_name\":%s,\"required_bytes\":%zu,\"struct_size\":%zu}\n",int(ar),label(ar).c_str(),requested,size_t(CUpti_Profiler_GetCounterAvailability_Params_STRUCT_SIZE));fflush(stdout);
    if(ar==CUPTI_SUCCESS&&requested>0&&requested<=16*1024*1024){
     constexpr size_t GUARD=64;std::vector<uint8_t> storage(requested+2*GUARD,0x5a);std::fill(storage.begin()+GUARD,storage.end()-GUARD,0xcd);p.pCounterAvailabilityImage=storage.data()+GUARD;p.counterAvailabilityImageSize=requested;
     auto fr=availability(&p);fill_calls=1;returned=p.counterAvailabilityImageSize;
     guards=std::all_of(storage.begin(),storage.begin()+GUARD,[](uint8_t x){return x==0x5a;})&&std::all_of(storage.end()-GUARD,storage.end(),[](uint8_t x){return x==0x5a;});
     printf("D104_RESULT {\"stage\":\"availability_fill\",\"result\":%d,\"result_name\":%s,\"allocated_bytes\":%zu,\"returned_bytes\":%zu,\"guard_words_checked\":128,\"guards_exact\":%s}\n",int(fr),label(fr).c_str(),requested,returned,guards?"true":"false");fflush(stdout);
     if(fr==CUPTI_SUCCESS&&returned>0&&returned<=requested&&guards){
      HANDLE file=CreateFileW(L"counter-availability.bin",GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);if(file==INVALID_HANDLE_VALUE)throw std::runtime_error("create-new availability output failed");DWORD wrote=0;BOOL ok=WriteFile(file,p.pCounterAvailabilityImage,DWORD(returned),&wrote,nullptr);BOOL flushed=FlushFileBuffers(file);CloseHandle(file);if(!ok||!flushed||wrote!=returned)throw std::runtime_error("availability write incomplete");obtained=true;
     }
    }
    cr=destroy(ctx);destroyed=cr==CUDA_SUCCESS?1:0;printf("D104_RESULT {\"stage\":\"context_destroy\",\"result\":%d}\n",int(cr));fflush(stdout);
   }
   CUpti_Profiler_DeInitialize_Params dp={};dp.structSize=CUpti_Profiler_DeInitialize_Params_STRUCT_SIZE;dr=deinitialize(&dp);printf("D104_RESULT {\"stage\":\"deinitialize\",\"result\":%d,\"result_name\":%s}\n",int(dr),label(dr).c_str());fflush(stdout);
  }
  CUcontext after=nullptr;auto after_result=current(&after);bool clean=dr==CUPTI_SUCCESS&&cr==CUDA_SUCCESS&&created==destroyed&&after_result==CUDA_SUCCESS&&after==nullptr;
  printf("D104_RESULT {\"stage\":\"complete\",\"availability_image_obtained\":%s,\"size_queries\":%d,\"fill_queries\":%d,\"requested_bytes\":%zu,\"returned_bytes\":%zu,\"private_contexts_created\":%d,\"private_contexts_destroyed\":%d,\"current_context_after_is_null\":%s,\"cleanup_success\":%s,\"guards_exact\":%s,\"application_kernel_launches\":0,\"profiling_sessions\":0,\"counter_collections\":0,\"live_process_attachments\":0,\"performance_measured\":false}\n",obtained?"true":"false",size_calls,fill_calls,requested,returned,created,destroyed,after==nullptr?"true":"false",clean?"true":"false",guards?"true":"false");fflush(stdout);return clean&&guards?0:2;'''
cpp=cpp[:a]+body+cpp[b:];(H/'probe.cpp').write_text(cpp,encoding='utf-8',newline='\n')
old.save(H/'api-review.json',{'at':old.now(),'official_sources':[{'url':'https://docs.nvidia.com/cupti/12.9/api/group__CUPTI__PROFILER__API.html','finding':'cuptiProfilerGetCounterAvailability queries a metadata image used to filter available raw metrics; active profiling/sampling can cause failure.'},{'url':'https://docs.nvidia.com/cupti/12.9.1/main/main.html','finding':'New host/range APIs are recommended for future range collection. This stage uses the common availability query only, not legacy event/metric collection.'}],'local_authority':'Pinned CUDA12.9.79API28headers and runtime. GetCounterAvailability official struct has ctx/imageSize/imagePointer, size40by macro, null image first, fill only after positive bounded size success. cuCtxCreate/cuCtxDestroy macros explicitly map to v2, typed bindings use matching exported names. No device architecture exception found in this query declaration/docs; D103reports range compatibility. No assertion of future collection support/privilege from that evidence.','scope':'One private context in a fresh process,2phase size/fill metadata query, destroy/deinitialize, zero app kernels/sessions/collections. Failure closes route without retry/privilege/global setting workaround.','previous_goal_turn_classification':'progress: E062/E063fixed speed failures closed, D102integer proof, D103compatibility result changes next action.'})
execute=r'''import json,os,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
OUT=H/'execution'
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3;assert not OUT.exists();OUT.mkdir();(H/'build').mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid'] in gpu['stdout'];old.save(OUT/'before.json',{'at':old.now(),'gpu':gpu,'protocol_sha256':sys.argv[1]})
 old.child(P['compile_command_line'],OUT,'cl',old.env(),120)
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'build/probe.exe'),'native_executions':0})
 env=old.env();env['PATH']=str(Path(P['sdk_dll_paths'][0]).parent)+os.pathsep+env.get('PATH','')
 # old.child uses REPO cwd; launch an owned subprocess from this script into OUT
 # so CreateFile(CREATE_NEW) writes metadata only to the off-tree research directory.
 import subprocess,time
 started=old.now();proc=None;fault=None;cleanup=None
 old.save(OUT/'probe.invocation.json',{'at':started,'command':[str(H/'build/probe.exe'),*P['sdk_dll_paths']],'cwd':str(OUT)})
 try:
  with (OUT/'probe.stdout.log').open('xb') as out,(OUT/'probe.stderr.log').open('xb') as err:
   proc=subprocess.Popen([str(H/'build/probe.exe'),*P['sdk_dll_paths']],cwd=OUT,env=env,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW);proc.wait(timeout=120)
 except BaseException as e:fault=repr(e);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(OUT/'probe.exit.json',{'started_at':started,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
 assert proc.returncode==0,(OUT/'probe.stderr.log').read_text(encoding='utf-8',errors='replace')[-2000:]
 markers=[json.loads(x.split('D104_RESULT ',1)[1]) for x in (OUT/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if x.startswith('D104_RESULT ')];assert markers[0]['stage']=='identity' and markers[-1]['stage']=='complete';c=markers[-1]
 assert c['cleanup_success'] and c['current_context_after_is_null'] and c['guards_exact'] and c['private_contexts_created']==c['private_contexts_destroyed']
 assert all(c[k]==0 for k in ['application_kernel_launches','profiling_sessions','counter_collections','live_process_attachments']);assert c['size_queries'] in [0,1] and c['fill_queries'] in [0,1]
 image=OUT/'counter-availability.bin'
 if c['availability_image_obtained']:assert image.is_file() and image.stat().st_size==c['returned_bytes'] and 0<image.stat().st_size<=16*1024**2
 else:assert not image.exists()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody();report={'id':'D104-counter-availability','at':old.now(),'status':'availability_metadata_obtained_collection_unverified' if c['availability_image_obtained'] else 'availability_query_unavailable','protocol_sha256':sys.argv[1],'markers':markers,'binary_sha256':old.sha(H/'build/probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'image':{'path':str(image),'bytes':image.stat().st_size,'sha256':old.sha(image)} if image.exists() else None,'all_owned_children_terminal':True,'application_kernel_launches':0,'profiling_sessions':0,'counter_collections':0,'source_activated':False,'performance_measured':False,'candidate_accepted':False,'limits':'Availability metadata query only, not runtime hardware counter values. Success does not establish permission to enable/collect, replay/graph correctness, observer overhead or speed. Private context destroyed and profiler deinitialized; no elevation/retries/global changes/live attach.'};old.save(H/'report.json',report);print(json.dumps(report),flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
P={k:prior[k] for k in ['gpu_uuid','sdk_dll_paths','required_remaining_reserve_bytes','maximum_additional_disk_reservation_bytes']}
P.update(id='D104-counter-availability',at=old.now(),status='FROZEN_PRE_COMPILER_AND_QUERY',compile_command_line=prior['compile_command_line'].replace(str(parent),str(H)),disk_free_bytes=shutil.disk_usage(ROOT).free,scope='One fresh owned process. CUPTI initialize,one private CUDAcontext,one size query and at mostone fill query after size succeeds(0<size<=16MiB), guarded image output create-new off-tree,context destruction/deinitialize. Zero application kernels/collection/profiling sessions/live attach/elevation/global settings. Stop unsupported/disabled/permission/error; no retry/fallback/version/privilege workaround.',rules='Preserve raw API statuses/image and128guard bytes. Compatibility/availability alone do not prove enable/collection permissions or source-matched performance. Any next enable or collection requires a separately frozen protocol.',performance_measured=False,source_activated=False)
P['input_sha256']=prior['input_sha256']|{str(p):old.sha(p) for p in [H/'probe.cpp',H/'execute.py',H/'api-review.json',Path(__file__),parent/'report.json',parent/'checkpoint.json',ROOT/'comparisons/D103-profiler-support-root-check/report.json']}
old.save(H/'protocol.json',P)
for p in H.iterdir():
 if not p.is_file():continue
 key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id']=='D104' for e in st['experiments']);st['experiments'].append({'id':'D104','at':old.now(),'kind':'diagnostic','title':'Counter availability metadata query','status':'running','correctness':'pending','stage':'Two-phase metadata query only','reason':'D103reports compatible configuration; availability image and real enable/collection permissions remain unverified. Query common SDK metadata API once in a fresh private context; zero app kernels/collection/sessions.','evidence':[{'label':'Frozen availability-only protocol','url':'evidence/D104-counter-availability/protocol.json'},{'label':'Official API and scope review','url':'evidence/D104-counter-availability/api-review.json'}]});st.update(updated_at=old.now(),state='running',active_experiment='D104',stage='D104availability metadata query',activity='Official typed API/driver exports, temporary private context. Query size then image only on success; no session/collection/elevation/global changes.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'status':'availability_query_frozen','protocol_sha256':old.sha(H/'protocol.json'),'inputs':len(P['input_sha256']),'native_executions':0}),flush=True)
