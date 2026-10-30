"""Freeze a source-matched, owned-process CUDA module capture and SASS diagnostic."""
import hashlib,json,shutil,subprocess,sys,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D098-driver-machine-code';assert not H.exists();H.mkdir()
V=ROOT/'runs/D085-cupti-activity/vendor'
CU=V/'cuda_cupti/cuda_cupti-windows-x86_64-12.9.79-archive'
RT=V/'cuda_cudart/cuda_cudart-windows-x86_64-12.9.79-archive'
manifest=ROOT/'runs/D085-cupti-activity/redistrib_12.9.1.json'
old.pin(manifest,'8335301010b0023ee1ff61eb11e2600ca62002d76780de4089011ad77e0c7630')
pkg=old.read(manifest)['cuda_nvdisasm']['windows-x86_64']
assert pkg['sha256']=='955ba1f52f7115031f10408ce3cec4c745df41dba8fdf6024c3983d899e9fbbc'
assert shutil.disk_usage(ROOT).free>=54*1024**3
url='https://developer.download.nvidia.com/compute/cuda/redist/'+pkg['relative_path']
archive=H/Path(pkg['relative_path']).name
with urllib.request.urlopen(url,timeout=45) as response,archive.open('xb') as out:shutil.copyfileobj(response,out)
assert archive.stat().st_size==int(pkg['size']);old.pin(archive,pkg['sha256'])
with zipfile.ZipFile(archive) as z:
    names=z.namelist()
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
    z.extractall(H/'vendor')
nvdisasm=next((H/'vendor').rglob('nvdisasm.exe'));assert len(list((H/'vendor').rglob('nvdisasm.exe')))==1
old.save(H/'bootstrap.json',{'at':old.now(),'url':url,'manifest_sha256':old.sha(manifest),'archive_sha256':old.sha(archive),'bytes':archive.stat().st_size,'extracted_sha256':{str(p.relative_to(H)):old.sha(p) for p in (H/'vendor').rglob('*') if p.is_file()},'system_installation_changed':False})
cpp=r'''// D098: owned source-matched module load only; no kernels or counters.
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
'''
(H/'probe.cpp').write_text(cpp,encoding='utf-8',newline='\n')
ptx=ROOT/'runs/E059-resource/execution/baseline.ptx'
resource=old.read(ROOT/'runs/E059-resource/report.json');old.pin(ptx,resource['ptx_sha256']['baseline'])
vcvars=Path(r'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat')
args=['cl','/nologo','/O2','/MT','/EHsc','/std:c++17','/W4','/I'+str(RT/'include'),'/I'+str(CU/'include'),str(H/'probe.cpp'),'/Fo:'+str(H/'build/probe.obj'),'/Fe:'+str(H/'build/probe.exe'),str(CU/'lib/cupti.lib')]
command='cmd.exe /d /s /c "call "'+str(vcvars)+'" >nul && '+subprocess.list2cmdline(args)+'"'
deps=[Path(__file__),H/'probe.cpp',H/'bootstrap.json',ptx,ROOT/'runs/E059-resource/report.json',ROOT/'runs/E059-resource/protocol.json',ROOT/'runs/E059-resource/probe.rs',ROOT/'runs/accepted-E051/baseline.json',old.REPO/'crates/solver/src/gpu/mod.rs',old.REPO/'crates/solver/src/gpu/kernels.cu',Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7\src\driver\result.rs'),vcvars,nvdisasm,CU/'lib/cupti.lib',CU/'lib/cupti64_2025.2.1.dll']
deps+=list((CU/'include').rglob('*.h'))+list((RT/'include').rglob('*.h'))
old.save(H/'protocol.json',{'id':H.name,'at':old.now(),'status':'FROZEN_PRE_BUILD_AND_MODULE_LOAD','command':command,'ptx':str(ptx),'nvdisasm':str(nvdisasm),'private_dll_dir':str(CU/'lib'),'input_sha256':{str(p):old.sha(p) for p in deps},'expected_entries':old.read(ROOT/'runs/E059-resource/protocol.json')['expected_entries'],'gpu_uuid':'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee','native_plan':'Compile once; capture the driver JIT CUBIN of exactly the retained accepted-source compute120 PTX using cuModuleLoadData (same cudarc loader API/default options) in an owned primary context. Query all9 functions and copy each module callback image while callback bytes valid. No CUDA calls inside callback. No kernel launch, activity collection, hardware counters, elevation, injection or live attach. Preserve every image and disassemble each once.','scope':'Source/PTX-matched driver-loaded code, not extraction from the frozen accepted benchmark executable. Static SASS counts are not dynamic executions or speed/precision evidence. Candidate exact reciprocal reuse is not implemented or admitted by this diagnostic.','decision':'Determine existing common-denominator reciprocal sharing and local spills/control flow before proposing any arithmetic change. No timing selection or previous candidate rescue.','official_references':['https://docs.nvidia.com/cupti/12.9.1/api/group__CUPTI__CALLBACK__API.html','https://docs.nvidia.com/cupti/12.9.1/api/structCUpti__ModuleResourceData.html','https://docs.nvidia.com/cuda/archive/12.9.1/cuda-binary-utilities/index.html#nvdisasm'],'reserve_bytes':54*1024**3,'source_activated':False,'kernel_launches':0})
# Finish the prior closed candidate's local commit evidence before new execution.
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip()
assert subprocess.check_output(['git','log','-1','--format=%s'],cwd=old.REPO,text=True).strip()=='research: record E059 allocation rejection and D097 address proof'
rec=ROOT/'runs/E059-closure/commit.json';old.save(rec,{'at':old.now(),'commit':commit,'committed_paths':['research/postflop-gpu-20261016/experiments.md'],'accepted_source':'E051','goal_active':True,'all_owned_children_terminal':True,'no_new_gain_adopted':True})
key='evidence/E059-closure/commit.json';dst=old.ar.DASHBOARD/key;assert not dst.exists();dst.write_bytes(rec.read_bytes())
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==rec.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS)
 next(e for e in s['experiments'] if e['id']=='E059')['evidence'].append({'label':'Local ledger commit','url':key})
 assert not any(e['id']=='D098' for e in s['experiments'])
 s['experiments'].append({'id':'D098','title':'Source-matched driver SASS audit','status':'running','correctness':'pending','notes':'Owned off-tree module capture only; no solves or performance measurement. Inspect whether action-update divisions already share reciprocal work.','evidence':[],'updated_at':old.now()})
 s.update(updated_at=old.now(),state='running',active_experiment='D098',stage='Inspecting compiled action-update divisions',activity='E059 allocation rejection preserved. D098 frozen source-matched module capture will inspect actual driver code without launching kernels. Accepted E051 remains unchanged.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'nvdisasm':str(nvdisasm),'source_activated':False,'E059_commit':commit}),flush=True)
