#define WIN32_LEAN_AND_MEAN
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
