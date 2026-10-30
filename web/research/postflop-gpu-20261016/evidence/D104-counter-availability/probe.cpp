#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <Windows.h>
#include <cuda.h>
#include <cupti_profiler_target.h>
#include <cupti_version.h>
#include <cstdio>
#include <string>
#include <stdexcept>
#include <vector>
#include <algorithm>
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
  auto initialize=fn<decltype(&cuptiProfilerInitialize)>(lib,"cuptiProfilerInitialize");auto availability=fn<decltype(&cuptiProfilerGetCounterAvailability)>(lib,"cuptiProfilerGetCounterAvailability");auto deinitialize=fn<decltype(&cuptiProfilerDeInitialize)>(lib,"cuptiProfilerDeInitialize");
  auto label=[&](CUptiResult r){const char* s=nullptr;resultstr(r,&s);return q(s);};uint32_t api_version=0;auto vr=getversion(&api_version);if(vr!=CUPTI_SUCCESS||api_version!=CUPTI_API_VERSION)throw std::runtime_error("CUPTI header/library version mismatch");
  printf("D104_RESULT {\"stage\":\"identity\",\"device\":%s,\"major\":%d,\"minor\":%d,\"driver_version\":%d,\"CUPTI_API_VERSION\":%u,\"initialize_struct_size\":%zu,\"support_struct_size\":%zu,\"deinitialize_struct_size\":%zu}\n",q(device_name).c_str(),major,minor,driver_version,api_version,size_t(CUpti_Profiler_Initialize_Params_STRUCT_SIZE),size_t(CUpti_Profiler_DeviceSupported_Params_STRUCT_SIZE),size_t(CUpti_Profiler_DeInitialize_Params_STRUCT_SIZE));fflush(stdout);
  CUpti_Profiler_Initialize_Params ip={};ip.structSize=CUpti_Profiler_Initialize_Params_STRUCT_SIZE;auto ir=initialize(&ip);
  printf("D104_RESULT {\"stage\":\"initialize\",\"result\":%d,\"result_name\":%s}\n",int(ir),label(ir).c_str());fflush(stdout);
  auto create=fn<decltype(&cuCtxCreate)>(d,"cuCtxCreate_v2");auto destroy=fn<decltype(&cuCtxDestroy)>(d,"cuCtxDestroy_v2");auto current=fn<decltype(&cuCtxGetCurrent)>(d,"cuCtxGetCurrent");
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
  printf("D104_RESULT {\"stage\":\"complete\",\"availability_image_obtained\":%s,\"size_queries\":%d,\"fill_queries\":%d,\"requested_bytes\":%zu,\"returned_bytes\":%zu,\"private_contexts_created\":%d,\"private_contexts_destroyed\":%d,\"current_context_after_is_null\":%s,\"cleanup_success\":%s,\"guards_exact\":%s,\"application_kernel_launches\":0,\"profiling_sessions\":0,\"counter_collections\":0,\"live_process_attachments\":0,\"performance_measured\":false}\n",obtained?"true":"false",size_calls,fill_calls,requested,returned,created,destroyed,after==nullptr?"true":"false",clean?"true":"false",guards?"true":"false");fflush(stdout);return clean&&guards?0:2;
 }catch(const std::exception& e){printf("D104_RESULT {\"stage\":\"invalid\",\"error\":%s}\n",q(e.what()).c_str());fflush(stdout);return 1;}
}
