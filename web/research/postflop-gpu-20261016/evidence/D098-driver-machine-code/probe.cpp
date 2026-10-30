// D098: owned source-matched module load only; no kernels or counters.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cuda.h>
#include <cupti.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <mutex>
#include <string>
#include <vector>
struct Image {uint32_t id;uintptr_t context;std::vector<char> bytes;};
struct State {std::mutex mu;std::vector<Image> images;unsigned faults=0;};
static void CUPTIAPI capture(void* opaque,CUpti_CallbackDomain domain,CUpti_CallbackId id,const void* data) noexcept {
 State* s=static_cast<State*>(opaque);
 try {
  std::lock_guard<std::mutex> guard(s->mu);
  if(domain!=CUPTI_CB_DOMAIN_RESOURCE || id!=CUPTI_CBID_RESOURCE_MODULE_LOADED || !data){s->faults++;return;}
  const auto* rd=static_cast<const CUpti_ResourceData*>(data);
  const auto* md=static_cast<const CUpti_ModuleResourceData*>(rd->resourceDescriptor);
  if(!md || !md->pCubin || md->cubinSize<64 || md->cubinSize>256ull*1024*1024 || s->images.size()>=32){s->faults++;return;}
  if(std::memcmp(md->pCubin,"\x7f" "ELF",4)!=0){s->faults++;return;}
  s->images.push_back(Image{md->moduleId,reinterpret_cast<uintptr_t>(rd->context),std::vector<char>(md->pCubin,md->pCubin+md->cubinSize)});
 } catch(...) {s->faults++;}
}
static void ck(CUresult r,const char* name){if(r!=CUDA_SUCCESS){std::fprintf(stderr,"CUDA %s %d\n",name,int(r));std::exit(10);}}
static void cp(CUptiResult r,const char* name){if(r!=CUPTI_SUCCESS){const char* text=nullptr;cuptiGetResultString(r,&text);std::fprintf(stderr,"CUPTI %s %d %s\n",name,int(r),text?text:"");std::exit(11);}}
template<class T>static T sym(HMODULE dll,const char* name){auto p=GetProcAddress(dll,name);if(!p){std::fprintf(stderr,"missing %s\n",name);std::exit(12);}return reinterpret_cast<T>(p);}
static void write_new(const std::string& path,const std::vector<char>& bytes){HANDLE h=CreateFileA(path.c_str(),GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);if(h==INVALID_HANDLE_VALUE)std::exit(13);DWORD n=0;bool ok=WriteFile(h,bytes.data(),DWORD(bytes.size()),&n,nullptr)&&n==bytes.size()&&FlushFileBuffers(h);CloseHandle(h);if(!ok)std::exit(14);}
int main(int argc,char** argv){
 if(argc!=3)return 2;
 std::ifstream input(argv[1],std::ios::binary);if(!input)return 3;
 std::vector<char> ptx((std::istreambuf_iterator<char>(input)),std::istreambuf_iterator<char>());if(ptx.empty() || ptx.size()>16*1024*1024)return 4;ptx.push_back(0);
 wchar_t directory[MAX_PATH];UINT n=GetSystemDirectoryW(directory,MAX_PATH);if(!n || n>=MAX_PATH)return 5;
 std::wstring driver(directory);driver+=L"\\nvcuda.dll";HMODULE dll=LoadLibraryExW(driver.c_str(),nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);if(!dll)return 6;
 auto init=sym<CUresult(CUDAAPI*)(unsigned)>(dll,"cuInit");
 auto devGet=sym<CUresult(CUDAAPI*)(CUdevice*,int)>(dll,"cuDeviceGet");
 auto devName=sym<CUresult(CUDAAPI*)(char*,int,CUdevice)>(dll,"cuDeviceGetName");
 auto devAttr=sym<CUresult(CUDAAPI*)(int*,CUdevice_attribute,CUdevice)>(dll,"cuDeviceGetAttribute");
 auto drvVersion=sym<CUresult(CUDAAPI*)(int*)>(dll,"cuDriverGetVersion");
 auto retain=sym<CUresult(CUDAAPI*)(CUcontext*,CUdevice)>(dll,"cuDevicePrimaryCtxRetain");
 auto release=sym<CUresult(CUDAAPI*)(CUdevice)>(dll,"cuDevicePrimaryCtxRelease_v2");
 auto current=sym<CUresult(CUDAAPI*)(CUcontext)>(dll,"cuCtxSetCurrent");
 auto load=sym<CUresult(CUDAAPI*)(CUmodule*,const void*)>(dll,"cuModuleLoadData");
 auto unload=sym<CUresult(CUDAAPI*)(CUmodule)>(dll,"cuModuleUnload");
 auto function=sym<CUresult(CUDAAPI*)(CUfunction*,CUmodule,const char*)>(dll,"cuModuleGetFunction");
 auto attribute=sym<CUresult(CUDAAPI*)(int*,CUfunction_attribute,CUfunction)>(dll,"cuFuncGetAttribute");
 auto occupancy=sym<CUresult(CUDAAPI*)(int*,CUfunction,int,size_t)>(dll,"cuOccupancyMaxActiveBlocksPerMultiprocessor");
 ck(init(0),"init");CUdevice device;ck(devGet(&device,0),"device");char name[256]={};ck(devName(name,256,device),"name");int major,minor,version;
 ck(devAttr(&major,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR,device),"major");ck(devAttr(&minor,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR,device),"minor");ck(drvVersion(&version),"version");
 if(std::strcmp(name,"NVIDIA GeForce RTX 5090") || major!=12 || minor!=0)return 7;
 std::printf("D098_DEVICE {\"name\":\"%s\",\"major\":%d,\"minor\":%d,\"driver_api_version\":%d}\n",name,major,minor,version);
 CUcontext ctx;ck(retain(&ctx,device),"retain");ck(current(ctx),"current");
 State state;CUpti_SubscriberHandle subscriber;cp(cuptiSubscribe(&subscriber,capture,&state),"subscribe");cp(cuptiEnableCallback(1,subscriber,CUPTI_CB_DOMAIN_RESOURCE,CUPTI_CBID_RESOURCE_MODULE_LOADED),"enable");
 CUmodule module;ck(load(&module,ptx.data()),"module load");
 const char* names[]={"copy_root","down_action","down_chance","up_fold","up_show","up_chance","up_action","down_eval","up_action_eval"};
 for(const char* k:names){CUfunction f;ck(function(&f,module,k),k);int regs,local,shared,maxthreads,binary,ptxver,a64,a128,a256;
 ck(attribute(&regs,CU_FUNC_ATTRIBUTE_NUM_REGS,f),"regs");ck(attribute(&local,CU_FUNC_ATTRIBUTE_LOCAL_SIZE_BYTES,f),"local");ck(attribute(&shared,CU_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES,f),"shared");ck(attribute(&maxthreads,CU_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK,f),"maxthreads");ck(attribute(&binary,CU_FUNC_ATTRIBUTE_BINARY_VERSION,f),"binary version");ck(attribute(&ptxver,CU_FUNC_ATTRIBUTE_PTX_VERSION,f),"ptx version");
 ck(occupancy(&a64,f,64,0),"occ64");ck(occupancy(&a128,f,128,0),"occ128");ck(occupancy(&a256,f,256,0),"occ256");
 std::printf("D098_KERNEL {\"name\":\"%s\",\"registers\":%d,\"local\":%d,\"shared\":%d,\"maxthreads\":%d,\"binary_version\":%d,\"ptx_version\":%d,\"occupancy64_128_256\":[%d,%d,%d]}\n",k,regs,local,shared,maxthreads,binary,ptxver,a64,a128,a256);
 }
 cp(cuptiEnableCallback(0,subscriber,CUPTI_CB_DOMAIN_RESOURCE,CUPTI_CBID_RESOURCE_MODULE_LOADED),"disable");cp(cuptiUnsubscribe(subscriber),"unsubscribe");
 if(state.faults || state.images.empty())return 8;
 for(size_t i=0;i<state.images.size();i++){const auto& image=state.images[i];if(image.context!=reinterpret_cast<uintptr_t>(ctx))return 9;std::string path=std::string(argv[2])+"\\module-"+std::to_string(i)+".cubin";write_new(path,image.bytes);std::printf("D098_MODULE {\"index\":%zu,\"module_id\":%u,\"bytes\":%zu,\"same_owned_context\":true,\"elf_magic\":true}\n",i,image.id,image.bytes.size());}
 ck(unload(module),"unload");ck(current(nullptr),"clear current");ck(release(device),"release");
 std::printf("D098_COMPLETE {\"callback_errors\":%u,\"modules\":%zu,\"kernel_launches\":0,\"solver_executions\":0,\"performance_measured\":false}\n",state.faults,state.images.size());return 0;
}
