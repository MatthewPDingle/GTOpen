"""Freeze one owned-process CUPTI compatibility query; collect no counters."""
import ast,json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>=54*1024**3
assert old.read(ROOT/'runs/E063-closure/decision.json')['decision']=='rejected_complete_cycle_speed'
H=ROOT/'runs/D103-profiler-support';assert not H.exists();H.mkdir()
V=ROOT/'runs/D085-cupti-activity/vendor';cupti=V/'cuda_cupti/cuda_cupti-windows-x86_64-12.9.79-archive';cuda=V/'cuda_cudart/cuda_cudart-windows-x86_64-12.9.79-archive'
assert (cupti/'include/cupti_profiler_target.h').is_file() and (cuda/'include/cuda.h').is_file()
cpp=r'''#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <Windows.h>
#include <cuda.h>
#include <cupti_profiler_target.h>
#include <cupti_version.h>
#include <cstdio>
#include <string>
#include <stdexcept>
static std::string q(const char* s){std::string o="\"";for(unsigned char c:std::string(s?s:"")){if(c=='"'||c=='\\'){o+='\\';o+=char(c);}else if(c=='\n')o+="\\n";else if(c=='\r')o+="\\r";else if(c=='\t')o+="\\t";else if(c<32){char b[8];sprintf_s(b,"\\u%04x",unsigned(c));o+=b;}else o+=char(c);}return o+'"';}
static HMODULE load(const wchar_t* path){auto m=LoadLibraryExW(path,nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);if(!m)throw std::runtime_error("LoadLibraryExW:"+std::to_string(GetLastError()));return m;}
template<class F> static F fn(HMODULE m,const char* name){auto p=GetProcAddress(m,name);if(!p)throw std::runtime_error(std::string("missing export:")+name);return reinterpret_cast<F>(p);}
int wmain(int argc,wchar_t** argv){
 try {
  if(argc!=4)throw std::runtime_error("expected3absolute SDK DLL paths");
  wchar_t system[MAX_PATH];UINT n=GetSystemDirectoryW(system,MAX_PATH);if(!n||n>=MAX_PATH)throw std::runtime_error("system directory");
  std::wstring driver=std::wstring(system)+L"\\nvcuda.dll";auto d=load(driver.c_str());
  auto init=fn<decltype(&cuInit)>(d,"cuInit");auto get=fn<decltype(&cuDeviceGet)>(d,"cuDeviceGet");auto name=fn<decltype(&cuDeviceGetName)>(d,"cuDeviceGetName");auto attr=fn<decltype(&cuDeviceGetAttribute)>(d,"cuDeviceGetAttribute");auto version=fn<decltype(&cuDriverGetVersion)>(d,"cuDriverGetVersion");
  if(init(0)!=CUDA_SUCCESS)throw std::runtime_error("cuInit failed");CUdevice device; if(get(&device,0)!=CUDA_SUCCESS)throw std::runtime_error("device0 lookup failed");
  char device_name[256]={};int major=0,minor=0,driver_version=0;
  if(name(device_name,256,device)!=CUDA_SUCCESS||attr(&major,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR,device)!=CUDA_SUCCESS||attr(&minor,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR,device)!=CUDA_SUCCESS||version(&driver_version)!=CUDA_SUCCESS)throw std::runtime_error("device identity query failed");
  if(std::string(device_name)!="NVIDIA GeForce RTX 5090"||major!=12||minor!=0)throw std::runtime_error("unexpected device");
  // Absolute private SDK dependencies, current process only. No system installation/settings.
  auto host=load(argv[2]);auto target=load(argv[3]);auto lib=load(argv[1]);(void)host;(void)target;
  auto getversion=fn<decltype(&cuptiGetVersion)>(lib,"cuptiGetVersion");auto resultstr=fn<decltype(&cuptiGetResultString)>(lib,"cuptiGetResultString");
  auto initialize=fn<decltype(&cuptiProfilerInitialize)>(lib,"cuptiProfilerInitialize");auto supported=fn<decltype(&cuptiProfilerDeviceSupported)>(lib,"cuptiProfilerDeviceSupported");auto deinitialize=fn<decltype(&cuptiProfilerDeInitialize)>(lib,"cuptiProfilerDeInitialize");
  auto label=[&](CUptiResult r){const char* s=nullptr;resultstr(r,&s);return q(s);};uint32_t api_version=0;auto vr=getversion(&api_version);if(vr!=CUPTI_SUCCESS||api_version!=CUPTI_API_VERSION)throw std::runtime_error("CUPTI header/library version mismatch");
  printf("D103_RESULT {\"stage\":\"identity\",\"device\":%s,\"major\":%d,\"minor\":%d,\"driver_version\":%d,\"CUPTI_API_VERSION\":%u,\"initialize_struct_size\":%zu,\"support_struct_size\":%zu,\"deinitialize_struct_size\":%zu}\n",q(device_name).c_str(),major,minor,driver_version,api_version,size_t(CUpti_Profiler_Initialize_Params_STRUCT_SIZE),size_t(CUpti_Profiler_DeviceSupported_Params_STRUCT_SIZE),size_t(CUpti_Profiler_DeInitialize_Params_STRUCT_SIZE));fflush(stdout);
  CUpti_Profiler_Initialize_Params ip={};ip.structSize=CUpti_Profiler_Initialize_Params_STRUCT_SIZE;auto ir=initialize(&ip);
  printf("D103_RESULT {\"stage\":\"initialize\",\"result\":%d,\"result_name\":%s}\n",int(ir),label(ir).c_str());fflush(stdout);
  bool compatible=false;int queries=0;CUptiResult dr=CUPTI_SUCCESS;
  if(ir==CUPTI_SUCCESS){
   CUpti_Profiler_DeviceSupported_Params p={};p.structSize=CUpti_Profiler_DeviceSupported_Params_STRUCT_SIZE;p.cuDevice=device;p.api=CUPTI_PROFILER_RANGE_PROFILING;auto sr=supported(&p);queries=1;
   compatible=sr==CUPTI_SUCCESS&&p.isSupported==CUPTI_PROFILER_CONFIGURATION_SUPPORTED;
   printf("D103_RESULT {\"stage\":\"range_support\",\"result\":%d,\"result_name\":%s,\"api\":%d,\"isSupported\":%d,\"architecture\":%d,\"sli\":%d,\"vGpu\":%d,\"confidentialCompute\":%d,\"cmp\":%d,\"wsl\":%d,\"supported_enum_value\":%d}\n",int(sr),label(sr).c_str(),int(p.api),int(p.isSupported),int(p.architecture),int(p.sli),int(p.vGpu),int(p.confidentialCompute),int(p.cmp),int(p.wsl),int(CUPTI_PROFILER_CONFIGURATION_SUPPORTED));fflush(stdout);
   CUpti_Profiler_DeInitialize_Params dp={};dp.structSize=CUpti_Profiler_DeInitialize_Params_STRUCT_SIZE;dr=deinitialize(&dp);
   printf("D103_RESULT {\"stage\":\"deinitialize\",\"result\":%d,\"result_name\":%s}\n",int(dr),label(dr).c_str());fflush(stdout);
  }
  printf("D103_RESULT {\"stage\":\"complete\",\"device_configuration_compatible\":%s,\"support_queries\":%d,\"cleanup_success\":%s,\"application_kernel_launches\":0,\"profiling_sessions\":0,\"counter_collections\":0,\"live_process_attachments\":0,\"explicit_cuda_context_creations\":0,\"performance_measured\":false}\n",compatible?"true":"false",queries,dr==CUPTI_SUCCESS?"true":"false");fflush(stdout);return dr==CUPTI_SUCCESS?0:2;
 }catch(const std::exception& e){printf("D103_RESULT {\"stage\":\"invalid\",\"error\":%s}\n",q(e.what()).c_str());fflush(stdout);return 1;}
}
'''
(H/'probe.cpp').write_text(cpp,encoding='utf-8',newline='\n')
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
 old.child([str(H/'build/probe.exe'),*P['sdk_dll_paths']],OUT,'probe',env,120)
 markers=[json.loads(x.split('D103_RESULT ',1)[1]) for x in (OUT/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if x.startswith('D103_RESULT ')];assert markers[0]['stage']=='identity' and markers[-1]['stage']=='complete';c=markers[-1]
 assert c['cleanup_success'] and all(c[k]==0 for k in ['application_kernel_launches','profiling_sessions','counter_collections','live_process_attachments','explicit_cuda_context_creations']);assert c['support_queries'] in [0,1]
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody();report={'id':'D103-profiler-support','at':old.now(),'status':'configuration_reports_compatible_collection_unverified' if c['device_configuration_compatible'] else 'profiler_configuration_unavailable','protocol_sha256':sys.argv[1],'markers':markers,'binary_sha256':old.sha(H/'build/probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'all_children_terminal':True,'application_kernel_launches':0,'counter_collections':0,'profiling_sessions':0,'source_activated':False,'performance_measured':False,'candidate_accepted':False,'limits':'Installed official SDK compatibility query in fresh owned process only. A supported result does not establish counter availability/permission, actual collection, replay fidelity, graph support, low observer overhead or a speedup. No elevation, retries, driver/global settings, live attach or application kernels.'};old.save(H/'report.json',report);print(json.dumps(report),flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
vcvars=Path(r'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat');assert vcvars.is_file()
args=['cl.exe','/nologo','/O2','/EHsc','/std:c++17','/I'+str(cupti/'include'),'/I'+str(cuda/'include'),'/Fe:'+str(H/'build/probe.exe'),'/Fo:'+str(H/'build/probe.obj'),'/Fd:'+str(H/'build/probe.pdb'),str(H/'probe.cpp')]
command='cmd.exe /d /s /c "call "'+str(vcvars)+'" >nul && '+subprocess.list2cmdline(args)+'"'
dlls=[cupti/'lib'/n for n in ['cupti64_2025.2.1.dll','nvperf_host.dll','nvperf_target.dll']]
paths=[H/'probe.cpp',H/'execute.py',Path(__file__),vcvars,*dlls,*list((cupti/'include').rglob('*.h')),*list((cuda/'include').rglob('*.h')),ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/E063-closure/decision.json',ROOT/'runs/D087-cupti-driver-profile/ability.rs',ROOT/'runs/D085-cupti-activity/redistrib_12.9.1.json',Path(r'C:\Windows\System32\nvcuda.dll')]
assert all(p.is_file() for p in paths)
P={'id':'D103-profiler-support','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_QUERY','compile_command_line':command,'sdk_dll_paths':[str(p) for p in dlls],'input_sha256':{str(p):old.sha(p) for p in paths},'gpu_uuid':old.read(ROOT/'runs/E063-resource/protocol.json')['gpu_uuid'],'scope':'Exactly one fresh-process official CUPTI profiler initialize, at most one RANGE_PROFILING compatibility query, and successful deinitialize when initialized. No context creation/app kernels/collection/session/live attach/elevation/global driver/settings changes. Unsupported/disabled/permission/error stops this route without retry or workaround.','rules':'Report raw result enums/flags. Even SUPPORTED is compatibility only, not permission/available metrics/actual collection/observer-quality proof. Any collection needs separately frozen source-matched exactness and observer protocol. Source stays acceptedE051.','required_remaining_reserve_bytes':50*1024**3,'maximum_additional_disk_reservation_bytes':256*1024**2,'disk_free_bytes':shutil.disk_usage(ROOT).free,'performance_measured':False,'source_activated':False};old.save(H/'protocol.json',P)
for p in H.iterdir():
 if not p.is_file():continue
 key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id']=='D103' for e in st['experiments']);st['experiments'].append({'id':'D103','at':old.now(),'kind':'diagnostic','title':'Official CUPTI profiler compatibility query','status':'running','correctness':'pending','stage':'One fresh-process compatibility query, no counters','reason':'CLI availability and old activity/graph traces did not query the separate profiler API. Check installed official SDK compatibility once, no collection/elevation/global changes/live attach.','evidence':[{'label':'Frozen query-only protocol','url':'evidence/D103-profiler-support/protocol.json'}]});st.update(updated_at=old.now(),state='running',active_experiment='D103',stage='D103 profiler compatibility query',activity='Fresh owned process, official typed ABI, private SDK libraries. Compatibility query only; zero application kernels/counters and no performance claim.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'status':'query_only_plan_frozen','protocol_sha256':old.sha(H/'protocol.json'),'pinned_inputs':len(P['input_sha256']),'compile_command_line':command}),flush=True)
